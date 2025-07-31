from enum import Enum
from typing import Optional
from typing import TypedDict

from django.http import HttpRequest


class Result(str, Enum):
    Success = "Success"
    Partial = "Partial"
    Failure = "Failure"
    NA = "NA"


class Severity(str, Enum):
    Informational = "Informational"
    Low = "Low"
    Medium = "Medium"
    High = "High"


class Client(TypedDict, total=False):
    """Dictionary to represent properties of the HTTP Client."""

    """Internet Protocol Address of the client making the Authentication
    event."""
    ip_address: Optional[str]
    """URL requested by the client."""
    requested_url: Optional[str]


class Server(TypedDict, total=False):
    """Dictionary to represent properties of the HTTP Server."""

    """
    The FQDN that this server is listening to HTTP requests on. For example:
        web.trade.gov.uk

    Defaults to the WSGI HTTP_HOST field if not provided.
    """
    domain_name: Optional[str]
    """Internet Protocol Address of the server serving this request."""
    ip_address: Optional[str]
    """
    A unique (within DBT) identifier for the software running on the server.
    For example: berry-auctions-frontend

    Defaults to combining the environment variables COPILOT_APPLICATION_NAME and
    COPILOT_SERVICE_NAME separated by a '-'.
    """
    service_name: Optional[str]


def _default_severity(result: Result) -> Severity:
    return Severity.Informational if result == Result.Success else Severity.Medium


def _get_client_ip_address(request: HttpRequest) -> Optional[str]:
    # Import here as ipware uses settings
    from ipware import get_client_ip

    client_ip, _ = get_client_ip(request)
    return client_ip
