import json
import os.path

import confjson

DEFAULT_CONFIG_FILENAME = "default.config.json"

USER_CONFIG_FILENAME = "user.config.json"

DEFAULT_CONFIG = {
    "key_unique_to_default": "value_unique_to_default",
    "key_in_both_configs": "default_value",
    "list": [
        "default list[0]",
        "default list[1]"
    ],
    "dict": {
        "key1": "default dict[key1]",
        "key2": "default dict[key2]"
    }
}

USER_CONFIG = {
    "key_unique_to_user": "value_unique_to_user",
    "key_in_both_configs": "user_value",
    "list": [
        "user list[0]",
        "user list[1]"
    ],
    "dict": {
        "key1": "user dict[key1]",
        "key2": "user dict[key2]"
    }
}


def _generate_default_config(folder):
    with open(os.path.join(folder, DEFAULT_CONFIG_FILENAME), "w") as file:
        json.dump(DEFAULT_CONFIG, file)


def _generate_user_config(folder):
    with open(os.path.join(folder, USER_CONFIG_FILENAME), "w") as file:
        json.dump(USER_CONFIG, file)


def test_containing_directory_is_used_if_path_argument_is_a_file(tmpdir):
    filename = os.path.join(tmpdir, "file.py")
    with open(filename, "w") as file:
        file.write("\\[T]/")
    conf = confjson.Config(filename)
    assert str(conf.dir) == tmpdir


def test_path_is_used_as_is_if_it_is_a_directory(tmpdir):
    conf = confjson.Config(tmpdir)
    assert str(conf.dir) == tmpdir


def test_user_config_is_created_if_missing(tmpdir):
    conf = confjson.Config(tmpdir)
    conf["a"] = "b"
    conf.save()
    with open(os.path.join(tmpdir, USER_CONFIG_FILENAME)) as file:
        user_json = json.load(file)
    assert user_json["a"] == conf["a"]


def test_user_config_is_loaded_if_extant(tmpdir):
    _generate_user_config(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["key_unique_to_user"] == "value_unique_to_user"


def test_default_config_is_loaded_if_extant(tmpdir):
    _generate_default_config(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["key_unique_to_default"] == "value_unique_to_default"


def test_user_config_takes_priority_on_overlap(tmpdir):
    _generate_default_config(tmpdir)
    _generate_user_config(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["key_in_both_configs"] == "user_value"


def test_changes_are_saved_only_to_user_config(tmpdir):
    _generate_default_config(tmpdir)
    _generate_user_config(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["new_key"] = "new_value"
    conf.save()

    with open(os.path.join(tmpdir, USER_CONFIG_FILENAME)) as file:
        user_json = json.load(file)
    assert user_json["new_key"] == "new_value"

    with open(os.path.join(tmpdir, DEFAULT_CONFIG_FILENAME)) as file:
        default_json = json.load(file)
    assert "new_key" not in default_json
