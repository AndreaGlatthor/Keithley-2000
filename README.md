# Heat Flow Calorimeter Data Acquisition

I operate a heat flow calorimeter using a Keithley 2000 multimeter with a scanner card. The model 2000 is a 6.5 digit multimeter with a RS-232 serial interface, which makes it easy to connect to a computer. The scanner card allows me to connect up to 10 channels, but I only use three of them for my calorimeter.

For many years, I used the OMI software (from Dr Michael Ecker Scientific Consulting, [https://mesicon.de/](https://mesicon.de/)) on a Windows 98 desktop PC with an RS-232 interface. However, after switching to a Windows 11 notebook without an RS-232 port and using a USB-to-serial converter, communication problems arose. This app was created as a result.

The app is built using Dash and Plotly, which provide a web-based interface for easy interaction. The app allows you to set the output file names, sample weights, measurement interval, and output directory. The measurements are displayed in real-time on a graph, and the data is saved in CSV format.

My instrument's identification string is: `KEITHLEY INSTRUMENTS INC.,MODEL 2000,1103202,A19  /A02`. This is an older device, built around the year 2000. Newer models may have slightly different programming syntax. For detailed information, please refer to the user manual for your device. The user manual for the Model 2000 is included in this repository: [Keithley 2000 User Manual (PDF)](Keithley%202000%20User%20Manual.pdf).

The calorimeter has one reference cell and three measuring cells. The difference between the reference cell and the measuring cell is supplied by the scanner card on the three channels, so I don't have to calculate anything. The scanner is supposed to query each of the three once every 20 seconds (editable) and save the data in a csv file.

![Calorimeter assembly with cylindrical metal housing shown open to reveal four sample containers inside the lower section. The upper section is placed to the side. The setup is situated on a plain white background, emphasizing a clean laboratory environment. No visible text is present in the image. The scene conveys a neutral, scientific tone focused on precision instrumentation.](Calorimeter.jpg)

## Requirements

- Keithley 2000 multimeter with scanner card
- Computer with RS-232 serial port or an USB-to-Serial adaptor (I use a Techconnect USB SERIAL ADAPTOR: [https://visionaudiovisual.com/en/product/tc-usbser](https://visionaudiovisual.com/en/product/tc-usbser))
- Python 3.7 or higher with the following libraries installed: (see `requirements.txt`)

    > This code makes use of the `f"..."` or [f-string syntax](https://www.python.org/dev/peps/pep-0498/). This syntax was introduced in Python 3.6, so please make sure you have at least this version installed.

- PyVISA
- Dash
- Plotly

See the pyvisa docs for more information about the needed backend: [https://pyvisa.readthedocs.io/en/latest/](https://pyvisa.readthedocs.io/en/latest/), I use NI-VISA on a Windows 11 notebook.

## Sample Execution & Output

Run the app with:

```bash
python app.py
```

In the Terminal you get:

```text
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: off
 ```

Click the link (ctrl + click) or open a browser and go to `http://127.0.0.1:8050/`.

- The file names are pre-filled with the current date and time, followed by a dash plus channel number. You can change them if you want.
- The sample weights are not set by default, enter the actual weights of your samples. If you leave a weight field empty the corresponding channel will be ignored.
- Select a directory where the csv files will be saved (only existing directories are listed, USB flash drives D, E or F are supported). If you want to set a specific directory that is not listed, you can change the `CSV_DIRECTORIES` variable in the code.
- Set the measurement point spacing in seconds (default is 20 seconds).
- Click the Run button to start the measurement. The Stop button is disabled until you start the measurement.
- The graph on the right will show the measurements in real time.

![Screenshot of the Keithley 2000 Monitor web application interface. On the left, a form allows users to input filenames and weights for three channels, set measurement point spacing in seconds, and select a directory for CSV files. The Run button is active, while the Stop button is disabled. Below the directory selection, a red warning message states that only existing directories are listed and USB flash drives D, E, or F are supported. On the right, a blank graph is displayed with axes labeled Heat flow in milliwatts per gram and Time in hours. The overall environment is clean and functional, designed for scientific data acquisition and monitoring.](image.png)


### Output file format

The output file is a simple text file with comma-separated values (.CSV), one measurement per line:

Time (hours), Measurement value (mW/g)

```text
0.00091, -1.9514702900637e-05
0.00644, -1.3973751238685e-05
0.01198, -1.7136046507979e-05
0.01751, -1.3821184267673999e-05
0.02304, -1.531911372243e-05
0.02857, -1.6907196236188997e-05
... 
```

## 