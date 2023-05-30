import opi
from opi.plugins import BasePlugin

class AnyDesk(BasePlugin):
    main_query = 'anydesk'
    description = 'AnyDesk remote access'
    queries = ['anydesk']

    @classmethod
    def run(cls, query):
        if not opi.ask_yes_or_no('Do you want to install AnyDesk from AnyDesk repository?'):
            return

        opi.add_repo(
            filename = 'anydesk',
            name = 'anydesk',
            url = 'http://rpm.anydesk.com/opensuse/$basearch/',
            gpgkey = 'https://keys.anydesk.com/repos/RPM-GPG-KEY'
        )

        opi.install_packages(['anydesk'])
        opi.ask_keep_repo('anydesk')
