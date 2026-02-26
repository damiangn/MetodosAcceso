# RAK811 Tracker Board

[Manual de usuario](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_MAN-EN.pdf)

[Datahseet](https://cdn-reichelt.de/documents/datenblatt/E910/RAK_7205_RAK811_DB-EN.pdf)

[Pi Supply](https://www.rxelectronics.id/datasheet/c5/pis-1025.pdf)

[github](https://github.com/RAKWireless/RAK811_BreakBoard)


[github PiSupply](https://github.com/PiSupply/RAK811/blob/master/Application%20Notes/How%C2%A0To%C2%A0Connect%C2%A0Lora%C2%A0RAK811%C2%A0to%C2%A0The%20Things%20Network.pdf)

[Comandos_AT](https://galopago.github.io/assets/pdf/RAK811_AT_Command_Manual_V1.0.pdf)


***

### Registrar RAK811 en TTN:

Hacerlo en modo manual, seleccionar:

- Frequency plan > `AU915 FSB2`

- LoRaWAN version> `LoRaWAN specification 1.0.2`

- Regional parameters version> `RP001 1.0.2`

- JoinEUI> `se debe escribir uno manualmente, o pedir a la IA que genere uno`.

- DevEUI> `Propio del equipop`.

- AppKEY> `Generar uno desde TTN`



---

### 1. Comandos de Configuración Inicial

Estos los usamos para que el módulo sepa en qué red y región trabajar.

| Comando | Para qué sirve | Respuesta exitosa |
| --- | --- | --- |
| `at+set_config=lora:region:AU915` | Define la región (Argentina). | `OK` |
| `at+set_config=lora:ch_mask:13:1` | Activa la **Sub-banda 2** uno por uno (canales 8-15). | `OK` |
| `at+set_config=lora:dev_eui:XXXX...` | Carga tu ID de dispositivo. | `OK` |
| `at+set_config=lora:app_eui:XXXX...` | Carga el ID de la aplicación. | `OK` |
| `at+set_config=lora:app_key:XXXX...` | Carga la clave de seguridad. | `OK` |
|``

### 2. Comandos de Conexión y Estado

Estos son los que confirmaron que todo está bien.

| Comando | Para qué sirve | Respuesta/Rangos|
| --- | --- | --- |
| `at+join` | Inicia la conexión a la red. | Te devolvió **`OK Join Success`**. |
| `at+get_config=lora:status` | Te da el resumen de todo. | Se puede ver los tiempo de las ventas, las claves, DR, ADR, la clase, etc  |
|`at+set_config=lora:adr:1`| Activa el Adaptive Data Rate. (1 = Activo, 0 = Inactivo)| El módulo y el Gateway ahora "negocian" la mejor velocidad para ahorrar batería y evitar errores.|
|`at+set_config=lora:dr:2`|Setea el Data Rate (velocidad).|Puede variar de DR0 al DR5|
| `at+set_config=device:sleep:0` | Despierta al módulo. | Ayuda a resolver el Error 86. |

La salida `at+get_config=lora:status`:
```
OK Work Mode: LoRaWAN
Region: AU915
MulticastEnable: false
DutycycleEnable: false
Send_repeat_cnt: 5
Join_mode: OTAA
DevEui: 3739343571375902
AppEui: 70B3D57ED0061597
AppKey: DB04F1A8F13C8F827A1AAB982C077A29
Class: A
Joined Network:false
IsConfirm: unconfirm
AdrEnable: false
EnableRepeaterSupport: false
RX2_CHANNEL_FREQUENCY: 923300000, RX2_CHANNEL_DR:8
RX_WINDOW_DURATION: 3000ms
RECEIVE_DELAY_1: 1000ms
RECEIVE_DELAY_2: 2000ms
JOIN_ACCEPT_DELAY_1: 5000ms
JOIN_ACCEPT_DELAY_2: 6000ms
Current Datarate: 2
Primeval Datarate: 2
ChannelsTxPower: 0
UpLinkCounter: 0
DownLinkCounter: 0
```

### 3. Comandos de Envío de Datos

Lo que usaste para mandar información al Gateway.

| Comando | Para qué sirve | Resultado |
| --- | --- | --- |
| `at+send=lora:1:686f6c61` | Manda la palabra "hola" en hexadecimal. | Te devolvió **`OK`** y luego **`at+recv`** (confirmación del servidor). |

---

### 4. Errores que ya sabemos 

Es normal que aparezcan, y ya sabemos qué significan para vos:

* **ERROR: 80 (Busy):** El módulo está procesando el envío anterior o está en las ventanas de recepción (RX1/RX2). **Solución:** Esperar 5 segundos entre comandos.
* **ERROR: 86:** El módulo está dormido. **Solución:** Mandar `at+set_config=device:sleep:0` (Wake up).
* **ERROR: 99:** Está intentando hacer el Join todavía. **Solución:** Esperar unos segundos más.

### 5. Firmwares cargados en el RAK
FLASH FIRMWARE DE RAKS:
HERRAMIENTAS: https://downloads.rakwireless.com/#LoRa/RAK811-TrackerBoard/

BINARIOS: https://downloads.rakwireless.com/#LoRa/RAK811/Firmware/