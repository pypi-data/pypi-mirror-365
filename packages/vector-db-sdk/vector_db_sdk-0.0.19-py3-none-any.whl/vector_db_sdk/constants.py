from enum import Enum

class VectorType(Enum):
    PgVector = "pgvector"
    TcVector = "tcvector"

class ConditionFields(Enum):
    Field = "field"
    Operator = "operator"
    Values = "values"

class IndexType(Enum):
    String = "string"
    Uint = "uint"
    Array = "array"
