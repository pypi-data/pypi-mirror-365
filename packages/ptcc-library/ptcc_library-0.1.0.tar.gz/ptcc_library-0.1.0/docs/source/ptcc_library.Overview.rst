Overview
========

This is a modular Python library for communicating with PTCC hardware devices over a custom byte-based protocol. It supports message construction, parsing, throttled I/O communication, device detection, and callback-based event handling.

Features
========
* Communication with PTCC devices and modules
* Simplified message generation for communication
* Interface abstraction for serial or custom communication backends
* Auto-detection of PTCC device/module types (NOMEM, MEM, LAB_M)
* Full PtccObject and PtccMessage encoding/decoding support
* Callback registration for received object IDs
* Values retrieving and setting in SI units

You can find source code at: https://gitlab.com/vigophotonics/ptcc-library
