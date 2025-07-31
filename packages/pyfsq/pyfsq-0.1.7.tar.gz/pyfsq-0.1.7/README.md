# pyfsq
Python-based FSQ API designed for transferring data to a FSQ server and
simple console client for demonstrating how to use the API.

The FSQ protocol explanation and server/client written in C is provided at [https://github.com/GSI-HPC/fsq](https://github.com/GSI-HPC/fsq)

## Installation
```pip3 install pyfsq```

## Requirements
### Python
* Python >= 3.7

## Console Tools
After installing the package, the console tools ```pyfsqc``` and ```pyfsqbench``` are available.
### FSQ Client
```bash
$ pyfsqc -f /lustre -a /lustre/fsqc -n polaris -p polaris -s localhost -v info src/fsqc.py
[2024-07-31 12:24:48,804 api.py:103 INFO] connect sucessfully to FSQ server localhost:7625
[2024-07-31 12:24:48,804 api.py:178 INFO] opened sucessfully on FSQ server file /lustre/fsqc/src/fsqc.py
[2024-07-31 12:24:48,847 api.py:230 INFO] send sucessfully 2471 bytes to file /lustre/fsqc/src/fsqc.py on FSQ server
[2024-07-31 12:24:48,848 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqc/src/fsqc.py
[2024-07-31 12:24:48,848 api.py:320 INFO] disconnect sucessfully from FSQ server localhost
```
### FSQ Benchmark Tool
```bash
$ pyfsqbench -t 2 -n polaris -p polaris -s localhost -v info
[2024-07-31 12:26:59,098 api.py:103 INFO] connect sucessfully to FSQ server localhost:7625
[2024-07-31 12:26:59,098 api.py:103 INFO] connect sucessfully to FSQ server localhost:7625
[2024-07-31 12:26:59,129 api.py:178 INFO] opened sucessfully on FSQ server file /lustre/fsqbench/PN18OzXV5mccV3Wl5Gm0VQz7vO6YheH1
[2024-07-31 12:26:59,129 api.py:178 INFO] opened sucessfully on FSQ server file /lustre/fsqbench/O83IhaSELK6uzPs8cvLW2rmkMiL3K4MQ
[2024-07-31 12:26:59,132 api.py:230 INFO] send sucessfully 16777216 bytes to file /lustre/fsqbench/PN18OzXV5mccV3Wl5Gm0VQz7vO6YheH1 on FSQ server
[2024-07-31 12:26:59,132 api.py:230 INFO] send sucessfully 16777216 bytes to file /lustre/fsqbench/O83IhaSELK6uzPs8cvLW2rmkMiL3K4MQ on FSQ server
[2024-07-31 12:26:59,133 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqbench/PN18OzXV5mccV3Wl5Gm0VQz7vO6YheH1
[2024-07-31 12:26:59,133 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqbench/O83IhaSELK6uzPs8cvLW2rmkMiL3K4MQ
...
...
[2024-07-31 12:26:59,180 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqbench/545Vutrtr8T9TQiv8GbMAE9ujBMltcrB
[2024-07-31 12:26:59,180 api.py:178 INFO] opened sucessfully on FSQ server file /lustre/fsqbench/RUnZKHB2zuAkbbqrFXjgrlCDsEzqajfj
[2024-07-31 12:26:59,183 api.py:230 INFO] send sucessfully 16777216 bytes to file /lustre/fsqbench/YuaSxx3ifs3yBWaki0DbLDhXHKNLudVP on FSQ server
[2024-07-31 12:26:59,183 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqbench/YuaSxx3ifs3yBWaki0DbLDhXHKNLudVP
[2024-07-31 12:26:59,183 api.py:320 INFO] disconnect sucessfully from FSQ server localhost
[2024-07-31 12:26:59,184 api.py:230 INFO] send sucessfully 16777216 bytes to file /lustre/fsqbench/RUnZKHB2zuAkbbqrFXjgrlCDsEzqajfj on FSQ server
[2024-07-31 12:26:59,184 api.py:278 INFO] closed sucessfully on FSQ server file /lustre/fsqbench/RUnZKHB2zuAkbbqrFXjgrlCDsEzqajfj
[2024-07-31 12:26:59,184 api.py:320 INFO] disconnect sucessfully from FSQ server localhost
Thread-1 (perform_task) transmitted 268435456 bytes in 0.0554 secs
Thread-2 (perform_task) transmitted 268435456 bytes in 0.0545 secs
total transmitted 536870912 bytes in 0.1099 secs (4.8848 Gbytes/secs)
```

## Example
### FSQ API
```
from fsq.api import Api as FsqApi
from fsq.struct import FsqStorageDest

fsq = FsqApi()
fsq.connect('polaris', 'polaris', 'localhost', 7625)
fsq.open(fs='/lustre', fpath='/lustre/physicsexp/pyfsq/helloworld.txt',
         desc='some desc', dest=FsqStorageDest.FSQ_STORAGE_LUSTRE)
buffer = b'hello world!'
size = len(buffer)
fsq.write(buffer, size)
fsq.close()
fsq.disconnect()
```

### Contextmanager FSQ API
```
from fsq.contextmanager import Connect, Open
from fsq.struct import FsqStorageDest

with Connect('polaris', 'polaris', 'localhost', 7625) as fsq:
    with Open(fsq, '/lustre', '/lustre/physicsexp/ctxmgr/helloworld.txt',
              'some desc', FsqStorageDest.FSQ_STORAGE_LOCAL):
        buffer = b'hello world!'
        size = len(buffer)
        fsq.write(buffer, size)
```
