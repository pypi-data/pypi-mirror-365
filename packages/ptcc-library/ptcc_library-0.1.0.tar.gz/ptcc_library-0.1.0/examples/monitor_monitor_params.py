import time

from ptcc_library import *

import serial


def monitor_parameters_callback(objects, device):
    print("PTCC Device Type: ", device.name)
    print("-------------------------------------------------")
    for o in objects:
        print(f"{o.name} = {o.value}")
    print("-------------------------------------------------")


# Open serial port
with serial.Serial('COM5', baudrate=57600, timeout=0.1) as ser:
    device = detect_device(comm=ser)
    device_type = device.module_type

    device.receiver.register_callback(CallbackPtccObjectID.PTCC_MONITOR, monitor_parameters_callback, user_data=device_type)
    device.receiver.register_callback(CallbackPtccObjectID.MODULE_LAB_M_MONITOR, monitor_parameters_callback, user_data=device_type)

    if device.module_type == ModuleType.LAB_M:
        device.write_msg_get_lab_m_monitor()
    elif device.module_type == ModuleType.NOMEM:
        device.write_msg_get_monitor()
    else:
        print(f"No monitor available for {device.module_type}")

    while True:
        byte = ser.read(1)
        if byte:
            if device.receiver.add_byte(byte[0]) == PtccMessageReceiveStatus.FINISHED:
                time.sleep(1)
                if device.module_type == ModuleType.LAB_M:
                    device.write_msg_get_lab_m_monitor()
                elif device.module_type == ModuleType.NOMEM:
                    device.write_msg_get_monitor()
