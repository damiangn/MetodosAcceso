# =============================================================================
# Análisis de Ganancia de Procesamiento (Processing Gain) en LoRa (CSS)
# 
# Este script:
#   - Lee el archivo CSV con tus mediciones LoRa
#   - Calcula la ganancia de procesamiento teórica: PG = 10 * log10(2^SF)
#   - Calcula SNR efectivo = SNR_medido + PG
#   - Genera estadísticas por SF y globales
#   - Muestra ejemplos de enlaces marginales (distancias largas / SNR bajos)
#   - Opcional: guarda resultados en un nuevo CSV
# =============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# --------------------------------------------------
# 1. Configuración
# --------------------------------------------------
CSV_PATH = 'tabla_analisis_gps_rssi_snr.csv'          # Cambia si el archivo está en otra carpeta
OUTPUT_CSV = 'analisis_lora_con_processing_gain.csv'  # Archivo de salida opcional

# --------------------------------------------------
# 2. Función para calcular Processing Gain (dB)
# Fórmula estándar en LoRa/CSS: PG = 10 * log10(2^SF)
# --------------------------------------------------
def processing_gain(sf):
    """
    Calcula la ganancia de procesamiento teórica en dB.
    Basado en el número de chips por símbolo = 2^SF.
    """
    if pd.isna(sf):
        return np.nan
    return 10 * np.log10(2 ** sf)

# --------------------------------------------------
# 3. Cargar y preparar los datos
# --------------------------------------------------
print("Cargando datos desde:", CSV_PATH)
df = pd.read_csv(CSV_PATH)

# Asegurarse de que las columnas existan y tengan el tipo correcto
required_cols = ['distance_m', 'rssi', 'snr', 'sf']
for col in required_cols:
    if col not in df.columns:
        print(f"¡Error! Falta la columna '{col}' en el CSV.")
        exit()

df['sf'] = pd.to_numeric(df['sf'], errors='coerce')
df['snr'] = pd.to_numeric(df['snr'], errors='coerce')
df['rssi'] = pd.to_numeric(df['rssi'], errors='coerce')
df['distance_m'] = pd.to_numeric(df['distance_m'], errors='coerce')

# --------------------------------------------------
# 4. Calcular Processing Gain y SNR efectivo
# --------------------------------------------------
df['PG_dB'] = df['sf'].apply(processing_gain)
df['SNR_efectivo_dB'] = df['snr'] + df['PG_dB']

# --------------------------------------------------
# 5. Estadísticas globales y por SF
# --------------------------------------------------
print("\n=== RESUMEN GLOBAL ===")
print(df[['distance_m', 'rssi', 'snr', 'PG_dB', 'SNR_efectivo_dB']].describe().round(2))

print("\n=== ESTADÍSTICAS POR SPREADING FACTOR ===")
stats_por_sf = df.groupby('sf')[['distance_m', 'rssi', 'snr', 'PG_dB', 'SNR_efectivo_dB']].agg(
    ['count', 'mean', 'min', 'max']
).round(2)
print(stats_por_sf)

# --------------------------------------------------
# 6. Ejemplos de enlaces marginales (distancias > 200 m o SNR < -5 dB)
# --------------------------------------------------
print("\n=== EJEMPLOS DE ENLACES MARGINALES (distancias lejanas o SNR muy bajo) ===")
marginales = df[(df['distance_m'] > 200) | (df['snr'] < -5)].sort_values('snr')
print(marginales[['distance_m', 'sf', 'snr', 'PG_dB', 'SNR_efectivo_dB', 'rssi']].head(10).round(2))

# --------------------------------------------------
# 7. Guardar resultados (opcional)
# --------------------------------------------------
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nResultados guardados en: {OUTPUT_CSV}")

# Opcional: si querés ver correlaciones
print("\nCorrelaciones clave:")
corrs = df[['distance_m', 'rssi', 'snr', 'sf', 'PG_dB', 'SNR_efectivo_dB']].corr().round(2)
print(corrs['snr'])  # Por ejemplo, correlación del SNR con otras variables

