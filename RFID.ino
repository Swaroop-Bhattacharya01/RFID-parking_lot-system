#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SS_PIN 10
#define RST_PIN 9
#define SERVO_PIN 6
#define GREEN_LED 7
#define RED_LED 8

MFRC522 rfid(SS_PIN, RST_PIN);
Servo doorServo;

// Struct for person info
struct Person {
  byte uid[4];
  const char* name;
  const char* role;
};

// List of permitted users
Person permittedUsers[] = {
  {{0x13, 0xD3, 0x09, 0x27}, "TESTER", "white card"},
  {{0x89, 0xD3, 0x9D, 0x94}, "SWAROOP", "Admin"}
};
const int permittedCount = sizeof(permittedUsers) / sizeof(permittedUsers[0]);

// List of denied users
struct DeniedPerson {
  byte uid[4];
  const char* name;
};

DeniedPerson deniedUsers[] = {
  {{0x11, 0x16, 0xF5, 0x7B}, "UNAUTHORISED USER"}  // Blue card
};
const int deniedCount = sizeof(deniedUsers) / sizeof(deniedUsers[0]);

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  doorServo.attach(SERVO_PIN);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  doorServo.write(0); // Initial position
  Serial.println("System Ready - Scan RFID Card...");
}

bool compareUID(byte *uid1, byte *uid2) {
  for (byte i = 0; i < 4; i++) {
    if (uid1[i] != uid2[i]) return false;
  }
  return true;
}

void processSerialCommand() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command.startsWith("ADD_PERMITTED:")) {
      // Handle adding permitted user
      // Format: ADD_PERMITTED:UID:NAME:ROLE
      Serial.println("Received command to add permitted user");
    }
    else if (command.startsWith("ADD_DENIED:")) {
      // Handle adding denied user
      // Format: ADD_DENIED:UID:NAME
      Serial.println("Received command to add denied user");
    }
  }
}

void loop() {
  processSerialCommand();
  
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    return;
  }

  Serial.print("Card UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? "0" : "");
    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  bool isPermitted = false;
  const char* name = nullptr;
  const char* role = nullptr;

  for (int i = 0; i < permittedCount; i++) {
    if (compareUID(rfid.uid.uidByte, permittedUsers[i].uid)) {
      isPermitted = true;
      name = permittedUsers[i].name;
      role = permittedUsers[i].role;
      break;
    }
  }

  if (isPermitted) {
    Serial.println("Access Granted!");
    if (name && role) {
      Serial.print("Welcome, ");
      Serial.print(name);
      Serial.print(" (");
      Serial.print(role);
      Serial.println(")");
    }

    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    doorServo.write(90);  // Open Door
    delay(5000);
    doorServo.write(0);
    digitalWrite(GREEN_LED, LOW);
  } else {
    // Check if explicitly denied
    const char* deniedName = nullptr;
    for (int i = 0; i < deniedCount; i++) {
      if (compareUID(rfid.uid.uidByte, deniedUsers[i].uid)) {
        deniedName = deniedUsers[i].name;
        break;
      }
    }

    Serial.println("Access Denied!");
    if (deniedName) {
      Serial.print("WARNING: ");
      Serial.println(deniedName);
    }

    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    delay(2000);
    digitalWrite(RED_LED, LOW);
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
} 