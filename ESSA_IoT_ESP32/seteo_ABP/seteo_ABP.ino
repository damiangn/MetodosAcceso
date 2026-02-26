#define loraReset 4

String respuesta;

// Declarar prototipo de funcion (necesario para compilar correctamente), esta abajo
String enviar(String comando, int tiempo_delay = 1000, int tiempo_delay2 = 0);

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
  delay(2000);

  configurarCanales();

// Verificar placa
  String placa_deveui = enviar("mac get deveui");
  String placa_devaddr, placa_appskey, placa_nwkskey;

// Diferenciar End Device
  if (placa_deveui == "0004A30B00218985") {
    placa_devaddr = "00A6E49E";
    placa_nwkskey = "A417C96AD43D70ECDA046D40C15ED582";
    placa_appskey = "323C92888AEEC0216119E3519C8BF3A8";
  } else if (placa_deveui == "70B3D57ED0065678") {
    placa_devaddr = "26011ABC";
    placa_nwkskey = "44A29384756AFBECD5647382910DACFE";
    placa_appskey = "FB82374928374AEF9823749823749823";
  } else if (placa_deveui == "0004A30B0021DC0F") {
    placa_devaddr = "012C8A30";
    placa_nwkskey = "685419634682A3C7CDE8DCBAF15810A7";
    placa_appskey = "3D29CF51671A3D8F65973D278EE8F095";
  }

  String comando_devaddr = "mac set devaddr " + placa_devaddr;
  String comando_nwkskey= "mac set nwkskey " + placa_nwkskey;
  String comando_appskey = "mac set appskey " + placa_appskey;
  
  SerialUSB.println("\n--- Seteo de credenciales ABP ---");
  limpiarBuffer(); 
  Serial1.println(comando_devaddr);
  delay(100);
  limpiarBuffer(); 
  Serial1.println(comando_nwkskey);
  delay(100);
  limpiarBuffer(); 
  Serial1.println(comando_appskey);
  delay(100);

  SerialUSB.println("\n--- Guardando credenciales en EPROOM ...");
  enviar("mac save");
}

void loop() {
  // No hace falta poner nada aquí si solo quieres setear las credenciales una vez
}

// Función auxiliar para vaciar el buzón
void limpiarBuffer() {
  while(Serial1.available()) {
    Serial1.read();
  }
}

// Funcion para enviar un comando al RN2903A
String enviar(String comando, int tiempo_delay, int tiempo_delay2){
  limpiarBuffer();
  Serial1.println(comando);
  delay(tiempo_delay);    // tiempo de espera (1) configurable, debe entrar como parametro en la funcion
  String respuesta_enviar = Serial1.readStringUntil('\n');
  respuesta_enviar.trim();
  SerialUSB.println(comando);
  SerialUSB.print("Respuesta: ");
  SerialUSB.println(respuesta_enviar);
  delay(tiempo_delay2);    // tiempo de espera (2) configurable, debe entrar como parametro en la funcion
  return respuesta_enviar;
}

void configurarCanales() {
  SerialUSB.println("\n--- Iniciando Configuración de Canales (Sub-banda 2) ---");
  
  // Recorremos todos los canales del 0 al 71
  for (int i = 0; i <= 71; i++) {
    
    // 1. Determinar si el canal debe ser ON u OFF
    String estado = "off"; // Por defecto apagado
    
    // Si está entre 8 y 15 (inclusive) O es el 65 -> Encender
    if ((i >= 8 && i <= 15) || (i == 65)) {
      estado = "on";
    }

    // 2. Construir y enviar el comando
    // Ejemplo: "mac set ch status 8 on"
    Serial1.print("mac set ch status ");
    Serial1.print(i);
    Serial1.print(" ");
    Serial1.println(estado);

    // 3. ¡IMPORTANTE! Leer la respuesta del módulo ('ok')
    // Si no hacemos esto, el buffer se llena y explota.
    // Usamos un timeout corto para que sea rápido.
    Serial1.setTimeout(100); 
    String respuesta = Serial1.readStringUntil('\n');
    
    // Opcional: Imprimir solo errores para no ensuciar la consola
    // if (!respuesta.startsWith("ok")) {
    //    SerialUSB.print("Error en canal "); SerialUSB.print(i); SerialUSB.println(": " + respuesta);
    // }
    
    delay(10); // Pequeña pausa de seguridad para el procesador del RN2903
  }

  // 4. Guardar cambios en la EEPROM
  Serial1.println("mac save");
  Serial1.readStringUntil('\n'); // Leer el 'ok' del save
  
  SerialUSB.println("--- Configuración de Canales Completada y Guardada ---");
  
  // Restaurar timeout normal si lo cambiaste
  Serial1.setTimeout(2000); 
}
