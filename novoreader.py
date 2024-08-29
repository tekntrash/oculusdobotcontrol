#import DobotDllType as dType
import struct
import serial.tools.list_ports
import serial
from datetime import datetime
import time
import os
import sys

os.system('stty -F /dev/ttyACM0 hupcl')
port_name = '/dev/ttyACM0'
baud_rate = 9600
available_ports = [port.device for port in serial.tools.list_ports.comports()]
if port_name in available_ports:
  port = serial.Serial(port_name, baud_rate)
  port.dtr = False
  time.sleep(0.5)  # Give the device time to reset
  port.dtr = True
  expected_packet_size = 42
  def read_exactly(num_bytes):
    # Continuously read until we have exactly num_bytes
    data = port.read(num_bytes)
    while len(data) < num_bytes:
        data += port.read(num_bytes - len(data))
    return data
  try:
    while True:
        if port.in_waiting >= expected_packet_size:
            packet = read_exactly(expected_packet_size)
            print(f"Received packet: {packet}")
            response = packet
            if len(response) == 42:
              print ("Response length=",len(response)) 
              if response[0] == 0xA5 and response[-1] == 0x5A:
                data_floats = struct.unpack('<10f', response[1:41])
                print("Initial Pose:")
                print(f"X: {data_floats[0]} mm")
                print(f"Y: {data_floats[1]} mm")
                print(f"Z: {data_floats[2]} mm")
                print(f"Rotation: {data_floats[3]} degrees")
                print(f"Base Angle: {data_floats[4]} degrees")
                print(f"Long Arm Angle: {data_floats[5]} degrees")
                print(f"Short Arm Angle: {data_floats[6]} degrees")
                print(f"Paw Arm Angle: {data_floats[7]} degrees")
                print(f"Is Grabbing: {data_floats[8]}")
                print(f"Gripper Angle: {data_floats[9]} degrees")
                initialx=data_floats[0]
                initialy=data_floats[1]
                initialz=data_floats[2]
                break
              else:
                print("Invalid response packet. Header or tail bytes are incorrect.")
            else:
              print(f"Unexpected response length: {len(response)} bytes. Expected 42 bytes.")
  except KeyboardInterrupt:
    print("Interrupted by user")

  while True:
    if initialx>179.983:
      x=initialx-179.983
    if initialx<179.983:
      x=179.983-initialx
    print ("x=",x) 
    #x=179.983
    y=-4.98535
    z=7.5321
    
    
    data = []
    while len(data) < 4:
      print ("waiting for data=",len(data))
      byte = port.read(1)
      if len(byte):
        data.append(byte[0])
    value = struct.unpack('<f', bytes(data))[0]
    port.write(bytes([0xa5]))  # Encode to bytes
    port.write(struct.pack('<f', 6.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', x))
    port.write(struct.pack('<f', y))
    port.write(struct.pack('<f', z))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 1.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 0.0))
    port.write(bytes([0x5a]))  # Encode to bytes
    
    print ("==================================================")

    x=-179.983
    y=42.5147
    z=7.5321
    data = []
    while len(data) < 4:
      print ("waiting for data=",len(data))
      byte = port.read(1)
      if len(byte):
        data.append(byte[0])
    value = struct.unpack('<f', bytes(data))[0]
    port.write(bytes([0xa5]))  # Encode to bytes
    port.write(struct.pack('<f', 6.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', x))
    port.write(struct.pack('<f', y))
    port.write(struct.pack('<f', z))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 1.0))
    port.write(struct.pack('<f', 0.0))
    port.write(struct.pack('<f', 0.0))
    port.write(bytes([0x5a]))  # Encode to bytes
    
    
    port.close
    #time.sleep(0.3)
else:
    print(f"Robot not found: port {port_name} does not exist or is not connected.")
    exit()
