#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10  // SDA pin
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);  // Create MFRC522 instance

void setup() {
  Serial.begin(9600);
  SPI.begin();         // Init SPI bus
  rfid.PCD_Init();     // Init MFRC522
  Serial.println("Scan an RFID tag...");
}

void loop() {
  // Look for new cards
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  Serial.print("UID tag: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();
  
  // Halt PICC (Power it down)
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}