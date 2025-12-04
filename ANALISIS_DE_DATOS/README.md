### Mensajes que llegaron a enviarse correctamente:

Los mensajes "Forward uplink data messaje" son los que llevan información del nodo. 
En este caso las siguientes líneas representan estos datos:
```bash
"uplink_message": {
      "session_key_id": "AZrLeXJwT0Mq55mkhYXwEQ==",
      "f_port": 1,
      "f_cnt": 6,
      "frm_payload": "AWcA4Q==",
      "rx_metadata": [
```
`"frm_payload": "AWcA4Q==",` es el valor medido (simulado en este caso por la EESA IOT 5.0).

**Decodificación del payload:**

- Base64 "AWcA4Q==" se traduce a hex: 016700E1.
- Interpretado como CayenneLPP:
    - 01: Canal 1 (sensor 1).
    - 67: Tipo de dato (103 en decimal, que corresponde a temperatura).
    - 00E1: Valor (225 en decimal, dividido por 10 según el estándar CayenneLPP) = 22.5 °C.

**Nota**: *Cada 5 o 6 mensajes enviados correctamente, se corta la comunicación y el nodo no llega más al Gateway. Una causa posible es que el nodo o el Gateway estén utilizando un plan de frecuencias o sub bandas equivocadas. En principio TTN soporta la sub banda 2, o FSB2.*

*Otra posible causa es el AdrLink, revisar bien cómo funciona esto*

### Canales Uplinks AU915-928 de 125KHz (separación de 200KHz):
| Channel ID | Frequency (MHz) | Sub-band | |
| ---------- | --------------- | ------- | -- |
| 0 | 915.2 | FSB1 | 
| -- | a | -- |
| 7 | 916.6 | FSB1 |
| 8 | 916.8  | **FSB2** |
| 9 | 917.0  | **FSB2** | 
| | 917.1 | | *---> freq central Radio 0*
| 10 | 917.2  | **FSB2** |
| 11 | 917.4  | **FSB2** |
| 12 | 917.6  | **FSB2** |
| 13 | 917.8  | **FSB2** |
| | 917.9 | | *---> freq central Radio 1*
| 14 | 918.0  | **FSB2** |
| 15 | 918.2  | **FSB2** |
| 16 | 918.4  | FSB3 |
| -- | a | -- |
|23 | 919.8  | FSB3 |
| 24 | 920.0  | FSB4 |
| -- | a  | -- |
| 31 | 921.4  | FSB4 |
| 32 | 921.6  | FSB5 |
| -- | --  | -- |
| 39 | 923.0  | FSB5 |
| 40 | 923.2  | FSB6 |
| -- | --  | -- |
| 47 | 924.6  | FSB6 |
| 48 | 924.8  | FSB7 |
| -- | ---  | -- |
| 55 | 926.2  | FSB7 |
| 56 | 926.4  | FSB8 |
| -- | --  | -- |
| 63 | 927.8  | FSB8 |

***
### Canales de uplinks de 500KHz:

Channel ID | Frequency (MHz) | In FSB2
---------- | --------------- | ------ |
64 | 915.9 | No
**65** | **917.5** | **Yes**
66 | 919.1 | No 
67 | 920.7 | No 
68 | 922.3 | No 
69 | 923.9 | No 
70 | 925.5 | No 
71 | 927.1 | No 
***

### RX2:
Frequency (MHz) | Data Rate | In FSB2
| --- | --- | --- |
**923.3** | **SF12 BW500** | **Yes**
***
### Fuentes:

[Frequency plan](https://www-thethingsnetwork-org.translate.goog/docs/lorawan/frequency-plans/?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc)

[Regional parameters](https://lora-alliance.org/wp-content/uploads/2020/11/lorawan_regional_parameters_v1.0.2_final_1944_1.pdf)
