import multiprocessing as mp
import struct
import xml.etree.ElementTree as ET
import serial.tools.list_ports
import serial
from datetime import datetime
from oculus_reader.FPS_counter import FPSCounter
from oculus_reader.buttons_parser import parse_buttons
import numpy as np
import threading
import time
import os
from ppadb.client import Client as AdbClient
import sys

def eprint(*args, **kwargs):
    RED = "\033[1;31m"  
    sys.stderr.write(RED)
    print(*args, file=sys.stderr, **kwargs)
    RESET = "\033[0;0m"
    sys.stderr.write(RESET)

class OculusReader:
    def __init__(self,
            ip_address=None,
            port = 5555,
            APK_name='com.rail.oculus.teleop',
            print_FPS=False,
            run=True
        ):
        self.running = False
        self.last_transforms = {}
        self.last_buttons = {}
        self._lock = threading.Lock()
        self.tag = 'wE9ryARX'

        self.ip_address = ip_address
        self.port = port
        self.APK_name = APK_name
        self.print_FPS = print_FPS
        if self.print_FPS:
            self.fps_counter = FPSCounter()

        self.device = self.get_device()
        self.install(verbose=False)
        if run:
            self.run()

    def __del__(self):
        self.stop()

    def run(self):
        self.running = True
        self.device.shell('am start -n "com.rail.oculus.teleop/com.rail.oculus.teleop.MainActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER')
        self.thread = threading.Thread(target=self.device.shell, args=("logcat -T 0", self.read_logcat_by_line))
        self.thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def get_network_device(self, client, retry=0):
        try:
            client.remote_connect(self.ip_address, self.port)
        except RuntimeError:
            os.system('adb devices')
            client.remote_connect(self.ip_address, self.port)
        device = client.device(self.ip_address + ':' + str(self.port))

        if device is None:
            if retry==1:
                os.system('adb tcpip ' + str(self.port))
            if retry==2:
                eprint('Make sure that device is running and is available at the IP address specified as the OculusReader argument `ip_address`.')
                eprint('Currently provided IP address:', self.ip_address)
                eprint('Run `adb shell ip route` to verify the IP address.')
                exit(1)
            else:
                self.get_device(client=client, retry=retry+1)
        return device

    def get_usb_device(self, client):
        try:
            devices = client.devices()
        except RuntimeError:
            os.system('adb devices')
            devices = client.devices()
        for device in devices:
            if device.serial.count('.') < 3:
                return device
        eprint('Device not found. Make sure that device is running and is connected over USB')
        eprint('Run `adb devices` to verify that the device is visible.')
        exit(1)

    def get_device(self):
        # Default is "127.0.0.1" and 5037
        client = AdbClient(host="127.0.0.1", port=5037)
        if self.ip_address is not None:
            return self.get_network_device(client)
        else:
            return self.get_usb_device(client)

    def install(self, APK_path=None, verbose=True, reinstall=False):
        try:
            installed = self.device.is_installed(self.APK_name)
            if not installed or reinstall:
                if APK_path is None:
                    APK_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'APK', 'teleop-debug.apk')
                success = self.device.install(APK_path, test=True, reinstall=reinstall)
                installed = self.device.is_installed(self.APK_name)
                if installed and success:
                    print('APK installed successfully.')
                else:
                    eprint('APK install failed.')
            elif verbose:
                print('APK is already installed.')
        except RuntimeError:
            eprint('Device is visible but could not be accessed.')
            eprint('Run `adb devices` to verify that the device is visible and accessible.')
            eprint('If you see "no permissions" next to the device serial, please put on the Oculus Quest and allow the access.')
            exit(1)

    def uninstall(self, verbose=True):
        try:
            installed = self.device.is_installed(self.APK_name)
            if installed:
                success = self.device.uninstall(self.APK_name)
                installed = self.device.is_installed(self.APK_name)
                if not installed and success:
                    print('APK uninstall finished.')
                    print('Please verify if the app disappeared from the list as described in "UNINSTALL.md".')
                    print('For the resolution of this issue, please follow https://github.com/Swind/pure-python-adb/issues/71.')
                else:
                    eprint('APK uninstall failed')
            elif verbose:
                print('APK is not installed.')
        except RuntimeError:
            eprint('Device is visible but could not be accessed.')
            eprint('Run `adb devices` to verify that the device is visible and accessible.')
            eprint('If you see "no permissions" next to the device serial, please put on the Oculus Quest and allow the access.')
            exit(1)

    @staticmethod
    def process_data(string):
        try:
            transforms_string, buttons_string = string.split('&')
        except ValueError:
            return None, None
        split_transform_strings = transforms_string.split('|')
        transforms = {}
        for pair_string in split_transform_strings:
            transform = np.empty((4,4))
            pair = pair_string.split(':')
            if len(pair) != 2:
                continue
            left_right_char = pair[0] # is r or l
            transform_string = pair[1]
            values = transform_string.split(' ')
            c = 0
            r = 0
            count = 0
            for value in values:
                if not value:
                    continue
                transform[r][c] = float(value)
                c += 1
                if c >= 4:
                    c = 0
                    r += 1
                count += 1
            if count == 16:
                transforms[left_right_char] = transform
        buttons = parse_buttons(buttons_string)
        return transforms, buttons

    def extract_data(self, line):
        output = ''
        if self.tag in line:
            try:
                output += line.split(self.tag + ': ')[1]
            except ValueError:
                pass
        return output

    def get_transformations_and_buttons(self):
        with self._lock:
            #return self.last_transforms, self.last_buttons
            return self.last_buttons

    def read_logcat_by_line(self, connection):
        file_obj = connection.socket.makefile()
        while self.running:
            try:
                line = file_obj.readline().strip()
                data = self.extract_data(line)
                if data:
                    transforms, buttons = OculusReader.process_data(data)
                    with self._lock:
                        self.last_transforms, self.last_buttons = transforms, buttons
                    if self.print_FPS:
                        self.fps_counter.getAndPrintFPS()
            except UnicodeDecodeError:
                pass
        file_obj.close()
        connection.close()

