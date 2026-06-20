from enum import Enum


class PredicateType(Enum):
    MODIFIED = "MODIFIED"
    REVIEWED = "REVIEWED"
    FIXED = "FIXED"
    CREATED = "CREATED"
    MERGED = "MERGED"
    COMMENTED = "COMMENTED"
    TOUCHED = "TOUCHED"