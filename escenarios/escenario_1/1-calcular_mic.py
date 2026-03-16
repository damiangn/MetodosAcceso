from cryptography.hazmat.primitives.cmac import CMAC
from cryptography.hazmat.primitives.ciphers import algorithms
import binascii

# 1. CONFIGURACIÓN
# Pegar aquí los 23 bytes en hexadecimal que se obtienen del campo "data" de Wireshark
data_hex = "00971506D07ED5B3700259377135343937273523692ABF"

# Pegar aquí la AppKey de 16 bytes (32 caracteres hexadecimales) tal cual está en TTN
app_key_hex = "DB04F1A8F13C8F827A1AAB982C077A29" 

# 2. FUNCIÓN AUXILIAR PARA INVERTIR BYTES
def invertir_bytes(hex_str):
    """Convierte Little Endian a Big Endian (Formato Humano) y le pone dos puntos"""
    # Convierte a bytes, invierte el orden, y vuelve a hex
    hex_invertido = bytes.fromhex(hex_str)[::-1].hex().upper()
    # Le agrega los ':' cada 2 caracteres para que se vea como un EUI
    return ':'.join(hex_invertido[i:i+2] for i in range(0, len(hex_invertido), 2))

# 3. EXTRACCIÓN Y FORMATEO DE CAMPOS
# Extraemos los campos según la estructura de LoRaWAN 1.0.x
# (Recordemos que 1 byte = 2 caracteres hexadecimales)
mhdr       = data_hex[0:2]     # 1 byte
join_eui   = data_hex[2:18]    # 8 bytes (AppEUI)
dev_eui    = data_hex[18:34]   # 8 bytes
dev_nonce  = data_hex[34:38]   # 2 bytes
mic_recib  = data_hex[38:46]   # 4 bytes

print("--- DATOS EXTRAÍDOS Y FORMATEADOS (BIG ENDIAN / HUMANO) ---")
print(f"MHDR      : {mhdr.upper()} (Debe ser 00 para Join-Request)")
print(f"JoinEUI   : {invertir_bytes(join_eui)}")
print(f"DevEUI    : {invertir_bytes(dev_eui)}")
print(f"DevNonce  : {invertir_bytes(dev_nonce).replace(':', '')} (Hexadecimal)")
print(f"MIC Recib.: {mic_recib.upper()} (El que envió el End Device)\n")

# 4. CÁLCULO DEL MIC (AES-CMAC)
try:
    # El mensaje a firmar es la concatenación exacta en Little Endian
    mensaje_a_firmar = mhdr + join_eui + dev_eui + dev_nonce
    
    # Convertimos de texto hexadecimal a bytes reales
    key_bytes = bytes.fromhex(app_key_hex)
    msg_bytes = bytes.fromhex(mensaje_a_firmar)
    
    # Aplicamos el algoritmo AES-CMAC usando la AppKey
    c = CMAC(algorithms.AES(key_bytes))
    c.update(msg_bytes)
    
    # Finalizamos el cálculo y tomamos solo los primeros 4 bytes
    mic_calculado = c.finalize()[:4].hex().upper()
    
    print("--- COMPROBACIÓN DEL MIC ---")
    print(f"Mensaje firmado : {mensaje_a_firmar.upper()}")
    print(f"MIC Calculado   : {mic_calculado}")
    
    if mic_calculado == mic_recib.upper():
        print("¡ÉXITO! El MIC coincide. El End Device está usando la AppKey correcta y formateando bien los datos.")
    else:
        print("ERROR: El MIC no coincide. Verifica que la AppKey sea exactamente la misma que en TTN.")
        
except ValueError:
    print("Asegúrate de haber pegado una AppKey válida de 32 caracteres hexadecimales.")
