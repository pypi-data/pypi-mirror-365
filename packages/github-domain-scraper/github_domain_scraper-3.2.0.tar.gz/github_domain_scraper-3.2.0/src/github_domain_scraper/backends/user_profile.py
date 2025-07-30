import contextlib
import re
from typing import List, Optional, Dict, Any

from github_domain_scraper.interfaces.user_profile import UserProfile


from github_domain_scraper.backends.base import BaseUserProfileBackend

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class UserProfileBackend(BaseUserProfileBackend):
    timeout = 0.5

    @property
    def _avatar(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@itemprop="image"]',
                timeout=self.timeout,
            )
            link: Optional[str] = element.get_attribute("href")
            return link
        return None

    @property
    def _fullname(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//h1[@class="vcard-names "]/span[1]',
                timeout=self.timeout,
            )
            fullname: str = element.text
            return fullname
        return None

    @property
    def _username(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//h1[@class="vcard-names "]/span[2]',
                timeout=self.timeout,
            )
            fullname: str = element.text
            return fullname
        return None

    @property
    def _bio(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//div[contains(@class, "user-profile-bio")]/div',
                timeout=self.timeout,
            )
            bio: str = element.text
            return bio
        return None

    @property
    def _followers(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//div[contains(@class, "js-profile-editable-area")]/div[2]//a[1]/span',
                timeout=self.timeout,
            )
            followers: str = element.text
            return followers
        return None

    @property
    def _following(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//div[contains(@class, "js-profile-editable-area")]/div[2]//a[2]/span',
                timeout=self.timeout,
            )
            following: str = element.text
            return following
        return None

    @property
    def _works_for(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//ul[@class="vcard-details"]/li[@itemprop="worksFor"]/span/div',
                timeout=self.timeout,
            )
            works_for: str = element.text
            return works_for
        return None

    @property
    def _home_location(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//ul[@class="vcard-details"]/li[@itemprop="homeLocation"]/span',
                timeout=self.timeout,
            )
            home_location: str = element.text
            return home_location
        return None

    @property
    def _email(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//ul[@class="vcard-details"]/li[@itemprop="email"]/a',
                timeout=self.timeout,
            )
            email: str = element.text
            return email
        return None

    @property
    def _profile_website_url(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//ul[@class="vcard-details"]/li[@itemprop="url"]/a',
                timeout=self.timeout,
            )
            profile_website_url: str = element.text
            return profile_website_url
        return None

    @property
    def _social(self) -> Optional[List[str]]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            elements = self.wd.web_driver_wait_till_all_existence(
                By.XPATH,
                '//ul[@class="vcard-details"]/li[@itemprop="social"]/a',
                timeout=self.timeout,
            )
            social: List[str] = [
                element.get_attribute("href")
                for element in elements
                if element.get_attribute("href")
            ]
            return list(set(social))
        return None

    @property
    def _achievements(self) -> Optional[List[str]]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            elements = self.wd.web_driver_wait_till_all_existence(
                By.XPATH,
                '//img[@data-hovercard-type="achievement"]',
                timeout=self.timeout,
            )
            achievements: List[str] = []
            for element in elements:
                if alt := element.get_attribute("alt"):
                    achievement = alt.replace("Achievement: ", "")
                    if achievement:
                        achievements.append(achievement)
            return list(set(achievements))
        return None

    @property
    def _organizations(self) -> Optional[List[str]]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            elements = self.wd.web_driver_wait_till_all_existence(
                By.XPATH,
                '//a[@data-hovercard-type="organization" and @itemprop="follows"]',
                timeout=self.timeout,
            )
            organizations: List[str] = [
                element.get_attribute("href")
                for element in elements
                if element.get_attribute("href")
            ]
            return list(set(organizations))
        return None

    @property
    def _number_of_repositories(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="repositories"]/span',
                timeout=self.timeout,
            )
            number_of_repositories: str = element.text
            return number_of_repositories

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i1repositories-tab"]/span[@class="Counter"]',
                timeout=self.timeout,
            )
            number_of_repositories = element.text
            return number_of_repositories

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i1repositories-tab"]/span',
                timeout=self.timeout,
            )
            number_of_repositories = element.text
            return number_of_repositories
        return None

    @property
    def _number_of_stars(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="stars"]/span',
                timeout=self.timeout,
            )
            number_of_stars: str = element.text
            return number_of_stars

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i4stars-tab"]/span[@class="Counter"]',
                timeout=self.timeout,
            )
            number_of_stars = element.text
            return number_of_stars

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i4stars-tab"]/span',
                timeout=self.timeout,
            )
            number_of_stars = element.text
            return number_of_stars

        return None

    @property
    def _pinned_repositories(self) -> Optional[List[str]]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            elements = self.wd.web_driver_wait_till_all_existence(
                By.XPATH,
                '//div[@class="pinned-item-list-item-content"]/div/div/span/a',
                timeout=self.timeout,
            )
            pinned_repositories: List[str] = [
                element.get_attribute("href")
                for element in elements
                if element.get_attribute("href")
            ]
            return list(set(pinned_repositories))
        return None

    @property
    def _uid(self) -> Optional[str]:
        with contextlib.suppress(Exception):
            if avatar := self._avatar:
                # Extract UID using regex: https://avatars.githubusercontent.com/u/58165487?v=4
                # -> 58165487
                result = re.search(r"/u/(\d+)", avatar)
                if result:
                    return result.group(1)
        return None

    @property
    def _projects(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="projects"]/span',
                timeout=self.timeout,
            )
            projects: str = element.text or "0"
            return projects

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i2projects-tab"]/span[@class="Counter"]',
                timeout=self.timeout,
            )
            projects = element.text or "0"
            return projects

        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.XPATH,
                '//a[@data-tab-item="i2projects-tab"]/span',
                timeout=self.timeout,
            )
            projects = element.text or "0"
            return projects

        return None

    @property
    def _contribs(self) -> Optional[str]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            element = self.wd.web_driver_wait_till_existence(
                By.ID,
                "js-contribution-activity-description",
                timeout=self.timeout,
            )

            text: str = element.text
            # text: 145 contributions in the last year
            # -> 145
            result = re.search(r"(\d+)", text)
            if result:
                return result.group(1)

        return None

    @property
    def _contrib_matrix(self) -> Optional[Dict[str, Any]]:
        with contextlib.suppress(TimeoutException, NoSuchElementException):
            _elements = self.wd.web_driver_wait_till_all_existence(
                By.XPATH,
                "//td[@data-date]",
                timeout=self.timeout,
            )
            contrib_matrix: Dict[str, Any] = {}
            for element in _elements:
                try:
                    data_date = element.get_attribute("data-date")
                    data_level = element.get_attribute("data-level")
                    data_id = element.get_attribute("id")
                    # data_id: contribution-day-component-1-2
                    # -> 1
                    data_x = int(data_id.split("-")[3])
                    data_y = int(data_id.split("-")[4])

                    contrib_matrix[data_date] = {
                        "level": data_level,
                        "x": data_x,
                        "y": data_y,
                    }
                except Exception as e:
                    self.logger.error(
                        f"[_contrib_matrix] Parsing error: {e}\n{self.wd.current_url}"
                    )
                    continue

            return contrib_matrix
        return None

    @property
    def _type(self) -> Optional[str]:
        return "profile"

    @property
    def _url(self) -> Optional[str]:
        return str(self.wd.current_url)

    def get_profile(self) -> UserProfile:
        return UserProfile(
            avatar=self._avatar or None,
            fullname=self._fullname or None,
            username=self._username or None,
            bio=self._bio or None,
            followers=self._followers or None,
            following=self._following or None,
            works_for=self._works_for or None,
            home_location=self._home_location or None,
            email=self._email or None,
            profile_website_url=self._profile_website_url or None,
            social=self._social or None,
            achievements=self._achievements or None,
            organizations=self._organizations or None,
            number_of_repositories=self._number_of_repositories or None,
            number_of_stars=self._number_of_stars or None,
            pinned_repositories=self._pinned_repositories or None,
            uid=self._uid or None,
            projects=self._projects or None,
            contribs=self._contribs or None,
            contrib_matrix=self._contrib_matrix or None,
            type=self._type or None,
            url=self._url or None,
        )
