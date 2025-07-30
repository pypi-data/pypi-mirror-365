"""SporeStack API request/response models"""

from datetime import datetime
from typing import Annotated, Optional, Union

from pydantic import BaseModel, Field

from .constants import Currency, Provider, ServerDeletedBy, TokenMessageSender
from .models import Invoice


class TokenAdd:
    url = "/token/{token}/add"
    method = "POST"

    class Request(BaseModel):
        currency: Currency
        dollars: int
        affiliate_token: Union[str, None] = None

    class Response(BaseModel):
        invoice: Invoice


class TokenBalance:
    url = "/token/{token}/balance"
    method = "GET"

    class Response(BaseModel):
        cents: int
        usd: str


class ServerQuote:
    url = "/server/quote"
    method = "GET"

    """Takes days and flavor as parameters, like ?days=7&flavor=vps-1vcpu-1gb"""

    class Response(BaseModel):
        cents: Annotated[
            int, Field(ge=1, title="Cents", description="(US) cents", example=1_000_00)
        ]
        usd: Annotated[
            str,
            Field(
                min_length=5,
                title="USD",
                description="USD in $1,000.00 format",
                example="$1,000.00",
            ),
        ]


class ServerLaunch:
    url = "/token/{token}/servers"
    method = "POST"

    class Request(BaseModel):
        flavor: str
        ssh_key: str
        operating_system: str
        days: Union[int, None] = None
        provider: Provider = Provider.DIGITALOCEAN
        region: Optional[str] = None
        """None is automatic, otherwise a string region slug."""
        hostname: str = ""
        """Hostname to refer to your server by."""
        autorenew: bool = False
        """
        Automatically renew the server with the token used, keeping it at 1 week
        expiration.
        """
        user_data: Annotated[
            Union[str, None],
            Field(
                title="Cloud Init User Data",
                description=("Can be used to configure the server when launched."),
                min_length=0,
                max_length=64 * 1024,
            ),
        ] = None

    class Response(BaseModel):
        machine_id: str


class ServerTopup:
    url = "/token/{token}/servers/{machine_id}/topup"
    method = "POST"

    class Request(BaseModel):
        days: int


class ServerInfo:
    url = "/token/{token}/servers/{machine_id}"
    method = "GET"

    class Response(BaseModel):
        created_at: int
        expiration: int
        running: bool
        machine_id: str
        ipv4: str
        ipv6: str
        region: str
        flavor_slug: str
        provider: str  # Technically, should be an enum but this may be more futureproof
        deleted_at: int
        deleted_by: Union[ServerDeletedBy, None]
        forgotten_at: Union[datetime, None]
        suspended_at: Union[datetime, None]
        operating_system: str
        hostname: str
        autorenew: bool


class ServersLaunchedFromToken:
    url = "/token/{token}/servers"
    method = "GET"

    class Response(BaseModel):
        servers: list[ServerInfo.Response]


class TokenMessage(BaseModel):
    message: Annotated[
        str,
        Field(
            title="Message",
            min_length=1,
            max_length=10_000,
        ),
    ]
    sent_at: Annotated[
        datetime,
        Field(
            title="Sent At",
            description="When the message was sent.",
        ),
    ]
    sender: Annotated[
        TokenMessageSender, Field(title="Sender", description="Who sent the message.")
    ]
