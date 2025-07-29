==========
 Examples
==========


Basics
======

Detect and Connect to Device
----------------------------
Example uses `serial <https://pyserial.readthedocs.io/en/latest/shortintro.html#opening-serial-ports>`_

    >>> from ptcc_library import detect_device
    >>> import serial
    >>> with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    >>>     device = detect_device(comm=ser)

Register Callbacks
------------------

    >>> from ptcc_library import CallbackPtccObjectID
    >>> def name_callback(name):
            print("Module Name:", name)
    >>> def temp_callback(temp, context):
            print(f"Temperature: {temp} K ({context})")
    >>> device.receiver.register_callback(CallbackPtccObjectID.MODULE_IDEN_NAME, name_callback)
    >>> device.receiver.register_callback(CallbackPtccObjectID.MODULE_BASIC_PARAMS_T_DET, temp_callback, "live")

Send Messages
-------------

    >>> device.write_msg_get_module_iden()
    >>> device.write_msg_set_temperature(value_in_kelvins=230)


Handle Incoming Data
--------------------

    >>> while True:
    >>>     byte = ser.read(1)
    >>>     if byte:
    >>>         if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
    >>>                 print("New message received")

Handle Containers
-----------------

    >>> def iden_callback(objects):
    >>>     for o in objects:
    >>>         print(f"{o.name} = {o.value}")
    >>> device.receiver.register_callback(CallbackPtccObjectID.DEVICE_IDEN, iden_callback)
