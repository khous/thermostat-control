#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// called this way, it uses the default address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(&Wire, 0x40);
// you can also call it with a different address you want
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x41);
// you can also call it with a different address and I2C interface
//Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(&Wire, 0x40);

// Depending on your servo make, the pulse width min and max may vary, you 
// want these to be as small/large as possible without hitting the hard stop
// for max range. You'll have to tweak them as necessary to match the servos you
// have!
#define SERVOMIN  150 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  600 // this is the 'maximum' pulse length count (out of 4096)

// our servo # counter
uint8_t servonum = 0;
uint8_t HZ = 60;
uint8_t current_degrees = 0;

void setup() {
  Serial.begin(9600);
  delay(100);
  Serial.println("8 channel Servo test!");

  pwm.begin();
  
  pwm.setPWMFreq(HZ);  // Analog servos run at ~60 Hz updates

  delay(100);
}

// you can use this function if you'd like to set the pulse length in seconds
// e.g. setServoPulse(0, 0.001) is a ~1 millisecond pulse width. its not precise!
void setServoPulse(uint8_t n, double pulse) {
  double pulselength;
  
  pulselength = 1000000;   // 1,000,000 us per second
  pulselength /= HZ;   // 60 Hz
//  Serial.print(pulselength); Serial.println(" us per period"); 
  pulselength /= 4096;  // 12 bits of resolution
//  Serial.print(pulselength); Serial.println(" us per bit"); 
  pulse *= 1000000;  // convert to us
  pulse /= pulselength;
  Serial.println(pulse);
  pwm.setPWM(n, 0, pulse);
}

// Apply torque softly and seek to a certain degree.
// Consider dispatching this as a task 
void seek_to_degrees (int deg) {
  // Fudge a slow torque ramp up like this
  int diff = 1;
  int total_movt = deg - current_degrees;
  int delay_step = 110;
  // Quit if no-op
  if (total_movt == 0) return;
  
  if (total_movt < 0) {
    diff = -1;
  }

  total_movt = abs(total_mvt);

  while (total_movt > 0) {    
    set_degrees(current_degrees - 1);
    if (delay_step > 10) delay_step -= 10;
    total_movt -= 1;
    delay(delay_step);    
  }  
}

void set_degrees (int deg) {
  // 0 = 2000 us
  // 90 = 1000 us
  long mapped_value = map(deg, 0, 90, 2000, 1000);
  setServoPulse(0, mapped_value / (float)1000000);  
  current_degrees = deg;
}
int counter = 0;
int diff = 5;
void loop() {
  seek_to_degrees(0);
  seek_to_degrees(90);
}
