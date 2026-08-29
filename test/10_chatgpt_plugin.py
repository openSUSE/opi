#!/usr/bin/python3

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

import opi.plugins.chatgpt as chatgpt


assert set(chatgpt.RPM_URLS) == {'x86_64', 'aarch64'}
assert chatgpt.RPM_URLS['x86_64'].endswith('chatgpt.x86_64.rpm')
assert chatgpt.RPM_URLS['aarch64'].endswith('chatgpt.aarch64.rpm')


with patch.object(chatgpt.opi, 'get_os_release', return_value={'NAME': 'openSUSE Leap'}), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no') as ask:
	chatgpt.ChatGPT.run('chatgpt')
	ask.assert_not_called()

with patch.object(chatgpt.opi, 'get_os_release', return_value={'NAME': 'openSUSE Tumbleweed'}), \
	 patch.object(chatgpt.opi, 'get_cpu_arch', return_value='ppc64le'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no') as ask:
	chatgpt.ChatGPT.run('chatgpt')
	ask.assert_not_called()

with patch.object(chatgpt.opi, 'get_os_release', return_value={'NAME': 'openSUSE Tumbleweed'}), \
	 patch.object(chatgpt.opi, 'get_cpu_arch', return_value='x86_64'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no', return_value=False), \
	 patch.object(chatgpt, 'cprint') as cprint:
	chatgpt.ChatGPT.run('chatgpt')
	assert any(
		'without signature verification' in call.args[0]
		for call in cprint.call_args_list
	)


builder = MagicMock()
with patch.object(chatgpt, 'RPMBuild', return_value=builder) as rpm_build, \
	 patch.object(chatgpt.opi, 'get_os_release', return_value={'NAME': 'openSUSE Tumbleweed'}), \
	 patch.object(chatgpt.opi, 'get_cpu_arch', return_value='aarch64'), \
	 patch.object(chatgpt.opi, 'ask_yes_or_no', return_value=True), \
	 patch.object(chatgpt.opi, 'install_packages') as install_packages:
	chatgpt.ChatGPT.run('chatgpt')
	kwargs = rpm_build.call_args.kwargs
	assert kwargs['requires'] == ['libvulkan_lvp']
	assert kwargs['provides'] == ['mesa-vulkan-drivers']
	assert kwargs['autoreq'] is False
	builder.build.assert_called_once_with()
	assert install_packages.call_args_list[0].args == ([builder.rpmfile_path],)
	assert install_packages.call_args_list[0].kwargs == {'allow_unsigned': True}
	assert install_packages.call_args_list[1].args == ([chatgpt.RPM_URLS['aarch64']],)
	assert install_packages.call_args_list[1].kwargs == {'allow_unsigned': True}

print('ChatGPT plugin tests passed')
