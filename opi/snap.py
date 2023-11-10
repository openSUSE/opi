import subprocess
import requests
import opi

def http_get_json(url):
	r = requests.get(url, headers={'Snap-Device-Series': '16'})
	r.raise_for_status()
	return r.json()

def get_snap(snap, channel='stable', arch=None):
	channels = http_get_json(f'https://api.snapcraft.io/v2/snaps/info/{snap}')['channel-map']
	if arch:
		arch.replace('x86_64', 'amd64')
		channels = [c for c in channels if c['channel']['architecture'] == arch]
	channels = [c for c in channels if c['channel']['name'] == channel]
	c = channels[0]
	return {"version": c['version'], "url": c['download']['url']}

def extract_snap(snap, target_dir):
	subprocess.check_call(['unsquashfs', '-d', target_dir, snap])
