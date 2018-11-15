# pylint: disable=missing-docstring
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
        "key_in_default": "d[dict_in_both][key_in_default]",
        "nested_dict_in_both": {
            "key_in_both": "d[dict_in_both][nested_dict_in_both][key_in_both]",
            "key_in_default": "d[dict_in_both][nested_dict_in_both][key_in_default]",
        },
    },
    "dict_in_default": {
        "key_d1": "d[dict_in_default][key_d1]",
        "key_d2": "d[dict_in_default][key_d2]",
        "originally_empty_dict": {},
    },
}

USER_CONFIG = {
    "string_in_both": "u[string_in_both]",
    "string_in_user": "u[string_in_user]",
    "list_in_both": ["u[list_in_both][0]", "u[list_in_both][0]"],
    "list_in_user": ["u[list_in_user][0]", "u[list_in_user][1]"],
    "dict_in_both": {
        "key_in_both": "u[dict_in_both][key_in_both]",
        "key_in_user": "u[dict_in_both][key_in_user]",
        "nested_dict_in_both": {
            "key_in_both": "u[dict_in_both][nested_dict_in_both][key_in_both]",
            "key_in_user": "u[dict_in_both][nested_dict_in_both][key_in_user]",
        },
    },
    "dict_in_user": {
        "key_u1": "u[dict_in_user][key_u1]",
        "key_u2": "u[dict_in_user][key_u2]",
    },
}


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
        _ = confjson.Config(os.path.join(tmpdir, "does_not_exist.wtf"))


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
    assert conf["list_in_both"] == USER_CONFIG["list_in_both"] + ["new_item"]
    assert conf.get_default("list_in_both") == DEFAULT_CONFIG["list_in_both"]


def test_add_item_to_list_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["list_in_user"].append("new_item")
    assert conf["list_in_user"] == USER_CONFIG["list_in_user"] + ["new_item"]
    with pytest.raises(KeyError):
        conf.get_default("list_in_user")


def test_add_item_to_list_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["list_in_default"].append("new_item")
    assert conf["list_in_default"] == DEFAULT_CONFIG["list_in_default"] + ["new_item"]
    assert conf.get_default("list_in_default") == DEFAULT_CONFIG["list_in_default"]


def test_get_item_from_dict_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_both"]["key_in_both"]
        == USER_CONFIG["dict_in_both"]["key_in_both"]
    )


def test_get_item_from_dict_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_default"]["key_d1"] == DEFAULT_CONFIG["dict_in_default"]["key_d1"]
    )


def test_get_item_from_dict_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf["dict_in_user"]["key_u1"] == USER_CONFIG["dict_in_user"]["key_u1"]


