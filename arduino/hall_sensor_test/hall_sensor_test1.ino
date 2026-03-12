// testing hall effect sensor and neopixel led strip on breadboard

#include <Adafruit_NeoPixel.h>

// define arduino pins for led strip/hall sensors
#define HALL_PIN 2
#define LED_PIN 6
#define NUM_LEDS 8

Adafruit_NeoPixel strip(NUM_LEDS, LED_PIN, NEO_GRB + NEO_KHZ800);

void setup() {
  // put your setup code here, to run once:

  // set arduino input D2 pin for reading 
  // D2 connected to output of hall effect on breadboard
  pinMode(HALL_PIN, INPUT);
  //start serial comms at 9600 baud speed
  Serial.begin(9600);
  // set brightness at 50/255
  strip.setBrightness(50);
  // initialise led strip - begin/show = leds start off
  strip.begin();
  strip.show();
}

void loop() {
  // put your main code here, to run repeatedly:

  // read D2 pin - will be HIGH (1) or LOW (0)
  int val = digitalRead(HALL_PIN);

  // LOW when magnet is near:
  if (val == LOW) {
    Serial.println("MAGNET DETECTED");
    // set led green
    strip.fill(strip.Color(0, 255, 0));
    strip.show();
  } else {
    Serial.println("no magnet");
    // clear/show = blank leds
    strip.clear();
    strip.show();
  }

  // wait 100ms before looping again
  delay(200);

}
