#include <Arduino.h>
#include <NewPing.h>
#include <Axle.hpp>
#include <Encoder.h>
#include <limits.h>

#include "variables.h"
#include "functions.hpp"
#include "ISAMobile.h"
#include <Odometry.hpp>
#include <sstream>
#include <string>
#include <unistd.h>


float YawCalibrationCenter = 90.0f;
float PitchCalibrationCenter = 58.0f;

const byte numChars = 64;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

dataPacket packet;


boolean newData = false;


float yawRequested = 0;
float pitchRequested = 0;


float yawErrorAccumulated = 0;
float pitchErrorAccumulated = 0;

Odometry odometry; 

//============

int speed = 50;
float turn_speed = 80;
float fast_turn_speed = 90;

//==============SENSORS VARIABLES==============
#define SONAR_NUM      3
#define MAX_DISTANCE 200
#define PING_INTERVAL 30
#define MIN_DISTANCE 200

unsigned long pingTimer[SONAR_NUM]; // Holds the times when the next ping should happen for each sensor.
unsigned int distances[SONAR_NUM];         // Where the ping distances are stored.
uint8_t currentSensor = 0;          // Keeps track of which sensor is active.
bool isObstacle[SONAR_NUM] = {false};

NewPing sonar[SONAR_NUM] = {   // Sensor object array.
  NewPing(ultrasound_trigger_pin[(int)UltraSoundSensor::Left], 
                     ultrasound_echo_pin[(int)UltraSoundSensor::Left], 
                     MAX_DISTANCE), // Each sensor's trigger pin, echo pin, and max distance to ping.
  NewPing(ultrasound_trigger_pin[(int)UltraSoundSensor::Front], 
                     ultrasound_echo_pin[(int)UltraSoundSensor::Front], 
                     MAX_DISTANCE),
  NewPing(ultrasound_trigger_pin[(int)UltraSoundSensor::Right], 
                     ultrasound_echo_pin[(int)UltraSoundSensor::Right], 
                     MAX_DISTANCE)
};
//===============================================


//==============SENSORS FUNCTIONS==============
void initSensors() {
    pingTimer[0] = millis() + 75;
 
  for (uint8_t i = 1; i < SONAR_NUM; i++)
    pingTimer[i] = pingTimer[i - 1] + PING_INTERVAL;
}

unsigned int getDistance(int index) {
    if(isObstacle[index]) {
        return distances[index];
    } 
    return 0;
}

void processPingResult(uint8_t sensor, int distanceInCm) {
  // The following code would be replaced with your code that does something with the ping result.
  if(distanceInCm < MIN_DISTANCE && distanceInCm != 0)
  {
    if(sensor == 1 && distanceInCm > MIN_DISTANCE-40)
        return;
     isObstacle[sensor] = true;
     distances[sensor] = distanceInCm;
    //  Serial.println("Obstacle detected, stop motors!!!");
    //  Serial.println("Sensor: " + String(sensor) + "; Distance: " + String(distanceInCm));
  }
  else
  {
     isObstacle[sensor] = false;
  }

  float x, y, theta;
  std::tie(x, y, theta) = odometry.GetPosition();

  String angle_str = String(theta);
  String packet = "<"+String(getDistance(0))+","+String(getDistance(1))+","+String(getDistance(2))+","+angle_str+">";
  Serial.write(packet.c_str());
}

void echoCheck() {
  if (sonar[currentSensor].check_timer())
    processPingResult(currentSensor, sonar[currentSensor].ping_result / US_ROUNDTRIP_CM);
}

void updateSensors() {
    for (uint8_t i = 0; i < SONAR_NUM; i++) {
    if (millis() >= pingTimer[i]) {
      pingTimer[i] += PING_INTERVAL * SONAR_NUM;
      sonar[currentSensor].timer_stop();
      currentSensor = i;
      sonar[currentSensor].ping_timer(echoCheck);
    }
  }
}
//===============================================

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

dataPacket parseData() {      // split the data into its parts

    dataPacket tmpPacket;

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(tmpPacket.message, strtokIndx); // copy it to messageFromPC

    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    tmpPacket.first = atof(strtokIndx);

    strtokIndx = strtok(NULL, ",");
    tmpPacket.second = atof(strtokIndx);

    return tmpPacket;
}


