# RFID Parking Lot System

Welcome to the RFID Parking Lot System project! 🚗🔑 This system uses RFID technology to manage access control for parking lots. The system allows authorized users to gain access to the parking lot by scanning their RFID cards.

## Overview

The RFID Parking Lot System is designed to:

- **Allow access control** to a parking lot based on RFID tags.
- **Grant/deny access** to authorized or unauthorized users.
- **Open and close gates** automatically using a servo motor.
- **Display user information** such as name and role for authorized users.

---

## Features

- **RFID Reader Integration:** Uses MFRC522 RFID module to read RFID tags.
- **Servo Motor Control:** Opens and closes parking gates with a servo.
- **User Management:** 
  - Permitted users' RFID tags are stored in a list.
  - Denied users' RFID tags can be set for access denial.
- **LED Indicators:** Green and red LEDs to indicate access granted or denied.
- **User Identification:** Displays the name and role of authorized users upon scanning.

---

## Hardware Requirements

To set up the system, you will need the following components:

- **Arduino Board** (Uno, Mega, etc.)
- **MFRC522 RFID Reader**
- **Servo Motor**
- **LEDs** (Green, Red)
- **Jumper Wires**
- **Breadboard** (optional for prototyping)
- **Power Supply for Arduino**

---

## Software Requirements

- **Arduino IDE:** Used to program the Arduino board.
- **Arduino Libraries:**
  - `SPI.h`
  - `MFRC522.h`
  - `Servo.h`

---

## Installation

1. **Clone the repository:**
   Clone this repository to your local machine using:

   ```bash
   git clone https://github.com/Swaroop-Bhattacharya01/RFID-parking_lot-system.git
Install necessary libraries: Make sure you have the following libraries installed in the Arduino IDE:

MFRC522: Used to interface with the RFID reader.

Servo: For controlling the servo motor.

Upload the code: Open the RFID.ino file in the Arduino IDE and upload it to your Arduino board.

Connect the components:

RFID Reader (MFRC522) Pinout:
Connect the RFID reader to the Arduino using the correct pins (SDA, SCK, MOSI, MISO, RST).

Servo Motor Pinout:
Connect the servo to one of the PWM pins on the Arduino (e.g., pin 6).

LEDs:
Connect green and red LEDs to the specified pins (e.g., pin 7 and pin 8).

How It Works
RFID Scanning:
The system continuously scans for RFID cards. When a card is detected, its UID is read and compared against the list of authorized UIDs.

Access Grant/Denial:

If the UID matches an authorized user, access is granted by opening the parking gate (servo motor moves).

If the UID is not authorized, access is denied, and the red LED lights up.

User Identification:
Authorized users' names and roles are displayed on the serial monitor when access is granted.

Example Output
Access Granted:
Card UID: 13 D3 09 27
Access Granted!
Welcome, Swaroop (Admin)
Access Denied:
Card UID: 11 16 F5 7B
Access Denied!
WARNING: UNAUTHORIZED USER
Contributing
Feel free to fork this project, make changes, and create a pull request. Contributions are welcome to improve the system.

License
This project is open-source and available under the MIT License.

Contact
If you have any questions or suggestions, feel free to reach out to me via GitHub 

GitHub: Swaroop-Bhattacharya01


Acknowledgments
MFRC522 Library: Used for interfacing with the RFID reader.

Servo Library: Used for controlling the servo motor.

Arduino IDE: Platform for coding and uploading to Arduino.


This README will give anyone who visits your GitHub repository a solid understanding of what your project is about, how to set it up, and how it works. You can update the email address with your actual one, or you can leave it out if you prefer not to share it.
