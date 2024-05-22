# ahk-client

A client for [ahk-server](https://github.com/spyoungtech/ahk-server).

## Installation

```bash
pip install ahk-client
```

## Usage

Usage is nearly identical to the [ahk](https://github.com/spyoungtech/ahk-server) package, except you specify 
a remote host (running `ahk-server`) to connect to instead of using a local installation of AutoHotkey.

```python
from ahk_client import AHKClient

ahk = AHKClient('http://127.0.0.1:8000')

print(ahk.get_mouse_position())
```


## Status

This project (and its server counterpart) is usable, but in **very** early stages of development. 
Notably, it does not currently include any authentication mechanisms for securing connection with the remote server, so use with caution.
