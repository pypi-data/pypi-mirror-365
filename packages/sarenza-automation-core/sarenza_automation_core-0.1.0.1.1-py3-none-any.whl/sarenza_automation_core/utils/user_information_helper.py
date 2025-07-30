import json
import os
from datetime import datetime
from threading import current_thread, Lock


class UserInformationHelper:
    def __init__(self, target_folder="user_info"):
        self.target_folder = target_folder
        os.makedirs(self.target_folder, exist_ok=True)
        self.lock = Lock()

    def _get_filename(self):
        """
        Returns a formatted filename based on the current date and the name of the current thread.

        :return: A string representing the formatted filename.
        :rtype: str
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        thread_name = current_thread().name
        return f"{self.target_folder}/{current_date}_{thread_name}.json"

    def _delete_old_files(self):
        """
        Deletes files in the target folder that are older than the current date.

        This function iterates over all the files in the target folder and checks if the file date is different from the current date. If the file date is different, the file is deleted using the `os.remove()` function.

        Parameters:
            self (UserInformationHelper): The instance of the UserInformationHelper class.

        Returns:
            None
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        for filename in os.listdir(self.target_folder):
            file_date = filename.split("_")[0]
            if file_date != current_date:
                os.remove(os.path.join(self.target_folder, filename))

    def save_user_info(self, user_info):
        """
        Saves the user information to a JSON file.

        Args:
            user_info (dict): A dictionary containing the user information to be saved.

        Returns:
            None
        """
        with self.lock:
            self._delete_old_files()
            filename = self._get_filename()
            existing_data = {}

            if os.path.exists(filename):
                with open(filename, "r") as file:
                    existing_data = json.load(file)

            existing_data.update(user_info)

            with open(filename, "w") as file:
                json.dump(existing_data, file)

    def fetch_user_info(self):
        """
        Retrieves user information from a JSON file.

        Parameters:
            self: The instance of the UserInformationHelper class.

        Returns:
            dict: A dictionary containing the user information retrieved from the file, or None if the file does not exist.
        """
        filename = self._get_filename()
        if os.path.exists(filename):
            with open(filename, "r") as file:
                return json.load(file)
        else:
            return None
