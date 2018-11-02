# ESP8266 Smart Energy Meter

This project aims to build a smart energy meter, getting readings from our ferraris energy meter (which we are not allowed to modify) by detecting a red stripe on a spinning wheel using an IR-diode and an IR-receiver.

## Setting up the API
On the machine that shall run the API, clone the repository and install the requirements listed in requirements.txt (maybe you will want to use a virtualenv or something like this). You are now ready to run the API using
```
python3 api.py
```
You can test if it works correctly using curl:
```
curl localhost:8080/tick
```
You can use the provided systemd service file as an example to run the API as a systemd service.

## Setting up the ESP

Upload the sketch to the ESP, connect the IR-LED, the IR-receiver and the resistor like shown in the wiring diagram. Attach the ESP to your computer and hold it to the Ferraris counter. Find a position that works best (where you have a clear change in the readings when the red stripe passes). Fix it. Set the correct IP, WiFi-password and name in the ESP as well as a threshold level that works for you. For me, the reading would drop from 200 to 100 while the red stripe was on, so I chose 150 as a threshold.

![Wiring Breadboard View](SmartMeter.png?raw=true "Smart Meter")
![Wiring Schematic View](SmartMeterSchematic.png?raw=true "Smart Meter Schematic")

## Acknowledgments

Thanks to [Martin Kompf](https://www.kompf.de/tech/emeir.html) for inspiring me to do this project as well as useful info on the IR-led and receiver.
