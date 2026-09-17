# L'ERREURSCOPE
 
![erreurscope_img](Images/erreurscope_img.jpg)
 
> Un coffret en bois interactif conçu pendant le Workshop 2026 B2 de l'EPSI Lille, inspiré de l'univers de Rick & Morty : une boîte verrouillée qui ne s'ouvre qu'en posant la « bonne » mouche imprimée en 3D (tag RFID dissimulé) sur le lecteur. Une fois ouverte, l'utilisateur énonce son prénom et sa date de naissance dans un microphone, et la machine lui répond par un horoscope volontairement acide — le but assumé étant de démarrer la journée avec un peu moins d'estime de soi.
 
---
 
## Sommaire
 
- [Concept et objectifs](#concept-et-objectifs)
- [Parcours utilisateur](#parcours-utilisateur)
- [Architecture matérielle](#architecture-matérielle)
- [Brochage et câblage](#brochage-et-câblage)
- [Structure interne — 4 étages](#structure-interne--4-étages)
- [Code embarqué Arduino](#code-embarqué-arduino)
- [Traitement vocal et audio — Raspberry Pi](#traitement-vocal-et-audio--raspberry-pi)
- [Fabrication numérique](#fabrication-numérique)
- [Organisation du projet](#organisation-du-projet)
- [Difficultés rencontrées](#difficultés-rencontrées)
- [Perspectives](#perspectives)
- [Arborescence du dépôt](#arborescence-du-dépôt)
- [Conclusion](#conclusion)
---
 
## Concept et objectifs
 
Le projet s'inscrit dans la philosophie du **RickLab™** : concevoir un dispositif parfaitement fonctionnel sur le plan de l'ingénierie, interactif, et délibérément absurde.
 
Là où un horoscope classique cherche à rassurer, L'Erreurscope fait l'inverse. Quel que soit le signe ou l'identité de la personne, la machine délivre une sentence ironique. L'accès aux prédictions n'est pas immédiat : il faut d'abord résoudre une énigme tangible pour déverrouiller le coffret.
 
Trois briques techniques sont combinées :
 
- **Mécatronique interactive** — verrouillage électromécanique piloté par RFID
- **Reconnaissance vocale** — acquisition et retranscription du prénom et de la date de naissance
- **Traitement audio** — restitution sonore de la réplique correspondant au signe astrologique
---
 
## Parcours utilisateur
 
| Étape | Action utilisateur | Réponse du système |
| --- | --- | --- |
| **1. Énigme des mouches** | Positionner la bonne mouche 3D (tag RFID caché) au-dessus de la zone du capteur | LED verte allumée, LCD affiche `Acces autorise !`, le servo soulève le couvercle |
| **2. Appuyer-pour-parler** | Maintenir le bouton bleu enfoncé et énoncer son prénom + sa date de naissance | Enregistrement du flux microphone |
| **3. Traitement** | — | Speech-to-Text côté Raspberry Pi, retranscription sur le LCD et déduction du signe astrologique |
| **4. Restitution** | — | Lecture de la réplique sarcastique sur les deux haut-parleurs |
 
> **Pourquoi des mouches ?** La référence vient d'un épisode où Rick assemble une combinaison de mouches pour faire apparaître un laboratoire magique dans son garage.
 
---
 
## Architecture matérielle
 
Le système repose sur une **architecture hybride coopérative** : un microcontrôleur pour le temps réel, un mini-PC pour la puissance de calcul audio.
 
| Unité | Rôle |
| --- | --- |
| **Arduino Yùn** | Acquisition temps réel du lecteur RFID RC522, pilotage du servomoteur de verrouillage, gestion de la LED témoin et affichage des messages d'état sur le LCD 16x2 |
| **Raspberry Pi 3** | Capture du signal microphone, exécution du script Python de reconnaissance vocale, logique d'horoscope et amplification audio vers les haut-parleurs |
 
### Nomenclature des composants
 
| Composant | Fonction | Interface |
| --- | --- | --- |
| Module RFID MFRC522 | Lecture des tags dissimulés dans les mouches | SPI |
| Servomoteur | Levier de levage mécanique du couvercle | PWM |
| Afficheur LCD 16x2 | Instructions et retranscription | Parallèle 4 bits |
| Bouton poussoir | Déclencheur « appuyer-pour-parler » | GPIO |
| Microphone | Acquisition vocale | Entrée audio RPi |
| Duo de haut-parleurs | Restitution des prédictions | Sortie audio RPi |
| LED verte | Témoin de détection RFID validée | GPIO |
| Breadboard + câblage Dupont | Rails de distribution 5V / 3.3V / GND | — |
 
---
 
## Brochage et câblage
 
L'alimentation est distribuée : **5V** pour le servomoteur, le LCD et le Raspberry Pi, **3.3V** pour le module RFID.
 
| Élément | Broches Arduino | Détail |
| --- | --- | --- |
| Module RFID MFRC522 | 9 à 13 | Bus SPI — `RST_PIN 9`, `SS_PIN 10` |
| Écran LCD 16x2 | 3, 4, 5, 6, 7, 8 | Mode 4 bits — `RS, EN, D4, D5, D6, D7` = 8, 7, 6, 5, 4, 3 |
| Servomoteur | A0 | Broche analogique utilisée en sortie numérique PWM |
| LED de validation | 2 | Sortie numérique |
 
---
 
## Structure interne — 4 étages
 
Pour garantir une intégration propre du câblage, une répartition correcte de la masse et un accès d'entretien simple, l'intérieur du coffret a été découpé en quatre plateaux fonctionnels.
 
![structure_face_profil](Images/structure_face_profil.png)
 
### Étage 1 — Base inférieure
 
Électronique de puissance et de contrôle : carte Arduino, breadboard principal de distribution et module RFID RC522 orienté vers la plaque supérieure.
 
![etage_1](Images/etage_1.png)
 
### Étage 2 — Plateau intermédiaire
 
Étage « invisible » : il sert de surface de pose aux mouches décoratives et assure l'isolation physique entre la base électronique et les étages supérieurs.
 
### Étage 3 — Unité centrale et audio
 
Raspberry Pi 3, breadboard secondaire et les deux enceintes orientées vers l'avant et l'arrière de l'écran intégré à la paroi.
 
![etage_3](Images/etage_3.png)
 
### Étage 4 — Interface utilisateur
 
Écran LCD encastré dans son support imprimé en 3D, bouton poussoir bleu, ouvertures haut-parleurs, et servomoteur couplé au bâton de balsa qui sert de levier de déverrouillage.
 
![etage_4](Images/etage_4.png)
 
---
 
## Code embarqué Arduino
 
Le programme gère la séquence d'accès sécurisé et le contrôle mécanique du couvercle.
 
### Inclusions et définition des broches
 
```cpp
#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal.h>
#include <Servo.h>
 
// --- Définition des broches ---
#define RST_PIN   9
#define SS_PIN    10
#define LED_PIN   2
#define SERVO_PIN A0
```
 
### Initialisation
 
Le servo est ramené à 0° (position fermée), puis le signal PWM est **détaché** pour éviter la chauffe et les vibrations parasites au repos.
 
```cpp
MFRC522 rfid(SS_PIN, RST_PIN);
LiquidCrystal lcd(8, 7, 6, 5, 4, 3);   // RS, EN, D4, D5, D6, D7
Servo monServo;
 
void setup() {
  SPI.begin();
  rfid.PCD_Init();
 
  pinMode(LED_PIN, OUTPUT);
 
  monServo.attach(SERVO_PIN);
  monServo.write(0);       // position fermée
  delay(300);
  monServo.detach();       // coupe le signal pour éviter les tremblements
 
  lcd.begin(16, 2);
  affichageParDefaut();
}
```
 
### Détection et maintien de l'ouverture
 
À la présentation de la mouche valide : LED verte, message sur le LCD et rotation du servo à 140° pour soulever la trappe. Le couvercle **reste ouvert tant que le badge est présent**, grâce à une boucle de ping (`PICC_WakeupA`) tolérant jusqu'à 3 échecs consécutifs avant de considérer le badge comme retiré.
 
```cpp
void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
 
    // --- 1. OUVERTURE ---
    lcd.clear();
    lcd.print("Acces autorise !");
    digitalWrite(LED_PIN, HIGH);
 
    monServo.attach(SERVO_PIN);
    monServo.write(140);
    rfid.PICC_HaltA();          // évite la relecture en boucle
    delay(300);
    monServo.detach();
 
    // --- 2. MAINTIEN (tant que le badge est là) ---
    int echecsLecture = 0;
 
    while (echecsLecture < 3) {   // tolérance : 3 échecs = badge retiré
      delay(300);
 
      byte bufferATQA[2];
      byte bufferSize = sizeof(bufferATQA);
 
      if (rfid.PICC_WakeupA(bufferATQA, &bufferSize) == MFRC522::STATUS_OK) {
        rfid.PICC_HaltA();
        echecsLecture = 0;        // le badge répond, on réinitialise
      } else {
        echecsLecture++;
      }
    }
 
    // --- 3. FERMETURE ---
    monServo.attach(SERVO_PIN);
    digitalWrite(LED_PIN, LOW);
    monServo.write(0);
    delay(300);
    monServo.detach();
 
    rfid.PCD_Init();              // réinitialise le lecteur pour le badge suivant
    affichageParDefaut();
  }
}
```
 
### Affichage par défaut
 
```cpp
void affichageParDefaut() {
  lcd.clear();
  lcd.print("Veuillez entrer");
  lcd.setCursor(0, 1);
  lcd.print("code secret");
}
```
 
---
 
## Traitement vocal et audio — Raspberry Pi
 
Le Raspberry Pi 3 orchestre toute la partie interaction vocale via un script Python dédié :
 
1. Détection de l'appui sur le bouton bleu
2. Enregistrement du flux audio provenant du microphone
3. Analyse du fichier par un moteur **Speech-to-Text** pour extraire la date de naissance
4. Déduction du signe astrologique correspondant
5. Sélection de la réplique acide préenregistrée associée au signe
6. Restitution via les deux haut-parleurs
### Place de l'IA dans le développement
 
Les modèles **Claude** et **Gemini** ont servi à structurer la logique algorithmique, optimiser le code Arduino, concevoir le script d'interaction Python et générer la trame rédactionnelle des répliques sarcastiques.
 
---
 
## Fabrication numérique
 
Le prototypage et la fabrication ont été entièrement réalisés au **myDiL**.
 
| Procédé | Pièces produites |
| --- | --- |
| **Découpe laser** | Coffret extérieur, cloisons des 4 étages, gravure du disque astrologique sur le couvercle |
| **Impression 3D (PLA)** | Mouches décoratives intégrant le tag RFID, cadre d'encastrement LCD, bouton poussoir, charnières mécaniques |
 
### Historique du prototypage
 
**Étape 1 — Validation électronique sur breadboard**
Câblage initial et validation des communications entre les modules.
 
![proto_breadboard](Images/proto_breadboard.jpg)
 
**Étape 2 — Prototype fonctionnel en carton**
Maquette volumétrique pour tester l'ergonomie, l'encastrement du LCD et le mécanisme de déverrouillage avant d'engager du bois.
 
![proto_carton](Images/proto_carton.jpg)
 
**Étape 3 — Découpe et assemblage**
Découpe des planches de contreplaqué et ajustement des panneaux.
 
![decoupe_panneaux](Images/decoupe_panneaux.jpg)
 
**Étape 4 — Finition structurale et intégration**
Assemblage des compartiments et découpe des ouvertures haut-parleurs.
 
![structure_bois](Images/structure_bois.jpg)
 
**Étape 5 — Éléments d'articulation 3D**
Conception puis renforcement itératif des charnières.
 
![pieces_3d](Images/pieces_3d.jpg)
 
**Étape 6 — Gravure laser du couvercle**
Gravure détaillée du cadran horoscope RickLab™.
 
![couvercle_grave](Images/couvercle_grave.jpg)
 
---
 
## Organisation du projet
 
Méthodologie **Agile**, avec un *daily stand-up* de 10 minutes chaque matin pour faire le bilan de la veille et réajuster les objectifs. Le suivi était centralisé sur le dépôt GitHub et sur le tableau blanc de la salle.
 
### Répartition des rôles
 
| Membre | Périmètre |
| --- | --- |
| **Yacine** | Schémas électroniques, modélisation 3D du coffret, cotations laser, usinage, assemblage matériel, gestion du dépôt GitHub |
| **Théo** | Configuration du Raspberry Pi 3, scripts audio, traitement du signal vocal, calibrage sonore |
| **Gauthier** | Soudure des composants, câblage matériel, intégration du bouton, préparation des présentations |
| **Cyril** | Modélisation et impression 3D des charnières et leviers, support de présentation, rédaction de la documentation technique |
| **Louis** | Idéation du concept d'horoscope, gestion documentaire, affiche, gravures laser |
 
### Déroulé des quatre journées
 
| Jour | Travaux |
| --- | --- |
| **Lundi** | Brainstorming, sélection de l'idée, câblage sur table, prototype carton, configuration initiale |
| **Mardi** | Schémas électroniques, cotations laser, premiers scripts vocaux |
| **Mercredi** | Découpe laser, impression 3D des pièces mécaniques, assemblage du coffret |
| **Jeudi** | Gravure finale, ajustements audio, tests généraux |
 
![brainstorming](Images/brainstorming.jpg)
 
![planning_tableau](Images/planning_tableau.jpg)
 
---
 
## Difficultés rencontrées
 
**Fragilité des charnières imprimées.** Le premier modèle cédait sous la contrainte. Une seconde version épaissie a été développée, puis un troisième modèle spécifique **encastré** a finalement été retenu pour s'adapter aux contraintes d'espace intérieur du couvercle.
 
**Vibrations et conflits du servomoteur.** Le servo maintenu sous tension tremblait et perturbait le bus SPI du lecteur RFID. La solution retenue a été de systématiquement `detach()` le signal PWM dès la fin de chaque mouvement, et de ne le rattacher qu'au moment d'actionner le levier.
 
**Panne de la carte SD du Raspberry Pi.** En fin d'après-midi du dernier jour, la carte SD a lâché. Il a fallu reconfigurer une nouvelle carte et réinstaller les scripts Python dans l'urgence pour que le projet reste opérationnel pour la présentation.
 
---
 
## Perspectives
 
- **Intégration interne du microphone** — l'incorporer directement dans la structure pour supprimer les câbles externes et améliorer le rendu esthétique
- **Finition et peinture thématique** — appliquer des visuels directement inspirés de l'univers Rick & Morty sur le bois
- **Génération dynamique par IA** — connecter le système à une API LLM en ligne pour produire des prédictions uniques à chaque utilisation, au lieu de répliques préenregistrées
---
 
## Arborescence du dépôt
 
```
L-erreurscope/
├── Code/              # Code Arduino (.ino) et scripts Python du Raspberry Pi
├── Documentation/     # Documentation technique complète (PDF)
├── Images/            # Photos de prototypage, schémas et plans des étages
└── README.md
```
 
---
 
## Conclusion
 
L'Erreurscope est un prototype abouti qui démontre l'intégration de trois domaines sur un délai très court : systèmes embarqués Arduino, traitement audio sur Raspberry Pi et fabrication numérique (découpe laser + impression 3D).
 
Ce projet nous a permis :
 
- de concevoir une architecture matérielle hybride répartissant temps réel et calcul entre un microcontrôleur et un mini-PC
- de mettre en œuvre le protocole SPI avec un lecteur RFID MFRC522 et de gérer proprement les conflits de bus liés au servomoteur
- de passer d'un schéma électronique à une pièce réelle via la modélisation 3D, les cotations laser et l'usinage
- de travailler en équipe de cinq en méthodologie Agile, avec gestion du dépôt Git comme point de centralisation
- de réagir à une panne matérielle critique à quelques heures de la présentation
---
 
*Réalisé par [Yacine Harrache](https://github.com/yacinehrc), [Théo Blaise](https://github.com/theoblaise1), [Gauthier Bernard](https://github.com/bernardgauthier10), [Louis Agthe](https://github.com/LGame127) et [Cyril Prevot](https://github.com/G-Cyril-P) — Étudiants en 2ème année | EPSI Lille*
