from configparser import ConfigParser


def read_configuration(category, key, fallback=None):
    config = ConfigParser()
    config.read("configurations/config.ini")
    if fallback:
        return config.get(category, key, fallback=fallback)
    return config.get(category, key)
