import sys
from typing import Dict, List, Optional, Union

from github_domain_scraper.interfaces import StargazerProfile, UserProfile
from github_domain_scraper.backends import (
    ListRepositoriesBackend,
    UserProfileBackend,
    StargazerProfileBackend,
)

from github_domain_scraper.logger import get_logger

logger = get_logger(__file__)


class LinkExtractor:
    def __init__(
        self, initial_link: str, total_links_to_download: Optional[int] = None
    ):
        self.initial_link = initial_link
        self.total_links_to_download = total_links_to_download or sys.maxsize

    def extract(self) -> List[Optional[str]]:
        logger.info("Extracting...")
        backend = ListRepositoriesBackend(
            total_links_to_download=self.total_links_to_download
        )
        urls = backend.process(url=self.initial_link)
        return urls[: self.total_links_to_download]


class UserProfileInformationExtractor:
    def __init__(
        self,
        github_username: Union[str, List[str]],
        headless: bool = False,
        login_first: bool = True,
        login_username: Optional[str] = None,
        login_password: Optional[str] = None,
    ):
        self.github_usernames = (
            github_username if isinstance(github_username, list) else [github_username]
        )
        self.backend = UserProfileBackend(
            headless=headless,
            login_first=login_first,
            login_username=login_username,
            login_password=login_password,
        )

    def extract(self) -> Dict[str, UserProfile]:
        logger.info(f"Extracting {len(self.github_usernames)} usernames...")
        return self.backend.process(usernames=self.github_usernames)


class StargazerProfilesExtractor:
    def __init__(
        self,
        initial_link: str,
        headless: bool = False,
        login_first: bool = True,
    ):
        self.initial_link = initial_link
        self.headless = headless
        self.login_first = login_first

    def extract(
        self, start_page: int, end_page: int
    ) -> Dict[int, List[StargazerProfile]]:
        logger.info("Extracting stargazer profiles...")
        backend = StargazerProfileBackend(
            headless=self.headless,
            login_first=self.login_first,
        )
        return backend.process(
            url=self.initial_link,
            start_page=start_page,
            end_page=end_page,
        )
