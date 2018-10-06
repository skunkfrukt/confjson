import collections
import json
import pathlib


class Config:
    def __init__(self, path):
        self.dir = pathlib.Path(path)
        if not self.dir.is_dir():
            self.dir = self.dir.parent
        self.default_config_path = self.dir / "default.config.json"
        self.user_config_path = self.dir / "user.config.json"

        self.load()

    def __getitem__(self, key):
        return self._chainmap[key]

    def __setitem__(self, key, value):
        self._chainmap[key] = value

    def load(self):
        if self.default_config_path.exists():
            with self.default_config_path.open() as file:
                default_config = json.load(file)
        else:
            default_config = {}

        if self.user_config_path.exists():
            with self.user_config_path.open() as file:
                user_config = json.load(file)
        else:
            user_config = {}

        self._chainmap = collections.ChainMap(user_config, default_config)

    def save(self):
        with self.user_config_path.open(mode="w") as file:
            json.dump(self._chainmap.maps[0], file)
