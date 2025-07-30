from typing import NewType, Any, TypedDict

PinterestReport = NewType('PinterestReport', dict[str, list[dict[str, Any]]])

class RefreshTokenResponse(TypedDict):
    access_token: str
    refresh_token: str
    refresh_token_expires_at: str
