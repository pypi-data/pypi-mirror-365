from loguru import logger
import traceback
from typing import Dict, List, Optional, Tuple, Union
from typing_extensions import deprecated

from vector_db_sdk.constants import VectorType, IndexType as IType
from vector_db_sdk.pgvector import PGVector
from vector_db_sdk.tcvector import TcVector
from vector_db_sdk.util import DistanceStrategy


class VectorDB:
    """
    *param* **connection_type**: *str*
    Type of connection to use for vector db. Currently only supports `pgvector` and `tcvector`.

    *param* **connection_info**: *Dict[str, str | int]*

    connection_info keys:

    * *required* **username**
    * *required* **password**
    * *required* **host**
    * *required* **port**
    * *required* **database**
    * *optional* **schema**

    *param* **distance**: *util.DistanceStrategy = DistanceStrategy.EUCLIDEAN*
    Distance metric used for vector comparison. Default `Euclidean` (L2).

    *param* **col_names**: *Dict[str, str] = {}*
    Dictionary used to map old sdk column names for flexibility. To map an old column name to an existing name in your table, use {"old_col_name": "new_col_name"}.
    Current old columns are:
    * `contents` *libvector.CONTENT_COL*: Usually the textual content represented by the embedding.
    * `embeddings` *libvector.EMBEDDING_COL*: Embedding representing the data.
    * `metadatas` *libvector.METADATA_COL*: Dictionary of metadata.
    """

    def __init__(self, connection_type: str, connection_info: Dict[str, Union[str, int]],
                 distance: DistanceStrategy = DistanceStrategy.COSINE, col_names: Dict[str, str] = {}, timeout: float = None) -> None:
        self.type = connection_type.lower()
        if self.type == VectorType.PgVector.value:
            self.db = PGVector(connection_info, distance, col_names=col_names, timeout=timeout)
        elif self.type == VectorType.TcVector.value:
            self.db = TcVector(connection_info, distance, col_names=col_names, timeout=timeout)
        else:
            raise ValueError("DB type is not supported, only supports [{}]".format(", ".join([v.value for v in VectorType])))

    def create_table(self, table_name: str, indices: Dict[str, IType], description: str, vector_length: int, num_rows: int = 1, model_name: str = ""):
        return self.db.create_table(table_name, indices, description, vector_length, num_rows=num_rows, model_name=model_name)

    def delete_row_by_id(self, table_name: str, partitions_list: List[Dict[str, any]], contents: List[str], ids: List[str] = []) -> int:
        return self.db.delete_row_by_id(table_name, partitions_list, contents, ids=ids)

    def delete_rows(self, table_name: str, conditions: List[dict]) -> int:
        return self.db.delete_rows(table_name, conditions)

    def delete_table(self, table_name: str):
        self.db.delete_table(table_name)

    def execute(self, query: Union[str, bytes, any], vars: any = None, fetchall : bool = False, commit: bool = True) -> Union[None, List[List[any]]]:
        return self.db.execute(query, vars=vars, fetchall=fetchall, commit=commit)

    def find_table_schemas(self, table_name: str) -> List[str]:
        table_schemas = []
        for schema in self.list_schemas():
            try:
                if table_name in self.list_tables(schema=schema):
                    table_schemas.append(schema)
            except Exception as e:
                logger.warning(traceback.format_exc())
        return table_schemas

    def list_schemas(self) -> List[str]:
        return self.db.list_schemas()

    def list_tables(self, schema: str = "") -> List[str]:
        return self.db.list_tables(schema=schema)

    def reindex(self, table_name: str, force: bool = False):
        self.db.add_index(table_name, force=force)

    def similarity_search_with_score(self, embedding: Union[List[float], None], tags: List[str],
                                     probes: int = None, k: int = 1, score_threshold: Union[float, None] = None,
                                     conditions: List[Dict[str, any]] = [], operators: List[str] = [], distance: DistanceStrategy = None,
                                     table_name: str = "", search_field: List[str] = [], content: str = "") -> List[Dict[str, any]]:
        """
            similarity_search_with_score

            Args:
                embedding: Embedding to look up documents similar to.
                tags: Search within documents which match the tags
                probes: Number of probes to use, the higher the more accurate, default will do full scan
                k: Topk result to return
                score_threshold : get result with prefer score range
                conditions : list of condition for the search  , dict in format
                                [{"field" :"xxx", #column name
                                 "operator" : "xxx", #refer here : https://www.postgresql.org/docs/6.3/c09.htm
                                 "values" : "xxx", #what value for the condition }]
                                 default is []

                operators  : list of operator to use between conditions , #refer here : https://www.postgresql.org/docs/current/functions-logical.html
                            default is []
                table_name: table name to search without specifying schema. If empty, will look up entire table catalogue "tb_collection".


        """
        if table_name != "":
            embeddings = [embedding] if embedding is not None else None
            return self.db._single_table_similarity_search(table_name, embeddings, probes, k, score_threshold, conditions, operators, distance=distance, search_fields=search_field, contents=[content])[0]
        result = self.db.similarity_search(embedding_result=embedding,
                                           tags=tags,
                                           probes=probes,
                                           k=k,
                                           score_threshold=score_threshold,
                                           conditions=conditions,
                                           operators=operators,
                                           distance=distance,
                                           search_fields=search_field,
                                           content=content)

        return result

    def similarity_search_with_score_multiple(self, embeddings: List[List[float]], tags: List[str],
                                     probes: int = None, k: int = 1, score_threshold: Union[float, None] = None,
                                     conditions: List[Dict[str, any]] = [], operators: List[str] = [], distance: DistanceStrategy = None,
                                     table_name: str = "", search_field: List[str] = [], contents: List[str] = []) -> List[List[Dict[str, any]]]:
        if self.type == VectorType.PgVector.value:
            return [self.similarity_search_with_score(embedding, tags, probes=probes, k=k, score_threshold=score_threshold, conditions=conditions, operators=operators,
                                                      distance=distance, table_name=table_name, search_field=search_field) for embedding in embeddings]
        return self.db._single_table_similarity_search(table_name, embeddings, probes, k, score_threshold, conditions, operators, distance=distance, search_fields=search_field, contents=contents)

    def insert_custom_data_table(self, table_name: str, embedding: Union[List[float], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        """
            insert_custom_data_table

            Args:
                table_name: Table name to store in
                embedding: Contents embedding
                **extra : column name and value , example result=3  result is column, 3 is value
        """

        self.db.insert_custom_db(table_name, embedding, partitions=partitions, filters=filters, uses_primary_key=uses_primary_key, build_index=build_index, **extra)


    def insert_custom_data_table_multiple(self, table_name: str, embeddings: Union[List[List[float]], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        """
            insert_custom_data_table_multiple

            Args:
                table_name: Table name to store in
                embeddings: Contents embedding
                **extra : column name and value , example result=3  result is column, 3 is value
        """

        self.db.insert_custom_db_multiple(table_name, embeddings, partitions=partitions, filters=filters, uses_primary_key=uses_primary_key, build_index=build_index, **extra)

    def query(self, table_name: str, limit: int = 16384, offset: int = 0, conditions: List[dict] = [], output_fields: List[str] = []) -> List[Dict[str, any]]:
        return self.db.query(table_name, limit=limit, offset=offset, conditions=conditions, output_fields=output_fields)

    def row_count(self, table_name: str) -> int:
        return self.db.row_count(table_name)

    @deprecated("vector-db-sdk should not support external langchain operations")
    def from_documents(self, table_name: str, documents: List, embeddingModel: any, tags: List[str],
                       dimension: int):
        """
            from_documents

            Args:
                table_name: Table name to store in
                documents: Documents loaded from langchain docs loader, Any loader in langchain.document_loaders
                embedding: Any embedding function implementing`langchain.embeddings.base.Embeddings` interface.
                tags: Tagging for this document
                dimension: Number of embedding dimension , for example OpenAIEmbeddings is 1536
        """
        contents = [d.page_content for d in documents]
        metadatas = [d.metadata for d in documents]
        embeddings = embeddingModel.embed_documents(list(contents))

        self.db.insert_db(table_name=table_name,
                          embeddings=embeddings,
                          contents=contents,
                          tags=tags,
                          dimension=dimension,
                          metadatas=metadatas)

        self.db.add_index(table_name=table_name)

    @deprecated("use insert_custom_data_table instead.")
    def from_existing_documents(self, table_name: str, contents: List[str], metadatas: Optional[List[Dict[str, any]]],
                                embeddings: List[List[float]], tags: List[str], dimension: int):
        """
            from_existing_documents

            Args:
                table_name: Table name to store in
                contents: Original text contents
                metadatas: Metadatas for contents
                embeddings: Contents embedding
                tags: Tagging for this document
                dimension: Number of embedding dimension , for example OpenAIEmbeddings is 1536
        """

        self.db.insert_db(table_name=table_name,
                          embeddings=embeddings,
                          contents=contents,
                          tags=tags,
                          dimension=dimension,
                          metadatas=metadatas)

        self.db.add_index(table_name=table_name)

    @deprecated("Users are encouraged to maintain own catalogue table.")
    def delete_collection(self, table_name: str):
        self.db.delete_table(table_name=table_name)

    @deprecated("Users are encouraged to maintain own catalogue table.")
    def retrieve_all_collection(self) -> list[dict]:
        result = self.db.retrieve_all_tables_tags()
        return result

    @deprecated("use similarity_search_with_score instead")
    def custom_similarity_search(self, table_name: str, embedding: List[float], probes: int = None, k: int = 1
                                 , distance: DistanceStrategy = DistanceStrategy.EUCLIDEAN,
                                 search_fields: List[str] = [], conditions: List[dict] = [], operators: List[str] = []):

        """
            insert_custom_data_table

            Args:
                table_name: Table name to store in
                embedding_result: Embedding to look up documents similar to
                probes: Number of probes to use, the higher the more accurate, default will do full scan
                k: Topk result to return
                distance: The distance strategy to use, please import DistanceStrategy from util
                search_fields : List of custom column want to search , default is []
                conditions : list of condition for the search  , dict in format
                                [{"field" :"xxx", #column name
                                 "operator" : "xxx", #refer here : https://www.postgresql.org/docs/6.3/c09.htm
                                 "values" : "xxx", #what value for the condition }]
                                 default is []

                operators  ：list of operator to use between conditions , #refer here : https://www.postgresql.org/docs/current/functions-logical.html
                            default is []

                example param  :
                    search_field = ["task_id", "user_name"]
                    condition =  [{"field" :"task_id",
                                 "operator" : "=",
                                 "values" : "3211"},
                                 {"field" :"user_name",
                                 "operator" : "!=",
                                 "values" : "william"}]
                    operators = ["AND"]

        """

        result = self.db.similarity_search(table_name=table_name,
                                                  embedding_result=embedding,
                                                  probes=probes,
                                                  k=k,
                                                  distance=distance,
                                                  search_fields=search_fields,
                                                  conditions=conditions,
                                                  operators=operators)
        return result

    def __del__(self):
        try:
            self.db.__del__()
        except:
            pass
