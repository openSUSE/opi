class GlobalState:
	default_state = {
		'arg_non_interactive': False,
	}
	state = {
	}

	def __setattr__(self, key, value):
		type(self).state[key] = value

	def __getattr__(self, key):
		return type(self).state.get(key, type(self).default_state[key])

global_state = GlobalState()
