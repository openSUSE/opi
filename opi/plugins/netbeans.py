import opi
from opi.plugins import BasePlugin
from opi import github

class NetBeans(BasePlugin):
	main_query = 'netbeans'
	description = 'Development environment, tooling platform and application framework'
	queries = ['netbeans', 'NetBeans']

	@classmethod
	def run(cls, query):
		arch = opi.get_cpu_arch()
		github.install_rpm_release('Friends-of-Apache-NetBeans', 'netbeans-installers',
			filters=[lambda a: a['name'].endswith(f'{arch}.rpm')],
			allow_unsigned=True # no key available
		)
