# Guía de Configuración del Nodo RAK811

## 1. Registrar el nodo en The Things Stack (TTN)

1. **Crear una nueva aplicación**  
   En TTN crea una nueva aplicación y dale cualquier nombre.

2. **Registrar el End Device**  
   - Ve a **Register end device** → selecciona **“Enter end device specifics manually”**.  
   - Plan de frecuencia: **AU915-928 FSB 2**.  
   - LoRaWAN version: **1.0.2**  
   - Regional Parameters: **RP001 revision B**  
   - **JoinEUI**: cualquier valor (ejemplo: `70B3D57ED0061595`)  
   - **DevEUI**: el del RAK811 (se obtiene con `at+get_config=lora:dev_eui`)  
   - Genera una **AppKey** desde TTN y guárdala.  
   - Dale un nombre al dispositivo y haz clic en **Register end device**.
