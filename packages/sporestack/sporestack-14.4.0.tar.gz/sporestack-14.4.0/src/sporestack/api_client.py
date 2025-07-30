import logging
import os
from dataclasses import dataclass
from typing import Optional, Union

import httpx
from pydantic import parse_obj_as

from . import __version__, api, exceptions
from .constants import Currency, Provider
from .models import (
    Flavor,
    Invoice,
    OperatingSystem,
    Region,
    ServerUpdateRequest,
    TokenInfo,
)

log = logging.getLogger(__name__)

LATEST_API_VERSION = 2
"""This is probably not used anymore."""

CLEARNET_ENDPOINT = "https://api.sporestack.com"
TOR_ENDPOINT = (
    "http://api.spore64i5sofqlfz5gq2ju4msgzojjwifls7rok2cti624zyq3fcelad.onion"
)

API_ENDPOINT = CLEARNET_ENDPOINT

TIMEOUT = httpx.Timeout(60.0)

HEADERS = {"User-Agent": f"sporestack-python/{__version__}"}


def _get_tor_proxy() -> str:
    """
    This makes testing easier.
    """
    return os.getenv("TOR_PROXY", "socks5h://127.0.0.1:9050")


def _is_onion_url(url: str) -> bool:
    """
    returns True/False depending on if a URL looks like a Tor hidden service
    (.onion) or not.
    This is designed to false as non-onion just to be on the safe-ish side,
    depending on your view point. It requires URLs like: http://domain.tld/,
    not http://domain.tld or domain.tld/.

    This can be optimized a lot.
    """
    try:
        url_parts = url.split("/")
        domain = url_parts[2]
        tld = domain.split(".")[-1]
        if tld == "onion":
            return True
    except Exception:
        pass
    return False


def _get_response_error_text(response: httpx.Response) -> str:
    """Get a response's error text. Assumes the response is actually an error."""
    if (
        "content-type" in response.headers
        and response.headers["content-type"] == "application/json"
    ):
        error = response.json()
        if "detail" in error:
            if isinstance(error["detail"], str):
                return error["detail"]
            else:
                return str(error["detail"])

    return response.text


def _handle_response(response: httpx.Response) -> None:
    status_code_first_digit = response.status_code // 100
    if status_code_first_digit == 2:
        return

    error_response_text = _get_response_error_text(response)
    if response.status_code == 402:
        raise exceptions.SporeStackPaymentRequiredError(error_response_text)
    elif response.status_code == 429:
        raise exceptions.SporeStackTooManyRequestsError(error_response_text)
    elif status_code_first_digit == 4:
        raise exceptions.SporeStackUserError(error_response_text)
    elif status_code_first_digit == 5:
        # User should probably retry.
        raise exceptions.SporeStackServerError(error_response_text)
    else:
        # This would be weird.
        raise exceptions.SporeStackServerError(error_response_text)


