import json
import os


def _load_translations():
    """
    Load translations from a JSON file.
    Returns:
        dict: Dictionary containing the translation data.
    """
    file_path = os.getenv("FILE_PATH", "languages/languages.json")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_translation(lang, key):
    """
    Get a translation for a specific language and key.

    Parameters:
        translations (dict): Dictionary containing translation data.
        lang (str): Language code (e.g., 'es', 'fr').
        key (str): The translation key to look up.

    Returns:
        str: The translation for the given key and language, or a message if not found.
    """
    try:
        return _load_translations()[lang][key]
    except KeyError:
        return f"Translation for '{key}' in '{lang}' not found."


def get_translated_value(key: str) -> str:
    """
    Retrieves a translated value for a given key, using the default language set in the config file.

    Parameters:
        key (str): The translation key to look up.

    Returns:
        str: The translated value for the given key, or a message if not found.
    """
    try:
        default_language = os.getenv("LANGUAGE")
        return get_translation(default_language, key)
    except KeyError:
        return f"Translation for '{key}' in '{default_language}' not found."
