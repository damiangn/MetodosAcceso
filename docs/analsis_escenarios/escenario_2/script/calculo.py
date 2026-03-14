import json
import base64
import math
import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.colors import ListedColormap

# Colores personalizados para SF7 a SF10 (inspirados en tu paleta)
sf_colors_sf7_to_10 = ['#1E9FFF', '#FF69B4', '#32CD3F', '#FFAFFF']  # azul, rosa fuerte, verde lima, naranja
# Crear el colormap discreto (solo 4 colores)
sf_cmap_custom = ListedColormap(sf_colors_sf7_to_10)

# Valores de SF que usamos (solo 7 a 10)
sf_values_custom = [7, 8, 9, 10]

# ────────────────────────────────────────────────
# CONFIGURACIÓN - CAMBIA ESTA RUTA A LA TUYA
# ────────────────────────────────────────────────
JSON_FILE = r"my-primer-aplicacion_live_data_1771974629554.json"
# Ejemplo en Linux/Mac: "/home/martina/proyecto_lorawan/my-primer-aplicacion_live_data_1771974629554.json"

# GPS fijo de tu gateway "gw-carcasa"
GATEWAY_LAT = -33.11227433216521
GATEWAY_LON = -64.2982041835785

# Función para calcular distancia real entre dos puntos GPS (en metros)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radio de la Tierra en metros
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Verificar si el archivo existe
if not os.path.exists(JSON_FILE):
    print(f"ERROR: No se encuentra el archivo:\n{JSON_FILE}")
    print("1. Guarda el JSON en esa carpeta")
    print("2. Cambia la ruta en JSON_FILE si es necesario")
    exit()

# Leer el JSON
with open(JSON_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Archivo cargado correctamente: {JSON_FILE}")
print(f"Cantidad total de eventos en el JSON: {len(data)}\n")

# Lista donde guardaremos solo los datos útiles
data_points = []

# Recorrer cada evento del JSON
for event in data:
    # Solo nos interesan los uplinks que llegan a la aplicación
    if event.get('name') == 'as.up.data.forward' and 'uplink_message' in event.get('data', {}):
        uplink = event['data']['uplink_message']
        
        # Solo procesamos los que usan puerto 2 (donde mandás las coordenadas GPS)
        if uplink.get('f_port') != 2:
            continue
        
        # Intentar decodificar el payload
        try:
            payload_b64 = uplink['frm_payload']
            payload_bytes = base64.b64decode(payload_b64)
            payload_str = payload_bytes.decode('utf-8').strip()
            
            # Solo continuar si parece una coordenada GPS válida
            if ',' in payload_str and payload_str.startswith('-33.'):
                lat_str, lon_str = [x.strip() for x in payload_str.split(',', 1)]
                node_lat = float(lat_str)
                node_lon = float(lon_str)
                
                # Extraer RSSI y SNR (tomamos el primero si hay varios gateways)
                rx_meta = uplink.get('rx_metadata', [{}])[0]
                rssi = rx_meta.get('rssi')
                snr = rx_meta.get('snr')
                
                # Extraer Spreading Factor (SF)
                settings = uplink.get('settings', {})
                dr_lora = settings.get('data_rate', {}).get('lora', {})
                sf = dr_lora.get('spreading_factor')
                
                # Packet Error Rate (convertido a porcentaje)
                per = uplink.get('packet_error_rate')
                per_pct = round(per * 100, 2) if per is not None else None
                
                # Timestamp (preferimos received_at)
                timestamp = uplink.get('received_at') or event.get('time') or event.get('received_at')
                
                # Calcular distancia al gateway
                distance = haversine(GATEWAY_LAT, GATEWAY_LON, node_lat, node_lon)
                
                # Guardar todo en un diccionario
                data_points.append({
                    'timestamp': timestamp,
                    'lat': node_lat,
                    'lon': node_lon,
                    'distance_m': round(distance, 2),
                    'rssi': rssi,
                    'snr': snr,
                    'sf': sf,
                    'per': per_pct
                })
                
        except Exception:
            # Si falla la decodificación o no es GPS → ignoramos silenciosamente
            continue

# ────────────────────────────────────────────────
# Si no encontramos datos útiles → avisar
# ────────────────────────────────────────────────
if not data_points:
    print("No se encontraron mensajes con coordenadas GPS válidas en puerto 2.")
    print("Posibles causas:")
    print("- El JSON no tiene uplinks en f_port=2")
    print("- Los payloads no son texto GPS")
    print("- El archivo está truncado o incompleto")
    exit()

# Convertir a tabla (DataFrame de Pandas)
df = pd.DataFrame(data_points)
df.sort_values('timestamp', inplace=True)

# Mostrar la tabla completa en consola
print("\nTABLA DE DATOS FILTRADOS (solo uplinks con GPS en puerto 2):")
print(df.to_string(index=False))

# Estadísticas rápidas
print("\nRESUMEN ESTADÍSTICO:")
print(df.describe())

# Guardar la tabla en CSV para abrir en Excel (opcional pero útil)
df.to_csv('tabla_analisis_gps_rssi_snr.csv', index=False)
print("\nTabla guardada como: tabla_analisis_gps_rssi_snr.csv")



# ────────────────────────────────────────────────
# GRÁFICOS – con colormap personalizado SF7 a SF10
# ────────────────────────────────────────────────

plt.style.use('ggplot')

# Gráfico 1: Distancia vs RSSI
plt.figure(figsize=(10, 6))
scatter_rssi = plt.scatter(
    df['distance_m'], 
    df['rssi'], 
    c=df['sf'], 
    cmap=sf_cmap_custom,          # ← ¡Tu paleta personalizada aquí!
    s=120, 
    alpha=0.9,
    edgecolor='black',
    vmin=7,
    vmax=10                       # Rango ajustado a 7-10
)

cbar = plt.colorbar(scatter_rssi, label='Spreading Factor (SF)')
cbar.set_ticks(sf_values_custom)
cbar.set_ticklabels(sf_values_custom)

plt.xlabel('Distancia al gateway (metros)')
plt.ylabel('RSSI (dBm)')
plt.title('RSSI vs Distancia – Paleta personalizada (SF7 a SF10)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# Gráfico 2: Distancia vs SNR
plt.figure(figsize=(10, 6))
scatter_snr = plt.scatter(
    df['distance_m'], 
    df['snr'], 
    c=df['sf'], 
    cmap=sf_cmap_custom,
    s=120, 
    alpha=0.9,
    edgecolor='black',
    vmin=7,
    vmax=10
)

cbar_snr = plt.colorbar(scatter_snr, label='Spreading Factor (SF)')
cbar_snr.set_ticks(sf_values_custom)
cbar_snr.set_ticklabels(sf_values_custom)

plt.xlabel('Distancia al gateway (metros)')
plt.ylabel('SNR (dB)')
plt.title('SNR vs Distancia – Paleta personalizada (SF7 a SF10)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()