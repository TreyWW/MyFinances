from dataclasses import dataclass, fields, field
from typing import Optional, Type, TypeVar, Any, TypedDict

# from github import Github
import github
import github.Repository
import github.Issue
import github.PullRequest
import github.Label
import github.IssueComment
import github.PullRequestComment
import github.NamedUser
from github.PaginatedList import PaginatedList

T = TypeVar("T")


def fill_dataclass_from_dict(dataclass_type: Type[T], data: dict) -> T | None:
    if not data:
        return None
    field_names = {f.name for f in fields(dataclass_type)}
    filtered_data = {k: v for k, v in data.items() if k in field_names}
    return dataclass_type(**filtered_data)


@dataclass
class User:
    id: str
    url: str
    login: str


@dataclass
class Comment:
    id: int
    body: str


@dataclass
class Issue:
    id: int
    number: int


@dataclass
class PullRequest:
    id: int
    number: int
    url: str
    state: str
    locked: bool
    user: User
    issue_url: Optional[str] = None


@dataclass
class Repository:
    id: int
    name: str
    full_name: str
    owner: User


@dataclass
class Changes:
    body: Optional[TypedDict("ChangeProperty", {"from": str})] = None
    title: Optional[TypedDict("ChangeProperty", {"from": str})] = None


@dataclass
class Context:
    event: dict
    action: str
    sender: User
    issue: Optional[Issue] = None
    pull_request: Optional[PullRequest] = None
    comment: Optional[Comment] = None
    repository: Optional[Repository] = None
    changes: Optional[Changes] = None


@dataclass
class Objects:
    github: github.MainClass.Github
    dict_context: Context
    repository: github.Repository.Repository
    sender: Optional[github.NamedUser] = None
    issue: Optional[github.Issue.Issue] = None
    pull_request: Optional[github.PullRequest.PullRequest] = None
    labels: PaginatedList[github.Label.Label] = None
    comment: Optional[github.IssueComment.IssueComment | github.PullRequestComment.PullRequestComment] = None

    def __post_init__(self):
        print("post_init")
        if not self.repository:
            print("no repository, returning")
            return

        if self.dict_context.issue:
            self.issue = self.repository.get_issue(self.dict_context.issue.number)

        if self.dict_context.pull_request:
            self.pull_request = self.repository.get_pull(self.dict_context.pull_request.number)

        if self.pull_request:
            self.labels = self.pull_request.get_labels()

        self.sender = self.github.get_user(self.dict_context.sender.login)
