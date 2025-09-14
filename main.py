
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
instrument.timeout = 10000  # 10 seconds

# Set required line terminators for Keithley 2000
instrument.write_termination = "\r"
instrument.read_termination = "\r"


# --- Send initialization and measurement commands ---
commands = "*RST.*WAI.*SRE 1.SYST:RWL.SENS:FUNC 'Volt:DC'.SYST:AZER:STAT 0.SENS:VOLT:DC:AVER:STAT 0.SENS:VOLT:DC:NPLC 10.SENS:VOLT:DC:RANG:AUTO 1.SENS:VOLT:DC:DIG 7.SENS:Volt:DC:REF:STAT 0.ROUT:OPEN:ALL.:route:close (@1).READ?"

try:
    cmd_list = commands.split('.')
    for cmd in cmd_list[:-1]:
        if cmd.strip():
            print(f"Sending: {cmd}")
            instrument.write(cmd)
            time.sleep(0.05)
    # The last command is READ? (query)
    last_cmd = cmd_list[-1]
    print(f"Querying: {last_cmd}")
    result = instrument.query(last_cmd)
    print("Measurement result:", result)
except Exception as e:
    print("Instrument did not respond or timed out. Details:", e)
