import os
import subprocess
import opi
from opi.plugins import BasePlugin
from opi import github
from opi import rpmbuild
from opi import http

# VERSION is only set on leap based distros - not tumbleweed, where this package is available via default repos
if opi.get_version():
    class Zellij(BasePlugin):
        main_query = 'zellij'
        description = 'A terminal workspace with batteries included'
        queries = [main_query]

        @classmethod
        def run(cls, query):
            org = "zellij-org"
            repo = "zellij"
            latest_release = github.get_latest_release(org, repo)
            if not latest_release:
                print(f'No release found for {org}/{repo}')
                return
            version = latest_release['tag_name'].lstrip('v')
            if not opi.ask_yes_or_no(f"Do you want to install {repo} release {version} from {org} github repo?"):
                return
            arch = opi.get_cpu_arch()
            asset_name = f'zellij-{arch}-unknown-linux-musl.tar.gz'
            asset = github.get_release_asset(latest_release, filters=[lambda e: e['name'] == asset_name])
            if not asset:
                print(f"No asset found for {org}/{repo} release {version}")
                return
            url = asset['url']

            binary_path = 'usr/bin/zellij'

            rpm = rpmbuild.RPMBuild('zellij', version, cls.description, arch, files=[
                f"/{binary_path}",
            ])

            bindir_abspath = os.path.join(rpm.buildroot, os.path.dirname(binary_path))
            binary_abspath = os.path.join(rpm.buildroot, binary_path)
            tarball_abspath = os.path.join(rpm.tmpdir.name, asset_name)

            http.download_file(url, tarball_abspath)
            os.makedirs(bindir_abspath, exist_ok=True)
            subprocess.call(['tar', 'xvf', tarball_abspath, '-C', bindir_abspath, 'zellij'])
            os.chmod(binary_abspath, 0o755)

            rpm.build()
            opi.install_packages([rpm.rpmfile_path], allow_unsigned=True)
