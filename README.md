# OculusDobotControl

## Overview

This project facilitates the integration of a Dobot V1 robotic arm with an Oculus Quest 1 headset using the Oculus Reader repository from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader). It enables control over the robotic arm's coordinates and the operation of the suction pump.

The system is specifically designed for the original Dobot robotic arm model, which utilizes the beta protocol. This protocol has since been updated in newer models such as the Dobot Magician, which simplifies operation through the use of the `pydobot` library available at https://pypi.org/project/pydobot/. While this code demonstrates basic serial command control, it can be adapted to utilize the more user-friendly `pydobot` library commands.

To identify the appropriate port for the Dobot, execute the command `dir /dev/tty*` with and without the Dobot connected, and observe which port appears. Replace "/dev/ttyACM0" in the code with the correct port identifier.

## Instructions

1. **Install Git Large File Storage (LFS)**: Follow the instructions provided in the RAIL Berkeley repository (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader). This step is critical as failing to install Git LFS will prevent the required APK from being cloned.

2. **Clone the Oculus Reader Repository**: Clone the repository from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader).

3. **Setup Oculus and ADB**:
   - Install Android Debug Bridge (ADB) as per the repository instructions.
   - Create a developer account on Meta’s website.
   - Set the Oculus headset to Developer Mode and enable connectivity with your computer.

4. **Add and Run the Script**:
   - Place the `novoreader.py` file from this repository into the `oculus_reader/oculus_reader` directory of the Oculus Reader repository and execute it. Alternatively, you may run the original `reader.py` file to use the Oculus headset without the added Dobot control functionality.

5. **Verify and Configure ADB**:
   - The script will check for ADB installation, initiate a daemon if necessary, confirm Oculus responsiveness, and install an APK on the Oculus headset to facilitate command reading from the headset and controllers. The RAIL Oculus Teleoperation program should appear on the Oculus (see screenshot).

6. **Prevent Oculus Headset Sleep Mode**:
   - To maintain continuous command reception, avoid using tape on the internal Oculus sensor, as it may cause malfunctions. Instead, install Sidequest on your computer, navigate to "Device Settings and Tools," and select "Disable proximity sensor" to reliably prevent the headset from going to sleep (refer to the attached picture).

7. **Control the Dobot**:
   - Use the left controller's joystick to adjust the Dobot's X and Y axes, the right controller's joystick for the Z axis and rotation, and the left controller's trigger button to control the suction pump.

## Future Enhancements

1. **Enhanced Tracking**:
   - The current implementation does not utilize the `last_transforms` data provided by the repository, which means head and controller tracking data are not utilized. Incorporating these features could enable control of the Dobot through head movements.

2. **Improved Calculation Methods**:
   - The current method for calculating X, Y, Z, and rotation values is rudimentary, simply modifying the robot's initial position based on the joystick inputs. More sophisticated methods could be developed for better precision and control.

3. **Reinforcement Learning**:
   - Implementing reinforcement learning could be beneficial for storing movement patterns and training models to replicate complex tasks, such as picking up objects and placing them in designated locations.
