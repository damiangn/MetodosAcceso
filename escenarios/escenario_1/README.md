# Demostración del protocolo de acceso escenario 1
Aquí se realizo utilizó un End Device (RAK A2) para hacer un Join OTAA a la red, se fueron capturando los mensajes correspondientes en Wireshark  
Además de hacer Join OTAA luego se envío un mensaje, el cual contiene la palabra "hola"

Para ver todo correctamente en Wireshark seguir los siguientes pasos:
- Utilizar el filtro `_ws.col.protocol == "RADIUS"`
- Click derecho donde dice _[Malformed Packet: RADIUS]_ y poner _Decode as_, debajo de _Current_ elegir *LoRaWAN*, darle a _OK_
- Utilizar el filtro `(_ws.col.protocol == "LoRaWAN") && (frame.len >= 200)`, este filtro es para ver únicamente los mensajes de LoRaWAN respectivos al Join-request, Join-accept y 2 mensajes de comunicación entre el End Device y el Network Server. Éste es el orden en el que aparecen los mensajes.

La IP 192.168.137.28 es la del Network Server  
La IP 192.168.137.15 es la del Gateway  
Lo que va de la IP .28 a la .15 son mensajes Dowlink (del Network Server hacia el End Device)  
Lo que va de la IP .15 a la .28 son mensajes Uplink (del End Device hacia el Network Server)  

_Nota: se toman los Frame Payloads para ver el contenido de los mensajes_

