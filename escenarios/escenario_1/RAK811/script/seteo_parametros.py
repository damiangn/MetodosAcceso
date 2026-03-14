# ================================================
# seteo_escenario1.py
# Configuración automática + Join OTAA para Escenario 1
# (Despliegue básico de la red LoRaWAN)
# ================================================

import serial
import time

PORT = '/dev/ttyUSB0'  
BAUD = 115200

# Comandos mínimos para Escenario 1 (solo Join básico)
config_commands = [
    "at+set_config=lora:dev_eui:3739343571375901",          
    "at+set_config=lora:region:AU915",
    "at+set_config=lora:join_mode:0",                      
    "at+set_config=lora:app_eui:70B3D57ED0061595",         
    "at+set_config=lora:app_key:F0CD5A528D65CA9EE3124271E59D2176", 
    "at+set_config=lora:adr:0",                            
    "at+set_config=lora:dr:2",                            
    "at+set_config=lora:class:0",                          
    "at+set_config=device:sleep:0",
    "at+join"                                             
]

def send_and_wait(ser, command, timeout=4):
    """Envía un comando y espera respuesta OK o ERROR"""
    print(f"→ Enviando: {command}")
    ser.write((command + '\r\n').encode())
    
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"  [RAK] {line}")
                if "OK" in line or "+JOINED" in line:
                    return True
                if "ERROR" in line:
                    print("  [!] Error en el comando")
                    return False
    print("  [!] Timeout - sin respuesta")
    return False

try:
    with serial.Serial(PORT, BAUD, timeout=1) as ser:
        print(f"Conectado a {PORT}\n" + "="*50)
        
        for cmd in config_commands:
            success = send_and_wait(ser, cmd)
            if not success and "at+join" not in cmd:
                print("Abortando por error...")
                break
            time.sleep(1.0)   # Pausa más segura para el join

        print("="*50)
        print(" Configuración Escenario 1 terminada.")
        print(" El nodo está intentando hacer JOIN OTAA...")

except Exception as e:
    print(f"Error de conexión: {e}")