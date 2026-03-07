# Escenario 4: Demostración de FDMA y Time-on-Air (ToA) en LoRaWAN (AU915)

Este escenario muestra cómo dos nodos RAK811 envían datos simultáneamente al mismo gateway usando **canales diferentes** en la sub-band 2 de AU915, demostrando FDMA y el impacto del Spreading Factor (SF) en el Time-on-Air (ToA).

## Hardware utilizado
- 2 módulos **RAK811** (o RAK WisNode con módulo RAK811)
- 2 puertos USB diferentes (ttyUSB0 y ttyUSB1)
- 1 gateway LoRaWAN 
- Analizador de espectro Anritsu MS2038C (para capturas visuales)

## Software y herramientas
- **CuteCom** (o cualquier terminal serial) para enviar comandos AT
- **Python 3** con librería `pyserial` (`pip install pyserial`)
- Scripts: `enviar_datos_ttyUSB0.py` y `enviar_datos_ttyUSB1.py`

## Pasos para reproducir el escenario

### 1. Configuración inicial de ambos módulos (OTAA) vía CuteCom
Conecta cada RAK811 a un puerto USB diferente y abre CuteCom (o minicom/screen) en 115200 baudios.

Ejecuta **en cada módulo** (uno por uno) los siguientes comandos AT (reemplaza XXXX con tus valores reales de TTN/The Things Stack u otra consola LoRaWAN):

```bash
at+set_config=lora:dev_eui:XXXXXXXXXXXXXXXX    # 16 caracteres hex
at+set_config=lora:app_eui:XXXXXXXXXXXXXXXX
at+set_config=lora:app_key:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
at+set_config=lora:region:AU915
at+set_config=lora:adr:0                       # Desactiva ADR para control manual
at+set_config=lora:dr:2                        # Data Rate inicial (puede cambiarse después)
at+set_config=lora:class:0                     # Clase A
at+set_config=device:sleep:0                   # Desactiva sleep para pruebas
at+join                                         # Inicia el join OTAA
```

Espera la respuesta `+JOINED` (puede tardar 10–30 segundos).  
Verifica canales disponibles:
```bash
at+get_config=lora:channel
```

### 2. Configuración de canales (sub-band 2, 8 canales)
Para usar solo canales de la **sub-band 2** (canales 8–15), activa solo esos canales (máscara de canales):

```bash
at+set_config=lora:ch_mask:8:1     # Canal 8
at+set_config=lora:ch_mask:9:1
at+set_config=lora:ch_mask:10:1
at+set_config=lora:ch_mask:11:1
at+set_config=lora:ch_mask:12:1
at+set_config=lora:ch_mask:13:1
at+set_config=lora:ch_mask:14:1
at+set_config=lora:ch_mask:15:1
```
### 3. Configuración específica de cada nodo
**Nodo 1 (puerto ttyUSB0)**:
```bash
at+set_config=lora:ch_mask:9:1     # Solo canal 9 activo
at+set_config=lora:dr:2            # SF10 (DR2 en AU915 para SF10/BW125)
```

**Nodo 2 (puerto ttyUSB1)**:
```bash
at+set_config=lora:ch_mask:13:1    # Solo canal 13 activo
at+set_config=lora:dr:0            # SF10
```

### 4. Ejecución de los scripts Python (envío periódico)
En la misma terminal (o en dos terminales distintas), ejecuta ambos scripts en segundo plano:

```bash
python3 enviar_datos_ttyUSB0.py & 
python3 enviar_datos_ttyUSB1.py &
wait
```

- Cada script envía el payload `"222222a2"` cada 10 segundos usando `at+send=lora:1:222222a2`.
- El gateway debería recibir paquetes de ambos nodos en canales diferentes sin colisiones.

### 5. Observaciones esperadas
- Analizador de espectro muestra picos separados en ~916.987 MHz (canal 9) y ~917.805 MHz (canal 13).
- ToA más largo con SF10 (~823 ms para payload pequeño) vs SF7 (~41 ms).
- Mayor SF = más robustez (PG ≈30 dB) pero más consumo y latencia.
