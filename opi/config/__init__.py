import os
import configparser

default_config = {
	'backend': 'zypp',
	'use_releasever_var': True,
	'new_repo_auto_refresh': True,
}

class ConfigError(Exception):
	pass

config_cache = None
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
				'use_releasever_var': ocfg.getboolean('use_releasever_var'),
				'new_repo_auto_refresh': ocfg.getboolean('new_repo_auto_refresh'),
			})
	return config_cache[key]
