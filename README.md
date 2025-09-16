# Heat Flow Calorimeter Data Acquisition

I operate a heat flow calorimeter on a Keithley 2000 multimeter with a scanner card.

My goal is to create a container app that runs in a browser. In addition to displaying the raw data, it should show the measurement curve in real time. I will implement this using Dash/Plotly. The calibration constants of the three measuring cells must be considered to display the measurement result directly in mW/g.

Instrument identification: KEITHLEY INSTRUMENTS INC.,MODEL 2000,1103202,A19  /A02

The calorimeter has one reference cell and three measuring cells. The difference between the reference cell and the measuring cell is supplied by the scanner card on the three channels, so I don't have to calculate anything. The scanner is supposed to query each of the three once every 20 seconds and save the data in a text file.
The program is written in Python (version 3.13) and uses the PyVISA library to communicate with the multimeter via this USB-to-Serial adaptor: [Techconnect USB SERIAL ADAPTOR: https://visionaudiovisual.com/en/product/tc-usbser](https://visionaudiovisual.com/en/product/tc-usbser).

See the pyvisa docs for more information about the needed backend: [https://pyvisa.readthedocs.io/en/latest/](https://pyvisa.readthedocs.io/en/latest/), I use NI-VISA. I use a Windows 11 ThinkPad X1 and a MacBook Air (M4, 2025) for my work.
## Output file format of main.py

The output file is a simple text file with comma-separated values, one measurement per line:

```text
Time (hours), Measurement value (mV)
0.000084, -1.14873630E-06
0.005615, -1.30359441E-06
0.011147, -1.22813628E-06
0.016679, -1.33175043E-06
0.022210, -1.49449222E-06
0.027741, -1.16281431E-06
0.033273, -1.31654618E-06
0.038804, -1.46408372E-06
```
