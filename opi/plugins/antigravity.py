import opi
from opi.plugins import BasePlugin

class Antigravity(BasePlugin):
    main_query = 'antigravity'
    description = 'IDE with AI from Google'
    queries = [main_query]

    @classmethod
    def run(cls, query):
        if not opi.ask_yes_or_no('Do you want to install Antigravity from Google repository?'):
            return

        opi.add_repo(
            filename = 'antigravity',
            name = 'antigravity',
            url = 'https://us-central1-yum.pkg.dev/projects/antigravity-auto-updater-dev/antigravity-rpm',
            gpgkey = 'https://us-central1-yum.pkg.dev/doc/repo-signing-key.gpg'
        )

        opi.install_packages(['antigravity'])
        opi.ask_keep_repo('antigravity')
