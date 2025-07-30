from typing import List, Optional
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import (
    element_to_be_clickable,
    presence_of_element_located,
    presence_of_all_elements_located,
)


from undetected_chromedriver import Chrome, ChromeOptions, WebElement


class SeleniumWebDriver(Chrome):  # type: ignore
    timeout = 10.0

    def __init__(self, download_path: Optional[str] = None, headless: bool = False):
        super().__init__(
            options=self.get_options(
                download_path=download_path,
                headless=headless,
            )
        )

    def get_options(
        self, download_path: Optional[str] = None, headless: bool = False
    ) -> ChromeOptions:
        options = ChromeOptions()

        if download_path:
            options.add_experimental_option(
                "prefs", {"download.default_directory": download_path}
            )

        if headless:
            options.add_argument("--headless")
        else:
            options.add_argument("--start-maximized")

        return options

    def switch_to_last_tab(self) -> None:
        self.switch_to.window(self.window_handles[-1])

    def web_driver_wait(
        self,
        timeout: Optional[float] = None,
    ) -> WebDriverWait["SeleniumWebDriver"]:
        return WebDriverWait(self, timeout=timeout or self.timeout)

    def web_driver_wait_till_existence(
        self,
        by: str,
        value: str,
        timeout: Optional[float] = None,
    ) -> WebElement:
        return self.web_driver_wait(timeout).until(
            presence_of_element_located((by, value))
        )

    def web_driver_wait_till_all_existence(
        self,
        by: str,
        value: str,
        timeout: Optional[float] = None,
    ) -> List[WebElement]:
        return self.web_driver_wait(timeout).until(
            presence_of_all_elements_located((by, value))
        )

    def web_driver_wait_and_click(
        self,
        by: str,
        value: str,
        timeout: Optional[float] = None,
    ) -> WebElement:
        element = self.web_driver_wait(timeout).until(
            element_to_be_clickable((by, value))
        )
        element.click()

    def web_driver_wait_and_send_inputs(
        self,
        by: str,
        value: str,
        input_text: str,
        timeout: Optional[float] = None,
    ) -> WebElement:
        element = self.web_driver_wait(timeout).until(
            element_to_be_clickable((by, value))
        )
        element.send_keys(input_text)
