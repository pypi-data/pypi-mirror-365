from math import sqrt
from typing import Dict, List, Optional, Union
from vector_db_sdk.util import DistanceStrategy
from abc import ABC

from vector_db_sdk.constants import IndexType as IType


CONTENT_COL = "contents"
EMBEDDING_COL = "embeddings"
METADATA_COL = "metadatas"

def ivfflat_index_list_calculation(total_row: int):
    if total_row >= 1000000:
        list_num = sqrt(total_row)
    elif 1000000 > total_row > 1000:
        list_num = total_row / 1000
    else:
        list_num = 1

    return list_num


class LibVector(ABC):
    def __init__(self, connection_dict: Dict[str, Union[str, int]], distance: DistanceStrategy, col_names: Dict[str, str] = {}, timeout: float = None) -> None:
        pass

    def create_table(self, table_name: str, indices: Dict[str, IType], description: str, vector_length: int, num_rows: int = 1, model_name: str = ""):
        raise Exception("Create table not supported for {}".format(self.__class__.__name__))

    def delete_row_by_id(self, table_name: str, partitions_list: List[Dict[str, any]], contents: List[str], ids: List[str] = []):
        raise Exception("Delete row not supported for {}".format(self.__class__.__name__))

    def delete_rows(self, table_name: str, conditions: List[dict]) -> int:
        raise Exception("Delete rows not supported for {}".format(self.__class__.__name__))

    def delete_table(self, table_name: str):
        raise Exception("Delete table not supported for {}".format(self.__class__.__name__))

    def execute(self, query: Union[str, bytes, any], vars: any = None, fetchall: bool = False, commit: bool = True) -> List[List[any]]:
        raise Exception("Execute not supported for {}".format(self.__class__.__name__))

    def insert_db(self, table_name: str, embeddings: Union[List[List[float]], None], contents: List[str],
                  tags: List[str], dimension: int, metadatas: Optional[List[Dict[str, any]]] = None, build_index: bool = False):
        raise Exception("Insert db not supported for {}".format(self.__class__.__name__))

    def insert_custom_db(self, table_name: str, embedding: Union[List[float], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        embeddings = [embedding] if embedding is not None else None
        self.insert_custom_db_multiple(table_name, embeddings, partitions=partitions, filters=filters, uses_primary_key=uses_primary_key, build_index=build_index, **{k: [v] for k, v in extra.items()})

    def insert_custom_db_multiple(self, table_name: str, embeddings: Union[List[List[float]], None], partitions: List[str] = [], filters: List[str] = [], uses_primary_key: bool = True, build_index: bool = False, **extra):
        raise Exception("Insert custom db multiple not supported for {}".format(self.__class__.__name__))

    def list_schemas(self) -> List[str]:
        raise Exception("List schemas not supported for {}".format(self.__class__.__name__))

    def list_tables(self, schema: str = "") -> List[str]:
        raise Exception("List tables not supported for {}".format(self.__class__.__name__))

    def query(self, table_name: str, limit: int = 16384, offset: int = 0, conditions: List[dict] = [], output_fields: List[str] = []) -> List[Dict[str, any]]:
        raise Exception("Query not supported for {}".format(self.__class__.__name__))

    def row_count(self, table_name: str) -> int:
        raise Exception("Row count not supported for {}".format(self.__class__.__name__))

    def similarity_search(self, tags: list[str], embedding_result: Union[List[float], None], probes: int = None,
                          k: int = 1, score_threshold: float = None, conditions: List[dict] = [],
                          operators: List[str] = [], distance: DistanceStrategy = None, search_fields: List[str] = [], content: str = "") -> List[Dict[str, any]]:
        raise Exception("Similarity search not supported for {}".format(self.__class__.__name__))

    def _single_table_similarity_search(self, table_name: str, embeddings: Union[List[List[float]], None], probes: int, k: int,
                                 score_threshold: Union[float, None], conditions: List[dict], operators: List[str],
                                 distance: DistanceStrategy = None, search_fields: List[str] = [], contents: List[str] = []) -> List[List[Dict[str, any]]]:
        raise Exception("Single similarity search not supported for {}".format(self.__class__.__name__))

    def add_index(self, table_name: str, force: bool = False):
        raise Exception("Add index not supported for {}".format(self.__class__.__name__))

    def delete_table(self, table_name: str):
        raise Exception("Delete table not supported for {}".format(self.__class__.__name__))

    def retrieve_all_tables_tags(self):
        raise Exception("Retrieve all table tags not supported for {}".format(self.__class__.__name__))

    def __del__(self):
        pass
