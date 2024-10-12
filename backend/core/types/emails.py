from dataclasses import dataclass, field
from typing import TypedDict

from mypy_boto3_sesv2.type_defs import SendEmailResponseTypeDef, SendBulkEmailResponseTypeDef

from backend.core.utils.dataclasses import BaseServiceResponse


class SingleEmailSendServiceResponse(BaseServiceResponse[SendEmailResponseTypeDef]): ...


class BulkEmailSendServiceResponse(BaseServiceResponse[SendBulkEmailResponseTypeDef]): ...


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


@dataclass
class BulkEmailEmailItem:
    destination: str
    template_data: dict | str
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)


@dataclass(frozen=False)
class BulkTemplatedEmailInput:
    email_list: list[BulkEmailEmailItem]
    template_name: str
    default_template_data: dict | str
    ConfigurationSetName: str | None = None
    from_address: str | None = None
    from_address_name_prefix: str | None = None
