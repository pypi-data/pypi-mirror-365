from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class UserProfile:
    """
    Data class for GitHub user profile information.

    This class represents the structure of GitHub user profile data
    with all the fields that can be extracted from a user's profile page.
    """

    avatar: Optional[str] = None
    """User's avatar URL."""

    fullname: Optional[str] = None
    """User's full name."""

    username: Optional[str] = None
    """User's GitHub username."""

    bio: Optional[str] = None
    """User's bio/description."""

    followers: Optional[str] = None
    """Number of followers."""

    following: Optional[str] = None
    """Number of users being followed."""

    works_for: Optional[str] = None
    """Company/organization the user works for."""

    home_location: Optional[str] = None
    """User's location."""

    email: Optional[str] = None
    """User's email address."""

    profile_website_url: Optional[str] = None
    """User's website URL."""

    social: Optional[List[str]] = None
    """List of social media links."""

    achievements: Optional[List[str]] = None
    """List of user achievements."""

    organizations: Optional[List[str]] = None
    """List of organizations the user belongs to."""

    number_of_repositories: Optional[str] = None
    """Number of repositories."""

    number_of_stars: Optional[str] = None
    """Number of stars received."""

    pinned_repositories: Optional[List[str]] = None
    """List of pinned repository URLs."""

    uid: Optional[str] = None
    """User's unique identifier."""

    projects: Optional[str] = None
    """Number of projects."""

    contribs: Optional[str] = None
    """Number of contributions."""

    contrib_matrix: Optional[Dict[str, Any]] = None
    """Contribution matrix data."""

    type: Optional[str] = None
    """Type of profile."""

    url: Optional[str] = None
    """Profile URL."""

    def to_dict(self, flatten: bool = False) -> Dict[str, Any]:
        """
        Convert the UserProfile to a dictionary.

        Returns:
            Dict containing all profile fields and their values.
        """
        result = {
            "avatar": self.avatar,
            "fullname": self.fullname,
            "username": self.username,
            "bio": self.bio,
            "followers": self.followers,
            "following": self.following,
            "works_for": self.works_for,
            "home_location": self.home_location,
            "email": self.email,
            "profile_website_url": self.profile_website_url,
            "social": self.social,
            "achievements": self.achievements,
            "organizations": self.organizations,
            "number_of_repositories": self.number_of_repositories,
            "number_of_stars": self.number_of_stars,
            "pinned_repositories": self.pinned_repositories,
            "uid": self.uid,
            "projects": self.projects,
            "contribs": self.contribs,
            "contrib_matrix": self.contrib_matrix,
            "type": self.type,
            "url": self.url,
        }

        if flatten:
            if self.achievements is not None:
                result["achievements"] = "\n".join(self.achievements)
            if self.organizations is not None:
                result["organizations"] = "\n".join(self.organizations)
            if self.pinned_repositories is not None:
                result["pinned_repositories"] = "\n".join(self.pinned_repositories)
            if self.social is not None:
                result["social"] = "\n".join(self.social)

            del result["contrib_matrix"]

        return result
