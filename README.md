👁️ Neural Tracking Interface: Advanced Eye & Hand Control System
Welcome to the Neural Tracking Interface! This project provides a revolutionary, hands-free way to interact with your computer using state-of-the-art computer vision. By leveraging advanced facial landmarking and hand-tracking algorithms, this system completely replaces your traditional mouse, allowing for ultra-precise cursor control, gesture-based scrolling, volume manipulation, and application launching.

Whether you are looking into accessibility tools, futuristic HCI (Human-Computer Interaction), or just want to feel like you're operating a sci-fi console, this repository has you covered.

🚀 Key Features
The repository currently includes two primary iterations of the tracking system, each packing a dense set of features:

🎯 Eye-Tracking Controls
Ultra-Accurate Cursor Control: Look anywhere on your screen to move the cursor. The v4.0 system uses enhanced calibration zones and exponential weighted averaging for full-screen coverage and accelerated, smooth movement.

Double Blink: Triggers a Left Click.

Right Eye Blink: Triggers a Right Click.

Triple Blink: Safely exits the program.

✋ Hand Gesture Controls
Dynamic Scrolling (v3.0): Move your open palm UP or DOWN to scroll web pages and documents naturally.

Volume Control (v3.0 & v4.0): Pinch your thumb and index finger together to adjust the master system volume.

Quick Launch Macros (v4.0): * Show 1 finger to instantly open YouTube.

Show 2 fingers to instantly open Google.

Show 3 fingers to safely exit the system.

🖥️ Sci-Fi User Interface
HUD Overlay: Features a high-performance visual overlay rendering a tessellated face mesh, glowing iris trackers, skeletal hand connections, and real-time data readouts (EAR values, gaze coordinates, and volume percentage).

🛠️ Tech Stack & Architecture
This project is built purely in Python and relies on robust machine learning and automation libraries:

Computer Vision: opencv-python for real-time video capture and HUD rendering.

Machine Learning: mediapipe (utilizing both the new Tasks API and legacy Solutions fallback) for detecting 468 face landmarks and 21 hand knuckles with high confidence.

OS Automation: pyautogui for translating spatial coordinates into seamless mouse movements, clicks, and scrolls.

Audio Control: pycaw and comtypes to interface directly with the Windows Core Audio API for precise master volume manipulation.

Math & Data Structuring: numpy for coordinate interpolation/smoothing, and collections.deque for memory-efficient frame history.

💻 Usage Guide
The repository contains distinct versions of the system. Run the version that best suits your needs:

1. Advanced Sci-Fi Tracker (v3.0)
Focuses on heavy visual feedback, a rich sci-fi mesh UI, and scroll mechanics.

Bash
python ADVANCECV.py
2. Revolutionary Tracking System (v4.0)
Focuses on ultra-precise, full-screen cursor control with advanced exponential smoothing, corrected camera flipping, and finger-counting macros for web browsing.

Bash
python "Revolutionary Tracking System.py"
System Notes & Tips:

Lighting: Ensure your face is well-lit for the most accurate EAR (Eye Aspect Ratio) calculations during blink detection.

Failsafe: The pyautogui failsafe is intentionally disabled (pyautogui.FAILSAFE = False) to prevent crashes during edge-of-screen tracking. Use the Triple Blink, 3-finger gesture, or the ESC key to exit safely.
