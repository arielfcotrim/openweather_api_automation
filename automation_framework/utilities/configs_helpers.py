import configparser
from configparser import NoSectionError, NoOptionError
from automation_framework.utilities.path_manager import PathManager as Path


class ConfigsHelper:
    def __init__(self, directory_name, file_name):
        # Read the config file
        self.config = configparser.RawConfigParser()
        self.config.read(Path.get_relative_path(directory_name, file_name))

    def get_configs(self, section, option):
        try:
            # Get the value from the config file
            config_value = self.config.get(section, option)
            return config_value
        except NoSectionError:
            print(f"Section {section} does not exist in the config file")
        except NoOptionError:
            print(f"Option {option} does not exist in the section {section}")