void showParsedData(dataPacket packet) {
    Serial.print("Message ");
    Serial.println(packet.message);
    Serial.print("Yaw ");
    Serial.println(packet.first);
    Serial.print("Pitch ");
    Serial.println(packet.second);
}



void setup() {

    initSerial(115200);
    Serial.println("This demo expects 3 pieces of data - text, an integer and a floating point value");
    Serial.println("Enter data in this style <HelloWorld, 12, 24.7>  ");
    Serial.println();

    initMotors();

    // Each platform has to do this independently, checked manually
    calibrateServo(ServoSelector::Yaw, (int)YawCalibrationCenter);
    calibrateServo(ServoSelector::Pitch, (int)PitchCalibrationCenter);

    initServos();
    centerServos();
    initSensors();
    odometry.Initialize();

    // initESP826();
    // initLED();
    Brake();
    delay(500);

    // Serial.println("Initalization ended");

}

//============



void loop() {
      
    updateSensors();

    // parse input data
    recvWithStartEndMarkers();

    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        packet = parseData();
        // showParsedData(packet);

        if (strcmp(packet.message, "servo") == 0)
        {
            if (isStopped == false)
            {
                yawRequested = packet.first;
                pitchRequested = packet.second;

                {
                    // float yawError = -(yawRequested / (HorizontalFOV/2) );
                    float yawError = -yawRequested;
                    float Kp = 25.0f;
                    float Ki = 4.0f;

                    float output = Kp * yawError + Ki * yawErrorAccumulated;
                    yawErrorAccumulated += yawError;
                    
                    moveServo(ServoSelector::Yaw, (int)(YawCalibrationCenter + output));

                }
                {
                    
                    // float pitchError = -(pitchRequested / (VerticalFOV/2));
                    float pitchError = - pitchRequested;
                    float Kp = 15.0f;
                    float Ki = 3.0f;

                    float output = Kp * pitchError + Ki * pitchErrorAccumulated;
                    pitchErrorAccumulated += pitchError;
                    
                    // move servo
                    moveServo(ServoSelector::Pitch,  (int)(PitchCalibrationCenter + output));
                }
                 
            }

        }

        if(strcmp(packet.message, "start")==0){
            MotorR_Move(speed);
            MotorL_Move(speed);
        }

        if(strcmp(packet.message, "stop")==0){
            Brake();
        }

        if(strcmp(packet.message, "turn_right")==0){
            MotorR_Move(-turn_speed);
            MotorL_Move(turn_speed);
        }

        if(strcmp(packet.message, "turn_left")==0){
            MotorR_Move(turn_speed);
            MotorL_Move(-turn_speed);
        }

        if(strcmp(packet.message, "turn_right_faster")==0){
            MotorR_Move(-fast_turn_speed);
            MotorL_Move(fast_turn_speed);
        }

        if(strcmp(packet.message, "turn_left_faster")==0){
            MotorR_Move(fast_turn_speed);
            MotorL_Move(-fast_turn_speed);
        }

        if(strcmp(packet.message, "go_back")==0){
            MotorR_Move(-speed);
            MotorL_Move(-speed);
        }

        if(strcmp(packet.message, "reset_angle")==0){
            odometry.ResetPosition();
        }

        if(strcmp(packet.message, "init")==0){
            odometry.ResetPosition();

            float x, y, prev_theta;
            std::tie(x, y, prev_theta) = odometry.GetPosition();

            for(int s=150; s>20; s-=5) {
                turn_speed = s;
                
                MotorR_Move(-s);
                MotorL_Move(s);

                delay(250);

                float theta;
                std::tie(x, y, theta) = odometry.GetPosition();

                float theta_delta = theta - prev_theta;
                if(theta_delta < 0) {
                    theta_delta += 2*PI;
                }
                prev_theta += theta_delta;

                // String packet = "<"+String(theta_delta)+">";
                // Serial.write(packet.c_str());

                if(theta_delta < 2*PI/3.5/4) {
                    break;
                }
            }

            delay(2000);

            MotorR_Move(0);
            MotorL_Move(0);
        }

        newData = false;
    }
}

