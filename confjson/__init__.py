"""confjson
A bafflingly simple, JSON-backend configuration manager for python programs.
"""

import copy
import json
import pathlib

DEFAULT_CONFIG_FILENAME = "default.config.json"
USER_CONFIG_FILENAME = "user.config.json"


class Config:
    """A manager for JSON-backed default and user-specified config settings."""

    def __init__(self, path):
        pathlib_path = pathlib.Path(path)

        if pathlib_path.is_dir():
            self.directory = pathlib_path
        elif pathlib_path.is_file():
            self.directory = pathlib_path.parent
        elif not pathlib_path.exists():
            raise ValueError(
                "Parameter `path` must be the path of an existing file"
                f" or directory; '{path}' does not exist."
            )
        else:
            raise ValueError(
                "Parameter `path` must be the path of an existing file"
                f" or directory; '{path}' exists but is not a file or"
                " a directory."
            )

        self.default_config_path = self.directory / DEFAULT_CONFIG_FILENAME
        self.user_config_path = self.directory / USER_CONFIG_FILENAME

        self._default_dict = {}
        self._user_dict = {}
        self.load()

    def __contains__(self, key):
        return key in self._user_dict or key in self._default_dict

    def __delitem__(self, key):
        del self._user_dict[key]

    def __getitem__(self, key):
        if key not in self._user_dict:
            self._user_dict[key] = copy.deepcopy(self._default_dict[key])
        return self._user_dict[key]

    def __len__(self):
        return len(set(self._user_dict).union(set(self._default_dict)))

    def __setitem__(self, key, value):
        # Will fail for values unsupported by JSON.
        json.dumps({key: value})
        self._user_dict[key] = value

    def default_keys(self):
        """Get only the keys present in the default config."""
        return self._default_dict.keys()

    def get(self, key, default=None):
        """Get the value of the given key from the user config, the
        default config or the optional `default` argument, in order of
        preference.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def get_default(self, key):
        """Get the default value of the given setting, even if there is
        a user setting.
        """
        return self._default_dict[key]

    def keys(self):
        """Get the keys present in the config."""
        return list(set(self._user_dict.keys()).union(self._default_dict.keys()))

    def load(self):
        """Load or reload config settings from the backing JSON files.
        Note that this will reset any unsaved user config settings.
        """
        try:
            with self.default_config_path.open() as file:
                self._default_dict = json.load(file)
        except FileNotFoundError:
            self._default_dict = {}

        try:
            with self.user_config_path.open() as file:
                self._user_dict = _get_dict_union(json.load(file), self._default_dict)
        except FileNotFoundError:
            self._user_dict = {}

    def save(self):
        """Save any user config settings that differ from their
        respective default values.
        """
        diff = _get_dict_diff(self._user_dict, self._default_dict)
        if diff:
            with self.user_config_path.open(mode="w") as file:
                json.dump(diff, file, indent=4, sort_keys=True)
        elif self.user_config_path.exists():
            self.user_config_path.unlink()


def _get_dict_diff(top_dict, bottom_dict):
    result_dict = {}
    for key, top_value in top_dict.items():
        if key in bottom_dict:
            bottom_value = bottom_dict[key]
            if top_value != bottom_value:
                if isinstance(top_value, dict) and isinstance(bottom_value, dict):
                    result_dict[key] = _get_dict_diff(top_value, bottom_value)
                else:
                    result_dict[key] = top_value
        else:
            result_dict[key] = top_value
    return result_dict


def _get_dict_union(top_dict, bottom_dict):
    result_dict = {}
    for key in set(top_dict.keys()).union(bottom_dict.keys()):
        if key in top_dict:
            top_value = top_dict[key]
            if (
                isinstance(top_value, dict)
                and key in bottom_dict
                and isinstance(bottom_dict[key], dict)
            ):
                result_dict[key] = _get_dict_union(top_value, bottom_dict[key])
            else:
                result_dict[key] = copy.deepcopy(top_value)
        else:
            result_dict[key] = copy.deepcopy(bottom_dict[key])
    return result_dict
