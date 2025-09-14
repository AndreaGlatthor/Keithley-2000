# Heat Flow Calorimeter Data Acquisition

I operate a heat flow calorimeter on a Keithley 2000 multimeter with a scanner card.

Instrument identification: KEITHLEY INSTRUMENTS INC.,MODEL 2000,1103202,A19  /A02

The calorimeter has one reference cell and three measuring cells. The difference between the reference cell and the measuring cell is supplied by the scanner card on the three channels, so I don't have to calculate anything. The scanner is supposed to query each of the three once every 20 seconds and save the data in a text file.
The program is written in Python and uses the PyVISA library to communicate with the multimeter via a USB interface. The data is saved in a text file for further analysis.
The output file is a simple text file with comma-separated values:

Time (hours)    (mV)
0.000084, -1.14873630E-06
0.005615, -1.46408372E-06
0.011147, -1.30359441E-06
0.016679, -1.31654618E-06
0.022210, -1.22813628E-06
0.027741, -1.29120576E-06
0.033273, -1.38243126E-06
0.038804, -1.33175043E-06
0.044335, -1.02935478E-06
0.049867, -1.49449222E-06
0.055398, -1.11832780E-06
0.060930, -1.16281431E-06