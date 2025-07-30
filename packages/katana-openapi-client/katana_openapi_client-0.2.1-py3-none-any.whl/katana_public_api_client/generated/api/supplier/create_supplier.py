from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.create_supplier_request import CreateSupplierRequest
from ...models.create_supplier_response_401 import CreateSupplierResponse401
from ...models.create_supplier_response_422 import CreateSupplierResponse422
from ...models.create_supplier_response_429 import CreateSupplierResponse429
from ...models.create_supplier_response_500 import CreateSupplierResponse500
from ...models.supplier_response import SupplierResponse
from ...types import Response


def _get_kwargs(
    *,
    body: CreateSupplierRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/suppliers",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
    | None
):
    if response.status_code == 200:
        response_200 = SupplierResponse.from_dict(response.json())

        return response_200
    if response.status_code == 401:
        response_401 = CreateSupplierResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 422:
        response_422 = CreateSupplierResponse422.from_dict(response.json())

        return response_422
    if response.status_code == 429:
        response_429 = CreateSupplierResponse429.from_dict(response.json())

        return response_429
    if response.status_code == 500:
        response_500 = CreateSupplierResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSupplierRequest,
) -> Response[
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
]:
    """Create a supplier

     Creates a new supplier object.

    Args:
        body (CreateSupplierRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[CreateSupplierResponse401, CreateSupplierResponse422, CreateSupplierResponse429, CreateSupplierResponse500, SupplierResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSupplierRequest,
) -> (
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
    | None
):
    """Create a supplier

     Creates a new supplier object.

    Args:
        body (CreateSupplierRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[CreateSupplierResponse401, CreateSupplierResponse422, CreateSupplierResponse429, CreateSupplierResponse500, SupplierResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSupplierRequest,
) -> Response[
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
]:
    """Create a supplier

     Creates a new supplier object.

    Args:
        body (CreateSupplierRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[CreateSupplierResponse401, CreateSupplierResponse422, CreateSupplierResponse429, CreateSupplierResponse500, SupplierResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: CreateSupplierRequest,
) -> (
    CreateSupplierResponse401
    | CreateSupplierResponse422
    | CreateSupplierResponse429
    | CreateSupplierResponse500
    | SupplierResponse
    | None
):
    """Create a supplier

     Creates a new supplier object.

    Args:
        body (CreateSupplierRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[CreateSupplierResponse401, CreateSupplierResponse422, CreateSupplierResponse429, CreateSupplierResponse500, SupplierResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
