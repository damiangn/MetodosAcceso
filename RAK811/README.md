# RAK811 Tracker Board

[Manual de usuario](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_MAN-EN.pdf)

[Datahseet](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_DB-EN.pdf)

[Pi Supply](https://www.rxelectronics.id/datasheet/c5/pis-1025.pdf)

[github](https://github.com/RAKWireless/RAK811_BreakBoard)

[Comandos_AT](https://galopago.github.io/assets/pdf/RAK811_AT_Command_Manual_V1.0.pdf)

***
### Comandos AT:

`at+help` ==> Lista todos los comandos AT disponibles para la versión de firmware.

Comandos que dan información necesaria:

`at+get_config=lora:status` ==> Da info. sobre DEV_EUI, APP_EUI, APP_KEY, frecuencias, tamaño de ventanas, los join, etc.

`at+version` ==> Versión del firmware del dispositivo.