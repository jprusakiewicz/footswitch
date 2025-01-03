const int footswitchPin1 = 2;  // Pin for footswitch 1
const int footswitchPin2 = 3;  // Pin for footswitch 2

int footswitchState1 = HIGH;  // State of footswitch 1
int footswitchState2 = HIGH;  // State of footswitch 2

// Previous state variables for detecting changes
static int lastState1 = HIGH;
static int lastState2 = HIGH;

void setup() {
  Serial.begin(115200);  // Baud rate must match Python script and Serial Monitor
  pinMode(footswitchPin1, INPUT_PULLUP);  // Enable internal pull-up resistor for footswitch 1
  pinMode(footswitchPin2, INPUT_PULLUP);  // Enable internal pull-up resistor for footswitch 2
}

void loop() {
  // Read footswitch states
  footswitchState1 = digitalRead(footswitchPin1);
  footswitchState2 = digitalRead(footswitchPin2);

  // Check footswitch 1 state
  if (footswitchState1 == LOW && lastState1 == HIGH) {
    // Send CC48 ON (value 127)
    sendCC(48, 127);
    lastState1 = LOW;  // Update state
  }
  else if (footswitchState1 == HIGH && lastState1 == LOW) {
    // Send CC48 OFF (value 0)
    sendCC(48, 0);
    lastState1 = HIGH;  // Update state
  }

  // Check footswitch 2 state
  if (footswitchState2 == LOW && lastState2 == HIGH) {
    // Send CC48 ON (value 127)
    sendCC(48, 127);
    lastState2 = LOW;  // Update state
  }
  else if (footswitchState2 == HIGH && lastState2 == LOW) {
    // Send CC48 OFF (value 0)
    sendCC(48, 0);
    lastState2 = HIGH;  // Update state
  }

  delay(50);  // Short debounce delay to prevent accidental bouncing
}

void sendCC(int controller, int value) {
  // Send MIDI CC message to channel 1 (0xB0 for channel 1)
  Serial.write(0xB0);  // Status byte for Control Change on channel 1
  Serial.write(controller);  // Controller number (48)
  Serial.write(value);  // Value (0 or 127)
}
