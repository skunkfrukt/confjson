# confjson

## What is it?
A bafflingly simple, JSON-backed configuration manager for Python programs.

## Why is it?
I kept implementing roughly the same thing from scratch in my various projects, so I figured it was time to do it properly.

## User guide
The `confjson.Config` class is similar to a ChainMap, and works by means of two JSON files in the same directory:
* `default.config.json`
  - The default config file is read-only as far as confjson is concerned. To add default settings, manually edit the file.
  - If the file does not exist, there are no defaults.
  - This file will typically be version controlled along with the code.
* `user.config.json`
  - Any changes made to the config (and saved) at runtime end up in this file.
  - If the file does not exist, it will be created when changes are saved.
  - User settings take priority over default settings.
  - This file should probably be added to .gitignore or such.

### Initialization
```python
config = confjson.Config(MY_DIR)

# If the supplied path refers to a file, confjson will look for config
# files in the containing directory.
# This is mainly to enable the following pattern, using __file__.
configer = confjson.Config(__file__)
```

### Data access
```python
# Items in the confjson config are accessed as in a dict.
if "username" in configest["user"]:
	do_something(configest["user"]["username"])
	configest["user"]["something_count"] += 1
```

### Persistence
```python
# The load() method (re-)loads the Config object with values from the
# backing JSON files. Loading is also performed on initialization.
config.load()

# The save() method saves any changed or added items **to user.config.json only**.
config.save()
```

### collections.ChainMap comparison
```python
import collections
import confjson

chain_map = collections.ChainMap({}, {"list_in_second_dict": [1, 2, 3]})
print(chain_map.maps[1])  # -> {'list_in_second_dict': [1, 2, 3]}
print(chain_map.maps[0])  # -> {}
chain_map["list_in_second_dict"].append(4)
print(chain_map.maps[1])  # -> {'list_in_second_dict': [1, 2, 3, 4]}
print(chain_map.maps[0])  # -> {}

conf = confjson.Config(__file__)  # Assuming that our default.config.json contains {"list_in_default_config": [1, 2, 3]}
print(conf._default_dict)  # -> {'list_in_default_config': [1, 2, 3]}
print(conf._user_dict)  # -> {}
conf["list_in_default_config"].append(4)
print(conf._default_dict)  # -> {'list_in_default_config': [1, 2, 3]}
print(conf._user_dict)  # -> {'list_in_default_config': [1, 2, 3, 4]}
