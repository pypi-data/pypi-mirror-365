# whl-com

## Installation

```bash
pip install whl-com
```

## Usage

### send single command

> send `log com1 gpgga ontime 1` to device

```bash
python3 whl_com.py --device /dev/ttyUSB0 --baudrate 460800 log com1 gpgga ontime 1
```

### send multiple commands

> create a file `commands.txt` with the following content:

```text
log com1 gpgga ontime 1
log com1 gpchcx ontime 0.01
saveconfig
```

> specify the file with `--input_file` option:

```bash
python3 whl_com.py --device /dev/ttyUSB0 --baudrate 460800 --input_file commands.txt
```
