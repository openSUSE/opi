#!/usr/bin/python3

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import opi.plugins.chatgpt as chatgpt


assert chatgpt.SUPPORTED_ARCHITECTURES == {'x86_64', 'aarch64'}


with patch.object(chatgpt.opi, 'get_cpu_arch', return_value='x86_64'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no', return_value=False) as ask:
	chatgpt.ChatGPT.run('chatgpt')
	ask.assert_called_once()

with patch.object(chatgpt.opi, 'get_cpu_arch', return_value='ppc64le'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no') as ask:
	chatgpt.ChatGPT.run('chatgpt')
	ask.assert_not_called()

with patch.object(chatgpt.opi, 'get_cpu_arch', return_value='x86_64'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no', return_value=False), \
	 patch.object(chatgpt, 'cprint') as cprint:
	chatgpt.ChatGPT.run('chatgpt')
	assert any(
		'unmodified official package' in call.args[0]
		for call in cprint.call_args_list
	)


builder = MagicMock()
with patch.object(chatgpt, 'RPMBuild', return_value=builder) as rpm_build, \
	 patch.object(chatgpt.opi, 'get_cpu_arch', return_value='aarch64'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no', return_value=True), \
	 patch.object(chatgpt.opi, 'install_packages') as install_packages, \
	 patch.object(chatgpt.opi, 'add_repo') as add_repo, \
	 patch.object(chatgpt.opi, 'ask_keep_repo') as ask_keep_repo, \
	 patch.object(chatgpt, 'install_file') as install_file, \
	 patch.object(chatgpt.subprocess, 'check_call') as check_call:
	chatgpt.ChatGPT.run('chatgpt')
	kwargs = rpm_build.call_args.kwargs
	assert kwargs['requires'] == ['libvulkan_lvp']
	assert kwargs['provides'] == ['mesa-vulkan-drivers']
	assert kwargs['autoreq'] is False
	builder.build.assert_called_once_with()
	assert install_packages.call_args_list[0].args == ([builder.rpmfile_path],)
	assert install_packages.call_args_list[0].kwargs == {'allow_unsigned': True}
	install_file.assert_any_call(chatgpt.REPO_KEY, chatgpt.REPO_KEY_PATH)
	install_file.assert_any_call('repo_add_once="false"\n', chatgpt.DEFAULTS_PATH)
	check_call.assert_called_once_with(['sudo', 'rpm', '--import', chatgpt.REPO_KEY_PATH])
	add_repo.assert_called_once_with(
		filename=chatgpt.REPO_ALIAS,
		name='ChatGPT',
		url=chatgpt.REPO_URL,
	)
	assert install_packages.call_args_list[1].args == (['chatgpt'],)
	assert install_packages.call_args_list[1].kwargs == {}
	ask_keep_repo.assert_called_once_with(chatgpt.REPO_ALIAS)

print('ChatGPT plugin tests passed')
