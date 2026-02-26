# RAK811 Tracker Board

[Manual de usuario](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_MAN-EN.pdf)

[Datahseet](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_DB-EN.pdf)

[Pi Supply](https://www.rxelectronics.id/datasheet/c5/pis-1025.pdf)

[github](https://github.com/RAKWireless/RAK811_BreakBoard)


[github PiSupply](https://github.com/PiSupply/RAK811/blob/master/Application%20Notes/How%C2%A0To%C2%A0Connect%C2%A0Lora%C2%A0RAK811%C2%A0to%C2%A0The%20Things%20Network.pdf)

[Comandos_AT](https://galopago.github.io/assets/pdf/RAK811_AT_Command_Manual_V1.0.pdf)

***
### Comandos AT:

**Nota:** *Utilizar los baudrates en 115200, y utilizar CR/LF*.

`at+help` ==> Lista todos los comandos AT disponibles para la versión de firmware.

- Comandos que dan información necesaria:

`at+get_config=lora:status` ==> Da info. sobre DEV_EUI, APP_EUI, APP_KEY, frecuencias, tamaño de ventanas, los join, etc.

`at+version` ==> Versión del firmware del dispositivo.
***

### Registrar RAK811 en TTN:

Hacerlo en modo manual, seleccionar:

- Frequency plan > `AU915 FSB2`

- LoRaWAN version> `LoRaWAN specification 1.0.2`

- Regional parameters version> `RP001 1.0.2`

- JoinEUI> `se debe escribir uno manualmente, o pedir a la IA que genere uno`.

- DevEUI> `Propio del equipop`.

- AppKEY> `Generar uno desde TTN`