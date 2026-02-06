from graphql import GraphQLError

from app.errors.base_exception import BaseException


def should_mask_error(error: GraphQLError) -> bool:
    if isinstance(error.original_error, BaseException):
        return False
    if error.original_error is None:
        return False
    return True
