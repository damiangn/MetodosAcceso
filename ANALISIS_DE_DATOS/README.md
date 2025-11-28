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

