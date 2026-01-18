## Pasos para agregar un nodo al gateway.

## 1. Crear una nueva aplicacion desde el servidor TTN.

Darle cualquier nonbre y crearla.

## 2. Registrar un nodo.

Ir a register end device, seleccionar `"Enter end device specifics manually"`, elegir el plan de frecuencia **"AU915-928 FSB 2"**.  
El firmware del equipo tiene la versión 1.0.5 para lorawan, asique en el server TTN hay que selccionar **"LoRaWAN version 1.0.2" y "RP001 ... revision B"**.\
En `"JoinEUI"` poner un valor cualquiera como por ejemplo: "70B3D57ED0000000".\
En `"DevEUI"` poner el código que corresponde al nodo (cada equipo tiene su propio DevEUI). En el esp que se probó el valor es **0004A30B00######**.\
Generar una `"APPKey"` desde la propia página de TTN, guardar estos tres códigos porque los vamos a necesitar en el programa que compilemos con Arduino IDE.\
Darle un nombre cualquiera (respetando el formato de TTN) y darle a `"Register end device"`.
Con esto el nodo ya estáregistrado, ahora solo falta compilar el código en el ESP32 para que comience a comunicarse con el gateway.

**Nota:** *Al DevEUI se lo obtiene desde el ropio arduino con el comando `sys get hweui`* desde el Arduino IDE.

## 3. Compilar en el ESP32 el siguiente sketch: [a926.ino](./documentos/a926.ino)

Reemplazar los valores que corraspondan en `AppKey` y `AppEUI`.

Una vez que compile ya debería comunicarse con el servidor, como muestra la siguiente imágen.

![](./imagenes/LiveData.jpg)







