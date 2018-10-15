"""confjson
A bafflingly simple, JSON-backend configuration manager for python programs.
"""

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
                f" or directory; '{path}' does not exist.")
        else:
            raise ValueError(
                "Parameter `path` must be the path of an existing file"
                f" or directory; '{path}' exists but is not a file or"
                " a directory.")

        self.default_config_path = self.directory / DEFAULT_CONFIG_FILENAME
        self.user_config_path = self.directory / USER_CONFIG_FILENAME

        self._default_dict = {}
        self._user_dict = {}
        self.load()

    def __contains__(self, key):
        return key in self._user_dict or key in self._default_dict

    def __getitem__(self, key):
        if key not in self._user_dict:
            default_value = self._default_dict[key]
            self._user_dict[key] = json.loads(json.dumps(default_value))
        return self._user_dict[key]

    def __setitem__(self, key, value):
        self._user_dict[key] = value

    def get(self, key, default=None):
        """Get the value of the given key from the user config, the
        default config or the optional `default` argument, in order of
        preference.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __len__(self):
        return len(set(self._user_dict).union(set(self._default_dict)))

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
                self._user_dict = json.load(file)
        except FileNotFoundError:
            self._user_dict = {}

    def save(self):
        """Save any user config settings that differ from their
        respective default values.
        """
        diff = {
            key: value
            for key, value in self._user_dict.items() if
            key not in self._default_dict or value != self._default_dict[key]
        }
        if diff:
            with self.user_config_path.open(mode="w") as file:
                json.dump(diff, file, indent=4, sort_keys=True)
        elif self.user_config_path.exists():
            self.user_config_path.unlink()
