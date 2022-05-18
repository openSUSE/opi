import os
import pwd
import subprocess
import json

cache = {}

default_config = {
	"backend": "zypp",
	"use_releasever_var": True
}

class ConfigError(Exception):
	pass

def create_default_config():
	path = pwd.getpwuid(os.getuid()).pw_dir + "/.config/opi/"
	subprocess.call(["mkdir", "-p", path])
	config_file = open(path + 'config.json', 'w')
	json.dump(default_config, config_file, indent=4)

def get_key_from_config(key: str):
	if not key in cache:
		path = pwd.getpwuid(os.getuid()).pw_dir + "/.config/opi/config.json"
		if not os.path.isfile(path):
			create_default_config()
		config = default_config.copy()
		config.update(json.loads(open(path).read()))
		cache[key] = config[key]
		return cache[key]
	else:
		return cache[key]

path = pwd.getpwuid(os.getuid()).pw_dir + "/.config/opi/config.json"
if not os.path.isfile(path):
	create_default_config()

