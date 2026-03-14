# Guía de Configuración del Nodo RAK811 en TTN – Escenario 2

## Descripción del Escenario
**Escenario 2**: Análisis de la **Capa Física** y **Adaptive Data Rate (ADR)**  

Se utiliza un módulo **RAK811** con **ADR activado**, permitiendo que The Things Network (TTN) controle automáticamente el **Spreading Factor (SF)** según la calidad de la señal (RSSI/SNR).  

Se envían coordenadas GPS reales periódicamente para generar tráfico y observar cómo el Network Server ajusta los parámetros de enlace mediante comandos **LinkADRReq**.

## Hardware utilizado
- Módulo **RAK811** (conectado por USB a la PC)
- GPS **Globalsat BU-353S4** (conectado al segundo puerto USB de la PC)
- Gateway LoRaWAN **MikroTik** (compatible AU915)

## Software y herramientas
- Terminal serial: **CuteCom**, **minicom** o **screen** (115200 baudios para RAK811)
- Puerto GPS: 4800 baudios
- Script Python: [`gps_enviar.py`](./scripts/gps_enviar.py)
- Librerías Python requeridas:
  ```bash
  pip install pyserial pynmea2
  ```

## 1. Registrar el nodo en The Things Network (TTN)

1. **Crear una nueva aplicación** en The Things Stack  
   → Applications → Add application

2. **Registrar el End Device** (manualmente)  
   - Selecciona: **Enter end device specifics manually**  
   - **Frequency plan**: AU915-928 FSB 2  
   - **LoRaWAN version**: 1.0.2  
   - **Regional Parameters revision**: RP001 revision B  
   - **JoinEUI** (AppEUI): cualquier valor fijo, ejemplo recomendado: `70B3D57ED0000000`  
   - **DevEUI**: obtener del RAK811 con `at+get_config=lora:dev_eui` (o genera uno y luego configúralo en el módulo)  
   - **AppKey**: genera uno nuevo desde la consola TTN (guárdalo)  
   - Asigna un **nombre** descriptivo al dispositivo  
   → **Register end device**

Con esto el dispositivo ya está preparado en el servidor.

## 2. Configuración del RAK811 (OTAA + ADR activado)

Conecta el RAK811 por USB y abre un terminal serial (115200, 8N1).

Ejecuta los siguientes comandos AT uno por uno:

```bash
at+set_config=lora:dev_eui:XXXXXXXXXXXXXXXX 
at+set_config=lora:app_eui:70B3D57ED0000000   
at+set_config=lora:app_key:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  
at+set_config=lora:region:AU915
at+set_config=lora:adr:1                    
at+set_config=lora:dr:2                       
at+set_config=lora:class:0                 
at+set_config=device:sleep:0                  
at+join
```

Espera la respuesta `+JOINED` (puede tardar 10–60 segundos).  
Si no se une, verifica DevEUI/AppEUI/AppKey y que el gateway esté en rango.

### Configuración de canales – Solo Sub-band 2 (FSB2)

Para este experimento se fuerza el uso de **un solo canal** (canal 13):

```bash
at+set_config=lora:ch_mask:8:0
at+set_config=lora:ch_mask:9:0
at+set_config=lora:ch_mask:10:0
at+set_config=lora:ch_mask:11:0
at+set_config=lora:ch_mask:12:0
at+set_config=lora:ch_mask:13:1    # ← único canal activo
at+set_config=lora:ch_mask:14:0
at+set_config=lora:ch_mask:15:0
```

## 3. Enviar datos de posición GPS (activar ADR)

Conecta también el GPS Globalsat BU-353S4 al segundo puerto USB de la PC.

Ejecuta el script:

```bash
python3 scripts/gps_enviar.py
```

**Comportamiento del script**:
- Lee tramas **$GPRMC** del GPS
- Cuando tiene señal válida (`status = A`), extrae latitud y longitud
- Envía la cadena `"lat,lon"` (5 decimales) como payload por LoRaWAN
- Intervalo de envío ≈ **15 segundos** (para evitar rechazos por "busy")
- Muestra en consola: posición enviada, DR actual, RSSI/SNR (si hay downlink)

## Resultados esperados

- El nodo se une correctamente (OTAA)
- Comienza a enviar posiciones cada ~15 s
- Después de varios uplinks, el Network Server envía **LinkADRReq**  
  → Puedes ver en la consola de TTN → Live data → Metadata → "Data rate" cambia  
  → El RAK811 ajusta automáticamente SF (típicamente entre SF7 y SF10)
- En Grafana (si tienes integración) o en la consola TTN se observan:
  - Cambios de **Spreading Factor**
  - Variación del **Time-on-Air**
  - Mejora / empeoramiento de RSSI/SNR según distancia o obstáculos

Esto demuestra el funcionamiento real del **Adaptive Data Rate** en una red LoRaWAN real.