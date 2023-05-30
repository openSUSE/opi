import opi.config as config

class BackendConstants:
	zypp = 'zypp'
	dnf = 'dnf'


def get_backend():
	backend = config.get_key_from_config('backend')
	if not backend in ['zypp', 'dnf']:
		raise config.ConfigError('Invalid backend configuration.')
	return backend
