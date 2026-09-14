#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>
#include <Servo.h>

#define RST_PIN 9
#define SS_PIN 10
#define LED_PIN 2
#define SERVO_PIN A0 

MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal lcd(8, 7, 6, 5, 4, 3); 
Servo monServo;

void setup() {
  SPI.begin();
  rfid.PCD_Init();
  
  pinMode(LED_PIN, OUTPUT);
  
  monServo.attach(SERVO_PIN);
  monServo.write(0); 
  
  lcd.begin(16, 2);
  affichageParDefaut();
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    lcd.clear();
    lcd.print("Acces autorise !");
    digitalWrite(LED_PIN, HIGH);
    monServo.write(140); 
    
    delay(3000); 
    
    digitalWrite(LED_PIN, LOW);
    monServo.write(0); 
    affichageParDefaut();
    
    rfid.PICC_HaltA();
  }
}

void affichageParDefaut() {
  lcd.clear();
  lcd.print("Veuillez entrer");
  lcd.setCursor(0, 1);
  lcd.print("code secret");
}