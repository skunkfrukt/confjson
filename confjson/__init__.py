import json
import pathlib


DEFAULT_CONFIG_FILENAME = "default.config.json"
USER_CONFIG_FILENAME = "user.config.json"


class Config:
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

    def __getitem__(self, key):
        if key not in self._user_dict:
            default_value = self._default_dict[key]
            self._user_dict[key] = json.loads(json.dumps(default_value))
        return self._user_dict[key]

    def __setitem__(self, key, value):
        self._user_dict[key] = value

    def load(self):
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
        diff = {
            key: value for key, value in self._user_dict.items()
            if key not in self._default_dict
            or value != self._default_dict[key]
        }
        if diff or self.user_config_path.exists():
            with self.user_config_path.open(mode="w") as file:
                json.dump(diff, file)
