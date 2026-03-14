# Escenario 5
**(Análisis de Ortogonalidad de Spreading Factors - Pseudo-ortogonalidad en LoRa)**

Este escenario evalúa en la práctica si los diferentes **Spreading Factors** son realmente ortogonales.  

### Hardware utilizado
- 2 módulos **RAK811** (ttyUSB0 y ttyUSB1)
- Gateway LoRaWAN MikroTik

### Configuración común
- Clase A 
- ADR desactivado
- Mismo subcanal (canal 13 de la sub-band 2)

### Procedimiento real realizado (barrido manual)

Se utilizó **CuteCom** para cambiar el SF manualmente en uno de los nodos. El procedimiento fue el siguiente:

1. **Configuración inicial de ambos nodos** (una sola vez):
   ```bash
   at+set_config=lora:class:0
   at+set_config=lora:adr:0
   at+set_config=lora:ch_mask:13:1     # Solo canal 13 activo
   ```

2. **Nodo fijo (ttyUSB0)**: SF10 bloqueado todo el experimento
   ```bash
   at+set_config=lora:dr:2             # DR0 = SF10
   ```

3. **Barrido manual del SF en el nodo variable (ttyUSB1)**:
   - Se ejecutaron los dos scripts de envío simultáneamente:
     ```bash
     python3 scripts/enviar_datos_ttyUSB0.py
     python3 scripts/enviar_datos_ttyUSB1.py
     ```
   - Se dejó correr **10 a 15 minutos** por cada configuración.
   - Se detuvo la transmisión (`Ctrl + C`).
   - En **CuteCom** se cambió el SF del nodo variable con el comando:
     ```bash
     at+set_config=lora:dr:X     # X = 2 (SF10), 3 (SF9), 4 (SF8) o 5 (SF7)
     ```
   - Se volvieron a lanzar los scripts y se repitió el proceso hasta completar el barrido completo (SF7 → SF8 → SF9 → SF10).

### Scripts utilizados
- **[enviar_datos_ttyUSB0.py](./scripts/enviar_datos_ttyUSB0.py)** → Nodo fijo (SF10)
- **[enviar_datos_ttyUSB1.py](./scripts/enviar_datos_ttyUSB1.py)** → Nodo variable (SF cambiado manualmente)

### Resultados esperados (como aparecen en el informe)
- SF coincidente (ambos en SF10) → pérdida mucho mayor (~46%)
- SF diferentes → pérdidas menores pero aún presentes (9-12%) debido a interferencia inter-SF
- Demuestra la **pseudo-ortogonalidad** real de LoRa en condiciones de laboratorio.

**Nota:** Todo el barrido se hizo manualmente con CuteCom porque permitía mayor control y observación en tiempo real de las respuestas `OK` y `+SEND`.
