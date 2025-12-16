/*
 * RFID Reader for Attendance System
 * Uses MFRC522 Library
 * 
 * Connections:
 * SDA (SS) -> Pin 10
 * SCK      -> Pin 13
 * MOSI     -> Pin 11
 * MISO     -> Pin 12
 * RST      -> Pin 9
 * GND      -> GND
 * 3.3V     -> 3.3V
 */

#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

void setup() { 
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522 

  Serial.println("RFID Reader Ready");
}

void loop() {
  // Reset the loop if no new card present on the sensor/reader. This saves the entire process when idle.
  if ( ! rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if ( ! rfid.PICC_ReadCardSerial())
    return;

  // print UID of the card in the serial monitor
  Serial.print("UID:");
  printHex(rfid.uid.uidByte, rfid.uid.size);
  Serial.println();

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
  
  delay(1000); // Wait a bit before reading again to avoid spamming
}

/**
 * Helper routine to dump a byte array as hex values to Serial. 
 */
void printHex(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? "0" : "");
    Serial.print(buffer[i], HEX);
  }
}
