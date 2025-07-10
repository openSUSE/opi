import os
import subprocess
from shutil import which
from opi import install_packages

def extract_deb(deb, target_dir):
	if not which('bsdtar'):
		print("Installing requirement: bsdtar")
		install_packages(['bsdtar'], no_recommends=True, non_interactive=True)
	os.makedirs(target_dir, exist_ok=True)
	subprocess.check_call(['bsdtar', 'xf', deb, '--directory', target_dir])
	data_tar = os.path.join(target_dir, 'data.tar.xz')
	subprocess.check_call(['bsdtar', 'xf', data_tar, '--directory', target_dir])
	os.unlink(data_tar)
