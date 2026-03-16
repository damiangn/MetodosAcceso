#define loraReset 4

String respuesta;

// CONFIGURACION DE SF (DATA RATE) PARA AU915 (Australia)
// En el modulo RN2903 para AU915:
// 0 = SF10 / 125 kHz (Es el SF mas lento para 125kHz en esta region)
// 1 = SF9  / 125 kHz
// 2 = SF8  / 125 kHz
// 3 = SF7  / 125 kHz
// NOTA: SF12 y SF11 generalmente no estan disponibles en 125kHz para AU915/US915.
int currentDR = 3; // MODIFICAR ESTE VALOR PARA CAMBIAR EL SF (0 a 3)

void setup() {
  // 1. Iniciar puertos
  SerialUSB.begin(115200);
  Serial1.begin(57600);

  pinMode(PIN_LED, OUTPUT);
  // Muy importante: apagar y prender el modulo RN para que responda bien
  pinMode(loraReset, OUTPUT);
  digitalWrite(loraReset, LOW);
  delay(1000);
  digitalWrite(loraReset, HIGH);
  delay(3500); 

  while(true){     
    limpiarBuffer();
    
    // 1. Desactivar ADR
    Serial1.println("mac set adr off");
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    SerialUSB.print("ADR OFF: ");
    SerialUSB.println(respuesta);
    
    // 2. Configurar Canales para Sub-banda 2 (AU915)
    // AU915 tiene canales 0-71. Sub-banda 2 son canales 8-15 (125kHz) y 65 (500kHz).
    
    // Desactivar canales 0-7
    for(int i = 0; i <= 7; i++) {
        Serial1.print("mac set ch status ");
        Serial1.print(i);
        Serial1.println(" off");
        delay(100);
        limpiarBuffer();
    }
    // Activar canales 8-15 (Sub-banda 2)
    for(int i = 8; i <= 15; i++) {
        Serial1.print("mac set ch status ");
        Serial1.print(i);
        Serial1.println(" on");
        delay(100);
        limpiarBuffer();
    }
    // Desactivar canales 16-71 (excepto el 65 que es parte de SB2)
    for(int i = 16; i <= 71; i++) {
        if (i != 65) {
            Serial1.print("mac set ch status ");
            Serial1.print(i);
            Serial1.println(" off");
            delay(100);
            limpiarBuffer();
        } else {
            Serial1.print("mac set ch status ");
            Serial1.print(i);
            Serial1.println(" on");
            delay(100);
            limpiarBuffer();
        }
    }
    SerialUSB.println("Sub-banda 2 configurada (Ch 8-15, 65).");

    // 4. Configuración ABP
    // El comando "mac join abp" devuelve "ok" si se activa. No devuelve "accepted" (eso es para OTAA).
    Serial1.println("mac join abp"); 
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    respuesta.trim();
    SerialUSB.print("Resultado ABP: ");
    SerialUSB.println(respuesta); 
    
    if (respuesta == "ok"){
        SerialUSB.println("Activacion ABP Exitosa!");
        delay(1000);
        break; // Salimos del setup() ya que estamos conectados
    } else {
        SerialUSB.println("Reintentando activacion...");
        delay(2000);
    }
  }
}

void loop() {
  digitalWrite(PIN_LED, HIGH);
  delay(500);
  digitalWrite(PIN_LED, LOW);
  delay(500);

  SerialUSB.print("\n--- Inicio de Ciclo ---\n");

  limpiarBuffer();
  Serial1.println("mac get status");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> MAC Status: ");
  SerialUSB.println(respuesta);

// 3. Establecer Data Rate (SF)
  Serial1.print("mac set dr ");
  Serial1.println(currentDR);
  delay(500);
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("Set DR ");
  SerialUSB.print(currentDR);
  SerialUSB.print(": ");
  SerialUSB.println(respuesta);

  // Información de diagnóstico
  delay(1000);
  limpiarBuffer();
  Serial1.println("mac get dr");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> Data Rate (DR) actual: ");
  SerialUSB.println(respuesta);

  
  Serial1.println("mac set pwridx 10"); 
  delay(500);
  respuesta = Serial1.readStringUntil('\n');
  respuesta.trim();
  SerialUSB.print("Potencia cambiada: ");
  SerialUSB.println(respuesta); 

  // Enviando mensaje confirmado (2 = puerto, payload hex)
  Serial1.println("mac tx cnf 2 016700E1"); 
  delay(5000);
  respuesta = Serial1.readStringUntil('\n');
  respuesta.trim();
  SerialUSB.print("   -> Transmisión: ");
  SerialUSB.println(respuesta);

  if (respuesta == "ok") {
      SerialUSB.println("   Esperando confirmación (ACK)...");
      respuesta = Serial1.readStringUntil('\n');
      respuesta.trim();
      SerialUSB.print("   -> Resultado de red: ");
      SerialUSB.println(respuesta);
  } else {
      SerialUSB.println("   Error al iniciar transmisión.");
  }

  // Información de diagnóstico

  limpiarBuffer();
  Serial1.println("mac get upctr");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> Mensajes subidos (Uplink): ");
  SerialUSB.print(respuesta);

  limpiarBuffer();
  Serial1.println("mac get dnctr");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> Mensajes bajados (Downlink): ");
  SerialUSB.println(respuesta);

  SerialUSB.println("Pausa de 30s...");
  delay(30000);
}

void limpiarBuffer() {
  while(Serial1.available()) {
    Serial1.read();
  }
}
