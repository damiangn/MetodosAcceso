from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import binascii

# 1. CONFIGURACIÓN
# Pegar aquí la cadena hexadecimal del Join-Accept (extraída del 'data' en base64)
data_hex = "203B1382AE252FE3F9299622E69CAA61CA" 

# La AppKey de 16 bytes (32 caracteres) de TTN
app_key_hex = "DB04F1A8F13C8F827A1AAB982C077A29"

# 2. SEPARACIÓN DE LA CABECERA (MHDR)
# El primer byte (MHDR) NUNCA se encripta. En un Join-Accept suele ser '20'
mhdr = data_hex[0:2]

# El resto del mensaje SÍ está encriptado (suele ser un múltiplo de 16 bytes)
payload_encriptado = data_hex[2:]

# 3. DESENCRIPTACIÓN
# Convertimos a bytes
key_bytes = bytes.fromhex(app_key_hex)
payload_bytes = bytes.fromhex(payload_encriptado)

# Configuramos AES en modo ECB (Electronic Codebook)
cipher = Cipher(algorithms.AES(key_bytes), modes.ECB())

# Usamos encryptor() para desencriptar el Join-Accept
encryptor = cipher.encryptor()
payload_desencriptado = encryptor.update(payload_bytes) + encryptor.finalize()

# Convertimos el resultado a texto hexadecimal
dec_hex = payload_desencriptado.hex().upper()

# 4. EXTRACCIÓN DE CAMPOS (Little Endian)
# Ahora que está en texto claro, cortamos los campos según la norma 1.0.x
app_nonce   = dec_hex[0:6]     # 3 bytes
net_id      = dec_hex[6:12]    # 3 bytes
dev_addr    = dec_hex[12:20]   # 4 bytes
dl_settings = dec_hex[20:22]   # 1 byte
rx_delay    = dec_hex[22:24]   # 1 byte
cf_list     = ""               # Opcional (Frecuencias extra)
mic         = ""               # 4 bytes

# Verificamos si tiene CFList (si el mensaje original era largo)
if len(dec_hex) > 32:
    cf_list = dec_hex[24:56]   # 16 bytes
    mic     = dec_hex[56:64]
else:
    mic     = dec_hex[24:32]


# Función auxiliar para invertir bytes para visualización
def invertir_bytes(hex_str):
    if not hex_str: return ""
    hex_inv = bytes.fromhex(hex_str)[::-1].hex().upper()
    return ':'.join(hex_inv[i:i+2] for i in range(0, len(hex_inv), 2))

print("--- MENSAJE JOIN-ACCEPT DESENCRIPTADO ---")
print(f"MHDR        : {mhdr.upper()} (No encriptado)")
print(f"AppNonce    : {invertir_bytes(app_nonce)} (Vital para las llaves de sesión)")
print(f"NetID       : {invertir_bytes(net_id)}")
print(f"DevAddr     : {invertir_bytes(dev_addr)}")
print(f"DLSettings  : {dl_settings}")
print(f"RxDelay     : {rx_delay}")
if cf_list:
    print(f"CFList      : {cf_list} (Canales adicionales)")
print(f"MIC         : {mic}")