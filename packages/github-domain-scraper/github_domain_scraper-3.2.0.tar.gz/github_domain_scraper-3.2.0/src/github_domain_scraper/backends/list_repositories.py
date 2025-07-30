import re
import urllib.parse

from typing import Dict
from github_domain_scraper.backends.base import BaseLink, BaseListRepositoriesBackend
from github_domain_scraper.exceptions import InvalidSearchType


class UserRepositoriesLink(BaseLink):
    pattern = r"^(https:\/\/github.com\/[a-zA-Z\d](?:[a-zA-Z\d]|-(?=[a-zA-Z\d])){0,38})\/?(\?tab=[\w-]+(.*)?)?$"

    def check_url_match(self) -> bool:
        return bool(re.match(self.pattern, self.url))

    def get_metadata(self) -> Dict[str, str]:
        match = re.match(self.pattern, self.url)
        if match is None:
            raise InvalidSearchType(
                "Provided link does not support extraction yet. Please contact package owner to add feature."
            )
        url = match.group(1)
        return {
            "url": f"{url}?tab=repositories",
            "xpath": '//div[@id="user-repositories-list"]/ul/li/div/div/h3/a[@href]',
            "next_xpath": '//a[@class="next_page"]',
        }


class SearchRepositoryLink(BaseLink):
    pattern = r"^https:\/\/github.com\/search\?"
    x_paths = {
        "repositories": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "issues": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "pullrequests": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "discussions": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "users": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "commits": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "registrypackages": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "wikis": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "topics": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
        "marketplace": '//div[@data-testid="results-list"]//div[contains(@class, "search-title")]//a[1]',
    }

    def check_url_match(self) -> bool:
        return bool(re.match(self.pattern, self.url))

    def get_metadata(self) -> Dict[str, str]:
        xpath = None
        try:
            parsed_url = urllib.parse.urlparse(self.url)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            search_type = query_params["type"][0].lower()
            xpath = self.x_paths[search_type]
        except (KeyError, IndexError):
            breakpoint()
            raise InvalidSearchType(
                "Provided link does not support extraction yet. Please contact package owner to add feature."
            )

        return {
            "url": self.url,
            "xpath": xpath,
            "next_xpath": '//a[text()="Next"]',
        }


class ListRepositoriesBackend(BaseListRepositoriesBackend):
    link_classes = [
        UserRepositoriesLink,
        SearchRepositoryLink,
    ]
