import serial
import mido
import time

# Configure the serial port
serial_port = '/dev/tty.usbmodem14601'  # Replace with your Arduino's port
baud_rate = 115200  # Ensure baud rate matches Arduino setup
arduino = serial.Serial(serial_port, baud_rate)

# Open the IAC Driver MIDI port
midi_out = mido.open_output('IAC Driver Bus 1')  # Ensure "Bus 1" exists in IAC Driver

print("Listening for MIDI messages from Arduino...")

# Initialize variables for filtering CC48 and CC49 states
last_state_48 = None
last_state_49 = None
median_window_48 = []
median_window_49 = []

def add_to_median_window(median_window, state, window_size=5):
    """Helper function to maintain a median window"""
    median_window.append(state)
    if len(median_window) > window_size:
        median_window.pop(0)
    return sorted(median_window)[len(median_window) // 2]  # Return median value

try:
    while True:
        if arduino.in_waiting >= 3:  # Check if we have enough data for a full MIDI message
            midi_data = arduino.read(3)  # Read 3 bytes
            
            try:
                # CC48 Handling
                if midi_data[0] == 0xB0 and midi_data[1] == 48:
                    current_state_48 = midi_data[2]
                    
                    # Add to the median window and get the filtered state
                    filtered_state_48 = add_to_median_window(median_window_48, current_state_48)
                    
                    # Only send a MIDI message if the state has changed
                    if filtered_state_48 != last_state_48:
                        midi_message = mido.Message('control_change', channel=0, control=48, value=filtered_state_48)
                        print(f"Sending: {midi_message}")
                        midi_out.send(midi_message)
                        last_state_48 = filtered_state_48

                # CC49 Handling
                if midi_data[0] == 0xB0 and midi_data[1] == 49:
                    current_state_49 = midi_data[2]
                    
                    # Add to the median window and get the filtered state
                    filtered_state_49 = add_to_median_window(median_window_49, current_state_49)
                    
                    # Only send a MIDI message if the state has changed
                    if filtered_state_49 != last_state_49:
                        midi_message = mido.Message('control_change', channel=0, control=49, value=filtered_state_49)
                        print(f"Sending: {midi_message}")
                        midi_out.send(midi_message)
                        
                        # If CC49 turns off and CC48 is on, resend CC48
                        if filtered_state_49 == 0 and last_state_48 == 127:
                            time.sleep(0.01)  # Small delay to avoid overwhelming the serial buffer
                            midi_message_48_resend = mido.Message('control_change', channel=0, control=48, value=filtered_state_48)
                            print(f"Resending CC48: {midi_message_48_resend}")
                            midi_out.send(midi_message_48_resend)
                        
                        last_state_49 = filtered_state_49

            except ValueError as e:
                print(f"Invalid MIDI message: {e}, data: {midi_data}")

        time.sleep(0.01)  # Small delay to avoid overwhelming the serial buffer

except KeyboardInterrupt:
    print("Exiting...")
finally:
    arduino.close()
    midi_out.close()
