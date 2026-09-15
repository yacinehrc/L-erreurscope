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
  monServo.write(0); // Position fermée initiale
  delay(300);
  monServo.detach(); // On le détache dès le début pour être tranquille
  
  lcd.begin(16, 2);
  affichageParDefaut();
}

void loop() {
  // Si un badge est détecté
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    // 1. Ouvre la boîte à 140°
    lcd.clear();
    lcd.print("Acces autorise !");
    digitalWrite(LED_PIN, HIGH);
    
    monServo.attach(SERVO_PIN); // <-- CORRECTION : ON RÉACTIVE LE MOTEUR ICI
    monServo.write(140); 
    
    rfid.PICC_HaltA(); // On met le badge en pause
    
    delay(300); // Laisse le temps au servo d'atteindre sa position avant de couper le signal
    monServo.detach(); // Coupe le PWM : plus de conflit avec le SPI, plus de vibrations
    
    // 2. Boucle de maintien : vérifie si le badge est toujours là
    int echecsLecture = 0;
    while (echecsLecture < 3) { // 3 échecs consécutifs = badge retiré
      delay(300); // Vérification moins fréquente
      
      byte bufferATQA[2];
      byte bufferSize = sizeof(bufferATQA);
      
      // PICC_WakeupA force le badge à répondre s'il est encore sur le lecteur
      if (rfid.PICC_WakeupA(bufferATQA, &bufferSize) == MFRC522::STATUS_OK) {
        rfid.PICC_HaltA(); // Il est là, on le remet en pause
        echecsLecture = 0; // On remet le compteur d'erreurs à 0
      } else {
        echecsLecture++; // Le badge ne répond pas
      }
    }
    
    // 3. Le badge a été retiré, on réactive le servo et on referme à 0°
    monServo.attach(SERVO_PIN); // Réactive le contrôle PWM avant de bouger
    digitalWrite(LED_PIN, LOW);
    monServo.write(0); 
    delay(300); // Laisse le temps d'atteindre la position fermée
    monServo.detach(); // Coupe à nouveau le signal une fois fermé
    
    // On réinitialise le lecteur RFID au cas où il serait resté endormi
    rfid.PCD_Init(); 
    
    affichageParDefaut();
  }
}

void affichageParDefaut() {
  lcd.clear();
  lcd.print("Veuillez entrer");
  lcd.setCursor(0, 1);
  lcd.print("code secret");
}
