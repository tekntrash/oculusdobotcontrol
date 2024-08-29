# oculusdobotcontrol
This project integrates a Dobot V1 with an Oculus Quest 1 using the Oculus Reader repo from RAIL Berkeley (https://github.com/rail-berkeley/oculus_reader/tree/main/oculus_reader), allowing the control of its coordinates and the opening and closing of the suction pump
It is designed to work on the very first Dobot robotic arm model which used the 
You will need to find what port isthe Dobot connected in your computer: a simple way is just typing "dir /dev/tty*" with and without the dobot connected and seeing which port shows up. Then replace that text for the "/dev/ttyACM0" found in this file
