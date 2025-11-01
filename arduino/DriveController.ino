// DriveController.ino — FWD/BACK/LEFT/RIGHT/STOP via série
// Protocole: "F:0.25", "B:0.20", "L:0.20", "R:0.20", "S"
const int ENA=5;  // PWM gauche
const int ENB=6;  // PWM droite
const int IN1=7;  // sens gauche A
const int IN2=8;  // sens gauche B
const int IN3=9;  // sens droite A
const int IN4=10; // sens droite B

unsigned long lastCmd = 0;
const unsigned long TIMEOUT_MS = 1500;

void setMotor(int ena, int inA, int inB, float speed, int dir){
  int pwm = constrain((int)(speed * 255.0), 0, 255);
  analogWrite(ena, pwm);
  if(dir>=0){ digitalWrite(inA, HIGH); digitalWrite(inB, LOW); }
  else      { digitalWrite(inA, LOW);  digitalWrite(inB, HIGH); }
}

void stopAll(){
  analogWrite(ENA, 0); analogWrite(ENB, 0);
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
}

void setup(){
  Serial.begin(115200);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  stopAll();
}

void loop(){
  if(Serial.available()){
    String s = Serial.readStringUntil('\n'); s.trim();
    lastCmd = millis();
    if(s == "S"){ stopAll(); return; }
    if(s.length()>=3 && s.charAt(1)==':'){
      char c = s.charAt(0);
      float sp = s.substring(2).toFloat(); if(sp <= 0) sp = 0.2;
      if(c=='F'){ // avant
        setMotor(ENA,IN1,IN2, sp, +1);
        setMotor(ENB,IN3,IN4, sp, +1);
      } else if(c=='B'){ // arrière
        setMotor(ENA,IN1,IN2, sp, -1);
        setMotor(ENB,IN3,IN4, sp, -1);
      } else if(c=='L'){ // tourne gauche
        setMotor(ENA,IN1,IN2, sp*0.5, -1);
        setMotor(ENB,IN3,IN4, sp*0.5, +1);
      } else if(c=='R'){ // tourne droite
        setMotor(ENA,IN1,IN2, sp*0.5, +1);
        setMotor(ENB,IN3,IN4, sp*0.5, -1);
      }
    }
  }
  // Watchdog sécurité: si plus de commande, stop
  if(millis() - lastCmd > TIMEOUT_MS){
    stopAll();
  }
}
