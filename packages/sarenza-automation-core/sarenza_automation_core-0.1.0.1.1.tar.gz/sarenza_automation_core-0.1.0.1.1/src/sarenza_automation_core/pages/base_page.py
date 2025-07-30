import os
import re
import time
import platform
import traceback
from typing import Tuple, Union, List

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)

from sarenza_automation_core.exceptions.selenium_base_exception import (
    ClickInterceptedException,
)
from sarenza_automation_core.utils.logger import logger


class BasePage:
    def __init__(self, driver):
        """
        Base class for all page objects. Encapsulates common Selenium operations.

        :param driver: Selenium WebDriver instance.
        """
        self.driver = driver
        self.timeout = int(os.getenv("TIMEOUT", 5))

    def get_driver(self):
        """Returns the current WebDriver instance."""
        return self.driver

    def sleep(self, timeout: int = 5):
        """Pauses execution for a specified number of seconds."""
        time.sleep(timeout)

    def go_to_page(self, page: str):
        """Navigates the browser to the specified relative page path."""
        self.sleep(2)
        self.driver.get(f'{os.getenv("SUT_URL")}{page}')

    def verify_page_title(self, expected_title: str) -> bool:
        """Checks whether the expected title is present in the current page's title."""
        return expected_title.lower() in str(self.driver.title).lower()

    def click_on_element(
        self, locator_type: str, locator_value: str, timeout: int = None
    ):
        """Finds and clicks an element based on locator type and value."""
        self.get_element(locator_type, locator_value, timeout).click()

    def click_element(self, by: Tuple, retries: int = 2, delay: int = 5):
        """Attempts to click an element with retry on click interception."""
        for attempt in range(retries):
            try:
                element = self.get_element_by(by)
                element.click()
                return
            except ElementClickInterceptedException as e:
                self._log_click_intercepted(e, by, attempt, delay)
                time.sleep(delay)
        raise ClickInterceptedException(
            f"Failed to click {by} after {retries} attempts", element=by
        )

    def click_on_web_element(
        self, element: WebElement, retries: int = 2, delay: int = 5
    ):
        """Attempts to click a WebElement directly with retry on click interception."""
        for attempt in range(retries):
            try:
                element.click()
                return
            except ElementClickInterceptedException as e:
                self._log_click_intercepted(e, element, attempt, delay)
                time.sleep(delay)
        raise ClickInterceptedException(
            f"Failed to click element after {retries} attempts", element=element
        )

    def _log_click_intercepted(self, exception, target, attempt, delay):
        """Logs detailed info about a click interception exception."""
        tb = traceback.extract_tb(exception.__traceback__)[-1]
        logger.error(
            f"[Retry {attempt+1}] Click intercepted on {target}, retrying in {delay}s"
        )
        logger.error(
            f"{exception}, File: {tb.filename}, Line: {tb.lineno}, Function: {tb.name}"
        )

    def type_into_element_by(self, by: Tuple[By, str], text: str):
        """Types text into an element, clearing it first if necessary."""
        element = self.get_element_by(by)
        if by[1] == "phone":
            self._clear_input_with_shortcut(by)
        element.send_keys(text)

    def _clear_input_with_shortcut(self, by: Tuple[By, str]):
        """Clears input using Ctrl+A/Delete or Cmd+A/Delete on macOS."""
        try:
            mod = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
            self.click_element((By.ID, "firstName"))
            self.click_element(by)
            ActionChains(self.driver).key_down(mod).send_keys("a").key_up(
                mod
            ).send_keys(Keys.DELETE).perform()
        except Exception as e:
            logger.error(f"Failed to clear input {by[1]}: {e}")

    def get_element_by(self, by: Tuple[By, str], timeout: int = None) -> WebElement:
        """Finds a visible element using a (By, locator) tuple."""
        timeout = timeout or self.timeout
        element = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(by)
        )
        self.driver.execute_script(
            "arguments[0].style.border = '3px dashed red';", element
        )
        return element

    def get_elements_by(
        self, by: Tuple[By, str], timeout: int = None
    ) -> List[WebElement]:
        """Finds all visible elements matching a given (By, locator) tuple."""
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_all_elements_located(by)
        )

    def get_element(
        self, locator_type: str, locator_value: str, timeout: int = None
    ) -> WebElement:
        """Finds a visible element using a string-based locator type and value."""
        timeout = timeout or self.timeout
        strategy = {
            "_id": By.ID,
            "_name": By.NAME,
            "_class_name": By.CLASS_NAME,
            "_link_text": By.LINK_TEXT,
            "_xpath": By.XPATH,
            "xpath": By.XPATH,
            "_css": By.CSS_SELECTOR,
        }
        for suffix, by in strategy.items():
            if locator_type.endswith(suffix):
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, locator_value))
                )
                self.driver.execute_script(
                    "arguments[0].style.border = '3px solid red';", element
                )
                return element
        raise ValueError(f"Invalid locator type: {locator_type}")

    def is_element_not_displayed(self, locator: Tuple[By, str], timeout: int) -> bool:
        """Checks if an element is not displayed or not present within timeout."""
        timeout = timeout or self.timeout
        self.driver.implicitly_wait(timeout)
        try:
            element = self.driver.find_element(*locator)
            return not element.is_displayed()
        except NoSuchElementException:
            return True
        finally:
            self.driver.implicitly_wait(0)

    def display_status(self, locator_type: str, locator_value: str) -> bool:
        """Returns whether the specified element is displayed."""
        return self.get_element(locator_type, locator_value).is_displayed()

    def select_from_dropdown_by_visible_text(
        self, locator: Union[Tuple[By, str], str], value: str
    ):
        """Selects an option in a dropdown by visible text."""
        el = (
            self.driver.find_element(*locator)
            if isinstance(locator, tuple)
            else self.driver.find_element(By.ID, locator)
        )
        Select(el).select_by_visible_text(value)

    def select_from_dropdown_by_value(
        self, locator: Union[Tuple[By, str], str], value: str
    ):
        """Selects an option in a dropdown by value attribute."""
        el = (
            self.driver.find_element(*locator)
            if isinstance(locator, tuple)
            else self.driver.find_element(By.ID, locator)
        )
        Select(el).select_by_value(value)

    def wait_for_element_to_be_visible(
        self, locator_type: str, locator_value: str, timeout: int = None
    ) -> WebElement:
        """Waits until an element becomes visible based on locator type/value."""
        timeout = timeout or self.timeout
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located((locator_type, locator_value))
        )

    def click_using_javascript(self, locator_value: str, timeout: int = None):
        """Attempts to click a CSS-located element using JavaScript."""
        timeout = timeout or self.timeout
        js = f"document.querySelector('{locator_value}').click()"
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, locator_value))
            )
            logger.info(f"[JS Click] Executing: {js}")
            self.driver.execute_script(js)
        except:
            el = self.get_element_by((By.CSS_SELECTOR, locator_value))
            self.driver.execute_script("arguments[0].click();", el)

    def scroll_down_until_element_by(
        self, locator: Tuple[By, str], step=100, delay=0.06
    ):
        """Scrolls down incrementally until the element is in view."""
        element = self.get_element_by(locator)
        target_y = element.location["y"]
        current_scroll = 0
        while current_scroll < target_y:
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            current_scroll += step
            self.sleep(delay)
        self.driver.execute_script(f"window.scrollTo(0, {target_y});")

    def scroll_up_to_element(self, locator: Tuple[By, str], step=100, delay=0.06):
        """Scrolls up incrementally until the element is in view."""
        element = self.get_element_by(locator)
        target_y = element.location["y"]
        current_scroll = self.driver.execute_script("return window.pageYOffset;")
        while current_scroll > target_y:
            current_scroll = max(target_y, current_scroll - step)
            self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            self.sleep(delay)
        self.driver.execute_script(f"window.scrollTo(0, {target_y});")
