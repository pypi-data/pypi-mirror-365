from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.unlink_manufacturing_order_request import UnlinkManufacturingOrderRequest
from ...models.unlink_manufacturing_order_response_204 import (
    UnlinkManufacturingOrderResponse204,
)
from ...models.unlink_manufacturing_order_response_401 import (
    UnlinkManufacturingOrderResponse401,
)
from ...models.unlink_manufacturing_order_response_500 import (
    UnlinkManufacturingOrderResponse500,
)
from ...types import Response


def _get_kwargs(
    *,
    body: UnlinkManufacturingOrderRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/manufacturing_order_unlink",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> (
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
    | None
):
    if response.status_code == 204:
        response_204 = UnlinkManufacturingOrderResponse204.from_dict(response.json())

        return response_204
    if response.status_code == 401:
        response_401 = UnlinkManufacturingOrderResponse401.from_dict(response.json())

        return response_401
    if response.status_code == 500:
        response_500 = UnlinkManufacturingOrderResponse500.from_dict(response.json())

        return response_500
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
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
    body: UnlinkManufacturingOrderRequest,
) -> Response[
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
]:
    """Unlink a manufacturing order from sales order row

     Unlinks the manufacturing order from a particular sales order row.

    Args:
        body (UnlinkManufacturingOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[UnlinkManufacturingOrderResponse204, UnlinkManufacturingOrderResponse401, UnlinkManufacturingOrderResponse500]]
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
    body: UnlinkManufacturingOrderRequest,
) -> (
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
    | None
):
    """Unlink a manufacturing order from sales order row

     Unlinks the manufacturing order from a particular sales order row.

    Args:
        body (UnlinkManufacturingOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[UnlinkManufacturingOrderResponse204, UnlinkManufacturingOrderResponse401, UnlinkManufacturingOrderResponse500]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: UnlinkManufacturingOrderRequest,
) -> Response[
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
]:
    """Unlink a manufacturing order from sales order row

     Unlinks the manufacturing order from a particular sales order row.

    Args:
        body (UnlinkManufacturingOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Response[Union[UnlinkManufacturingOrderResponse204, UnlinkManufacturingOrderResponse401, UnlinkManufacturingOrderResponse500]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: UnlinkManufacturingOrderRequest,
) -> (
    UnlinkManufacturingOrderResponse204
    | UnlinkManufacturingOrderResponse401
    | UnlinkManufacturingOrderResponse500
    | None
):
    """Unlink a manufacturing order from sales order row

     Unlinks the manufacturing order from a particular sales order row.

    Args:
        body (UnlinkManufacturingOrderRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.


    Returns:
        Union[UnlinkManufacturingOrderResponse204, UnlinkManufacturingOrderResponse401, UnlinkManufacturingOrderResponse500]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
