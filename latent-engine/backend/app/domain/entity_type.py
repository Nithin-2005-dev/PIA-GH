from enum import Enum


class EntityType(Enum):
    DEVELOPER = "DEVELOPER"
    MODULE = "MODULE"
    FILE = "FILE"
    REPOSITORY = "REPOSITORY"
    PULL_REQUEST = "PULL_REQUEST"
    ISSUE = "ISSUE"
    RELEASE = "RELEASE"