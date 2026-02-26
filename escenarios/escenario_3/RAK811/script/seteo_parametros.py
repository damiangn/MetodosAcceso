import serial
import time

PORT = '/dev/ttyUSB0'
BAUD = 115200

# Lista de comandos según tu terminal de CuteCom
config_commands = [
    "at+set_config=lora:dev_eui:3739343571375901",
    "at+set_config=lora:region:AU915",  # Ajusta a tu región
    "at+set_config=lora:join_mode:0",   # 0 para OTAA
    "at+set_config=lora:app_eui:70B3D57ED0061595",
    "at+set_config=lora:app_key:F0CD5A528D65CA9EE3124271E59D2176",
    "at+set_config=lora:adr:1",        # Activa el algoritmo de adaptación
    "at+set_config=lora:confirm:1",    # Recomendado: al confirmar, el server sabe si debe ajustar el DR
    "at+set_config=lora:dr:2",     # Arranca el DR en 0 para SF10
    "at+join"     # Reinicia para aplicar cambios
]

def send_and_wait(ser, command, timeout=3):
    """Envía un comando y espera el 'OK' del RAK."""
    print(f"Enviando: {command}")
    ser.write((command + '\r\n').encode())
    
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"  [RAK]: {line}")
                if "OK" in line:
                    return True
                if "ERROR" in line:
                    print("  [!] Error en el comando.")
                    return False
    print("  [!] Tiempo de espera agotado (Timeout)")
    return False

try:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print(f"Conectado a {PORT}\n" + "-"*30)
        
        for cmd in config_commands:
            success = send_and_wait(ser, cmd)
            if not success:
                print("Abortando por error en la configuración.")
                break
            time.sleep(0.9) # Pequeña pausa de cortesía

        print("-"*30 + "\nConfiguración terminada.")

except Exception as e:
    print(f"Error de conexión: {e}")