@dataclass
class APIClient:
    api_endpoint: str = API_ENDPOINT

    def __post_init__(self) -> None:
        headers = httpx.Headers(HEADERS)
        proxy = None
        if _is_onion_url(self.api_endpoint):
            proxy = _get_tor_proxy()
        self._httpx_client = httpx.Client(headers=headers, proxy=proxy, timeout=TIMEOUT)

    def server_launch(
        self,
        token: str,
        flavor: str,
        operating_system: str,
        ssh_key: str,
        provider: Provider = Provider.DIGITALOCEAN,
        region: Optional[str] = None,
        hostname: str = "",
        days: Union[int, None] = None,
        autorenew: bool = False,
        user_data: Union[str, None] = None,
    ) -> api.ServerLaunch.Response:
        """Launch a server."""
        request = api.ServerLaunch.Request(
            days=days,
            flavor=flavor,
            region=region,
            provider=provider,
            operating_system=operating_system,
            ssh_key=ssh_key,
            hostname=hostname,
            autorenew=autorenew,
            user_data=user_data,
        )
        url = self.api_endpoint + api.ServerLaunch.url.format(token=token)
        response = self._httpx_client.post(url=url, json=request.dict())
        _handle_response(response)
        return api.ServerLaunch.Response.parse_obj(response.json())

    def server_topup(
        self,
        token: str,
        machine_id: str,
        days: int,
    ) -> None:
        """Topup a server."""
        request = api.ServerTopup.Request(days=days)
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/topup"
        response = self._httpx_client.post(url=url, json=request.dict())
        _handle_response(response)

    def server_quote(
        self, days: int, flavor: str, provider: Provider = Provider.DIGITALOCEAN
    ) -> api.ServerQuote.Response:
        """Get a quote for how much a server will cost."""

        url = self.api_endpoint + api.ServerQuote.url
        response = self._httpx_client.get(
            url,
            params={"days": days, "flavor": flavor, "provider": provider.value},
        )
        _handle_response(response)
        return api.ServerQuote.Response.parse_obj(response.json())

    def server_start(self, token: str, machine_id: str) -> None:
        """Power on a server."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/start"
        response = self._httpx_client.post(url)
        _handle_response(response)

    def server_stop(self, token: str, machine_id: str) -> None:
        """Power off a server."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/stop"
        response = self._httpx_client.post(url)
        _handle_response(response)

    def server_reboot(self, token: str, machine_id: str) -> None:
        """Reboot a server."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/reboot"
        response = self._httpx_client.post(url)
        _handle_response(response)

    def server_delete(self, token: str, machine_id: str) -> None:
        """Delete a server."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}"
        response = self._httpx_client.delete(url)
        _handle_response(response)

    def server_forget(self, token: str, machine_id: str) -> None:
        """Forget about a deleted server to hide it from view."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/forget"
        response = self._httpx_client.post(url)
        _handle_response(response)

    def server_rebuild(self, token: str, machine_id: str) -> None:
        """
        Rebuilds the server with the operating system and SSH key set at launch time.

        Deletes all of the data on the server!
        """
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}/rebuild"
        response = self._httpx_client.post(url)
        _handle_response(response)

    def server_info(self, token: str, machine_id: str) -> api.ServerInfo.Response:
        """Returns info about the server."""
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}"
        response = self._httpx_client.get(url)
        _handle_response(response)
        response_object = api.ServerInfo.Response.parse_obj(response.json())
        return response_object

    def server_update(
        self,
        token: str,
        machine_id: str,
        hostname: Union[str, None] = None,
        autorenew: Union[bool, None] = None,
    ) -> None:
        """Update server settings."""
        request = ServerUpdateRequest(hostname=hostname, autorenew=autorenew)
        url = f"{self.api_endpoint}/token/{token}/servers/{machine_id}"
        response = self._httpx_client.patch(url=url, json=request.dict())
        _handle_response(response)

    def servers_launched_from_token(
        self,
        token: str,
        hostname: Union[str, None] = None,
        include_deleted: bool = True,
        include_forgotten: bool = True,
    ) -> api.ServersLaunchedFromToken.Response:
        """Returns info for servers launched from a given token."""
        url = self.api_endpoint + api.ServersLaunchedFromToken.url.format(token=token)
        params = {} if hostname is None else {"hostname": hostname}
        params["include_deleted"] = "true" if include_deleted else "false"
        params["include_forgotten"] = "true" if include_forgotten else "false"
        response = self._httpx_client.get(url, params=params)
        _handle_response(response)
        response_object = api.ServersLaunchedFromToken.Response.parse_obj(
            response.json()
        )
        return response_object

    def operating_systems(
        self, provider: Union[Provider, None] = None
    ) -> list[OperatingSystem]:
        """Returns available operating systems."""
        url = self.api_endpoint + "/slugs/os"
        params = {} if provider is None else {"provider": provider.value}
        response = self._httpx_client.get(url, params=params)
        _handle_response(response)
        return parse_obj_as(list[OperatingSystem], response.json())

    def regions(self, provider: Union[Provider, None] = None) -> list[Region]:
        """Returns available regions."""
        url = self.api_endpoint + "/slugs/regions"
        params = {} if provider is None else {"provider": provider.value}
        response = self._httpx_client.get(url, params=params)
        _handle_response(response)
        return parse_obj_as(list[Region], response.json())

    def flavors(self, provider: Union[Provider, None] = None) -> list[Flavor]:
        """Returns available flavors."""
        url = self.api_endpoint + "/slugs/flavors"
        params = {} if provider is None else {"provider": provider.value}
        response = self._httpx_client.get(url, params=params)
        _handle_response(response)
        return parse_obj_as(list[Flavor], response.json())

    def aup(self) -> str:
        """Returns the Acceptable Use Policy."""
        url = self.api_endpoint + "/aup"
        response = self._httpx_client.get(url)
        _handle_response(response)
        return response.text

    def changelog(self) -> str:
        """Returns the API changelog."""
        url = self.api_endpoint + "/changelog"
        response = self._httpx_client.get(url)
        _handle_response(response)
        return response.text

    def token_add(
        self,
        token: str,
        dollars: int,
        currency: Currency,
    ) -> api.TokenAdd.Response:
        """Add balance (money) to a token."""
        url = self.api_endpoint + api.TokenAdd.url.format(token=token)
        request = api.TokenAdd.Request(dollars=dollars, currency=currency)
        response = self._httpx_client.post(url, json=request.dict())
        _handle_response(response)
        response_object = api.TokenAdd.Response.parse_obj(response.json())
        return response_object

    def token_balance(self, token: str) -> api.TokenBalance.Response:
        """Return a token's balance."""
        url = self.api_endpoint + api.TokenBalance.url.format(token=token)
        response = self._httpx_client.get(url)
        _handle_response(response)
        response_object = api.TokenBalance.Response.parse_obj(response.json())
        return response_object

    def token_info(self, token: str) -> TokenInfo:
        """Return information about a token, including balance."""
        url = self.api_endpoint + f"/token/{token}/info"
        response = self._httpx_client.get(url)
        _handle_response(response)
        response_object = TokenInfo.parse_obj(response.json())
        return response_object

    def token_get_messages(self, token: str) -> list[api.TokenMessage]:
        """Get messages to/from the token."""
        url = self.api_endpoint + f"/token/{token}/messages"
        response = self._httpx_client.get(url=url)
        _handle_response(response)

        return parse_obj_as(list[api.TokenMessage], response.json())

    def token_send_message(self, token: str, message: str) -> None:
        """Send a message to SporeStack support."""
        url = self.api_endpoint + f"/token/{token}/messages"
        response = self._httpx_client.post(url=url, json={"message": message})
        _handle_response(response)

    def token_invoice(self, token: str, invoice: str) -> Invoice:
        """Gets a particular invoice."""
        url = self.api_endpoint + f"/token/{token}/invoices/{invoice}"
        response = self._httpx_client.get(url=url)
        _handle_response(response)

        return parse_obj_as(Invoice, response.json())

    def token_invoices(self, token: str) -> list[Invoice]:
        """Get token invoices."""
        url = self.api_endpoint + f"/token/{token}/invoices"
        response = self._httpx_client.get(url=url)
        _handle_response(response)

        return parse_obj_as(list[Invoice], response.json())
