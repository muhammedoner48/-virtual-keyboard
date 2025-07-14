# -virtual-keyboard
This project enables users to type on a virtual keyboard by tracking hand movements through a webcam. It detects finger positions using MediaPipe and simulates keyboard inputs with PyAutoGUI. Additionally, key presses play sound effects using Pygame.

Features
* Single-hand virtual keyboard control
* Key press sound effects
* Continuous backspace deletion by holding the backspace key
* Shift key support for uppercase letters
* Full keyboard functionality including Enter, Space, and Backspace keys
* Simple on-screen text box displaying typed text

Requirements
* Python 3.x
* OpenCV
* MediaPipe
* PyAutoGUI
* Pygame
* Numpy

Installation

"pip install opencv-python mediapipe pyautogui pygame numpy"

Usage
1. Clone or download the project files.
2. Make sure the .wav sound files for each key are present in the sounds folder.
3. Run the program with python virtual_keyboard.py.
4. When the webcam opens, use your hand to press the keys by moving your fingers in front of the camera.
5. Press the ESC key to exit the program.

