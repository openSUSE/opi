import opi
from opi.plugins import BasePlugin
from opi import github

class Libation(BasePlugin):
	main_query = 'libation'
	description = 'Tool for managing audible audiobooks'
	queries = [main_query, 'Libation']

	@classmethod
	def run(cls, query):
		arch = opi.get_cpu_arch().replace('aarch64', 'amd64').replace('x86_64', 'amd64')
		github.install_rpm_release('rmcrackan', 'Libation',
			filters=[lambda a: a['name'].endswith(f'{arch}.rpm')],
			allow_unsigned=True # no key available
		)
