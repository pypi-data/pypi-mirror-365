# PTCC Communication Framework

A modular Python library for communicating with PTCC hardware devices over a custom byte-based protocol. It supports message construction, parsing, throttled I/O communication, device detection, and callback-based event handling.

- Project Homepage: https://gitlab.com/vigophotonics/ptcc-library
- Download Page: https://pypi.org/project/pttcc-library

## Features
- Communication with PTCC devices and modules
- Simplified message generation for communication
- Interface abstraction for serial or custom communication backends
- Auto-detection of PTCC device/module types (NOMEM, MEM, LAB_M)
- Full PtccObject and PtccMessage encoding/decoding support
- Callback registration for received object IDs
- Values retrieving and setting in SI units

## Documentation
Full documentation can be found at https://ptcc-library.readthedocs.io/


## Installation
ptcc_library can be installed from PyPI:
``pip install ptcc-library``

Detailed information can be found at https://pypi.org/project/pttcc-library


## Quick Start Example

### 1. Detect and Connect to Device

```python
from ptcc_library import detect_device
import serial

with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
        device = detect_device(comm=ser)
```

### 2. Register Callbacks

```python
from ptcc_library import CallbackPtccObjectID


def name_callback(name):
        print("Module Name:", name)


def temp_callback(temp, context):
        print(f"Temperature: {temp} K ({context})")


device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, name_callback)
device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temp_callback, "live")
```

### 3. Send Messages

```python
device.write_msg_get_module_iden()
device.write_msg_set_temperature(value_in_kelvins=230)
```


### 4. Handle Incoming Data

```python
while True:
    byte = ser.read(1)
    if byte:
        if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
                print("New message received")
```


## 👤 Author

**Wojciech Szczytko**  
[wszczytko@vigo.com.pl](mailto:wszczytko@vigo.com.pl)  
GitLab: [@wszczytko1](https://gitlab.com/wszczytko1)
        [@wszczytko](https://gitlab.com/wszczytko)
        [@wszczytk](https://gitlab.com/wszczytk)