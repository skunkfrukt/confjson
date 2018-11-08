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
The names of both files are configurable. The above names are the defaults.

### Initialization
The path given when initializing the Config object can be either a directory or a file. If it refers to a file, confjson will look for config files in the containing directory. The reason for this is that it enables the pattern of using `__file__` to find config files in the same directory as the program.
```python
config = confjson.Config(__file__)
config = confjson.Config(".")
config = confjson.Config(
	"./configs",
	user_config_filename=f"{os.getenv('username')}.cfg",
	default_config_filename="global.cfg",
)
```

### Data access
Items in the confjson config are accessed as in a dict.
```python
if "username" in config["user"]:
	do_something(config["user"]["username"])
	config["user"]["something_count"] += 1
```
It is also possible to access items as attributes, *unless they share a name with a method of the Config class*.
```python
config.my_key = "my value"
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

## Version history

### 1.3.0
* Made filenames of both user.config.json and default.config.json configurable.

### 1.2.1
* Improved attribute-style access and enabled mixed style access.

### 1.2.0
* Enabled attribute-style access to config items.

### 1.1.0
* Fixed handling of nested dicts.
* Added check to prevent insertion of JSON-incompatible values right away rather than fail on save.
* Added some more dict-like dunder methods.

### 1.0.1
* Changed `__init__` to also load the config files.

### 1.0.0
* Initial release.
