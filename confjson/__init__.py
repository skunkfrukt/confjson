"""confjson
A bafflingly simple, JSON-backend configuration manager for python programs.
"""

import copy
import json
import pathlib

VERSION = "1.2.1"

DEFAULT_CONFIG_FILENAME = "default.config.json"
USER_CONFIG_FILENAME = "user.config.json"


class ConfigItemProxy:
    """Proxy object for attribute-style access to config items."""

    def __init__(self, dict_):
        super().__setattr__("_dict", dict_)

    def __eq__(self, other):
        if isinstance(other, dict):
            return self._dict == other
        if isinstance(other, ConfigItemProxy):
            return self._dict == other.get_dict()
        return False

    def __getattr__(self, key):
        value = self._dict[key]
        if isinstance(value, dict):
            return ConfigItemProxy(value)
        return value

    def __getitem__(self, key):
        value = self._dict[key]
        if isinstance(value, dict):
            return ConfigItemProxy(value)
        return value

    def __setattr__(self, key, value):
        json.dumps({key: value})
        self._dict[key] = value

    def __setitem__(self, key, value):
        json.dumps({key: value})
        self._dict[key] = value

    def get_dict(self):
        """Return the backing dict."""
        return self._dict


class Config:
    """A manager for JSON-backed default and user-specified config settings."""

    def __init__(
        self,
        path,
        *,
        user_config_filename=USER_CONFIG_FILENAME,
        default_config_filename=DEFAULT_CONFIG_FILENAME,
    ):
        pathlib_path = pathlib.Path(path)

        if pathlib_path.is_dir():
            super().__setattr__("directory", pathlib_path)
        elif not pathlib_path.exists():
            raise ValueError(
                "Parameter `path` must be the path of an existing file"
                f" or directory; '{path}' does not exist."
            )
        else:
            super().__setattr__("directory", pathlib_path.parent)

        super().__setattr__(
            "default_config_path", self.directory / default_config_filename
        )
        super().__setattr__("user_config_path", self.directory / user_config_filename)
        super().__setattr__("_default_dict", {})
        super().__setattr__("_user_dict", {})
        super().__setattr__("_original_attrs", dir(self))
        self.load()

    def __contains__(self, key):
        return key in self._user_dict or key in self._default_dict

    def __delitem__(self, key):
        del self._user_dict[key]

    def __getattr__(self, key):
        return self[key]

    def __getitem__(self, key):
        if key not in self._user_dict:
            self._user_dict[key] = copy.deepcopy(self._default_dict[key])
        value = self._user_dict[key]
        if isinstance(value, dict):
            return ConfigItemProxy(value)
        return value

    def __len__(self):
        return len(self.keys())

    def __setattr__(self, key, value):
        if key in self._original_attrs:
            raise KeyError(
                "Cannot use attribute-style access to set config item '{key}';"
                " attribute name is reserved."
            )
        self[key] = value

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
                super().__setattr__("_default_dict", json.load(file))
        except FileNotFoundError:
            super().__setattr__("_default_dict", {})

        try:
            with self.user_config_path.open() as file:
                super().__setattr__(
                    "_user_dict", _get_dict_union(json.load(file), self._default_dict)
                )
        except FileNotFoundError:
            super().__setattr__("_user_dict", {})

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
