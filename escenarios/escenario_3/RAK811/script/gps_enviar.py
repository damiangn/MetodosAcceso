import serial
import time
import pynmea2
import re

# Configuracion (Configuration)
LORA_PORT = '/dev/ttyUSB3'
GPS_PORT = '/dev/ttyUSB1'
BAUD_LORA = 115200
BAUD_GPS = 4800 

try:
    ser_lora = serial.Serial(LORA_PORT, BAUD_LORA, timeout=2)
    ser_gps = serial.Serial(GPS_PORT, BAUD_GPS, timeout=1)
    print("Conectado a LoRa (RAK811) y GPS G-STAR IV")
    print("Esperando senal GPS (Status A)... Sal al exterior si tarda mucho.")

    def obtener_dr():
        ser_lora.write(b"at+get_config=lora:status\r\n")
        time.sleep(0.5)
        if ser_lora.in_waiting:
            respuesta = ser_lora.read_all().decode(errors='replace')
            match = re.search(r"Current Datarate: (\d+)", respuesta)
            if match:
                return match.group(1)
        return "No detectado"

    def enviar_lora(mensaje):
        payload = mensaje.encode('utf-8').hex()
        # Formato de 3 parametros para evitar ERROR: 2
        comando = f"at+send=lora:2:{payload}\r\n"
        
        print(f"\nEnviando ubicacion: {mensaje}")
        ser_lora.write(comando.encode())
        
        # Esperamos respuesta del envio y posibles datos de red (RSSI/SNR)
        time.sleep(4) # Aumentamos a 4s para captar el downlink (at+recv)
        if ser_lora.in_waiting:
            respuesta = ser_lora.read_all().decode(errors='replace').strip()
            print(f"RAK811 responde:\n{respuesta}")
            
            # Si la respuesta tiene at+recv, extraemos RSSI y SNR
            # Formato: at+recv=port,rssi,snr,len
            if "at+recv" in respuesta:
                partes = respuesta.split(',')
                if len(partes) >= 3:
                    print(f"Calidad de Red -> RSSI: {partes[1]} dBm, SNR: {partes[2]}")
        
        dr = obtener_dr()
        print(f"Data Rate actual: DR{dr}")

    while True:
        try:
            # LIMPIEZA CRITICA: Borramos datos viejos del buffer antes de leer
            ser_gps.reset_input_buffer()
            
            linea = ser_gps.readline().decode('ascii', errors='replace').strip()
            
            if linea.startswith('$GPRMC'):
                msg = pynmea2.parse(linea)
                
                if msg.status == 'A':
                    lat = msg.latitude
                    lon = msg.longitude
                    # Usamos 5 decimales para notar variaciones pequenas
                    ubi = f"{lat:.5f},{lon:.5f}"
                    
                    enviar_lora(ubi)
                    
                    # Subimos a 15s para evitar el ERROR: 93 (Busy)
                    print("Pausa de 15s...")
                    time.sleep(15)
                else:
                    print(f"GPS: {linea[:15]}... -> Buscando senal (Status V)")
        
        except pynmea2.ParseError:
            continue
        except Exception as e:
            print(f"Error en el bucle: {e}")

except serial.SerialException as e:
    print(f"Error de conexion serial: {e}")
except KeyboardInterrupt:
    print("\nScript detenido por el usuario.")
finally:
    if 'ser_lora' in locals(): ser_lora.close()
    if 'ser_gps' in locals(): ser_gps.close()
    print("Puertos cerrados.")