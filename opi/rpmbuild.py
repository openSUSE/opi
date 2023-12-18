import os
import tempfile
import re
import subprocess
import glob
import shutil

def copy(src, dst):
	"""
		Copy src to dst using hardlinks.
		dst will be the full final path.
		Directories will be created as needed.
	"""
	if os.path.islink(src) or os.path.isfile(src):
		os.makedirs(os.path.dirname(dst), exist_ok=True)
	if os.path.islink(src):
		link_target = os.readlink(src)
		os.symlink(link_target, dst)
	elif os.path.isfile(src):
		shutil.copy2(src, dst)
	else:
		shutil.copytree(src, dst, copy_function=os.link, symlinks=True, ignore_dangling_symlinks=False)

def dedent(s):
	""" Other than textwrap's implementation this one has no problems with some lines unindented.
	    It will unconditionally strip any leading whitespaces for each line.
	"""
	return re.sub(r"^\s*", "", s, flags=re.M)

class RPMBuild:
	def __init__(self, name, version, description, buildarch="noarch",
	             requires=[], recommends=[], provides=[], suggests=[], conflicts=[], autoreq=True,
		         files=[], dirs=[], config=[]):
		self.name = name
		self.version = version
		self.description = description
		self.buildarch = buildarch
		self.requires = requires
		self.recommends = recommends
		self.provides = provides
		self.suggests = suggests
		self.conflicts = conflicts
		self.autoreq = autoreq
		self.files = files
		self.dirs = dirs
		self.config = config

		self.tmpdir = tempfile.TemporaryDirectory()

		self.buildroot = os.path.join(self.tmpdir.name, "buildroot") # buildroot where plugins copy files to
		self.spec_path = os.path.join(self.tmpdir.name, "specfile.spec")
		self.rpm_out_dir = os.path.join(self.tmpdir.name, "rpms")

		os.mkdir(self.buildroot)
		os.mkdir(self.rpm_out_dir)

	def mkspec(self):
		nl = "\n"
		spec = dedent(f"""
			Name:      {self.name}
			Version:   {self.version}
			Release:   0
			Summary:   {self.description}
			License:   n/a
			BuildArch: {self.buildarch}
			{nl.join(f"Requires: {r}" for r in self.requires)}
			{nl.join(f"Recommends: {r}" for r in self.recommends)}
			{nl.join(f"Provides: {r}" for r in self.provides)}
			{nl.join(f"Suggests: {r}" for r in self.suggests)}
			{nl.join(f"Conflicts: {r}" for r in self.conflicts)}
			{"AutoReq: no" if not self.autoreq else ''}

			%description
			{self.description}
			Built locally using OPI.

			%files
			{nl.join(self.files)}
			{nl.join(f"%dir {d}" for d in self.dirs)}
			{nl.join(f"%config {c}" for c in self.config)}

			%changelog
		""")
		return spec

	def add_desktop_file(self, cmd, icon, **kwargs):
		os.makedirs(os.path.join(self.buildroot, 'usr/share/applications'))
		desktop_path = f'usr/share/applications/{self.name}.desktop'
		desktop_abspath = os.path.join(self.buildroot, desktop_path)
		self.files.append(f"/{desktop_path}")
		with open(desktop_abspath, 'w') as f:
			nl = "\n"
			f.write(dedent(f"""
				[Desktop Entry]
				Name={self.name}
				Comment={self.description}
				Exec={cmd}
				Icon={icon}
				Type=Application
				{nl.join(["%s=%s" % (k, v) for k, v in kwargs.items()])}
			"""))

	def build(self):
		print(f"Creating RPM for {self.name}")
		with open(self.spec_path, 'w') as f:
			spec = self.mkspec()
			f.write(spec)
		subprocess.check_call([
			"rpmbuild", "-bb", "--build-in-place",
			"--buildroot", self.buildroot,
			"--define", f"_rpmdir {self.rpm_out_dir}",
			"specfile.spec"
		], cwd=self.tmpdir.name)
		rpmfile = glob.glob(f"{self.rpm_out_dir}/*/*.rpm")[0]
		self.rpmfile_path = rpmfile
		return rpmfile
