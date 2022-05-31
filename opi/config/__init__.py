import os
import pwd
import subprocess
import configparser

parser = configparser.ConfigParser()
parser.read("/etc/opi.cfg")

default_config = {
	"backend": "zypp",
	"use_releasever_var": True
}

config_cache = None

class ConfigError(Exception):
	pass

def get_key_from_config(key: str):
	global config_cache
	if not config_cache:
		config_cache = default_config.copy()
		path = os.environ.get('OPI_CONFIG', '/etc/opi.cfg')
		if os.path.exists(path):
			cp = configparser.ConfigParser()
			cp.read(path)
			ocfg = cp['opi']
			config_cache.update({
				'backend': ocfg.get('backend'),
				'use_releasever_var': ocfg.getboolean('use_releasever_var')
			})
	return config_cache[key]
