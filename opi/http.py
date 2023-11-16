import os
import requests

def download_file(url, local_filename):
	response = requests.get(url, stream=True)
	response.raise_for_status()

	total_size = int(response.headers.get('content-length', 0))
	block_size = 1024*512

	os.makedirs(os.path.dirname(local_filename), exist_ok=True)

	print(f"Downloading to {local_filename}:")
	with open(local_filename, 'wb') as local_file:
		total_bytes_received = 0
		for data in response.iter_content(chunk_size=block_size):
			local_file.write(data)
			total_bytes_received += len(data)
			print_progress(total_bytes_received, total_size)
	print()

def print_progress(bytes_received, total_size):
	progress = (bytes_received / total_size) * 100
	progress = min(100, progress)
	print(f"Progress: [{int(progress)}%] [{'=' * int(progress / 2)}{' ' * (50 - int(progress / 2))}]", end='\r')
