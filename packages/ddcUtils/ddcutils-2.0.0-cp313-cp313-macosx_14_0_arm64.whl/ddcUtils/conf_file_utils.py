import configparser
import errno
import os
import sys


class ConfFileUtils:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def _get_default_parser() -> configparser.ConfigParser:
        """
        Returns the parser
        :return configparser.ConfigParser:
        """

        parser = configparser.ConfigParser(delimiters="=", allow_no_value=True)
        parser.optionxform = str  # this will not change all values to lowercase
        parser._interpolation = configparser.ExtendedInterpolation()
        return parser

    @staticmethod
    def _get_parser_value(
        parser: configparser.ConfigParser,
        section: str,
        config_name: str,
    ) -> str | int | list | None:
        """
        Returns the value of the specified section in the given parser
        :param parser:
        :param section:
        :param config_name:
        :return: str | int | None
        """

        try:
            value = parser.get(section, config_name).replace('"', "")
            if "," in value:
                # Handle comma-separated values
                value = [int(item.strip()) if item.strip().isnumeric() else item.strip() for item in value.split(",")]
            elif value.isnumeric():
                value = int(value)
            elif not value:
                value = None
        except (configparser.Error, ValueError, AttributeError) as e:
            sys.stderr.write(repr(e))
            value = None
        return value

    def _get_section_data(
        self,
        parser: configparser.ConfigParser,
        section: str,
        final_data: dict,
        mixed_values: bool = True,
        include_section_name: bool = False,
    ) -> dict:
        """
        Returns the section data from the given parser
        :param parser:
        :param section:
        :param final_data:
        :param mixed_values:
        :param include_section_name:
        :return: dict
        """

        for name in parser.options(section):
            section_name = section.replace(" ", "_")
            config_name = name.replace(" ", "_")
            value = self._get_parser_value(parser, section, name)
            if mixed_values and include_section_name:
                final_data[f"{section_name}.{config_name}"] = value
            elif mixed_values and not include_section_name:
                final_data[config_name] = value
            else:
                final_data[section_name][config_name] = value
        return final_data

    def get_all_values(self, file_path: str, mixed_values: bool = False) -> dict:
        """
        Get all values from an .ini config file structure and returns them as a dictionary
        :param file_path:
        :param mixed_values:
        :return: dict
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        final_data = {}
        parser = self._get_default_parser()
        try:
            parser.read(file_path)
            for section in parser.sections():
                if not mixed_values:
                    section_name = section.replace(" ", "_")
                    final_data[section_name] = {}
                final_data = self._get_section_data(parser, section, final_data, mixed_values, True)
        except (configparser.Error, OSError, UnicodeDecodeError) as e:
            sys.stderr.write(repr(e))
        return final_data

    def get_section_values(self, file_path: str, section: str) -> dict:
        """
        Get all section values from an .ini config file structure and returns them as a dictionary
        :param file_path:
        :param section:
        :return: dict
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        final_data = {}
        parser = self._get_default_parser()
        try:
            parser.read(file_path)
            final_data = self._get_section_data(parser, section, final_data)
        except (configparser.Error, OSError, UnicodeDecodeError) as e:
            sys.stderr.write(repr(e))
        return final_data

    def get_value(self, file_path: str, section: str, config_name: str) -> str | int | None:
        """
        Get value from an .ini config file structure and returns it
        :param file_path:
        :param section:
        :param config_name:
        :return: str | int | None
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        parser = self._get_default_parser()
        parser.read(file_path)
        value = self._get_parser_value(parser, section, config_name)
        return value

    def set_value(self, file_path: str, section_name: str, config_name: str, new_value, commas: bool = False) -> bool:
        """
        Set value from an .ini config file structure and returns True or False
        :param file_path:
        :param section_name:
        :param config_name:
        :param new_value:
        :param commas:
        :return: True or False
        """

        if not os.path.isfile(file_path):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), file_path)
        parser = self._get_default_parser()
        parser.read(file_path)
        if commas:
            new_value = f'"{new_value}"'
        parser.set(section_name, config_name, new_value)
        try:
            with open(file_path, "w") as configfile:
                parser.write(configfile, space_around_delimiters=False)
        except configparser.DuplicateOptionError as e:
            sys.stderr.write(repr(e))
            return False
        return True
