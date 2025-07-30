from selenium.webdriver.remote.webdriver import WebDriver
import json
from loguru import logger


class LocalStorageHelper:
    """
    A helper class to interact with the browser's localStorage via Selenium WebDriver.
    """

    def __init__(self, driver: WebDriver):
        """
        Initialize the helper with a Selenium WebDriver instance.

        :param driver: Selenium WebDriver instance.
        """
        self.driver = driver

    def set_item(self, key: str, value):
        """
        Sets a key-value pair in localStorage.

        :param key: The key to set.
        :param value: The value to store (will be JSON-serialized).
        """
        try:
            json_value = json.dumps(value)
            self.driver.execute_script(
                f"window.localStorage.setItem('{key}', arguments[0]);", json_value
            )
            logger.info(f"[LocalStorage] Set key: '{key}' with value: {value}")
        except Exception as e:
            logger.error(f"[LocalStorage][Error] Failed to set item '{key}': {e}")

    def get_item(self, key: str):
        """
        Retrieves a value from localStorage.

        :param key: The key to retrieve.
        :return: The deserialized value, or None if not found or error occurs.
        """
        try:
            result = self.driver.execute_script(
                f"return window.localStorage.getItem('{key}');"
            )
            if result is None:
                logger.info(f"[LocalStorage] Key '{key}' not found.")
                return None
            value = json.loads(result)
            logger.info(f"[LocalStorage] Retrieved key: '{key}' with value: {value}")
            return value
        except Exception as e:
            logger.error(f"[LocalStorage][Error] Failed to get item '{key}': {e}")
            return None

    def remove_item(self, key: str):
        """
        Removes an item from localStorage.

        :param key: The key to remove.
        """
        try:
            self.driver.execute_script(f"window.localStorage.removeItem('{key}');")
            logger.info(f"[LocalStorage] Removed key: '{key}'")
        except Exception as e:
            logger.error(f"[LocalStorage][Error] Failed to remove item '{key}': {e}")
