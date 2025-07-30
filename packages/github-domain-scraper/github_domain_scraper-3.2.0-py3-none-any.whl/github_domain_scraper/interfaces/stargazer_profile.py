from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class StargazerProfile:
    type: Optional[str] = None
    """Type of profile."""

    username: Optional[str] = None
    """User's GitHub username."""

    avatar: Optional[str] = None
    """User's avatar URL."""

    url: Optional[str] = None
    """User's profile URL."""

    sub_text: Optional[str] = None
    """User's sub text."""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "username": self.username,
            "avatar": self.avatar,
            "url": self.url,
            "sub_text": self.sub_text,
        }
