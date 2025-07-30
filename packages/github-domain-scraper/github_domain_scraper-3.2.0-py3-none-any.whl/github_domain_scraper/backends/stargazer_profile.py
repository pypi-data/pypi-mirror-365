import contextlib
from typing import List, Optional, Any

from bs4 import BeautifulSoup

from github_domain_scraper.interfaces import StargazerProfile

from github_domain_scraper.backends.base import BaseStarGazerBackend

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class StargazerProfileBackend(BaseStarGazerBackend):
    timeout = 0.5

    def _get_stargazer_profile(self, element: Any) -> Optional[StargazerProfile]:
        profile = StargazerProfile(type="stargazer_profile")

        # Find avatar image
        avatar_element = element.find("img", class_="avatar avatar-user")
        if avatar_element:
            profile.avatar = avatar_element.get("src")

        # Find username and URL
        h2_element = element.find("h2")
        if h2_element:
            username_element = h2_element.find("a")
            if username_element:
                profile.username = username_element.get_text(strip=True)
                profile.url = username_element.get("href")

        # Find sub text
        p_element = element.find("p")
        if p_element:
            sub_text_element = p_element.find("span")
            if sub_text_element:
                profile.sub_text = sub_text_element.get_text(strip=True)
            else:
                profile.sub_text = p_element.get_text(strip=True)

        return profile

    def get_profiles(self) -> List[StargazerProfile]:
        profiles = []
        ol_element: Any = None
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            ol_element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                "//ol",
                timeout=self.timeout,
            )

        if ol_element:
            ol_html = ol_element.get_attribute("innerHTML")
            soup = BeautifulSoup(ol_html, "lxml")

            for element in soup.select("li > div"):
                profile = self._get_stargazer_profile(element)
                if profile:
                    profiles.append(profile)

        return profiles
