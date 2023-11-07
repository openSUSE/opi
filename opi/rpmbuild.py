import os
import tempfile
import textwrap
import re
import subprocess
import glob

class RPMBuild:
	def __init__(self, name, version, description, buildarch="noarch", files=[], dirs=[], config=[]):
		self.name = name
		self.version = version
		self.description = description
		self.buildarch = buildarch
		self.files = files
		self.dirs = dirs
		self.config = config

		self.tmpdir = tempfile.TemporaryDirectory()

		self.src_root_dir = os.path.join(self.tmpdir.name, "root")
		self.spec_path = os.path.join(self.tmpdir.name, "specfile.spec")
		self.tmp_buildroot_dir = os.path.join(self.tmpdir.name, "buildroot")
		self.rpm_out_dir = os.path.join(self.tmpdir.name, "rpms")

		os.mkdir(self.src_root_dir)
		os.mkdir(self.rpm_out_dir)

	@staticmethod
	def _mkspec(name, version, description, buildarch="noarch", files=[], dirs=[], config=[]):
		nl = "\n"
		spec = re.sub(r"^\s*", "", f"""
			Name:      {name}
			Version:   {version}
			Release:   0
			Summary:   {description}
			License:   n/a
			BuildArch: {buildarch}

			%description
			{description}
			Built locally using OPI.

			%install
			cp -lav ./root/* %{{buildroot}}/

			%files
			{nl.join(files)}
			{nl.join(f"%dir {d}" for d in dirs)}
			{nl.join(f"%config {c}" for c in config)}

			%changelog
		""", flags=re.M)
		return spec

	def add_desktop_file(self, cmd, icon):
		os.makedirs(os.path.join(self.src_root_dir, 'usr/share/applications'))
		desktop_path = f'usr/share/applications/{self.name}.desktop'
		desktop_abspath = os.path.join(self.src_root_dir, desktop_path)
		self.files.append(f"/{desktop_path}")
		with open(desktop_abspath, 'w') as f:
			f.write(textwrap.dedent(f"""
				[Desktop Entry]
				Name={self.name}
				Comment={self.description}
				Exec={cmd}
				Icon={icon}
				Type=Application
			"""))

	def build(self):
		print(f"Creating RPM for {self.name}")
		with open(self.spec_path, 'w') as f:
			spec = type(self)._mkspec(self.name, self.version, self.description, self.buildarch,
			                          self.files, self.dirs, self.config)
			f.write(spec)
		subprocess.check_call([
			"rpmbuild", "-bb", "--build-in-place",
			"--buildroot", self.tmp_buildroot_dir,
			"--define", f"_rpmdir {self.rpm_out_dir}",
			"specfile.spec"
		], cwd=self.tmpdir.name)
		rpmfile = glob.glob(f"{self.rpm_out_dir}/*/*.rpm")[0]
		self.rpmfile_path = rpmfile
		return rpmfile