# --------------------------------------------------
# 8. Preparar DataFrame agrupado por SF para gráficos (esto faltaba)
# --------------------------------------------------
df_sf = df.groupby('sf').agg({
    'distance_m': ['mean', 'min', 'max'],
    'rssi': ['mean', 'min', 'max'],
    'snr': ['mean', 'min', 'max'],
    'PG_dB': 'mean',              # PG es constante por SF
    'SNR_efectivo_dB': ['mean', 'min', 'max']
}).reset_index()

# Renombrar columnas para que sea más fácil usarlas
df_sf.columns = ['sf', 
                 'dist_mean', 'dist_min', 'dist_max',
                 'rssi_mean', 'rssi_min', 'rssi_max',
                 'snr_mean', 'snr_min', 'snr_max',
                 'PG_mean',
                 'snr_ef_mean', 'snr_ef_min', 'snr_ef_max']

print("\n=== DataFrame para gráficos (resumen por SF) ===")
print(df_sf.round(2))

# --------------------------------------------------
# 9. Generar gráficas útiles con matplotlib
# --------------------------------------------------
import matplotlib.pyplot as plt

# Gráfico 1: Ganancia de Procesamiento Teórica vs SF (barras)
plt.figure(figsize=(8, 5))
plt.bar(df_sf['sf'], df_sf['PG_mean'], color='skyblue', edgecolor='black')
plt.xlabel('Spreading Factor (SF)')
plt.ylabel('Ganancia de Procesamiento (dB)')
plt.title('Ganancia de Procesamiento Teórica en LoRa (CSS)')
plt.xticks(df_sf['sf'].astype(int))
for i, v in enumerate(df_sf['PG_mean']):
    plt.text(df_sf['sf'][i], v + 0.3, f'{v:.2f}', ha='center', va='bottom')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('fig_ganancia_procesamiento_teorica.png')  # guarda como imagen
plt.show()  # muestra en pantalla (opcional si estás en terminal)

# Gráfico 2: SNR Medido vs SNR Efectivo por SF (barras agrupadas)
plt.figure(figsize=(9, 6))
bar_width = 0.35
x = np.arange(len(df_sf['sf']))

plt.bar(x - bar_width/2, df_sf['snr_mean'], bar_width, label='SNR Medido (promedio)', color='salmon')
plt.bar(x + bar_width/2, df_sf['snr_ef_mean'], bar_width, label='SNR Efectivo (promedio)', color='limegreen')

plt.xlabel('Spreading Factor (SF)')
plt.ylabel('SNR (dB)')
plt.title('SNR Medido vs. SNR Efectivo por Spreading Factor')
plt.xticks(x, df_sf['sf'].astype(int))
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Añadir valores encima de las barras
for i in range(len(x)):
    plt.text(x[i] - bar_width/2, df_sf['snr_mean'][i] + 0.5, f'{df_sf["snr_mean"][i]:.1f}', ha='center')
    plt.text(x[i] + bar_width/2, df_sf['snr_ef_mean'][i] + 0.5, f'{df_sf["snr_ef_mean"][i]:.1f}', ha='center')

plt.tight_layout()
plt.savefig('fig_snr_medio_vs_efectivo.png')
plt.show()

# Gráfico 3: SNR Efectivo vs Distancia Media (scatter)
plt.figure(figsize=(8, 5))
scatter = plt.scatter(df_sf['dist_mean'], df_sf['snr_ef_mean'], 
                      s=150, c=df_sf['sf'], cmap='viridis', edgecolor='black')
plt.colorbar(scatter, label='Spreading Factor (SF)')

for i, txt in enumerate(df_sf['sf']):
    plt.annotate(f'SF{txt}', (df_sf['dist_mean'][i], df_sf['snr_ef_mean'][i]), 
                 xytext=(5, 5), textcoords='offset points')

plt.xlabel('Distancia Media (m)')
plt.ylabel('SNR Efectivo Promedio (dB)')
plt.title('SNR Efectivo vs. Distancia Media por SF')
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('fig_snr_efectivo_vs_distancia.png')
plt.show()