import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=2)
    print(f"✅ Conectado a {PORT}")

    def send_at(command):
        print(f"Enviando: {command}")
        ser.write((command + '\r\n').encode())
        time.sleep(1) 
        while ser.in_waiting:
            response = ser.readline().decode('utf-8').strip()
            print(f"Respuesta RAK_A1: {response}")

    # --- AQUÍ EMPIEZA EL BUCLE ---
    while True:
        # Enviamos el dato
        send_at("at+send=lora:1:111111a1")
        
        print("Esperando 10 segundos para el próximo envío...")
        time.sleep(10) # Pausa entre envíos
    # -----------------------------

except KeyboardInterrupt:
    # Esto permite cerrar el programa limpiamente con Ctrl+C
    print("\n🛑 Detenido por el usuario.")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Conexión cerrada.")