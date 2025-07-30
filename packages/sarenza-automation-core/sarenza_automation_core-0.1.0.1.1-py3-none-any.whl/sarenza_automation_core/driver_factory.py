import os
from enum import Enum
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
from appium import webdriver as appiumdriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from appium.options.common.base import AppiumOptions
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class BrowserType(Enum):
    SAFARI = "safari"
    REMOTE_CHROME = "remote_chrome"
    REMOTE_FIREFOX = "remote_firefox"
    REMOTE_EDGE = "remote_edge"
    CHROME = "chrome"
    CHROME_HEADLESS = "chrome_headless"
    FIREFOX = "firefox"
    EDGE = "edge"


def delete_safari_cookies(driver):
    try:
        driver.delete_all_cookies()
        logger.info("All cookies deleted.")
    except Exception as e:
        logger.error(f"Failed to delete cookies: {e}")


def get_safari_driver():
    command_executor = RemoteConnection(os.getenv("APPIUM_SERVER_URL"))
    command_executor.set_timeout(int(os.getenv("APPIUM_COMMAND_TIMEOUT", 300)))
    options = AppiumOptions()
    options.load_capabilities(
        {
            "platformName": "iOS",
            "appium:automationName": "XCUITest",
            "browserName": "Safari",
            "appium:udid": os.getenv("DEVICE_UDID"),
            "appium:includeSafariInWebviews": True,
            "appium:connectHardwareKeyboard": True,
            "safariAllowPopups": False,
            "safariIgnoreFraudWarning": True,
            "appium:fullReset": True,
            "appium:safariClearData": True,
        }
    )
    return appiumdriver.Remote(command_executor=command_executor, options=options)


def get_remote_chrome_driver(load_strategy: str, remote_hub_url: str):
    logger.info(
        f"Initializing remote Chrome at {remote_hub_url} with strategy {load_strategy}."
    )
    options = ChromeOptions()
    options.page_load_strategy = load_strategy
    try:
        return webdriver.Remote(command_executor=remote_hub_url, options=options)
    except Exception as e:
        logger.error(f"Failed to initialize remote Chrome WebDriver: {e}")
        raise


def get_remote_firefox_driver(load_strategy: str, remote_hub_url: str):
    logger.info(
        f"Initializing remote Firefox at {remote_hub_url} with strategy {load_strategy}."
    )
    options = FirefoxOptions()
    options.page_load_strategy = load_strategy
    try:
        return webdriver.Remote(command_executor=remote_hub_url, options=options)
    except Exception as e:
        logger.error(f"Failed to initialize remote Firefox WebDriver: {e}")
        raise


def get_chrome_driver(load_strategy):
    options = ChromeOptions()
    options.page_load_strategy = load_strategy
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )


def get_chrome_headless_driver(load_strategy):
    options = ChromeOptions()
    options.page_load_strategy = load_strategy
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--enable-logging")
    options.add_argument("--v=1")
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()), options=options
    )


def get_firefox_driver(load_strategy="eager"):
    options = FirefoxOptions()
    options.page_load_strategy = load_strategy
    return webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()), options=options
    )


def get_edge_driver():
    return webdriver.Edge()


BROWSER_FACTORY = {
    BrowserType.SAFARI: get_safari_driver,
    BrowserType.REMOTE_CHROME: lambda: get_remote_chrome_driver(
        os.getenv("LOAD_STRATEGY", "eager"), os.getenv("REMOTE_HUB_URL", "")
    ),
    BrowserType.REMOTE_FIREFOX: lambda: get_remote_firefox_driver(
        os.getenv("LOAD_STRATEGY", "eager"), os.getenv("REMOTE_HUB_URL", "")
    ),
    BrowserType.CHROME: lambda: get_chrome_driver(os.getenv("LOAD_STRATEGY", "eager")),
    BrowserType.CHROME_HEADLESS: lambda: get_chrome_headless_driver(
        os.getenv("LOAD_STRATEGY", "eager")
    ),
    BrowserType.FIREFOX: lambda: get_firefox_driver(
        os.getenv("LOAD_STRATEGY", "eager")
    ),
    BrowserType.EDGE: get_edge_driver,
}


def get_driver():
    browser_name = os.getenv("BROWSER_NAME", "chrome").lower()
    try:
        browser_type = BrowserType(browser_name)
        return BROWSER_FACTORY[browser_type]()
    except (ValueError, KeyError) as e:
        raise RuntimeError(f"Failed to initialize browser '{browser_name}': {e}")
