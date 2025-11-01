
// Protocole série: F:0.25  / S
void setup(){ Serial.begin(115200); }
void loop(){
  if(Serial.available()){
    String s = Serial.readStringUntil('\n');
    s.trim();
    if(s.startsWith("F:")) { /* TODO: moteurs avant */ }
    if(s=="S") { /* TODO: stop */ }
  }
}
