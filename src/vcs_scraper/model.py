# pylint: disable=no-name-in-module
# Standard Library
import os
from enum import Enum
from typing import Annotated

# Third Party
from pydantic import BaseModel, Field, StringConstraints, field_validator

# First Party
from vcs_scraper.constants import AZURE_DEVOPS, BITBUCKET, GITHUB_PUBLIC


class Repository(BaseModel):
    repository_name: str
    repository_id: str
    repository_url: str
    project_key: str
    vcs_instance_name: str
    latest_commit: str


class VCSProviders(str, Enum):
    AZURE_DEVOPS = AZURE_DEVOPS
    BITBUCKET = BITBUCKET
    GITHUB_PUBLIC = GITHUB_PUBLIC


class VCSInstance(BaseModel):
    name: Annotated[str, StringConstraints(max_length=200)]
    provider_type: VCSProviders
    hostname: Annotated[str, StringConstraints(max_length=200)]
    port: Annotated[int, Field(gt=-0, lt=65536)]
    scheme: str
    username: Annotated[str, StringConstraints(max_length=200)]
    token: Annotated[str, StringConstraints(max_length=200)]
    exceptions: list[str] | None = []
    scope: list[str] | None = []
    organization: str | None = None

    @field_validator("scheme", mode="before")
    @classmethod
    def check_scheme(cls, value):
        allowed_schemes = ["http", "https"]
        if value not in allowed_schemes:
            raise ValueError(f"The scheme '{value}' must be one of the following {', '.join(allowed_schemes)}")
        return value

    @field_validator("organization", mode="before")
    @classmethod
    def check_organization(cls, value, values):
        if not value:
            if values.data["provider_type"] == AZURE_DEVOPS:
                raise ValueError("The organization field needs to be specified for Azure devops vcs instances")
        return value

    @field_validator("scope", mode="before")
    @classmethod
    def check_scope_and_exceptions(cls, value, values):
        if value and values.data["exceptions"]:
            raise ValueError(
                "You cannot specify bot the scope and exceptions to the scan, only one setting" " is supported."
            )
        return value

    @field_validator("username", mode="before")
    @classmethod
    def check_presence_of_username(cls, value, values):
        if not os.environ.get(value):
            raise ValueError(
                f"The username for VCS Instance {values.data['name']} could not be found in the "
                f"environment variable {value}"
            )
        return os.environ.get(value)

    @field_validator("token", mode="before")
    @classmethod
    def check_presence_of_token(cls, value, values):
        if not os.environ.get(value):
            raise ValueError(
                f"The access token for VCS Instance {values.data['name']} could not be found in the "
                f"environment variable {value}"
            )
        return os.environ.get(value)
