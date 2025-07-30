import hashlib
import json
from loguru import logger
import math
import requests
import tcvectordb
from tcvectordb.model.document import Document, Filter, SearchParams
from tcvectordb.model.collection import Collection, Embedding
from tcvectordb.model.enum import FieldType, IndexType, MetricType, EmbeddingModel
from tcvectordb.model.index import Index, VectorIndex, FilterIndex, IVFFLATParams
import time
from typing import Dict, List, Optional, Tuple, Union
from typing_extensions import override

from vector_db_sdk.constants import ConditionFields, IndexType as IType
from vector_db_sdk.libvector import CONTENT_COL, METADATA_COL, LibVector
from vector_db_sdk.util import DistanceStrategy

BATCH_LIMIT = 1_000
TC_VECTOR_FIELD = "vector"


class TcVector(LibVector):
    def __init__(self, connection_dict: Dict[str, Union[str, int]], distance: DistanceStrategy, col_names: Dict[str, str] = {}, timeout: float = None) -> None:
        self.connection_dict = connection_dict
        host = connection_dict["host"]
        if not host.startswith("http://"):
            host = "http://" + host
            connection_dict["host"] = host
        self.db = tcvectordb.VectorDBClient("{}:{}".format(
            host, connection_dict["port"]),
            connection_dict["user"],
            connection_dict["password"]
        )
        self.distance = DistanceStrategy(distance)
        self.content_col = col_names.get(CONTENT_COL, CONTENT_COL)
        self.metadata_col = col_names.get(METADATA_COL, METADATA_COL)
        self.timeout = timeout
        self._checked = {}

        schema = connection_dict.get("schema", "public")
        self.schema = self.db.create_database_if_not_exists(schema, timeout=self.timeout)

    def _create_table(self, table_name: str, partitions: Dict[str, any], vector_length: int, num_rows: int) -> Collection:
        table_name = table_name.lower()
        if table_name in self._checked:
            return self.schema.collection(table_name)
        indices = {}
        for partition, value in partitions.items():
            if isinstance(value, str):
                indices[partition] = IType.String
            elif isinstance(value, int):
                indices[partition] = IType.Uint
            elif isinstance(value, list):
                indices[partition] = IType.Array
        table = self.create_table(table_name, indices, "auto-generated", vector_length, num_rows)
        self._checked[table_name] = 1
        return table

    def _generate_id(self, partition_kv: List[Tuple[str, any]], content: str) -> str:
        partition_kv = sorted(partition_kv, key=lambda x: x[0])
        id_components = [str(v) for _, v in partition_kv]
        id_components.append(hashlib.md5(content.encode(encoding="utf-8")).hexdigest())
        id = "_".join([component if len(component) <= 32 else hashlib.md5(component.encode(encoding="utf-8")).hexdigest() for component in id_components])
        return id

    def _parse_conditions(self, conditions: List[dict]) -> Union[Filter, None]:
        conditions_str = []
        for condition in conditions:
            operator = condition[ConditionFields.Operator.value].lower()
            value = condition[ConditionFields.Values.value]
            if isinstance(value, str):
                value = f"\"{value}\""
            elif isinstance(value, list):
                if isinstance(value[0], str):
                    value = "({})".format(",".join(["\"{}\"".format(element) for element in value]))
                else:
                    value = "({})".format(",".join(value))
            conditions_str.append("{} {} {}".format(condition[ConditionFields.Field.value], operator, value))
        tc_filter = None if len(conditions_str) == 0 else Filter(conditions_str[0])
        for condition in conditions_str[1:]:
            tc_filter = tc_filter.And(condition)
        return tc_filter

    @override
    def create_table(self, table_name: str, indices: Dict[str, IType], description: str, vector_length: int, num_rows: int = 1, model_name: str = "") -> Collection:
        table_name = table_name.lower()
        index = Index()
        # vector column must be named vector
        # nlist [4, 16] * sqrt(rows), https://cloud.tencent.com/document/product/1709/98689
        # 1536, 2478
        n_lists = max(1, int(min(num_rows / 30, 4 * math.sqrt(num_rows))))
        metric_type = MetricType.COSINE
        if self.distance == DistanceStrategy.COSINE:
            metric_type = MetricType.COSINE
        elif self.distance == DistanceStrategy.EUCLIDEAN:
            metric_type = MetricType.L2
        elif self.distance == DistanceStrategy.MAX_INNER_PRODUCT:
            metric_type = MetricType.IP
        index.add(VectorIndex(TC_VECTOR_FIELD, vector_length, IndexType.FLAT, metric_type))
        index.add(FilterIndex("id", FieldType.String, IndexType.PRIMARY_KEY))
        index.add(FilterIndex(self.content_col, FieldType.String, IndexType.FILTER))
        for index_name, index_type in indices.items():
            if index_type == IType.String:
                index.add(FilterIndex(index_name, FieldType.String, IndexType.FILTER))
            elif index_type == IType.Uint:
                index.add(FilterIndex(index_name, FieldType.Uint64, IndexType.FILTER))
            elif index_type == IType.Array:
                index.add(FilterIndex(index_name, FieldType.Array, IndexType.FILTER))

        embedding = None
        if model_name in ["BAAI/bge-m3"]:
            embedding = Embedding(vector_field=TC_VECTOR_FIELD, field=self.content_col, model_name=model_name)

        replica_num = 0
        last_e = Exception("create table failed")
        for _ in range(2):
            try:
                table = self.schema.create_collection(table_name, 1, replica_num, description, index, embedding=embedding, timeout=self.timeout)
                table.index.indexes.get(TC_VECTOR_FIELD)
                return table
            except tcvectordb.exceptions.ServerInternalError as e:
                last_e = e
                if e.message.startswith("replicanum"):
                    _, _, info = e.message.partition("between ")
                    info, _, _ = info.partition(",")
                    nums = info.split(" and ")
                    if len(nums) != 2:
                        raise e
                    logger.debug("Db supports replicas [{},{}]".format(int(nums[0]), int(nums[1])))
                    replica_num = min(2, int(nums[1]))
                elif e.message == "Collection already exist: {}".format(table_name):
                    logger.debug("Table {} already exists".format(table_name))
                    return self.schema.collection(table_name)
                else:
                    raise e
        raise last_e

    @override
    def delete_row_by_id(self, table_name: str, partitions_list: List[Dict[str, any]], contents: List[str], ids: List[str] = []) -> int:
        table_name = table_name.lower()
        partition_kvs_list = [[(k, v) for k, v in partitions_list[i].items()] for i in range(len(contents))]
        new_ids = [self._generate_id(partition_kvs_list[i], contents[i]) for i in range(len(contents))]
        new_ids.extend(ids)
        table = self.schema.collection(table_name)
        return table.delete(document_ids=new_ids, timeout=self.timeout).get("affectedCount", 0)

    @override
    def delete_rows(self, table_name: str, conditions: List[dict]) -> int:
        table_name = table_name.lower()
        tc_filter = self._parse_conditions(conditions)
        table = self.schema.collection(table_name)
        return table.delete(filter=tc_filter, timeout=self.timeout).get("affectedCount", 0)

    @override
    def delete_table(self, table_name: str):
        table_name = table_name.lower()
        self.schema.drop_collection(table_name, timeout=self.timeout)
        if table_name in self._checked:
            del self._checked[table_name]

    @override
    def insert_db(self, table_name: str, embeddings: Union[List[List[float]], None], contents: List[str],
                  tags: List[str], dimension: int, metadatas: Optional[List[Dict[str, any]]] = None, build_index: bool = False):
        table_name = table_name.lower()
        if embeddings is not None:
            table = self._create_table(table_name, {}, len(embeddings[0]), len(embeddings))
            documents = [Document(id=hashlib.md5(content.encode(encoding="utf-8")).hexdigest(), vector=embedding, metadatas=json.dumps(metadata, ensure_ascii=False))
                        for embedding, content, metadata in zip(embeddings, contents, metadatas)]
        else:
            # TODO: use create table
            table = self.schema.collection(table_name)
            documents = [Document(id=hashlib.md5(content.encode(encoding="utf-8")).hexdigest(), metadatas=json.dumps(metadata, ensure_ascii=False))
                        for content, metadata in zip(contents, metadatas)]
        table.upsert(documents, build_index=build_index, timeout=self.timeout)

    @override
    def insert_custom_db_multiple(self, table_name: str, embeddings: Union[List[List[float]], None], partitions: List[str] = [], filters: List = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        table_name = table_name.lower()
        partition_dict = {partition: extra[partition][0] for partition in partitions}
        for filter in filters:
            partition_dict[filter] = extra[filter][0]

        if embeddings is not None and len(embeddings) > 0 and len(embeddings[0]) > 0:
            table = self._create_table(table_name, partition_dict, len(embeddings[0]), len(embeddings))
        table = self.schema.collection(table_name)

        other_cols = {}
        rows = len(extra[self.content_col])
        partition_kvs_list = [[(k, v[i]) for k, v in extra.items() if k in partitions] for i in range(rows)]
        ids = [self._generate_id(partition_kvs_list[i], extra[self.content_col][i]) for i in range(rows)]
        for key, value in extra.items():
            if isinstance(value[0], dict):
                value = [json.dumps(value_row, ensure_ascii=False) for value_row in value]
            other_cols[key] = value

        if self.metadata_col not in other_cols:
            other_cols[self.metadata_col] = [json.dumps({}, ensure_ascii=False)] * rows
        if embeddings is not None and len(embeddings) > 0 and len(embeddings[0]) > 0:
            documents = [Document(id=ids[i], vector=embeddings[i], **{k: v[i] for k, v in other_cols.items()}) for i in range(rows)]
        else:
            documents = [Document(id=ids[i], **{k: v[i] for k, v in other_cols.items()}) for i in range(rows)]
        for i in range(int(len(documents) // BATCH_LIMIT) + 1):
            docs = documents[i * BATCH_LIMIT: (i + 1) * BATCH_LIMIT]
            if len(docs) == 0:
                break
            for _ in range(3):
                try:
                    table.upsert(docs, build_index=build_index, timeout=self.timeout)
                except tcvectordb.exceptions.ServerInternalError as e:
                    if e.message != "There was an error with the embedding: token rate limit reached":
                        raise e
                    else:
                        logger.warning("embedding rate limit, retrying")
                        time.sleep(1)

    @override
    def list_schemas(self) -> List[str]:
        return [d.database_name for d in self.db.list_databases(timeout=self.timeout)]

    @override
    def list_tables(self, schema: str = "") -> List[str]:
        if schema != "":
            return [c.collection_name for c in self.db.list_collections(schema, timeout=self.timeout)]
        else:
            return [c.collection_name for c in self.schema.list_collections(timeout=self.timeout)]

    @override
    def query(self, table_name: str, limit: int = 16384, offset: int = 0, conditions: List[dict] = [], output_fields: List[str] = []) -> List[Dict[str, any]]:
        table_name = table_name.lower()
        table = self.schema.collection(table_name)
        tc_filter = self._parse_conditions(conditions)
        return table.query(limit=limit, offset=offset, filter=tc_filter, output_fields=output_fields if len(output_fields) > 0 else None, timeout=self.timeout)

    @override
    def row_count(self, table_name: str) -> int:
        table_name = table_name.lower()
        table = self.schema.collection(table_name)
        return table.document_count

    def _single_table_similarity_search(self, table_name: str, embeddings: Union[List[List[float]], None], probes: int, k: int,
                                 score_threshold: Union[float, None], conditions: List[dict], operators: List[str],
                                 distance: DistanceStrategy = None, search_fields: List[str] = [], contents: List[str] = []) -> List[List[Dict[str, any]]]:
        if distance is not None:
            logger.warning("distance is deprecated for tencent vector similarity search function.")
        table_name = table_name.lower()
        table = self.schema.collection(table_name)
        if probes is None:
            ivf_flat_params = table.index.indexes.get(TC_VECTOR_FIELD).param
            if ivf_flat_params is not None:
                probes = ivf_flat_params["nlist"]
        params = SearchParams(nprobe=probes) if probes is not None else None
        index_distance = table.index.indexes[TC_VECTOR_FIELD].metricType.value.lower()

        tc_filter = self._parse_conditions(conditions)
        if embeddings is not None:
            results = table.search(embeddings, tc_filter, params=params, retrieve_vector=False, limit=k, radius=score_threshold, output_fields=[self.content_col, self.metadata_col, *search_fields], timeout=self.timeout)
        else:
            text_result = table.searchByText(contents, tc_filter, params=params, retrieve_vector=False, limit=k, radius=score_threshold, output_fields=[self.content_col, self.metadata_col, *search_fields], timeout=self.timeout)
            if text_result.get("warning", "") != "":
                logger.warning(text_result["warning"])
            results = text_result.get("documents", [])
        search_results = []
        for result in results:
            single_search_result = []
            for item in result:
                if score_threshold is not None and ((item["score"] > score_threshold and index_distance == MetricType.L2) or (item["score"] < score_threshold and index_distance != MetricType.L2)):
                    continue
                data = {key: item.get(key) for key in search_fields}
                data["text"] = item[self.content_col]
                data["metadata"] = json.loads(item[self.metadata_col])
                data["score"] = item["score"]
                single_search_result.append(data)
            search_results.append(single_search_result)
        return search_results

    @override
    def add_index(self, table_name: str, force: bool = False):
        table_name = table_name.lower()

        if not force:
            table = self.schema.collection(table_name)
            table.rebuild_index(timeout=self.timeout)
        else:
            connection_dict = self.connection_dict
            url = "{}:{}/index/rebuild".format(connection_dict["host"], connection_dict["port"])
            headers = {
                "Authorization": "Bearer account={}&api_key={}".format(connection_dict["user"], connection_dict["password"])
            }
            data = {
                "database": connection_dict.get("schema", "public"),
                "collection": table_name,
                "dropBeforeRebuild": False,
                "throttle": 1,
                "force_rebuild": True
            }
            requests.post(url, headers=headers, json=data, timeout=self.timeout)
        status = ""
        while status not in ["ready", "failed"]:
            time.sleep(3)
            status = self.schema.describe_collection(table_name).index_status["status"]
        if status == "failed":
            raise Exception("Failed to build index")

    def __del__(self):
        self.db.close()
