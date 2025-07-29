"""Model definitions for the Cloudflare Turnstile response."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class MetaData(BaseModel):
    """
    Represents metadata associated with the Turnstile response.

    Attributes:
        ephemeral_id (Optional[str]): An optional identifier for the ephemeral session.
    """

    ephemeral_id: Optional[str] = None

    result_with_testing_key: bool = False


class Response(BaseModel):
    """
    Represents the response from the Cloudflare Turnstile verification.

    Attributes:
        success (bool): Indicates whether the verification was successful.
        hostname (Optional[str]): The hostname of the site where the Turnstile was used.
        action (Optional[str]): An optional action name associated with the Turnstile request.
        cdata (Optional[str]): An optional custom data field.
        metadata (MetaData): Optional metadata related to the Turnstile response.
        timestamp (Optional[datetime]): The time when the challenge was solved.
        error_codes (list[str]): A list of error codes that may be returned in case of failure.
    """

    success: bool
    """Indicates whether the verification was successful."""

    hostname: Optional[str] = None
    """The hostname of the site where the Turnstile was used."""

    action: Optional[str] = None
    """An optional action name associated with the Turnstile request."""

    cdata: Optional[str] = (
        None  # TODO: Get clarification on the type of cdata from Cloudflare.
    )
    """An optional custom data field."""

    metadata: MetaData = MetaData()
    """Optional metadata related to the Turnstile response."""

    timestamp: Optional[datetime] = Field(alias="challenge_ts", default=None)
    """The time when the challenge was solved."""

    error_codes: list[str] = Field(validation_alias="error-codes", default_factory=list)
    """A list of error codes that may be returned in case of failure."""
