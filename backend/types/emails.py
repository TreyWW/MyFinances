from dataclasses import dataclass
from typing import Literal, TypedDict

from mypy_boto3_sesv2.type_defs import SendEmailResponseTypeDef, SendBulkEmailResponseTypeDef, BulkEmailEntryResultTypeDef


class SingleTemplatedEmailContent(TypedDict):
    template_name: str
    template_data: dict | str


@dataclass(frozen=False)
class SingleEmailInput:
    destination: str | list[str]
    subject: str | None
    content: str | SingleTemplatedEmailContent
    ConfigurationSetName: str | None = None
    from_address: str | None = None
    from_address_name_prefix: str | None = None


@dataclass(frozen=True)
class SingleEmailSuccessResponse:
    response: SendEmailResponseTypeDef
    success: Literal[True] = True


@dataclass(frozen=True)
class SingleEmailErrorResponse:
    message: str
    response: SendEmailResponseTypeDef | None
    success: Literal[False] = False


@dataclass
class BulkEmailEmailItem:
    destination: str
    template_data: dict | str


@dataclass(frozen=False)
class BulkTemplatedEmailInput:
    email_list: list[BulkEmailEmailItem]
    template_name: str
    default_template_data: dict | str
    ConfigurationSetName: str | None = None
    from_address: str | None = None
    from_address_name_prefix: str | None = None


@dataclass(frozen=True)
class BulkEmailSuccessResponse:
    response: SendBulkEmailResponseTypeDef
    success: Literal[True] = True


@dataclass(frozen=True)
class BulkEmailErrorResponse:
    message: str
    response: SendBulkEmailResponseTypeDef | None
    success: Literal[False] = False
