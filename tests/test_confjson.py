import json
import os.path

import pytest

import confjson

DEFAULT_CONFIG_FILENAME = "default.config.json"

USER_CONFIG_FILENAME = "user.config.json"

DEFAULT_CONFIG = {
    "string_in_both": "d[string_in_both]",
    "string_in_default": "d[string_in_default]",
    "list_in_both": ["d[list_in_both][0]", "d[list_in_both][1]"],
    "list_in_default": ["d[list_in_default][0]", "d[list_in_default][1]"],
    "dict_in_both": {
        "key_in_both": "d[dict_in_both][key_in_both]",
        "key_in_default": "d[dict_in_both][key_in_default]"
    },
    "dict_in_default": {
        "key_d1": "d[dict_in_default][key_d1]",
        "key_d2": "d[dict_in_default][key_d2]"
    }
}

USER_CONFIG = {
    "string_in_both": "u[string_in_both]",
    "string_in_user": "u[string_in_user]",
    "list_in_both": ["u[list_in_both][0]", "u[list_in_both][0]"],
    "list_in_user": ["u[list_in_user][0]", "u[list_in_user][1]"],
    "dict_in_both": {
        "key_in_both": "u[dict_in_both][key_in_both]",
        "key_in_user": "u[dict_in_both][key_in_user]"
    },
    "dict_in_user": {
        "key_u1": "u[dict_in_user][key_u1]",
        "key_u2": "u[dict_in_user][key_u2]"
    }
}

XFAIL_CLEANUP_NOT_IMPLEMENTED = pytest.mark.xfail(
    reason="Cleanup of user config file not yet implemented.", strict=True)


def _generate_default_config(folder):
    with open(os.path.join(folder, DEFAULT_CONFIG_FILENAME), "w") as file:
        json.dump(DEFAULT_CONFIG, file)


def _generate_user_config(folder):
    with open(os.path.join(folder, USER_CONFIG_FILENAME), "w") as file:
        json.dump(USER_CONFIG, file)


def _generate_both_config_files(folder):
    _generate_default_config(folder)
    _generate_user_config(folder)


def test_init_with_file_path(tmpdir):
    filename = os.path.join(tmpdir, "file.py")
    with open(filename, "w") as file:
        file.write("\\[T]/")
    conf = confjson.Config(filename)
    assert str(conf.directory) == tmpdir


def test_init_with_directory_path(tmpdir):
    conf = confjson.Config(tmpdir)
    assert str(conf.directory) == tmpdir


def test_init_with_nonexistant_file_path(tmpdir):
    with pytest.raises(ValueError):
        conf = confjson.Config(os.path.join(tmpdir, "does_not_exist.wtf"))


def test_create_user_config_file_if_missing(tmpdir):
    conf = confjson.Config(tmpdir)
    conf["a"] = "b"
    conf.save()
    with open(os.path.join(tmpdir, USER_CONFIG_FILENAME)) as file:
        user_json = json.load(file)
    assert user_json["a"] == conf["a"]


def test_load_user_config_file_if_it_exists(tmpdir):
    _generate_user_config(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["string_in_user"] == USER_CONFIG["string_in_user"]


def test_load_default_config_if_it_exists(tmpdir):
    _generate_default_config(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["string_in_default"] == DEFAULT_CONFIG["string_in_default"]


def test_use_value_from_user_config_if_key_is_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["string_in_both"] == USER_CONFIG["string_in_both"]


def test_save_changes_only_to_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["new_key"] = "new_value"
    conf.save()

    with open(os.path.join(tmpdir, USER_CONFIG_FILENAME)) as file:
        user_json = json.load(file)
    assert user_json["new_key"] == "new_value"

    with open(os.path.join(tmpdir, DEFAULT_CONFIG_FILENAME)) as file:
        default_json = json.load(file)
    assert "new_key" not in default_json


def test_get_item_from_list_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["list_in_both"][0] == USER_CONFIG["list_in_both"][0]


def test_get_item_from_list_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["list_in_default"][0] == DEFAULT_CONFIG["list_in_default"][0]


def test_get_item_from_list_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["list_in_user"][0] == USER_CONFIG["list_in_user"][0]


def test_add_item_to_list_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["list_in_both"].append("new_item")
    assert (
        conf._user_dict["list_in_both"]
        == USER_CONFIG["list_in_both"] + ["new_item"])
    assert (
        conf._default_dict["list_in_both"] == DEFAULT_CONFIG["list_in_both"])


def test_add_item_to_list_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["list_in_user"].append("new_item")
    assert (
        conf._user_dict["list_in_user"]
        == USER_CONFIG["list_in_user"] + ["new_item"])
    assert "list_in_user" not in conf._default_dict


def test_add_item_to_list_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["list_in_default"].append("new_item")
    assert (
        conf._user_dict["list_in_default"]
        == DEFAULT_CONFIG["list_in_default"] + ["new_item"])
    assert (
        conf._default_dict["list_in_default"]
        == DEFAULT_CONFIG["list_in_default"])


def test_get_item_from_dict_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_both"]["key_in_both"]
        == USER_CONFIG["dict_in_both"]["key_in_both"])


def test_get_item_from_dict_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_default"]["key_d1"]
        == DEFAULT_CONFIG["dict_in_default"]["key_d1"])


def test_get_item_from_dict_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_user"]["key_u1"]
        == USER_CONFIG["dict_in_user"]["key_u1"])


def test_add_item_to_dict_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_both"]["new_key"] = "new_value"
    assert conf._user_dict["dict_in_both"]["new_key"] == "new_value"
    assert "new_key" not in conf._default_dict["dict_in_both"]


def test_add_item_to_dict_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_user"]["new_key"] = "new_value"
    assert conf._user_dict["dict_in_user"]["new_key"] == "new_value"
    assert "dict_in_user" not in conf._default_dict


def test_add_item_to_dict_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_default"]["new_key"] = "new_value"
    assert conf._user_dict["dict_in_default"]["new_key"] == "new_value"
    assert (
        conf._default_dict["dict_in_default"]
        == DEFAULT_CONFIG["dict_in_default"])


def test_create_no_user_config_file_if_default_values_unchanged(tmpdir):
    _generate_default_config(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["string_in_default"] = DEFAULT_CONFIG["string_in_default"]
    conf.save()
    assert not conf.user_config_path.exists()


def test_remove_items_from_user_config_if_identical_to_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["string_in_both"] == USER_CONFIG["string_in_both"]
    conf["string_in_both"] = DEFAULT_CONFIG["string_in_both"]
    conf.save()
    with conf.user_config_path.open() as file:
        json_from_user_config_file = json.load(file)
    assert "string_in_both" not in json_from_user_config_file


def test_delete_user_config_file_on_save_if_identical_to_default(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf._user_dict = json.loads(json.dumps(conf._default_dict))
    assert conf.user_config_path.exists()
    conf.save()
    assert not conf.user_config_path.exists()
