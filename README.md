# oculusdobotcontrol
This project integrates a Dobot V1 with an Oculus Quest 1 using the Oculus Reader repo from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader), allowing the control of its coordinates and the opening and closing of the suction pump

It is designed to work on the very first Dobot robotic arm model which used the beta protocol. This protocol was later changed and is used in newer models such as the Magician. These are much simpler to operate, as all you have to do is to use the pydobot library found at https://pypi.org/project/pydobot/. This code shows how to import it, but uses regular serial commands to control the dobot: you can edit it to simply use the commands from the pydobot library (much easier!)

You will need to find what port is the Dobot using: a simple way is just typing "dir /dev/tty*" with and without the dobot connected and seeing which port shows up. Then replace that text for the "/dev/ttyACM0" found in this file

**INSTRUCTIONS**

1 - Install the git-lfs tool as instructed at the repo RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader. This is CRITICAL, as if otherwise when you clone the repo it will not bring a required APK

2 - Clone the Oculus Reader repo from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader

3 - Follow the instruction of the repo in terms of installing ADB, creating a development organization at Meta's website, setting up the oculus to developer mode, and allowing it to connect to your computer

3 - Add the file novoreader.py of this repo to the oculus_reader/oculus_reader folder of the Oculus Reader repo and run it. You can also run the original file reader.py to just use the Oculus

4 - This file will detect if ADB is installed and running (otherwise will start a daemon), if the oculus is responding, and will install an APK in the oculus to read the commands from the oculus headset and handsets. You will see in the Oculus the RAIL Oculus Teleoperation program running (see printscreen)

5 - You will notice that unless you keep the headset on, it will stop receive commands. To prevent it, do NOT use the technique of simply putting a piece of tape on the internal oculus sensor, as it just confuses it. Instead, install Sidequest in your computer and go to "Device Settings and Tools", and click on "Disable proximity sensor". This is the most foolproof method (others such as one that uses the oculus software do not stay put). See the attached picture

6 - You can use now the left handset's joystick to control the X and Y axis of the dobot and the right handset's joystick to control the Z and rotation axis, and the left handset's trigger button to open and close the suction pump


**TO DO**<br>
1 - This file does not use the last_transforms read by the repo, only the buttons. That means that head and controller tracking data are simply ignored. It'd be interesting to control the dobot by, for example, moving the head

2 - The x,y,z,r calculations are really simple: the code simply obtains the initial position of the robot and adds or substracts the x,y,z,r variables accordingly. 

3 - Reinforcement learning: it'd be useful if the movements were stored in order to train a model to later replicate it in, for example, picking up an orange and dropping it in a box
