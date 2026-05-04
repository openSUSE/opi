import opi
from opi.plugins import BasePlugin
from opi import github

class RustDesk(BasePlugin):
	main_query = 'rustdesk'
	description = 'Open Source remote desktop application'
	queries = ['rustdesk', 'RustDesk']

	@classmethod
	def run(cls, query):
		arch = opi.get_cpu_arch()
		github.install_rpm_release('rustdesk', 'rustdesk',
			filters=[lambda a: a['name'].endswith(f'{arch}-suse.rpm')],
			allow_unsigned=True # no key available
		)
