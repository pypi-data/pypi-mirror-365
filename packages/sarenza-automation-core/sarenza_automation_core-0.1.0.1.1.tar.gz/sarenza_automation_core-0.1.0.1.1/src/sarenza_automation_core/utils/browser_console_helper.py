from selenium import webdriver
from loguru import logger


class BrowserConsoleInteractor:
    def __init__(self, driver: webdriver.Remote):
        """
        Initializes the interactor with a Selenium WebDriver instance.
        :param driver: A Selenium WebDriver instance configured to interact with the browser.
        """
        self.driver = driver

    def get_variable(self, variable_name: str):
        """
        Executes a JavaScript snippet to fetch a variable from the browser's global scope.
        :param variable_name: The name of the variable to fetch (e.g., 'tc_full_events').
        :return: The value of the variable, or None if it doesn't exist.
        """
        try:
            value = self.driver.execute_script(
                f"return typeof {variable_name} !== 'undefined' ? {variable_name} : null;"
            )
            return value
        except Exception as e:
            logger.error(f"Error retrieving variable '{variable_name}': {e}")
            return None

    def list_global_variables(self):
        """
        Retrieves a list of global variables defined in the browser's context.
        :return: A list of global variable names.
        """
        try:
            script = "return Object.keys(window);"
            variables = self.driver.execute_script(script)
            return variables
        except Exception as e:
            logger.error(f"Error listing global variables: {e}")
            return []

    def execute_custom_script(self, script):
        """
        Executes a custom JavaScript script in the browser context.

        :param script: A string containing the JavaScript code to be executed.
        :return: The result of the executed script, or None if an error occurs.
        """
        try:
            response = self.driver.execute_script(script)
            return response
        except Exception as e:

            logger.error(f"Error executing custom script: {e}")
            return None
