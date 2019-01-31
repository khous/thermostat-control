#include <DHT.h>
#include <DHT_U.h>

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
#define DHTPIN 13
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

///////// TEMP VARS /////////
// Fahrenheit obviously
float desired_temp = 68;
float allowable_deviation = 2;
float average_observed_temp = 0;

//////// SERVO VARS /////////
// TODO set this via grpc
// Sweep range
int off_degrees = 5;
int on_degrees = 80;
// our servo # counter
uint8_t servonum = 0;
uint8_t HZ = 60;
uint8_t current_degrees = 0;
int desired_degrees = off_degrees;

TaskHandle_t TemperatureHoldTask;

void hold_temperature (void * parameter) {
  float difference;
  for(;;) {
    difference = average_observed_temp - desired_temp;
    Serial.print("Current temp: "); Serial.println(String(average_observed_temp, 2));
    Serial.print("Current difference: "); Serial.println(String(difference, 2));
    Serial.print("Desired Temp: "); Serial.println(String(desired_temp, 2));
  
    // Current temp is higher than desired temp
    if (difference > 0) {
      // Turn the heat off
      Serial.println("Turning heat off");
      turn_heat_on_or_off(false);
    } else if (difference < 0 && abs(difference) > allowable_deviation) {
      // This will debounce the control 
      Serial.println("Turning heat on");
      turn_heat_on_or_off(true);
    }   
    Serial.print(F("Audio Stack HighWater @ "));
    Serial.println(uxTaskGetStackHighWaterMark(NULL));
    // Yield a lot. This doesn't need to be extremely precise
    delay(5000);
  }
}

//void sample_temperature (void * parameter) {
//  average_observed_temperature = get_temperature();
//  for (;;) {
//
//    
//  }  
//}

void setup() {
  Serial.begin(9600);
  delay(100);
  dht.begin();
  Serial.print("Booting Thermostat Sensor Manipulator ... ");

  pwm.begin();
  
  pwm.setPWMFreq(HZ);  // Analog servos run at ~60 Hz updates

  delay(100);
  // Set absolute
  set_degrees(off_degrees);
  // Wait for servo to get to the off position
  delay(1000);

  Serial.println(" done");
  xTaskCreatePinnedToCore(
      hold_temperature, /* Function to implement the task */
      "TemperatureHoldTask", /* Name of the task */
      1000,  /* Stack size in words */
      NULL,  /* Task input parameter */
      0,  /* Priority of the task */
      &TemperatureHoldTask,  /* Task handle. */
      1
    ); /* Core where the task should run */
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
//  Serial.println(pulse);
  pwm.setPWM(n, 0, pulse);
}

// Apply torque softly and seek to a certain degree.
// Consider dispatching this as a task 
void seek_to_degrees (int deg) {
  // Fudge a slow torque ramp up like this
  Serial.println("Seeking to " + String(deg));
  int diff = 1;
  int total_movt = deg - current_degrees;
  int delay_step = 110;
  // Quit if no-op
  if (total_movt == 0) return;
  
  if (total_movt < 0) {
    diff = -1;
  }

  total_movt = abs(total_movt);

  while (total_movt > 0) {    
    set_degrees(current_degrees + diff);
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

float get_temperature () {
//  float temp = 0;
  return dht.readTemperature(true);
//  do {
//    temp = 
//    Serial.print("Got temp: "); Serial.println(String(temp, 2));
//    delay(100);
//  } while (isnan(temp));
//  return temp;
}

void turn_heat_on_or_off (bool on) {
  desired_degrees = on ? on_degrees : off_degrees;
}

void loop() { 
  average_observed_temp = get_temperature();
  String message = "Temp: " + String(average_observed_temp, 2);
  seek_to_degrees(desired_degrees);
  delay(1000);
}





