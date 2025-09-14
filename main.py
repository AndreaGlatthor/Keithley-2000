import pyvisa
import time

rm = pyvisa.ResourceManager()
print("Available VISA resources:", rm.list_resources())

# Use COM1 for Keithley 2000
resource_str = "ASRL1::INSTR"  # ASRL1 usually maps to COM1
print(f"Connecting to {resource_str} (COM1)...")
instrument = rm.open_resource(resource_str)

# Set serial communication parameters
instrument.baud_rate = 9600
instrument.data_bits = 8
instrument.stop_bits = pyvisa.constants.StopBits.one
instrument.parity = pyvisa.constants.Parity.none
instrument.flow_control = pyvisa.constants.ControlFlow.none  # Set flow control to none
instrument.timeout = 5000  # 5 seconds

instrument.write_termination = "\r"
instrument.read_termination = "\r"
instrument.write("*IDN?")
print("Instrument identification:", instrument.read())  

# --- Send initialization and measurement commands ---
instrument.write("*RST") # Reset the instrument
instrument.write("*WAI") # Wait for previous operations to complete
instrument.write("SRE 1") # Enable service request on operation complete
instrument.write("SYST:RWL") # Enable remote lockout
instrument.write("SENS:FUNC 'Volt:DC'") # Set function to DC Voltage
instrument.write("SYST:AZER:STAT 0") # Disable auto zero
instrument.write("SENS:VOLT:DC:AVER:STAT 0") # Disable averaging
instrument.write("SENS:VOLT:DC:NPLC 10") # Set number of power line cycles to 10
instrument.write("SENS:VOLT:DC:RANG:AUTO 1") # Enable auto range
instrument.write("SENS:VOLT:DC:DIG 7") # Set resolution to 7 digits
instrument.write("SENS:Volt:DC:REF:STAT 0") # Disable reference junction compensation
instrument.write("ROUT:OPEN:ALL") # Open all channels
instrument.write("ROUT:CLOS (@1)") # Close channel 1
result = instrument.query("READ?") # Perform a measurement
print("Measurement result:", result)

# --- Three-line scan loop ---
# Change the interval_seconds variable to adjust the scan interval.
# The actual interval will be slightly longer due to command execution time.
# 19 seconds give approximately a measurement interval of 20 seconds.
interval_seconds = 19  
output_files = ["line1.txt", "line2.txt", "line3.txt"]

try:
    print("Starting scan loop. Press Ctrl+C to stop.")
    while True:
        for channel in range(1, 4):
            try:
                instrument.write("*SRE 1") # Enable service request on operation complete
                instrument.write("SENS:FUNC 'Volt:DC'") # Set function to DC Voltage
                instrument.write("ROUT:OPEN:ALL") # Open all channels. If I open just the current channel, the instrument beeps every time at this point in the loop.
                instrument.write(f"ROUT:CLOS (@{channel})") # Close the current channel
                time.sleep(0.05)  # Wait a bit between commands
                result = instrument.query("READ?") # Perform a measurement
                print(f"Channel {channel}: Measurement result: {result.strip()}")
                
                # Append result to corresponding file
                with open(output_files[channel - 1], "a") as f:
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    f.write(f"{timestamp}, {result.strip()}\n")
            except Exception as e:
                print(f"Error with channel {channel}: {e}")
        print(f"Waiting for {interval_seconds} seconds before next scan...")
        time.sleep(interval_seconds)
except KeyboardInterrupt:
    print("Scan loop stopped by user.")
except Exception as e:
    print("An error occurred:", e)
finally:
    instrument.write("ROUT:CLOS:ALL") # Close all channels before exiting
    instrument.close() # Close the instrument connection and free the resource. 
    print("Instrument connection closed.")
