# confjson
[![Build Status](https://travis-ci.org/skunkfrukt/confjson.svg?branch=master)](https://travis-ci.org/skunkfrukt/confjson)
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
The path given when initializing the Config object can be either a directory or a file. If it refers to a file, confjson will look for config files in the containing directory. The reason for this is that it enables the following pattern, using `__file__` to find config files in the same directory as the program.
```python
config = confjson.Config(__file__)
```

### Data access
Items in the confjson config are accessed as in a dict.
```python
if "username" in config["user"]:
	do_something(config["user"]["username"])
	config["user"]["something_count"] += 1
```

### Persistence
The load() method (re-)loads the Config object with values from the backing JSON files. Loading is also performed on initialization, so this is mainly for discarding changes.
```python
config.load()
```
The save() method saves any changed or added items **to user.config.json only**.
```python
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

# Assuming that our default.config.json contains
# {"list_in_default_config": [1, 2, 3]}
config = confjson.Config(__file__)
print(config._default_dict)  # -> {'list_in_default_config': [1, 2, 3]}
print(config._user_dict)  # -> {}
config["list_in_default_config"].append(4)
print(config._default_dict)  # -> {'list_in_default_config': [1, 2, 3]}
print(config._user_dict)  # -> {'list_in_default_config': [1, 2, 3, 4]}
