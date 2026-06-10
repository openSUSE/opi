import opi
from opi.plugins import BasePlugin
from opi import github

class Tolaria(BasePlugin):
    main_query = 'tolaria'
    description = 'Personal knowledge and life management app'
    queries = [main_query]

    @classmethod
    def run(cls, query):
        github.install_rpm_release(
            'refactoringhq',
            'tolaria',
            filters=[
                lambda a: (
                    a['name'].startswith('Tolaria-')
                    and a['name'].endswith('.x86_64.rpm')
                )
            ],
            allow_unsigned=True
        )
