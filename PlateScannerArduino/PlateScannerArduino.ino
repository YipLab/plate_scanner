//Plate Scanner Arduino
//YIP LAB - Aaron Au

//Constants
int pinDir[] = {6,3}; //Motor Direction {x,y}
int pinEn[] = {5,2}; //Motor Enable {x,y}
int pinPul[] = {7,4}; //Motor Pulse {x,y}
int pinLim[2][2] = {{11,10},{8,9}};//Limit switch X positive direction {{x+,x-},{y+,y-}}
int pinLight = 13;

int pulseTime = 300;  //Time between High and Low for a pulse (us)
float stepsPerMillimeter = 800.*16./25.4; //800 steps/rotation * 16 rotations/inch * 1/25.4 inch/mm 

boolean limitNotHit;

void setup() {
  Serial.begin(9600);

  for (int i=0; i<2; i++) {
    pinMode(pinDir[i], OUTPUT);
    pinMode(pinEn[i], OUTPUT);
    pinMode(pinPul[i], OUTPUT);
    pinMode(pinLim[i][0], INPUT_PULLUP);
    pinMode(pinLim[i][1], INPUT_PULLUP);
  }

  pinMode(12, OUTPUT);
  digitalWrite(12, HIGH);
  pinMode(pinLight, OUTPUT);
  digitalWrite(pinLight, LOW);
 

  Serial.println("Plate Scanner Arduino");
}

boolean moveSteps(int axis, boolean dir, long nrsteps, boolean limits) {
  digitalWrite(pinEn[axis], HIGH);
  digitalWrite(pinDir[axis], dir);
  for (int i=0; i<nrsteps; i++) {
    digitalWrite(pinPul[axis], HIGH);
    delayMicroseconds(pulseTime/2);
    digitalWrite(pinPul[axis], LOW);
    delayMicroseconds(pulseTime/2);
    if (limits && (digitalRead(pinLim[axis][0])==LOW || digitalRead(pinLim[axis][1])==LOW)) {
      digitalWrite(pinDir[axis], !dir);
      for (int j=0; j<500; j++) {
        digitalWrite(pinPul[axis], HIGH);
        delayMicroseconds(pulseTime/2);
        digitalWrite(pinPul[axis], LOW);
        delayMicroseconds(pulseTime/2);
      }
      digitalWrite(pinEn[axis], LOW);
      return false;
    }
  }
  digitalWrite(pinEn[axis], LOW);
  return true;
}

void doCommand(String command) {
  if (command.substring(1,3) == "pr") {
    //pr = Position Relative
    int axis = command.substring(0,1).toInt();
    float distance = command.substring(3,10).toFloat();
    boolean dir = distance > 0.0;
    long steps = (long) abs(distance) * stepsPerMillimeter + 0.5;  // + 0.5 for rounding
    Serial.println(moveSteps(axis, dir, steps, true));
  } else if (command.substring(1,3) == "or") {
    zero();
  } else if (command.substring(1,3) == "lo") {
    //Serial.println(command.substring(3,4).toInt());
    digitalWrite(pinLight,command.substring(3,4).toInt());
  }

}

boolean zero() {
for (int i = 0; i<2; i++) {  
  limitNotHit = true;
  while (limitNotHit) {
      limitNotHit = moveSteps(i, false, 100,true);
    }
  moveSteps(i,true, 500, false);
}
Serial.println("or");
}

void loop() {
if (Serial.available()) {
  String command = Serial.readStringUntil(';');
  String axis;
  if (command.substring(0,1) == "0" || command.substring(0,1) == "1") {
    doCommand(command);
  }
}
}

