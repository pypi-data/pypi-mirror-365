import glob
import importlib.util
from typing import Any, Awaitable, Callable, List, TypeVar, cast

import jwt
from fastapi import Request, Response
from pydantic.generics import GenericModel
from sqlmodel import SQLModel

from one_public_api.common import constants
from one_public_api.core.settings import settings
from one_public_api.schemas.response_schema import MessageSchema, ResponseSchema

T = TypeVar("T", bound=SQLModel)


def create_response_data(
    schema: GenericModel,
    results: Any | List[Any] | None = None,
    count: int | None = None,
    detail: List[MessageSchema] | None = None,
) -> ResponseSchema[T]:
    """
    Creates a response data object compliant with the `ResponseSchema[T]`
    model.

    This method validates the provided results data against the
    specified schema and then encapsulates it in a standardized response
    object. It supports single or multiple data results by handling both
    individual and list inputs. Optionally, it includes additional metadata
    such as count and detailed message schema.

    Parameters
    ----------
    schema : GenericModel
        The schema model used to validate the provided results data. This should be
        callable with a
        `model_validate` method to perform validation.
    results : Any or List[Any] or None
        The data object(s) to be validated and included in the response. It can be a
        single instance,
        a list of instances, or None.
    count : int or None, optional
        The count metadata is typically used to indicate the total number of items in a
        paginated context, or can be None if not applicable.
    detail : List[MessageSchema] or None, optional
        A list of detail messages that provide additional information regarding the
        response or process, or can be None if no details are provided.

    Returns
    -------
    ResponseSchema[T]
        A response object containing the validated results data, optional count
        metadata, and optional detailed messages.
    """

    if type(results) is list:
        rst = [getattr(schema, "model_validate")(d) for d in results]
    elif results is None:
        rst = None
    else:
        rst = getattr(schema, "model_validate")(results)

    rsp: ResponseSchema[T] = ResponseSchema(results=rst, count=count, detail=detail)

    return rsp


def get_username_from_token(token: str) -> str | None:
    payload = jwt.decode(
        token, settings.SECRET_KEY, algorithms=[constants.JWT_ALGORITHM]
    )
    return str(payload.get("sub")) if payload.get("sub") else None


def load_route_handler(
    input_dir: str, module_name: str, handler_name: str
) -> (
    Callable[[Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]]
    | None
):
    for file in glob.glob(input_dir, recursive=True):
        spec = importlib.util.spec_from_file_location(module_name, file)
        if spec:
            mod = importlib.util.module_from_spec(spec)
            if spec.loader and mod:
                spec.loader.exec_module(mod)
                return cast(
                    Callable[
                        [Request, Callable[[Request], Awaitable[Response]]],
                        Awaitable[Response],
                    ],
                    getattr(mod, handler_name),
                )

    return None
