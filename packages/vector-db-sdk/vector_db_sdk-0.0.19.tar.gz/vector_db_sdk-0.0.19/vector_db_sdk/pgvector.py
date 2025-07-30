import json
from loguru import logger
from psycopg2.extras import Json
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.pool import QueuePool
from threading import Lock
import time
from typing import Dict, List, Optional, Union
from typing_extensions import override

from vector_db_sdk.constants import ConditionFields
from vector_db_sdk.libvector import CONTENT_COL, EMBEDDING_COL, METADATA_COL, LibVector, ivfflat_index_list_calculation
from vector_db_sdk.util import DistanceStrategy

SCHEMA_PREFIX = "schema_"
TABLE_PREFIX = "table_"
INDEX_PREFIX = "index_"
PROBE_PREFIX = "probes_"

COLLECTION_TABLE = "tb_collection"
TABLE_NAME_COL = "table_name"
TAG_NAME_COL = "tags"
CONTENT_CONSTRAINT_FORMAT = "md5({}::TEXT)"

def _clean(text: str) -> str:
    return text.replace("'", "''").replace("%", "%%")


class PGVector(LibVector):
    def __init__(self, connection_dict: Dict[str, Union[str, int]], distance: DistanceStrategy, col_names: Dict[str, str] = {}, timeout: float = None) -> None:
        url = URL.create(drivername="postgresql",
                         username=connection_dict["user"],
                         password=connection_dict["password"],
                         host=connection_dict["host"],
                         port=connection_dict["port"],
                         database=connection_dict["database"])
        self._connections = 0
        self._mutex = Lock()
        self._engine = create_engine(url, poolclass=QueuePool, client_encoding="utf8", pool_size=5, pool_use_lifo=True, pool_pre_ping=True, connect_args={"connect_timeout": 10})
        self.distance = DistanceStrategy(distance)
        self._checked = {}

        self.content_col = col_names.get(CONTENT_COL, CONTENT_COL)
        self.embedding_col = col_names.get(EMBEDDING_COL, EMBEDDING_COL)
        self.metadata_col = col_names.get(METADATA_COL, METADATA_COL)

        self.schema = connection_dict.get("schema", "public")

    def _check_schema(self):
        key = SCHEMA_PREFIX + self.schema
        if key in self._checked:
            return

        query = f"SELECT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = '{self.schema}')"
        with self._get_connection() as (connection, cursor):
            cursor.execute(query)
            result = cursor.fetchone()
            connection.commit()

        if not result[0]:
            query = f"CREATE SCHEMA {self.schema}"
            self.execute(query, commit=True)
        self._checked[key] = 1

    def _check_collection_table(self):
        key = TABLE_PREFIX + COLLECTION_TABLE
        if key in self._checked:
            return

        query = f"CREATE TABLE IF NOT EXISTS {self.schema}.{COLLECTION_TABLE} (" \
                "table_name VARCHAR(255) PRIMARY KEY, " \
                "tags VARCHAR(255))"
        self.execute(query, commit=True)
        self._checked[key] = 1

    def _check_table(self, table_name: str, tags: List[str], dimension: int, partitions: List[str], other_columns: Dict[str, any]):
        key = INDEX_PREFIX + table_name
        if key in self._checked:
            return

        if len(tags) > 0:
            tags_str = " ".join(tags) + " "
            query = f"INSERT INTO {self.schema}.{COLLECTION_TABLE} ({TABLE_NAME_COL}, {TAG_NAME_COL}) VALUES ('{table_name}', '{tags_str}')"\
                    f"ON CONFLICT({TABLE_NAME_COL}) DO UPDATE SET {TAG_NAME_COL} = EXCLUDED.{TAG_NAME_COL}"
            self.execute(query, (table_name, tags_str), commit=True)

        other_columns_definition = [""]
        for col_name, value in other_columns.items():
            if col_name in [self.content_col, self.metadata_col]:
                continue
            col_type = ""
            if isinstance(value, str):
                col_type = "VARCHAR(64)"
            elif isinstance(value, int):
                col_type = "INTEGER"
            elif isinstance(value, float):
                col_type = "DECIMAL"
            if col_type == "":
                raise Exception("Unknown column type: {} {}".format(col_name, value))
            other_columns_definition.append(f"{col_name} {col_type}")
        other_columns_str = ",".join(other_columns_definition)
        query = f"CREATE TABLE IF NOT EXISTS {self.schema}.{table_name} (" \
                f"{self.content_col} TEXT," \
                f"{self.embedding_col} VECTOR({dimension})," \
                f"{self.metadata_col} JSON {other_columns_str})"
        if len(partitions) > 0:
            query += " PARTITION BY LIST({})".format(partitions[0])
        self.execute(query, commit=True)

        constraints = self._get_pkey_constraints(partitions)
        query = f"CREATE UNIQUE INDEX IF NOT EXISTS {self.schema}_{table_name}_pkey_md5hash_idx" \
                f" ON {self.schema}.{table_name} USING BTREE ({constraints})"
        self.execute(query, commit=True)

        self._checked[key] = 1

    def _create_partition_table(self, table_name: str, partition_val: list):
        if len(partition_val) == 0:
            return

        key = TABLE_PREFIX + table_name + "_" + "_".join([row[1].replace("-", "") for row in partition_val])
        if key in self._checked:
            return
        is_last_partition = len(partition_val) == 1
        partition, value = partition_val[0]
        partition_name = value.replace("-", "")
        partition_table_name = f"{table_name}_{partition_name}"

        if is_last_partition:
            query = f"CREATE TABLE IF NOT EXISTS {self.schema}.{partition_table_name} PARTITION OF {self.schema}.{table_name} FOR VALUES IN ('{value}')"
        else:
            next_col = partition_val[1][0]
            query = f"CREATE TABLE IF NOT EXISTS {self.schema}.{partition_table_name} PARTITION OF {self.schema}.{table_name} FOR VALUES IN ('{value}') "\
                    f"PARTITION BY LIST({next_col})"
        self.execute(query, commit=True)

        self._create_partition_table(partition_table_name, partition_val[1:])
        self._checked[key] = 1

    def _get_connection(self):
        return PgConnManager(self)

    def _get_table_def(self, table_name):
        return Table(table_name, MetaData(schema=self.schema), autoload_with=self._engine)

    def _get_pkey_constraints(self, partitions: List[str]):
        constraints = partitions + [CONTENT_CONSTRAINT_FORMAT.format(self.content_col)]
        return ",".join(constraints)

    def _get_probes(self, table_name: str) -> int:
        key = PROBE_PREFIX + table_name
        if key in self._checked:
            return self._checked[key]

        query = f"SELECT COUNT(*) FROM {self.schema}.{table_name}"
        total_row = self.execute(query, fetchall=True, commit=True)[0][0]
        probes = ivfflat_index_list_calculation(total_row)
        self._checked[key] = probes
        return probes

    def _parse_conditions(self, conditions: List[dict], distance: Union[DistanceStrategy, None] = None, embedding: List[float] = [], score_threshold: Union[float, None] = None) -> str:
        if distance is DistanceStrategy.EUCLIDEAN:
            distance_query = f"{self.embedding_col} <-> '{embedding}'"
        elif distance is DistanceStrategy.MAX_INNER_PRODUCT:
            distance_query = f"({self.embedding_col} <#> '{embedding}')"
        else:
            distance_query = f"({self.embedding_col} <=> '{embedding}')"

        conditions_str = []
        if score_threshold is not None:
            conditions_str.append(f"{distance_query} <= {score_threshold}")

        for condition in conditions:
            value = condition[ConditionFields.Values.value]
            if isinstance(value, str):
                value = f"'{value}'"
            elif isinstance(value, list):
                value = "ANY('{}')".format("{" + ",".join(value) + "}")
            conditions_str.append("{} {} {}".format(condition[ConditionFields.Field.value], condition[ConditionFields.Operator.value], value))
        query_condition = "" if len(conditions_str) == 0 else "WHERE {} ".format(" AND ".join(conditions_str))
        return query_condition

    @override
    def delete_row_by_id(self, table_name: str, partitions_list: List[Dict[str, any]], contents: List[str], ids: List[str] = []) -> int:
        count = 0
        for i in range(len(contents)):
            partitions = partitions_list[i]
            content = contents[i]
            conditions_str = []
            for key, value in partitions.items():
                if isinstance(value, str):
                    value = "'{}'".format(_clean(value))
                elif isinstance(value, dict):
                    value = "'{}'".format(_clean(json.dumps(value, ensure_ascii=False)))
                conditions_str.append("{}={}".format(key, value))
            conditions_str.append("{}='{}'".format(self.content_col, _clean(content)))

            query_condition = " AND ".join(conditions_str)
            query = f"DELETE FROM {self.schema}.{table_name} WHERE {query_condition}"
            count += self.execute(query, commit=True)
        return count

    @override
    def delete_rows(self, table_name: str, conditions: List[dict]) -> int:
        query_condition = self._parse_conditions(conditions)
        query = f"DELETE FROM {self.schema}.{table_name} {query_condition}"
        return self.execute(query, commit=True)

    @override
    def delete_table(self, table_name: str):
        self.execute(f"DROP TABLE {self.schema}.{table_name}")

    @override
    def execute(self, query: Union[str, bytes, any], vars: any = None, fetchall: bool = False, commit: bool = True) -> List[List[any]]:
        res = None
        with self._get_connection() as (connection, cursor):
            cursor.execute(query, vars=vars)
            if fetchall:
                res = cursor.fetchall()
            elif hasattr(cursor, "rowcount"):
                res = cursor.rowcount
            if commit:
                connection.commit()
        return res

    @override
    def insert_db(self, table_name: str, embeddings: Union[List[List[float]], None], contents: List[str],
                  tags: List[str], dimension: int, metadatas: Optional[List[Dict[str, any]]] = None, build_index: bool = False):
        if build_index:
            logger.warning("Unsupported parameter: build_index")
        self._check_schema()
        self._check_collection_table()
        self._check_table(table_name, tags, dimension, [], {})
        constraints = self._get_pkey_constraints([])

        for content, metadata, embedding in zip(contents, metadatas, embeddings):
            cleaned_content = _clean(content)
            cleaned_metadata = _clean(json.dumps(metadata, ensure_ascii=False))
            query = f"INSERT INTO {self.schema}.{table_name} ({self.content_col}, {self.embedding_col}, {self.metadata_col}) VALUES ('{cleaned_content}', '{embedding}', '{cleaned_metadata}') " \
                    f"ON CONFLICT({constraints}) " \
                    f"DO UPDATE SET {self.embedding_col} = EXCLUDED.{self.embedding_col}, {self.metadata_col} = EXCLUDED.{self.metadata_col}"
            self.execute(query, vars=(content, embedding, Json(metadata, dumps=json.dumps)), commit=True)

    @override
    def insert_custom_db(self, table_name: str, embedding: Union[List[float], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        if build_index:
            logger.warning("Unsupported parameter: build_index")
        self._check_schema()
        self._check_collection_table()
        self._check_table(table_name, [], len(embedding), partitions, extra)
        # create missing partitions
        partition_val = [(partition, extra[partition]) for partition in partitions]
        self._create_partition_table(table_name, partition_val)

        # insert data
        columns = [self.embedding_col]
        values = ["'{}'".format(str(embedding))]
        for column, value in extra.items() :
            if isinstance(value, str):
                value = "'{}'".format(_clean(value))
            elif isinstance(value, dict):
                value = "'{}'".format(_clean(json.dumps(value, ensure_ascii=False)))
            columns.append(column)
            values.append(value)

        conflict_update = ",".join([f"{column} = EXCLUDED.{column}" for column in columns if column != self.content_col])
        partition_conflict = self._get_pkey_constraints(partitions)
        query = f"INSERT INTO {self.schema}.{table_name} ({', '.join(columns)}) VALUES ({', '.join(values)}) "
        if uses_primary_key:
            query += f"ON CONFLICT({partition_conflict}) " \
                f"DO UPDATE SET {conflict_update}"

        self.execute(query, vars=tuple(values), commit=True)

    @override
    def insert_custom_db_multiple(self, table_name: str, embeddings: Union[List[List[float]], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        for i in range(len(embeddings)):
            self.insert_custom_db(table_name, embeddings[i], partitions=partitions, uses_primary_key=uses_primary_key, build_index=build_index, **{k: v[i] for k, v in extra.items()})

    @override
    def list_schemas(self) -> List[str]:
        query = "SELECT DISTINCT(table_schema) FROM information_schema.tables ORDER BY table_schema;"
        res = self.execute(query, fetchall=True, commit=True)
        res = [row[0] for row in res]
        return res

    @override
    def list_tables(self, schema: str = "") -> List[str]:
        if schema == "":
            schema = self.schema
        query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{schema}' ORDER BY table_name;"
        res = self.execute(query, fetchall=True, commit=True)
        res = [row[0] for row in res]
        return res

    @override
    def similarity_search(self, tags: list[str], embedding_result: Union[List[float], None], probes: int = None,
                          k: int = 1, score_threshold: Union[float, None] = None, conditions: List[dict] = [],
                          operators: List[str] = [], distance: DistanceStrategy = None, search_fields: List[str] = [], content: str = "") -> List[Dict[str, any]]:
        query = f"SELECT {TABLE_NAME_COL} FROM {self.schema}.{COLLECTION_TABLE} WHERE "
        query += " AND ".join([f"{TAG_NAME_COL} ~ '{tag} '" for tag in tags])
        res = self.execute(query, fetchall=True, commit=True)
        search_result = []
        for table_name in res:
            search_result.extend(self._single_table_similarity_search(table_name[0],
                                 [embedding_result],
                                 probes=probes,
                                 k=k,
                                 score_threshold=score_threshold,
                                 conditions=conditions,
                                 operators=operators,
                                 distance=distance,
                                 search_fields=search_fields)[0])
        search_result = sorted(search_result, key=lambda x: x['score'], reverse=False)[:k]
        return search_result

    def _single_table_similarity_search(self, table_name: str, embeddings: Union[List[List[float]], None], probes: int, k: int,
                                 score_threshold: Union[float, None], conditions: List[dict], operators: List[str],
                                 distance: DistanceStrategy = None, search_fields: List[str] = [], contents: List[str] = []) -> List[List[Dict[str, any]]]:
        if probes is None:
            probes = self._get_probes(table_name)
        # TODO: support multiple
        embedding = embeddings[0]
        if distance is None:
            distance = self.distance
        if distance is DistanceStrategy.EUCLIDEAN:
            distance_query = f"{self.embedding_col} <-> '{embedding}'"
        elif distance is DistanceStrategy.MAX_INNER_PRODUCT:
            distance_query = f"({self.embedding_col} <#> '{embedding}')"
        else:
            distance_query = f"({self.embedding_col} <=> '{embedding}')"

        query_condition = self._parse_conditions(conditions, distance=distance, embedding=embedding, score_threshold=score_threshold)

        search_field_str = ", ".join([""] + search_fields)
        pre_query = f"BEGIN; SET LOCAL ivfflat.probes = {probes}; SET LOCAL enable_seqscan = no; SET LOCAL enable_sort=no"
        query = f"SELECT {self.content_col}, {self.metadata_col}, {distance_query} AS distance{search_field_str} " \
                f"FROM {self.schema}.{table_name} {query_condition}" \
                f"order by {distance_query} limit {k}"

        with self._get_connection() as (connection, cursor):
            cursor.execute(pre_query)
            cursor.execute(query)
            res = [list(result) for result in cursor.fetchall()]
            connection.commit()
        single_search_result = []
        for item in res:
            if score_threshold is not None and item[2] > score_threshold:
                continue
            data = {k: item[3 + i] for i, k in enumerate(search_fields)}
            data["text"] = item[0]
            data["metadata"] = item[1]
            data["score"] = item[2]
            single_search_result.append(data)
        return [single_search_result]

    @override
    def add_index(self, table_name: str, force: bool = False):
        distance_index = ["vector_l2_ops", "vector_ip_ops", "vector_cosine_ops"]

        query = f"SELECT COUNT(*) FROM {self.schema}.{table_name}"
        total_row = self.execute(query, fetchall=True, commit=True)[0][0]
        list_num = ivfflat_index_list_calculation(total_row)

        with self._get_connection() as (connection, cursor):
            for index in distance_index:
                index_name = index + f"_{table_name}"
                query = f"DROP INDEX IF EXISTS {self.schema}.{index_name}"
                cursor.execute(query)
                connection.commit()
                query = f"CREATE INDEX {index_name} ON {self.schema}.{table_name} USING ivfflat ({self.embedding_col} {index}) " \
                        f"WITH (lists = {int(list_num)})"
                cursor.execute(query)
                connection.commit()

    @override
    def delete_table(self, table_name):
        query = f"DROP table {self.schema}.{table_name}"
        self.execute(query, commit=True)
        query = f"DELETE FROM {self.schema}.{COLLECTION_TABLE} where {TABLE_NAME_COL}='{table_name}'"
        self.execute(query, commit=True)

    @override
    def retrieve_all_tables_tags(self):
        query = f"SELECT {TABLE_NAME_COL}, {TAG_NAME_COL} FROM {self.schema}.{COLLECTION_TABLE}"
        table_list = self.execute(query, fetchall=True, commit=True)
        result = [{
            TABLE_NAME_COL: table_info[0],
            TAG_NAME_COL: table_info[1]
        } for table_info in table_list]
        return result

    def __del__(self):
        while self._connections > 0:
            time.sleep(1)
        self._engine.dispose()


class PgConnManager():
    def __init__(self, pg: PGVector):
        self.pg = pg

    def __enter__(self):
        self.connection = self.pg._engine.raw_connection()
        cursor = self.connection.cursor()
        with self.pg._mutex:
            self.pg._connections += 1
        return self.connection, cursor

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.connection.close()
        with self.pg._mutex:
            self.pg._connections -= 1
