#define loraReset 4

String respuesta;

// ==========================================
// CONFIGURACION DE PAYLOAD VARIABLE
// ==========================================
// 1. Spreading Factor (Data Rate) - AU915: 0=SF10, 1=SF9, 2=SF8, 3=SF7
int currentDR = 1;

// 2. Intervalo base entre uplinks (segundos) - para saturación ALOHA
int baseIntervalSecs = 1;  // ← CAMBIA AQUÍ: 1 o 2 para pruebas de carga alta

// 3. Canal único (canal 8 = 916.8 MHz, sub-banda 2)
int singleChannel = 8;

// 4. Tamaño del payload en bytes (bajar para ToA más corto y más carga)
int payloadSizeBytes = 50;  // Recomendado: 20-50 para saturación

// ==========================================

// Genera string hexadecimal repetitivo
String generarPayloadHex(int m_bytes) {
  String out = "";
  for (int i = 0; i < m_bytes; i++) {
    out += "A1";
  }
  return out;
}

// Payload precalculado
String payloadHex;

void setup() {
  SerialUSB.begin(115200);
  Serial1.begin(57600);

  pinMode(PIN_LED, OUTPUT);  // Si lo usás después, si no → quitalo

  // Reset módulo RN2903
  pinMode(loraReset, OUTPUT);
  digitalWrite(loraReset, LOW);
  delay(1000);
  digitalWrite(loraReset, HIGH);
  delay(3500);

  while (true) {
    limpiarBuffer();

    // Desactivar ADR (SF fijo)
    Serial1.println("mac set adr off");
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    SerialUSB.print("ADR OFF: "); SerialUSB.println(respuesta);

    // Configurar solo un canal activo
    SerialUSB.println("Configurando Canal Único...");
    for (int i = 0; i <= 71; i++) {
      Serial1.print("mac set ch status ");
      Serial1.print(i);
      Serial1.println((i == singleChannel) ? " on" : " off");
      delay(50);
      limpiarBuffer();
    }
    SerialUSB.print("Forzado a transmitir SOLO en canal "); SerialUSB.println(singleChannel);

    // Fijar Data Rate
    Serial1.print("mac set dr ");
    Serial1.println(currentDR);
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    SerialUSB.print("Set DR "); SerialUSB.print(currentDR); SerialUSB.print(": "); SerialUSB.println(respuesta);

    // Join ABP
    Serial1.println("mac join abp");
    delay(500);
    respuesta = Serial1.readStringUntil('\n');
    respuesta.trim();
    SerialUSB.print("Resultado ABP: "); SerialUSB.println(respuesta);

    if (respuesta == "ok") {
      SerialUSB.println("Activacion ABP Exitosa!");
      delay(1000);
      break;
    } else {
      SerialUSB.println("Reintentando activacion...");
      delay(2000);
    }
  }

  // Cambiar a Class C (efectivo DESPUÉS del próximo uplink)
  limpiarBuffer();
  Serial1.println("mac set class c");
  delay(500);
  respuesta = Serial1.readStringUntil('\n');
  respuesta.trim();
  SerialUSB.print("Set Class C: "); SerialUSB.println(respuesta);
  if (respuesta != "ok") {
    SerialUSB.println("ERROR seteando Class C - quedando en Class A");
  }

  // Preparar payload
  payloadHex = generarPayloadHex(payloadSizeBytes);

  SerialUSB.print("\nPayload pre-generado (");
  SerialUSB.print(payloadSizeBytes);
  SerialUSB.print(" bytes): ");
  SerialUSB.println(payloadHex.substring(0, 40) + "...");

  SerialUSB.println("Listo. Ingrese 'A' (may/min) + Enter para iniciar saturación ALOHA.\n");

  // Espera 'A' o 'a'
  char c;
  do {
    while (!SerialUSB.available()) {
      delay(50);
    }
    c = SerialUSB.read();
  } while (c != 'A' && c != 'a');

  while (SerialUSB.available()) SerialUSB.read();
  SerialUSB.println("¡Iniciando saturación! Envíos cada ~1-2s con variabilidad...\n");
}

void loop() {
  limpiarBuffer();

  // === ENVIAR UPLINK INMEDIATAMENTE ===
  Serial1.print("mac tx uncnf 2 ");
  Serial1.println(payloadHex);

  delay(400);  // Mínimo para leer respuestas ("ok" + tx result) - ajusta si es necesario

  respuesta = Serial1.readStringUntil('\n');
  respuesta.trim();
  // SerialUSB.print(" -> Respuesta módulo: "); SerialUSB.println(respuesta);  // Comentar en pruebas largas

  if (respuesta == "ok") {
    // SerialUSB.println(" Esperando confirmación de transmisión...");
    respuesta = Serial1.readStringUntil('\n');
    respuesta.trim();
    // SerialUSB.print(" -> Resultado Tx: "); SerialUSB.println(respuesta);
  } else {
    SerialUSB.println(" ERROR al iniciar transmisión");
  }

  // Pausa con random para simular ALOHA asíncrono (variabilidad 0-100 ms)
  uint32_t pausaMs = (baseIntervalSecs * 1000UL) + random(-100, 100);  // ← random agregado aquí
  SerialUSB.print(" | Próximo en ~"); SerialUSB.print(pausaMs / 1000.0, 1); SerialUSB.println(" s");
  // Opcional: log cada 10 envíos para no saturar Serial
//  static uint32_t contador = 0;
//  contador++;
//  if (contador % 10 == 0) {
//    SerialUSB.print("Uplink #"); SerialUSB.print(contador);
//    SerialUSB.print(" | Próximo en ~"); SerialUSB.print(pausaMs / 1000.0, 1); SerialUSB.println(" s");
//  }
//
  delay(pausaMs);
}

void limpiarBuffer() {
  while (Serial1.available()) {
    Serial1.read();
  }
}