import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# 1. CONFIGURACIÓN
# Pegar aquí el valor del campo "data" (Base64) del mensaje "rxpk" en Wireshark
base64_data = "QFFrOgAAAAABWes9xVaM2fE=" 

# Pegar aquí la AppSKey generada previamente
appskey_hex = "7BA067B9C8D5A3718E4C6D6E05C9180F"

# 2. PROCESAMIENTO Y DESENCRIPTACIÓN
def desencriptar_payload_lorawan(b64_string, appskey):
    try:
        # Decodificamos de Base64 a Bytes
        datos = base64.b64decode(b64_string)
        
        # Extraemos la cabecera (MHDR, DevAddr, FCtrl, FCnt)
        mhdr = datos[0]
        dev_addr = datos[1:5]       # 4 bytes (Little Endian)
        fctrl = datos[5]            # 1 byte
        fcnt = datos[6:8]           # 2 bytes (Little Endian)
        
        # Calculamos si hay opciones extra en la cabecera (FOpts)
        fopts_len = fctrl & 0x0F
        header_len = 8 + fopts_len
        mic_len = 4
        
        # Verificamos si realmente hay datos (FRMPayload) en el mensaje
        if len(datos) <= header_len + mic_len:
            print("Este mensaje no contiene datos de sensor (solo MAC commands o confirmación).")
            return

        # Extraemos el Puerto y los datos encriptados
        fport = datos[header_len]
        payload_encriptado = datos[header_len + 1 : -mic_len]
        
        print("--- METADATOS DEL MENSAJE ---")
        print(f"Tipo (MHDR) : {hex(mhdr).upper()}")
        print(f"DevAddr     : {dev_addr[::-1].hex().upper()} (Big Endian)")
        print(f"FCnt (Cont) : int.from_bytes(fcnt, 'little')")
        print(f"FPort       : {fport}")
        print(f"Carga Útil  : {payload_encriptado.hex().upper()} (Encriptada)")
        
        # --- ALGORITMO DE DESENCRIPTACIÓN LORAWAN ---
        key = bytes.fromhex(appskey)
        cipher = Cipher(algorithms.AES(key), modes.ECB())
        encryptor = cipher.encryptor()
        
        payload_desencriptado = bytearray()
        bloques_necesarios = (len(payload_encriptado) + 15) // 16
        
        for i in range(1, bloques_necesarios + 1):
            # Construimos el "Bloque A" exacto según la LoRa Alliance
            # 0x01 | 00 00 00 00 | Dir(0=Uplink) | DevAddr(4) | FCnt(4) | 00 | Contador(1)
            bloque_a = bytearray([0x01, 0x00, 0x00, 0x00, 0x00, 0x00]) # 0x00 es Uplink
            bloque_a.extend(dev_addr)
            bloque_a.extend(fcnt)
            bloque_a.extend([0x00, 0x00]) # Relleno del FCnt a 32 bits
            bloque_a.extend([0x00, i])    # Número de bloque
            
            # Generamos el flujo de llaves (Keystream)
            keystream = encryptor.update(bytes(bloque_a)) + encryptor.finalize()
            
            # Aplicamos XOR (Keystream ^ Payload Encriptado)
            inicio = (i - 1) * 16
            fin = min(i * 16, len(payload_encriptado))
            for j in range(fin - inicio):
                payload_desencriptado.append(payload_encriptado[inicio + j] ^ keystream[j])
                
        print("\n--- RESULTADO DE LA DESENCRIPTACIÓN ---")
        print(f"Hexadecimal : {payload_desencriptado.hex().upper()}")
        
        # Intentar leer el mensaje como texto
        try:
            texto = payload_desencriptado.decode('utf-8')
            print(f"Texto ASCII : {texto}")
        except:
            print("Texto ASCII : (No es texto legible. Son datos binarios puros).")
            
    except Exception as e:
        print(f"Error al procesar: {e}")

# 3. EJECUCIÓN
desencriptar_payload_lorawan(base64_data, appskey_hex)
