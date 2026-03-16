# Análisis de Datos - Escenario 2 (LoRaWAN)

Carpeta dedicada al **procesamiento y visualización** de los datos recolectados en el **Escenario 2**  
(Análisis de la capa física: RSSI, SNR, distancia, ganancia de procesamiento y Adaptive Data Rate).

Aquí se encuentran:
- Scripts de Python para cálculos y generación de gráficos
- Archivos CSV con datos procesados
- Gráficos finales (PNG)
- Datos exportados desde TTN (JSON)

---
### 📁 Estructura de archivos (con vínculos corregidos)

| Archivo | Descripción |
|--------------------------------------|-----------|
| [**calculo.py**](../escenario_2/script/calculo.py) | Script principal: procesa datos crudos, calcula distancias, promedios de RSSI/SNR y genera la mayoría de los gráficos |
| [**calculo_GP.py**](../escenario_2/script/calculo_GP.py) | Cálculo específico de **Ganancia de Procesamiento** (Processing Gain) y comparación SNR medido vs. SNR efectivo |
| [**analisis_lora_con_processing_gain.csv**](../escenario_2/analisis_lora_con_processing_gain.csv) | Datos procesados con ganancia de procesamiento incluida |
| [**tabla_analisis_gps_rssi_snr.csv**](../escenario_2/tabla_analisis_gps_rssi_snr.csv) | Tabla limpia con distancia, RSSI, SNR, SF y coordenadas GPS |
| [**trafico_actual.txt**](../escenario_2/script/trafico_actual.txt) | Resumen de tráfico (cantidad de paquetes, tasa de éxito, etc.) |
| [**gw_carcasa_live_data_*.json**](../escenario_2/script/gw-carcasa_live_data_1771974643948.json) | Datos en vivo exportados del gateway (ejemplo con timestamp) |
| [**my-primer-aplicacion_live_data_*.json**](../escenario_2/script/my-primer-aplicacion_live_data_*.json) | Datos en vivo de la aplicación TTN |
| [**rak-811-a1-device_live_data_*.json**](../escenario_2/script/rak-811-a1-device_live_data_*.json) | Datos crudos del nodo RAK811 (dos sesiones) |
| [**RSSI_vs_distancia.png**](../escenario_2/img/RSSI_vs_distancia.png) | Gráfico RSSI vs Distancia (coloreado por SF) |
| [**SNR_vs_Distancia.png**](../escenario_2/img/SNR_vs_Distancia.png) | Gráfico SNR vs Distancia (coloreado por SF) |
| [**fig_ganancia_procesamiento_teorica.png**](../escenario_2/img/fig_ganancia_procesamiento_teorica.png) | Ganancia teórica de procesamiento por SF |
| [**fig_snr_efectivo_vs_distancia.png**](../escenario_2/img/fig_snr_efectivo_vs_distancia.png) | SNR efectivo vs distancia |
| [**fig_snr_medio_vs_efectivo.png**](../escenario_2/img/fig_snr_medio_vs_efectivo.png) | Comparación SNR medido vs SNR efectivo por SF |

---

## Cómo reproducir el análisis

### Requisitos
```bash
pip install pandas numpy matplotlib seaborn
```

### Pasos recomendados

1. **Coloca todos los archivos JSON y CSV** en la misma carpeta.
2. Ejecuta primero el script principal:

```bash
python3 calculo.py
```

   → Genera automáticamente:
   - RSSI_vs_distancia.png
   - SNR_vs_Distancia.png
   - fig_snr_efectivo_vs_distancia.png
   - fig_snr_medio_vs_efectivo.png

3. Ejecuta el cálculo de ganancia de procesamiento:

```bash
python3 calculo_GP.py
```

   → Genera:
   - fig_ganancia_procesamiento_teorica.png

---

## Notas importantes

- Los scripts están diseñados para los datos recolectados con el nodo RAK811 y el gateway MikroTik.
- Las distancias se calcularon usando coordenadas GPS del nodo (columna `gps` en los CSV).
- Los gráficos usan una paleta personalizada por Spreading Factor (SF7 = azul, SF8 = verde, SF9 = rosa, SF10 = rojo).
- Todo el análisis corresponde al **Escenario 2** del informe (SNR/RSSI vs distancia + Processing Gain).
