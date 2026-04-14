<<<<<<< HEAD
# IMAV Challenge - Drone Vision System

This repository contains the software and vision systems developed for the IMAV Configuration Challenge. The project focuses on creating a comprehensive vision system for autonomous drones, utilizing state-of-the-art computer vision techniques and machine learning algorithms.

### Authors
Drone Ops Team
=======
# IMAV Challenge - Autonomous Drone Vision System

Autonomous control system for DJI Tello drones based on ArUco marker detection and PID control. 

## Project Overview

This repository contains the implementation of a vision and autonomous navigation system for unmanned aerial vehicles. The system utilizes:

- ArUco marker detection to identify reference points
- PID control for maintaining stability and precision during navigation
- Real-time video processing using OpenCV
- DJI Tello library for drone communication and control

## Project Objectives

- Navigate autonomously using visual markers as reference points
- Maintain stability through feedback control systems (PID)
- Detect and navigate through racing gates (work in progress)

## Project Structure

```
IMAV-Challenge/
├── README.md                    Documentation file
├── src/                         Source code
│   ├── MissionControl.py        Primary drone control system
│   ├── Control_Aruco.py         ArUco marker controller
│   ├── coordinatesAruco.py      ArUco marker detection module
│   └── __pycache__/
└── tests/                       Unit and integration tests
    ├── ArucoTest.py             ArUco detection tests
    ├── camera.py                Camera utilities
    ├── CheckVel.py              Velocity verification
    ├── telloCamera.py           Tello camera interface
    └── vision.py                Vision system tests
```

## Core Components

### MissionControl.py

Primary control module responsible for:
- Establishing connection with the Tello drone
- Initializing video stream acquisition
- Managing flight cycle (takeoff, navigation, landing)
- Monitoring battery status and system health

### Control_Aruco.py

Controller module that implements:
- ArUco marker detection and tracking
- PID control algorithm for autonomous navigation
- Control signal transmission to the drone

**Configurable PID Parameters:**
```python
Kp = 0.20  # Proportional gain
Ki = 0.10  # Integral gain
Kd = 0.10  # Derivative gain
```

### coordinatesAruco.py

Detection module providing:
- Frame conversion to grayscale for optimal detection
- Real-time ArUco marker identification
- Visual overlay of detection centers and error vectors
- Error calculation relative to frame center

## Requirements

- Python 3.7 or higher
- OpenCV (cv2)
- djitellopy
- numpy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/IMAV-Challenge.git
cd IMAV-Challenge
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Alternatively, install packages manually:
```bash
pip install opencv-python djitellopy numpy
```

## Usage

### Primary Execution

```bash
cd src
python3 MissionControl.py
```

The system will:
1. Connect to the Tello drone
2. Display current battery level
3. Execute automatic takeoff sequence
4. Initiate autonomous navigation using ArUco markers
5. Execute landing sequence upon completion or when interrupted with Ctrl+C


### ArUco Dictionary Selection
## License

This project is licensed under [Specify License - MIT, Apache, etc.]

## Contact

For questions or suggestions regarding this project, please open an issue on the repository.

---

## Safety Notice

This system controls physical equipment. Ensure the following:
- Flight area is clear of obstacles and personnel
- Drone has sufficient battery charge
- Operation is conducted in controlled indoor environments
- All local drone regulations and airspace restrictions are observed

Modify in `src/Control_Aruco.py`:
```python
self.aruco = coordinatesAruco.ArucoDetector(cv2.aruco.DICT_6X6_50)
# Available options: DICT_4X4_50, DICT_5X5_100, DICT_6X6_250, etc.
```

## Troubleshooting

### Drone Connection Failure
- Verify that the drone is powered on and within WiFi range
- Manually connect to the drone's WiFi network before executing the program

### Failed Marker Detection
- Ensure adequate lighting conditions
- Verify that markers are visible within the camera frame
- Adjust ArUco dictionary to match markers in use

### Unstable Control Behavior
- Gradually adjust PID parameters
- Increase Kp for enhanced responsiveness
- Increase Kd for improved stability

## Work in Progress

- [ ] Racing gate detection and autonomous navigation with YOLO
- [ ] PID parameter optimization

## Authors

Drone Ops Team
>>>>>>> dev
