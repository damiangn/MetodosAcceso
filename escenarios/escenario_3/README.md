# Escenario 3  
**(Análisis de Escalabilidad y Colisiones - Protocolo de Acceso ALOHA)**.

Este escenario demuestra el comportamiento real del **método de acceso ALOHA puro** en LoRaWAN.  
Se generaron colisiones intencionales aumentando progresivamente la carga de la red.

### Hardware utilizado
- **2 módulos RAK811** (conectados por USB)
- **3 nodos EESA-IOT** (programados en Arduino IDE)
- Gateway LoRaWAN MikroTik

### Configuración común de todos los nodos
- **Clase C** (escucha continua) → permite intervalos de envío muy cortos sin depender de las ventanas RX1/RX2.
- Payload del mismo tamaño que los nodos Elemon (CayenneLPP).
- ADR desactivado.
- Mismo canal y mismo SF (para generar colisiones).

### Scripts utilizados (para los 2 RAK811)
- **[enviar_datos_ttyUSB0.py](.RAK811/scripts/enviar_datos_ttyUSB0.py)** 
- **[enviar_datos_ttyUSB1.py](.RAK811/scripts/enviar_datos_ttyUSB1.py)** 

### Scripts utilizados (para los 3 EESA)
- **[EESA-ABP-DELAY-CERO.ino](./EESA_IoT/EESA-ABP-DELAY-CERO.ino)** 

### Pasos para reproducir el escenario

1. **Configurar los nodos en Clase C**  
   En los RAK811 (por CuteCom o script):
   ```bash
   at+set_config=lora:class:2        # Clase C
   at+set_config=lora:adr:0
   at+set_config=lora:dr:2
   ```

   En los 3 nodos EESA-IOT (por comandos Serial UART a traves del USB):
   ```bash
   Serial1.println("mac set class c");
   ```

2. **Ejecutar los scripts de los RAK811** (en dos terminales):

   **Terminal 1**:
   ```bash
   python3 scripts/enviar_datos_ttyUSB0.py
   ```

   **Terminal 2**:
   ```bash
   python3 scripts/enviar_datos_ttyUSB1.py
   ```
   **En los EESA IoT**
   Modificar la línea:
   ```bash
   int baseIntervalSecs = 1;
   ```

3. **Variar los tiempos de envío** (como se explica en el informe)  
   Se comenzó con intervalos largos (~10 s) y se fueron reduciendo progresivamente (hasta 2-3 s) para aumentar la carga y observar el aumento de colisiones.

### Resultados esperados
- A medida que se reducen los intervalos de envío, la cantidad de paquetes recibidos en TTN cae drásticamente.
- Se observa claramente la saturación del canal y el comportamiento típico de **ALOHA puro** (probabilidad de éxito ≈ e^(-2G)).
- Los 3 nodos EESA-IOT + 2 RAK811 generan suficiente tráfico para visualizar el punto de saturación.

**Nota:** Para detener los scripts usa `Ctrl + C`.  
En los nodos EESA-IOT se debe desconectar la alimentación.