def test_add_item_to_dict_present_in_both_configs(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_both"]["new_key"] = "new_value"
    assert conf["dict_in_both"]["new_key"] == "new_value"
    assert "new_key" not in conf.get_default("dict_in_both")


def test_add_item_to_dict_present_only_in_user_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_user"]["new_key"] = "new_value"
    assert conf["dict_in_user"]["new_key"] == "new_value"
    with pytest.raises(KeyError):
        conf.get_default("dict_in_user")


def test_add_item_to_dict_present_only_in_default_config(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_default"]["new_key"] = "new_value"
    assert conf["dict_in_default"]["new_key"] == "new_value"
    assert conf.get_default("dict_in_default") == DEFAULT_CONFIG["dict_in_default"]


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
    # This is callable. Shut up.
    # pylint: disable=not-callable
    all_keys = conf.keys()
    # pylint: enable=not-callable
    default_keys = conf.default_keys()
    for key in all_keys:
        if key in default_keys:
            conf[key] = conf.get_default(key)
        else:
            del conf[key]
    assert conf.user_config_path.exists()
    conf.save()
    assert not conf.user_config_path.exists()


def test_access_user_item_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.string_in_user == conf["string_in_user"]


def test_access_user_item_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.string_in_both == conf["string_in_both"]


def test_access_default_item_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.string_in_default == conf["string_in_default"]


def test_access_user_list_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.list_in_user[0] == conf["list_in_user"][0]


def test_access_user_list_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.list_in_both[0] == conf["list_in_both"][0]


def test_access_default_list_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.list_in_default[0] == conf["list_in_default"][0]


def test_access_user_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_user.key_u1 == conf["dict_in_user"]["key_u1"]


def test_access_user_dict_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_both.key_in_both == conf["dict_in_both"]["key_in_both"]


def test_access_default_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_default.key_d1 == conf["dict_in_default"]["key_d1"]


def test_access_default_nested_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf.dict_in_both.nested_dict_in_both.key_in_default
        == conf["dict_in_both"]["nested_dict_in_both"]["key_in_default"]
    )


def test_set_user_item_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.string_in_user = "new_value"
    assert conf["string_in_user"] == "new_value"


def test_set_user_item_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.string_in_both = "new_value"
    assert conf["string_in_both"] == "new_value"


def test_set_default_item_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.string_in_default = "new_value"
    assert conf["string_in_default"] == "new_value"


def test_set_user_list_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.list_in_user[0] = "new_value_0"
    conf.list_in_user.append("new_value_-1")
    assert conf["list_in_user"][0] == "new_value_0"
    assert conf["list_in_user"][-1] == "new_value_-1"


def test_set_user_list_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.list_in_both[0] = "new_value_0"
    conf.list_in_both.append("new_value_-1")
    assert conf["list_in_both"][0] == "new_value_0"
    assert conf["list_in_both"][-1] == "new_value_-1"


def test_set_default_list_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.list_in_default[0] = "new_value_0"
    conf.list_in_default.append("new_value_-1")
    assert conf["list_in_default"][0] == "new_value_0"
    assert conf["list_in_default"][-1] == "new_value_-1"


def test_set_user_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.dict_in_user.key_u1 = "new_value"
    assert conf["dict_in_user"]["key_u1"] == "new_value"


def test_set_user_dict_overriding_default_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.dict_in_both.key_in_both = "new_value"
    assert conf["dict_in_both"]["key_in_both"] == "new_value"


def test_set_default_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.dict_in_default.key_d1 = "new_value"
    assert conf["dict_in_default"]["key_d1"] == "new_value"


def test_set_default_nested_dict_as_attribute(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf.dict_in_both.nested_dict_in_both.key_in_default = "new_value"
    assert conf["dict_in_both"]["nested_dict_in_both"]["key_in_default"] == "new_value"


def test_save_only_changed_items_in_nested_dicts(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    conf["dict_in_default"]["originally_empty_dict"]["key_added_to_user"] = "krafs"
    conf.save()
    with conf.user_config_path.open() as file:
        user_json = json.load(file)
    assert "dict_in_default" in user_json
    assert len(user_json["dict_in_default"]["originally_empty_dict"]) == 1
    assert (
        user_json["dict_in_default"]["originally_empty_dict"]["key_added_to_user"]
        == "krafs"
    )


def test_access_nested_dicts_missing_in_user_but_present_in_default(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_both"]["key_in_default"]
        == DEFAULT_CONFIG["dict_in_both"]["key_in_default"]
    )


@pytest.mark.parametrize(
    "value",
    [
        pytest.param({"a": 1, "b": 2, "c": 3}, id="dict"),
        pytest.param({"a": 1, "b": {"c": 2, "d": 3}}, id="nested dict"),
        pytest.param([1, 2, 3, 4], id="list"),
        pytest.param([1, [2, [3, [4]]]], id="nested list"),
        pytest.param((6, 7, 8, 9), id="tuple"),
        pytest.param((6, (7, (8, 9))), id="nested tuple"),
        pytest.param("krafs", id="str"),
        pytest.param(42, id="int"),
        pytest.param(3.1415926536, id="float"),
        pytest.param(True, id="True"),
        pytest.param(False, id="False"),
        pytest.param(None, id="None"),
    ],
)
def test_allow_json_compatible_values(tmpdir, value):
    conf = confjson.Config(tmpdir)
    conf["thing"] = value
    assert conf["thing"] == value


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(confjson.Config, id="class"),
        pytest.param(object(), id="object"),
        pytest.param(set(), id="set"),
        pytest.param([set()], id="set inside list"),
        pytest.param({object(): "wtf"}, id="object as key"),
        pytest.param({tuple(): "wtf"}, id="tuple as key"),
    ],
)
def test_disallow_json_incompatible_values(tmpdir, value):
    conf = confjson.Config(tmpdir)
    with pytest.raises(TypeError):
        conf["thing"] = value


def test_disallow_overwriting_original_attributes(tmpdir):
    conf = confjson.Config(tmpdir)
    with pytest.raises(KeyError):
        conf.keys = "better_keys"


@pytest.mark.parametrize("key", ["string_in_default", "string_in_user"])
def test_contains(tmpdir, key):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert key in conf


def test_len(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert len(conf) == len(set(USER_CONFIG.keys()).union(DEFAULT_CONFIG.keys()))


@pytest.mark.parametrize("key", ["string_in_default", "string_in_user"])
def test_get_when_key_exists(tmpdir, key):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.get(key) == conf[key]


def test_get_when_key_does_not_exist(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    with pytest.raises(KeyError):
        _ = conf["key-does-not-exist"]
    assert conf.get("key-does-not-exist") is None
    assert conf.get("key-does-not-exist", "no-it-does-not") == "no-it-does-not"


def test_dict_to_attr_mixed_style_access(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf["dict_in_both"].key_in_both == USER_CONFIG["dict_in_both"]["key_in_both"]
    )


def test_attr_to_dict_mixed_style_access(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert (
        conf.dict_in_both["key_in_both"] == USER_CONFIG["dict_in_both"]["key_in_both"]
    )


def test_get_backing_dict(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    backing_dict = conf.dict_in_user.get_dict()
    assert isinstance(backing_dict, dict)
    assert backing_dict == USER_CONFIG["dict_in_user"]


def test_config_item_proxy_equality(tmpdir):
    _generate_both_config_files(tmpdir)
    con = confjson.Config(tmpdir)
    fig = confjson.Config(tmpdir)
    assert con.dict_in_both == fig.dict_in_both


def test_config_item_proxy_inequality_because_mindless_coverage_hunting_is_good(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_both != json.dumps(conf.dict_in_both.get_dict())


@pytest.mark.parametrize("key", ["key_in_user", "key_in_default"])
def test_nested_contains(tmpdir, key):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert key in conf.dict_in_both


@pytest.mark.parametrize("key", ["key_in_user", "key_in_default"])
def test_nested_get_when_exists(tmpdir, key):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_both.get(key) == conf.dict_in_both[key]


def test_nested_get_when_notexists(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert conf.dict_in_both.get("hubris") is None
    assert conf.dict_in_both.get("snorlax", "pikachu") == "pikachu"


def test_nested_keys(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert set(conf.dict_in_both.keys()) == set(
        USER_CONFIG["dict_in_both"].keys()
    ).union(DEFAULT_CONFIG["dict_in_both"].keys())


def test_nested_items(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir)
    assert len(tuple(conf.dict_in_both.items())) == len(
        set(USER_CONFIG["dict_in_both"].keys()).union(
            DEFAULT_CONFIG["dict_in_both"].keys()
        )
    )
    for key, value in conf.dict_in_both.items():
        assert conf["dict_in_both"][key] == value


def test_placeholder_equality(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert conf.does_not_exist != "krafs"


def test_placeholder_getattr(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert not conf.does_not_exist.not_at_all
    assert conf.does_not_exist.is_placeholder


def test_placeholder_getitem(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert not conf["does_not_exist"]["not_at_all"]
    assert conf["does_not_exist"].is_placeholder


def test_getattr_unsuppressed_key_error(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=False)
    with pytest.raises(KeyError):
        _ = conf.dict_in_both.does_not_exist


def test_getattr_suppressed_key_error(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert conf.dict_in_both.does_not_exist.is_placeholder


def test_getitem_unsuppressed_key_error(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=False)
    with pytest.raises(KeyError):
        _ = conf["dict_in_both"]["does_not_exist"]


def test_getitem_suppressed_key_error(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert conf["dict_in_both"]["does_not_exist"].is_placeholder


def test_placeholder_setattr(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert conf.fake_dict.is_placeholder
    assert conf.fake_dict.fake_key.is_placeholder
    assert conf.fake_dict.fake_key.fake_subkey.is_placeholder
    conf.fake_dict.fake_key.fake_subkey = "so fake ._. wow"
    assert not conf.fake_dict.is_placeholder
    assert not conf.fake_dict.fake_key.is_placeholder
    assert conf.fake_dict.fake_key.fake_subkey == "so fake ._. wow"
    conf.save()
    igur = confjson.Config(tmpdir, use_placeholders=False)
    assert not igur.fake_dict.is_placeholder
    assert not igur.fake_dict.fake_key.is_placeholder
    assert igur.fake_dict.fake_key.fake_subkey == "so fake ._. wow"


def test_placeholder_setitem(tmpdir):
    _generate_both_config_files(tmpdir)
    conf = confjson.Config(tmpdir, use_placeholders=True)
    assert conf["fake_dict"].is_placeholder
    assert conf["fake_dict"]["fake_key"].is_placeholder
    assert conf["fake_dict"]["fake_key"]["fake_subkey"].is_placeholder
    conf["fake_dict"]["fake_key"]["fake_subkey"] = "._. much placeholder"
    assert not conf["fake_dict"].is_placeholder
    assert not conf["fake_dict"]["fake_key"].is_placeholder
    assert conf["fake_dict"]["fake_key"]["fake_subkey"] == "._. much placeholder"
    conf.save()
    igur = confjson.Config(tmpdir, use_placeholders=False)
    assert not igur["fake_dict"].is_placeholder
    assert not igur["fake_dict"]["fake_key"].is_placeholder
    assert igur["fake_dict"]["fake_key"]["fake_subkey"] == "._. much placeholder"
