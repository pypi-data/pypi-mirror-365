# core-ftp
_______________________________________________________________________________

This project/library provides a comprehensive set of common components and 
interfaces designed to facilitate and streamline FTP connections, 
ensuring efficient communication and data transfer...


## Execution Environment

### Install libraries
```shell
pip install --upgrade pip 
pip install virtualenv
```

### Create the Python Virtual Environment.
```shell
virtualenv --python={{python-version}} .venv
virtualenv --python=python3.11 .venv
```

### Activate the Virtual Environment.
```shell
source .venv/bin/activate
```

### Install required libraries.
```shell
pip install .
```

### Check tests and coverage...
```shell
python manager.py run-tests
python manager.py run-tests --test-type functional --pattern "*.py"
python manager.py run-coverage
```

## How to Use

### Installation...
```shell
pip install core-ftp
```

### Examples...
```python
from core_ftp.clients.sftp import SftpClient

with SftpClient("test.rebex.net", 22, "demo", "password") as client:
    for x in client.list_files("/"):
        print(x)
```

```python
from core_ftp.clients.sftp import SftpClient

with SftpClient(
        host="localhost", port=23,
        user="foo", private_key_path="key_path") as client:

    for x in client.list_files("/"):
        print(x)
```

## Docker
You can use docker to create an SFTP server to test the client using the functional 
tests via command `python manager.py run-tests --test-type functional --pattern "*.py"` and the following docker
image: <atmoz/sftp> (https://hub.docker.com/r/atmoz/sftp/).

### Authentication via user & password...
```shell
docker run \
  -v ./tests/resources/upload:/home/foo/upload:rw \
  -p 22:22 -d atmoz/sftp foo:pass:::upload
```

### Authentication via SSH key... 
```shell
docker run \
  -v ./tests/resources/ssh_keys/id_rsa.pub:/home/foo/.ssh/keys/id_rsa.pub:ro \
  -v ./tests/resources/upload:/home/foo/upload:rw \
  -p 23:22 -d atmoz/sftp foo::1001
```