def init():
  manager = mp.Manager()
  shared_dict = manager.dict()
  shared_dict['keys'] = "" 
  
  oculus_process = mp.Process(target=oculus, args=(shared_dict,))
  robot_process = mp.Process(target=robot, args=(shared_dict,))

  oculus_process.start()
  robot_process.start()
  
  oculus_process.join()
  robot_process.join()


def robot(shared_dict):
    print ("Starting robot process")
    port_name = '/dev/ttyACM0'
    baud_rate = 9600
    
    os.system('stty -F /dev/ttyACM0 hupcl')
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    if port_name in available_ports:
      port = serial.Serial(port_name, baud_rate)
      print ("Resetting serial port ",port)
      port.dtr = False
      time.sleep(0.5)  # Give the device time to reset
      port.dtr = True
    else:
      print(f"Robot not found: port {port_name} does not exist or is not connected.")
      exit()

    expected_packet_size = 42
    def read_exactly(num_bytes):
        data = port.read(num_bytes)
        while len(data) < num_bytes:
          data += port.read(num_bytes - len(data))
        return data
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
                x=data_floats[0]
                y=data_floats[1]
                z=data_floats[2]
                r=data_floats[3]
                is_grab=0.0
                port.close
                break
              else:
                print("Invalid response packet. Header or tail bytes are incorrect.")
            else:
              print(f"Unexpected response length: {len(response)} bytes. Expected 42 bytes.")
  
    while True:
      move=0
      if str(shared_dict['keys'])=="{}":
        print ("NOT RECEIVING DATA: PUT YOUR HEADSET ON")
      else:
        for key, value in shared_dict['keys'].items():
          print(f"Key: {key}, Value: {value}")
          if key=="leftJS":
            if value:
                x0, y0 = value
                x=x+x0
                y=y+x0
                x = round(x, 2)
                y = round(y, 2)
                print(f"X: {x}")
                print(f"Y: {y}")
                move=1
                
          if key=="rightJS":
            if value:
                z0, r0 = value
                z=z+z0
                r=r+r0
                z = round(z, 2)
                r = round(r, 2)
                print(f"z: {z}")
                print(f"r: {r}")
                move=1
                
          if key=="LG":
            if value:
              if is_grab==1.0 :
                is_grab=0.0
                move=1
              elif is_grab==0.0:
                is_grab=1.0
                move=1
                
          if move==1:
            port = serial.Serial(port_name, baud_rate)
            data = []
            while len(data) < 4:
              #print ("waiting for data=",len(data))
              byte = port.read(1)
              if len(byte):
                data.append(byte[0])
            dados = struct.unpack('<f', bytes(data))[0]
            #print("Data to send: ",dados)
            port.write(bytes([0xa5]))  # Encode to bytes
            port.write(struct.pack('<f', 3.0))
            port.write(struct.pack('<f', 0.0))
            port.write(struct.pack('<f', x))
            port.write(struct.pack('<f', y))
            port.write(struct.pack('<f', z))
            port.write(struct.pack('<f', 0.0))
            port.write(struct.pack('<f', is_grab))
            port.write(struct.pack('<f', 1.0))
            port.write(struct.pack('<f', 0.0))
            port.write(struct.pack('<f', 0.0))
            port.write(bytes([0x5a]))  # Encode to bytes
            port.close
            move=0

def oculus(shared_dict):
  print ("Starting oculus process")
  oculus_reader = OculusReader()
  while True:
    time.sleep(0.3)
    shared_dict['keys']=oculus_reader.get_transformations_and_buttons()
    #for key, value in shared_dict['keys'].items():
    #  print(f"Key: {key}, Value: ={value}=")


if __name__ == "__main__":
  mp.set_start_method('spawn')
  current_method = mp.get_start_method()
  print(f"Current start method: {current_method}")
  init()
