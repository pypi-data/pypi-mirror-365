import enum


class DistanceStrategy(enum.Enum):
    EUCLIDEAN = "l2"
    COSINE = "cosine"
    MAX_INNER_PRODUCT = "ip"
