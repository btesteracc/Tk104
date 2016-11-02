# Tk104
A Plugin for Owntracks for the Tk104 tracker
This is the first version of a plugin for the owntracks system to integrate data from the Tk104 GPS-tracker.
It makes use of the gammu-smsd project to receive sms from the tk104 device, converts the data into a json 
string and sends it to the mqtt server. The Tk104 uses 4 different format to present the data, according to how the 
request was triggered or at which state the gps-signal is.
Needs more development on the config-reading and on exeption handling.
Also could be extendet to make use of the Tk104 gprs mode. 
