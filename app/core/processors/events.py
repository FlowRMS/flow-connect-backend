from enum import Enum


class RepositoryEvent(str, Enum):
    PRE_CREATE = "pre_create"
    POST_CREATE = "post_create"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"
    PRE_DELETE = "pre_delete"
    POST_DELETE = "post_delete"
