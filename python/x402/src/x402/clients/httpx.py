from typing import Optional, Dict, List
from httpx import Request, Response, AsyncClient
from eth_account import Account

from x402.clients.base import (
    x402Client,
    MissingRequestConfigError,
    PaymentError,
    PaymentSelectorCallable,
)
from x402.types import x402PaymentRequiredResponse


class HttpxHooks:
    def __init__(self, client: x402Client):
        self.client = client

    async def on_request(self, request: Request):
        """Handle request before it is sent."""
        # Nothing needed here for x402
        return

    async def on_response(self, response: Response) -> Response:
        """Handle response after it is received."""
        request = response.request

        # Non-402 → just return
        if response.status_code != 402:
            if request:
                request.extensions.pop("x402_is_retry", None)
            return response

        if not request:
            raise MissingRequestConfigError("Missing request configuration")

        # Prevent infinite retry loops
        if request.extensions.get("x402_is_retry"):
            request.extensions.pop("x402_is_retry", None)
            return response

        try:
            # Ensure response body is fully read
            await response.aread()
            data = response.json()

            payment_response = x402PaymentRequiredResponse(**data)

            # Select acceptable payment requirements
            selected_requirements = self.client.select_payment_requirements(
                payment_response.accepts
            )

            # Build payment header
            payment_header = self.client.create_payment_header(
                selected_requirements,
                payment_response.x402_version,
            )

            # Mark this request as a retry
            request.extensions["x402_is_retry"] = True

            # Clone request headers and add payment
            headers = dict(request.headers)
            headers["X-Payment"] = payment_header
            headers["Access-Control-Expose-Headers"] = "X-Payment-Response"

            retry_request = Request(
                method=request.method,
                url=request.url,
                headers=headers,
                content=request.content,
                extensions=request.extensions,
            )

            # Re-send request
            async with AsyncClient() as client:
                retry_response = await client.send(retry_request)

            # Replace original response contents
            response.status_code = retry_response.status_code
            response.headers.clear()
            response.headers.update(retry_response.headers)
            response._content = retry_response.content

            return response

        except PaymentError:
            raise
        except Exception as e:
            raise PaymentError(f"Failed to handle payment: {str(e)}") from e
        finally:
            if request:
                request.extensions.pop("x402_is_retry", None)


def x402_payment_hooks(
    account: Account,
    max_value: Optional[int] = None,
    payment_requirements_selector: Optional[PaymentSelectorCallable] = None,
) -> Dict[str, List]:
    """
    Create httpx event hooks for handling 402 Payment Required responses.
    """
    client = x402Client(
        account,
        max_value=max_value,
        payment_requirements_selector=payment_requirements_selector,
    )

    hooks = HttpxHooks(client)

    return {
        "request": [hooks.on_request],
        "response": [hooks.on_response],
    }


class x402HttpxClient(AsyncClient):
    """AsyncClient with built-in x402 payment handling."""

    def __init__(
        self,
        account: Account,
        max_value: Optional[int] = None,
        payment_requirements_selector: Optional[PaymentSelectorCallable] = None,
        **kwargs,
    ):
        hooks = x402_payment_hooks(
            account,
            max_value,
            payment_requirements_selector,
        )

        super().__init__(event_hooks=hooks, **kwargs)