## Información
Ver las siguientes 2 fuentes:  
[https://www.thethingsnetwork.org/docs/lorawan/message-types/](https://www.thethingsnetwork.org/docs/lorawan/message-types/)  
En nuestro caso la versión de LoRaWAN es 1.0.x  
Join-request no está encriptado  
Join-accept está encriptado con el AppKey en LoraWAN 1.0  

[https://www.thethingsnetwork.org/docs/lorawan/end-device-activation/#over-the-air-activation-in-lorawan-10x](https://www.thethingsnetwork.org/docs/lorawan/end-device-activation/#over-the-air-activation-in-lorawan-10x)  
El AppEUI y DevEUI son visibles  
El AppKey es secreto (nunca se envía sobre la red)  
Join-request, tiene los siguientes campos: AppEUI - DevEUI - DevNonce  
El DevNonce es un número de 2 bytes que permite saber la cantidad de veces que quiso hacer JOIN un end device, si se repite un numero usado, puede ser un ataque de repetición  

The Message Integrity Code (MIC) is calculated over all the fields in the Join-request message using the AppKey. The calculated MIC is then added to the Join-request message.  
Join-accept, tiene los siguientes campos: AppNonce - NetID - DevAddr - DLSettings - RXDelay - CFList  
The Join-accept message itself is then encrypted with the AppKey. The Network Server uses an AES decrypt operation in ECB mode to encrypt the Join-accept message.  

AppNonce – a random value or unique ID provided by the Network Server. The AppNonce is used by the end device to derive the two session keys, AppSKey and NwkSKey.

## Join-request
Paquete capturado en Wireshark:  
Paquete de 291 bytes (Join-request)  
hexa:  
01450004f41cffff496af37b227278706b223a5b7b226368616e223a382c22636f6472223a22342f35222c2264617461223a22414a63564274422b31624e77416c6b33635455304f54636e4e534e704b72383d222c2264617472223a225346384257353030222c2266726571223a3931372e3530303030302c226c736e72223a31322e3735303030302c226d6f6475223a224c4f5241222c2272666368223a302c2272737369223a2d33312c2273697a65223a32332c2273746174223a312c2274696d65223a22323032362d30322d32365432313a30353a33302e3831313932395a222c22746d7374223a313431323033383430307d5d7d

Pasandolo a ascii:  
.E..ô.ÿÿIjó{"rxpk":[{"chan":8,"codr":"4/5","data":"AJcVBtB+1bNwAlk3cTU0OTcnNSNpKr8=","datr":"SF8BW500","freq":917.500000,"lsnr":12.750000,"modu":"LORA","rfch":0,"rssi":-31,"size":23,"stat":1,"time":"2026-02-26T21:05:30.811929Z","tmst":1412038400}]}

el _data_ está en base64, se lo pasa a hexa:  
00971506D07ED5B3700259377135343937273523692ABF

Esta secuencia hexa se debe separar en bytes según los siguientes campos:  
campo		| tamaño en bytes | se debe invertir o se lee directo  
MHDR		| 1 byte	| se lee directo  
JoinEUI		| 8 bytes	| se debe invertir  
DevEUI		| 8 bytes	| se debe invertir  
DevNonce	| 2 bytes	| se debe invertir  
MIC 		| 4 bytes	| se lee directo

## Join-accept
Paquete capturado en Wireshark:  
Paquete de 232 bytes (Join-accept)  
hexa:  
0002037b227478706b223a7b22696d6d65223a66616c73652c22746d7374223a313431373033383430302c2266726571223a3932332e392c2272666368223a302c22706f7765223a32372c226d6f6475223a224c4f5241222c2264617472223a225346374257353030222c22636f6472223a22342f35222c2269706f6c223a747275652c2273697a65223a31372c226e637263223a747275652c2264617461223a22494473546771346c4c2b50354b5a59693570797159636f3d227d7d

pasandolo a ascii:  
...{"txpk":{"imme":false,"tmst":1417038400,"freq":923.9,"rfch":0,"powe":27,"modu":"LORA","datr":"SF7BW500","codr":"4/5","ipol":true,"size":17,"ncrc":true,"data":"IDsTgq4lL+P5KZYi5pyqYco="}}

el _data_ está en base64, se lo pasa a hexa:  
203B1382AE252FE3F9299622E69CAA61CA

Y luego se desencripta con el código de python 2-desencriptar_join_accept.py

## Obtener llaves generadas - AppSKey y NwkSKey
Utilizar los datos obtenidos en ambos scripts anteriores según sea necesario en las variables en el script 3-obtener_llaver_sesion.py  
Luego ejecutar el script

## Desencriptar (leer) un mensaje de un End Device
Se debe colocar en el script 4-desencriptar_mensaje_lora.py el AppSKey obtenido en el paso anterior  
Paquete capturado en Wireshark:  
Paquete de 283 bytes (mensaje de End Device)  
hexa:  
01600004f41cffff496af37b227278706b223a5b7b226368616e223a382c22636f6472223a22342f35222c2264617461223a22514646724f67414141414142576573397856614d3266453d222c2264617472223a225346384257353030222c2266726571223a3931372e3530303030302c226c736e72223a31312e3530303030302c226d6f6475223a224c4f5241222c2272666368223a302c2272737369223a2d33302c2273697a65223a31372c2273746174223a312c2274696d65223a22323032362d30322d32365432313a30363a31322e3130313839385a222c22746d7374223a313435333333383632347d5d7d

pasandolo a ascii:  
.`..ô.ÿÿIjó{"rxpk":[{"chan":8,"codr":"4/5","data":"QFFrOgAAAAABWes9xVaM2fE=","datr":"SF8BW500","freq":917.500000,"lsnr":11.500000,"modu":"LORA","rfch":0,"rssi":-30,"size":17,"stat":1,"time":"2026-02-26T21:06:12.101898Z","tmst":1453338624}]}

Ahora tomamos el _data_ en base64 (no lo pasamos a hexa):  
QFFrOgAAAAABWes9xVaM2fE=

Éste es el mensaje enviado por el End Device y el cual debemos desencriptar con el script 4-desencriptar_mensaje_lora.py, colocar el _data_ en la variable base64_data  

Luego ejecutar el script

## Conclusión
Al ver que el mensaje desencriptado dice "hola", confirmamos que el intercambio de llaves producido por el mecanismo Join OTAA fue correcto. Por lo tanto se completa el flujo necesario que comprende desde aceptar un End Device únicamente si es válido (con el MIC), hasta recibir el mensaje del NS y derivar las llaves de sesión para que los End Devices se puedan comunicar de forma segura con el NS.
