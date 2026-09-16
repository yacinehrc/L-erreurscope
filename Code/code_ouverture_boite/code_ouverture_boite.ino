#include <SPI.h>            
#include <MFRC522.h>        
#include <LiquidCrystal.h>  
#include <Servo.h>          

// --- Définition des broches ---
#define RST_PIN 9           
#define SS_PIN 10           
#define LED_PIN 2           
#define SERVO_PIN A0        

// --- Initialisation des composants ---
MFRC522 rfid(SS_PIN, RST_PIN);          // Création de l'objet RFID
LiquidCrystal lcd(8, 7, 6, 5, 4, 3);    // Création de l'objet LCD avec ses broches (RS, EN, D4, D5, D6, D7)
Servo monServo;                         // Création de l'objet servomoteur

void setup() {
  SPI.begin();       // Initialisation du bus SPI
  rfid.PCD_Init();   // Initialisation du lecteur RFID
  
  pinMode(LED_PIN, OUTPUT); // Configuration de la broche LED en sortie
  
  // Initialisation du servomoteur (fermé par défaut)
  monServo.attach(SERVO_PIN);
  monServo.write(0); // Met le servo à 0°
  delay(300);        // Attente pour laisser le moteur se positionner
  monServo.detach(); // Coupe le signal pour éviter qu'il ne tremble
  
  // Initialisation de l'écran LCD
  lcd.begin(16, 2);  // Définit l'écran comme un modèle 16 colonnes x 2 lignes
  affichageParDefaut();
}

void loop() {
  // Vérifie si un NOUVEAU badge est physiquement présent ET si on peut lire son ID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    
    // --- 1. OUVERTURE ---
    lcd.clear();
    lcd.print("Acces autorise !");
    digitalWrite(LED_PIN, HIGH); // Allume la LED
    
    monServo.attach(SERVO_PIN);  // Réactive le servomoteur
    monServo.write(140);         // Ouvre à 140°
    
    rfid.PICC_HaltA(); // Met le badge en pause pour ne pas le lire en boucle infinie
    
    delay(300);          // Laisse le temps au servo de s'ouvrir
    monServo.detach();   // Coupe le signal pour éviter les vibrations et conflits SPI
    
    // --- 2. MAINTIEN (Tant que le badge est là) ---
    int echecsLecture = 0; // Compteur pour vérifier si le badge a disparu
    
    while (echecsLecture < 3) { // Tolérance : 3 échecs consécutifs = badge retiré
      delay(300); 
      
      byte bufferATQA[2];
      byte bufferSize = sizeof(bufferATQA);
      
      // PICC_WakeupA envoie un "ping" au badge endormi. 
      // S'il répond (STATUS_OK), c'est qu'il est toujours sur le lecteur.
      if (rfid.PICC_WakeupA(bufferATQA, &bufferSize) == MFRC522::STATUS_OK) {
        rfid.PICC_HaltA(); // Le badge est bien là, on le rendort
        echecsLecture = 0; // On réinitialise le compteur d'erreurs
      } else {
        echecsLecture++;   // Le badge ne répond pas, on incrémente l'erreur
      }
    }
    
    // --- 3. FERMETURE (Le badge a été retiré) ---
    monServo.attach(SERVO_PIN);  // Réactive le servomoteur
    digitalWrite(LED_PIN, LOW);  // Éteint la LED
    monServo.write(0);           // Referme à 0°
    delay(300);                  // Laisse le temps de se fermer
    monServo.detach();           // Coupe le signal
    
    rfid.PCD_Init(); // Réinitialise complètement le lecteur RFID pour le prochain badge
    
    affichageParDefaut(); // Remet le texte de base sur l'écran
  }
}

// Fonction personnalisée pour simplifier l'affichage de base
void affichageParDefaut() {
  lcd.clear();
  lcd.print("Veuillez entrer");
  lcd.setCursor(0, 1); // Passe à la 2ème ligne (colonne 0, ligne 1)
  lcd.print("code secret");
}