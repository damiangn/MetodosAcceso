#define loraReset 4

String respuesta;

// ==========================================
// CONFIGURACION DEL EXPERIMENTO - ESCENARIO 3
// ==========================================

// 1. Configuración de Spreading Factor (Data Rate)
// Para forzar colisiones usando paquetes rápidos (SF7), usamos DR 3.
// En AU915: 0=SF10, 1=SF9, 2=SF8, 3=SF7
int currentDR = 3; 

// 2. Intervalo de Transmisión (en segundos)
// Prueba A: 60 s
// Prueba B: 30 s
// Prueba C: 10 s
int txIntervalSecs = 60; 

// 3. Canal de Transmisión (Único Canal)
// Usaremos el canal 8 (916.8 MHz) de la sub-banda 2.
int singleChannel = 8;

// ==========================================

void setup() {
  SerialUSB.begin(115200);
  Serial1.begin(57600);

  pinMode(PIN_LED, OUTPUT);
  
  // Apagar y prender el módulo RN2903
  pinMode(loraReset, OUTPUT);
  digitalWrite(loraReset, LOW);
  delay(1000);
  digitalWrite(loraReset, HIGH);
  delay(3500); 

  while(true){     
    limpiarBuffer();
    
    // Desactivar ADR para mantener el SF fijo
    Serial1.println("mac set adr off");
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    SerialUSB.print("ADR OFF: ");
    SerialUSB.println(respuesta);
    
    // Configurar MÁSCARA DE CANALES EXTREMA (1 Solo Canal)
    SerialUSB.println("Configurando Canal Único para ALOHA...");
    for(int i = 0; i <= 71; i++) {
        if (i != singleChannel) {
            Serial1.print("mac set ch status ");
            Serial1.print(i);
            Serial1.println(" off");
        } else {
            Serial1.print("mac set ch status ");
            Serial1.print(i);
            Serial1.println(" on");
        }
        delay(50); // Reducido un poco para que no tarde tanto
        limpiarBuffer();
    }
    SerialUSB.print("Forzado a transmitir SOLO en el Canal ");
    SerialUSB.println(singleChannel);

    // Establecer Data Rate (SF)
    Serial1.print("mac set dr ");
    Serial1.println(currentDR);
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    SerialUSB.print("Set DR ");
    SerialUSB.print(currentDR);
    SerialUSB.print(": ");
    SerialUSB.println(respuesta);

    // Configuración ABP
    Serial1.println("mac join abp"); 
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    respuesta.trim();
    SerialUSB.print("Resultado ABP: ");
    SerialUSB.println(respuesta); 
    
    if (respuesta == "ok"){
        SerialUSB.println("Activacion ABP Exitosa!");
        delay(1000);
        break; // Salimos del setup() exitosamente
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

  SerialUSB.print("\n--- Inicio de Ciclo (Escenario 3 ALOHA) ---\n");

  limpiarBuffer();
  Serial1.println("mac get status");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> MAC Status: ");
  SerialUSB.println(respuesta);

  // Enviando mensaje (En este caso no confirmado o confirmado, 
  // OJO: ALOHA clásico suele no usar ACKs, pero usaremos cnf 
  // para seguir tu esquema original, o uncnf si quieres evitar downlink)
  Serial1.println("mac tx uncnf 2 016700E1"); // Cambiado a 'uncnf' para reducir colisiones del gateway enviando acks
  delay(5000);
  respuesta = Serial1.readStringUntil('\n');
  respuesta.trim();
  SerialUSB.print("   -> Transmisión: ");
  SerialUSB.println(respuesta);

  if (respuesta == "ok") {
      SerialUSB.println("   Esperando fin de transmision...");
      respuesta = Serial1.readStringUntil('\n');
      respuesta.trim();
      SerialUSB.print("   -> Resultado Tx: ");
      SerialUSB.println(respuesta);
  } else {
      SerialUSB.println("   Error al iniciar transmisión.");
  }

  // Información de diagnóstico
  delay(500);
  limpiarBuffer();
  Serial1.println("mac get ch freq 8");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> Frecuencia del Canal 8 (Hz): ");
  SerialUSB.println(respuesta);

  limpiarBuffer();
  Serial1.println("mac get upctr");
  respuesta = Serial1.readStringUntil('\n');
  SerialUSB.print("   -> Mensajes subidos (Uplink): ");
  SerialUSB.print(respuesta);

  SerialUSB.print("Pausa de ");
  SerialUSB.print(txIntervalSecs);
  SerialUSB.println(" s...");
  
  // Pausa configurable (menos los ~6 seg que ya gastamos en la lógica arriba)
  // Para ser exactos, hacemos delay(txIntervalSecs * 1000)
  delay(txIntervalSecs * 1000UL);
}

void limpiarBuffer() {
  while(Serial1.available()) {
    Serial1.read();
  }
}
