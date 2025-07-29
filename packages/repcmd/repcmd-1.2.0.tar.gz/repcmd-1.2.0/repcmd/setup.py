import urllib.request
import tarfile
import io
import os

release_tag = 'v1.2.0'

if __name__ == '__main__':
    url = f'https://github.com/tamuto/repcmd/releases/download/{release_tag}/repcmd.tar.gz'

    response = urllib.request.urlopen(url)

    with tarfile.open(fileobj=io.BytesIO(response.read()), mode='r:gz') as tar:
        extract_dir = os.path.dirname(__file__)
        tar.extractall(path=extract_dir)
