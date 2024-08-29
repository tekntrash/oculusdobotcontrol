# oculusdobotcontrol
This project integrates a Dobot V1 with an Oculus Quest 1 using the Oculus Reader repo from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader), allowing the control of its coordinates and the opening and closing of the suction pump

It is designed to work on the very first Dobot robotic arm model which used the beta protocol. This protocol was later changed and is used in newer models such as the Magician. Theseare much simpler to operate, as all you have to do is to use the pydobot library found at https://pypi.org/project/pydobot/. This code shows how to import it, but uses regular serial commands to control the dobot

You will need to find what port is the Dobot using: a simple way is just typing "dir /dev/tty*" with and without the dobot connected and seeing which port shows up. Then replace that text for the "/dev/ttyACM0" found in this file

INSTRUCTIONS
1 - Install the git-lfs tool as instructed at the repo RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader. This is CRITICAL, as if otherwise when you clone the repo it will not bring a required APK
2 - Clone the Oculus Reader repo from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader
3 - Follow the instruction of the repo in terms of installing ADB, creating a development organization at Meta's website, setting up the oculus to developer mode, and allowing it to connect to your computer
3 - Add the file novoreader.py of this repo to the oculus_reader/oculus_reader folder of the Oculus Reader repo and run it
4 - This file will detect if ADB is installed and running (otherwise will start a daemon), if the oculus is responding, and will install an APK in the oculus to read the commands from the oculus VR and handsets 
