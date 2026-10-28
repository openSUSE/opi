#!/usr/bin/python3

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import opi


class RepoVariableTests(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		self.root = Path(self.temp.name)
		self.system = self.root / 'etc/zypp'
		self.vendor = self.root / 'usr/etc/zypp'
		self.vars = self.system / 'vars.d'
		self.vars.mkdir(parents=True)
		self.enter_patch(patch.object(opi, 'ZYPP_CONFIG_DIR', str(self.system)))
		self.enter_patch(patch.object(opi, 'ZYPP_VENDOR_CONFIG_DIR', str(self.vendor)))
		self.enter_patch(patch.object(opi, 'get_version', return_value='16.0'))
		self.enter_patch(patch.object(opi, 'get_cpu_arch', return_value='x86_64'))
		self.enter_patch(patch.dict(os.environ))
		os.environ.pop('ZYPP_CONF', None)

	def enter_patch(self, context):
		context.start()
		self.addCleanup(context.stop)

	def write(self, path, value):
		path.parent.mkdir(parents=True, exist_ok=True)
		path.write_text(value)

	def test_builtin_variables(self):
		self.assertEqual(opi.expand_vars('$releasever/${releasever}/$basearch/${basearch}'),
			'16.0/16.0/x86_64/x86_64')

	def test_custom_variables_in_repository_name_url_and_key(self):
		self.write(self.vars / 'mirror', 'mirror.example\nignored.example\n')
		self.write(self.vars / 'channel', 'stable\n')
		for value, expected in [
			('Repo ${channel}', 'Repo stable'),
			('https://$mirror/$channel/$basearch', 'https://mirror.example/stable/x86_64'),
			('https://${mirror}/${channel}/key.gpg', 'https://mirror.example/stable/key.gpg'),
		]:
			with self.subTest(value=value):
				self.assertEqual(opi.expand_vars(value), expected)

	def test_first_line_preserves_spaces_and_empty_values(self):
		self.write(self.vars / 'spaced', ' leading and trailing \nsecond line\n')
		self.write(self.vars / 'empty', '')
		self.assertEqual(opi.expand_vars('${spaced}/${empty}/$empty'), ' leading and trailing //')

	def test_existing_repository_matches_expanded_url(self):
		self.write(self.vars / 'mirror', 'mirror.example')
		self.write(self.vars / 'channel', 'stable')
		repos = self.system / 'repos.d'
		self.write(repos / 'custom.repo', '[custom]\nname=Repo $channel\n'
			'baseurl=https://$mirror/${channel}/$basearch/\nenabled=1\n')
		with patch.object(opi, 'REPO_DIR', str(repos)):
			repo = opi.get_enabled_repo_by_url('https://mirror.example/stable/x86_64')
		self.assertIsNotNone(repo)
		self.assertEqual(repo.name_expanded(), 'Repo stable')
		self.assertEqual(repo.url_expanded(), 'https://mirror.example/stable/x86_64/')

	def test_whole_names_and_unknown_variables(self):
		self.write(self.vars / 'repo', 'short')
		self.write(self.vars / 'repo_extra', 'long')
		self.assertEqual(opi.expand_vars('$repo/$repo_extra/${repo}_extra/$repo_missing/${missing}/$releasever_extra'),
			'short/long/short_extra/$repo_missing/${missing}/$releasever_extra')

	def test_values_are_not_recursively_expanded(self):
		self.write(self.vars / 'literal', '$releasever')
		self.assertEqual(opi.expand_vars('$literal/${literal}'), '$releasever/$releasever')

	def test_custom_builtin_overrides(self):
		self.write(self.vars / 'releasever', '99.0')
		self.write(self.vars / 'basearch', 'custom_arch')
		self.assertEqual(opi.expand_vars('$releasever/$basearch'), '99.0/custom_arch')

	def test_empty_releasever_override_and_basearch_fallback(self):
		self.write(self.vars / 'releasever', '')
		self.write(self.vars / 'basearch', '')
		self.assertEqual(opi.expand_vars('$releasever/$basearch'), '/x86_64')

	def test_unavailable_builtin_stays_unexpanded(self):
		with patch.object(opi, 'get_version', return_value=None):
			self.assertEqual(opi.expand_vars('$releasever/${releasever}'), '$releasever/${releasever}')

	def test_invalid_names_and_directories_are_ignored(self):
		self.write(self.vars / 'repo.backup', 'not a variable')
		self.write(self.vars / '.hidden', 'not a variable')
		(self.vars / 'directory').mkdir()
		self.assertEqual(opi.get_repo_vars(), {})

	def test_missing_vars_directory(self):
		self.vars.rmdir()
		self.assertEqual(opi.expand_vars('$missing/$basearch'), '$missing/x86_64')

	def test_custom_varsdir(self):
		custom = self.root / 'custom%vars'
		self.write(custom / 'channel', 'custom')
		self.write(self.vars / 'channel', 'default')
		self.write(self.system / 'zypp.conf', f'[main]\nvarsdir = {custom}\n')
		self.assertEqual(opi.expand_vars('$channel'), 'custom')

	def test_configdir_changes_default_varsdir(self):
		custom = self.root / 'custom'
		self.write(custom / 'vars.d/channel', 'custom')
		self.write(self.system / 'zypp.conf', f'[main]\nconfigdir = {custom}\n')
		self.assertEqual(opi.expand_vars('$channel'), 'custom')

	def test_vendor_config_and_system_drop_in(self):
		custom = self.root / 'custom'
		self.write(custom / 'channel', 'custom')
		self.write(self.vendor / 'zypp.conf', '[main]\nvarsdir = /missing\n')
		self.write(self.system / 'zypp.conf.d/90-custom.conf', f'[main]\nvarsdir = {custom}\n')
		self.assertEqual(opi.expand_vars('$channel'), 'custom')

	def test_empty_system_files_mask_vendor_files(self):
		self.write(self.vars / 'channel', 'default')
		for name in ['zypp.conf', 'zypp.conf.d/50-vars.conf']:
			self.write(self.vendor / name, '[main]\nvarsdir = /missing\n')
			self.write(self.system / name, '')
		self.assertEqual(opi.expand_vars('$channel'), 'default')

	def test_drop_ins_use_filename_order_across_both_directories(self):
		custom = self.root / 'custom'
		self.write(custom / 'channel', 'custom')
		self.write(self.system / 'zypp.conf.d/10-first.conf', '[main]\nvarsdir = /missing\n')
		self.write(self.vendor / 'zypp.conf.d/90-last.conf', f'[main]\nvarsdir = {custom}\n')
		self.assertEqual(opi.expand_vars('$channel'), 'custom')

	def test_environment_configuration_replaces_default_files(self):
		custom = self.root / 'custom'
		self.write(custom / 'channel', 'custom')
		self.write(self.system / 'zypp.conf', '[main]\nvarsdir = /missing\n')
		conf = self.root / 'alternative.conf'
		self.write(conf, f'[main]\nvarsdir = {custom}\n')
		os.environ['ZYPP_CONF'] = str(conf)
		self.assertEqual(opi.expand_vars('$channel'), 'custom')


if __name__ == '__main__':
	unittest.main()
