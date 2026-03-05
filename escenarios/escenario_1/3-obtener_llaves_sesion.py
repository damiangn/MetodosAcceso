from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# La AppKey de 16 bytes (32 caracteres) de TTN
app_key_hex = "DB04F1A8F13C8F827A1AAB982C077A29"

# ¡IMPORTANTE! Estos valores deben estar en Little Endian (tal cual salieron de la encriptación/desencriptación)
app_nonce_lsb = "180000"  # Salió del Join-Accept desencriptado (equivale a 00:00:18)
net_id_lsb    = "000000"  # Salió del Join-Accept desencriptado
dev_nonce_lsb = "2735"    # Salió del Join-Request original

# 2. FUNCIÓN DE DERIVACIÓN (LoRaWAN 1.0.x)
def derivar_llave(app_key, prefijo_hex, app_nonce, net_id, dev_nonce):
    # Construimos el bloque exacto de 16 bytes estipulado por la LoRa Alliance
    # Prefijo (1 byte) + AppNonce (3) + NetID (3) + DevNonce (2) + Padding (7 bytes de ceros)
    bloque_hex = prefijo_hex + app_nonce + net_id + dev_nonce + "00000000000000"
    
    # Configuramos AES-ECB con la llave maestra (AppKey)
    cipher = Cipher(algorithms.AES(bytes.fromhex(app_key)), modes.ECB())
    encryptor = cipher.encryptor()
    
    # Encriptamos el bloque para generar la nueva llave
    llave_generada = encryptor.update(bytes.fromhex(bloque_hex)) + encryptor.finalize()
    return llave_generada.hex().upper()


# 3. EJECUCIÓN
# El prefijo 01 es exclusivo para NwkSKey. El prefijo 02 es para AppSKey.
nwk_s_key = derivar_llave(app_key_hex, "01", app_nonce_lsb, net_id_lsb, dev_nonce_lsb)
app_s_key = derivar_llave(app_key_hex, "02", app_nonce_lsb, net_id_lsb, dev_nonce_lsb)

print("--- LLAVES DE SESIÓN GENERADAS ---")
print(f"NwkSKey : {nwk_s_key}")
print(f"AppSKey : {app_s_key}")
