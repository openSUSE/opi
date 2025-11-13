import opi
from opi.plugins import BasePlugin
from opi import github

# only available for x86_64
if opi.get_cpu_arch() == 'x86_64':
    class OnlyOffice(BasePlugin):
        main_query = 'onlyoffice'
        description = 'Office suite'
        queries = [main_query]

        @classmethod
        def run(cls, query):
            f1 = lambda a: a['name'] == 'onlyoffice-desktopeditors.suse12.x86_64.rpm'
            github.install_rpm_release('ONLYOFFICE', 'DesktopEditors', filters=[f1], allow_unsigned=True) # no key available
            print("Installation done.\nIf you experience scaling issues with the UI, try calling:\nonlyoffice-desktopeditors --force-scale=1")
