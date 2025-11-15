/*
 * EESA-IOT 5.0 LoRaWAN Node Example
 * 
 * This sketch configures the RN2903 LoRa module on the EESA-IOT 5.0 board
 * to join a LoRaWAN network (e.g., local The Things Network server) using OTAA
 * and sends periodic data packets using CayenneLPP format.
 * 
 * Requirements:
 * - Install Arduino IDE and set up the board as per "Placa Elemon IOT Puesta en Marcha.pdf"
 * - Install libraries: CayenneLPP (via Library Manager), RTCZero (via Library Manager), SerialRAM (from provided test sketch or GitHub: https://github.com/EESA-IOT/Elemon)
 * - Replace placeholders for APPEUI, DEV_EUI, APPKEY with your actual values from TTN console.
 * - The gateway is assumed to be on US915 band (902-928 MHz). Adjust if needed.
 * 
 * Note: This uses dummy sensor data (temperature). Connect real sensors as needed.
 *       For ABP mode, modify the join and session setup accordingly.
 */

#include <SerialRAM.h>
#include <CayenneLPP.h>
#include <RTCZero.h>

// Macros from provided info
#define debugSerial SerialUSB
#define loraSerial Serial1
#define loraReset 4
#define RESPONSE_LEN 100

// Variables
static char response[RESPONSE_LEN];
SerialRAM ram;
CayenneLPP lpp(51);  // Buffer size for Cayenne LPP payload
RTCZero rtc;

// LoRaWAN Parameters (placeholders - replace with your TTN values)
const char* DEV_EUI = "0004A30B00######";  // Obtained from sys get hweui or TTN console
const char* APP_EUI = "70B3D57ED0000000";  // From TTN Application
const char* APP_KEY = "02102F53631D24085D2A8A50609FE723";  // From TTN Application

// Timing
const unsigned long SEND_INTERVAL = 60000;  // Send every 60 seconds (adjust for duty cycle)

// Function to clear LoRa serial buffer
void loraClearReadBuffer() {
  while (loraSerial.available())
    loraSerial.read();
}

// Function to send command to LoRa module and wait for response
bool loraSendCommand(const char* command, int timeout = 5000, bool printResponse = true) {
  loraClearReadBuffer();
  debugSerial.print("Sending: ");
  debugSerial.println(command);
  loraSerial.println(command);

  loraSerial.setTimeout(timeout);
  size_t read = loraSerial.readBytesUntil('\n', response, RESPONSE_LEN);
  if (read > 0) {
    response[read - 1] = '\0';  // Remove \r
    if (printResponse) {
      debugSerial.print("Response: ");
      debugSerial.println(response);
    }
    return (strstr(response, "ok") != NULL || strstr(response, "accepted") != NULL);
  } else {
    debugSerial.println("Response timeout");
    return false;
  }
}

// Function to join LoRaWAN network via OTAA
bool loraJoinOTAA() {
  // Set DevEUI (if not using hardware EUI)
  char cmd[64];
  sprintf(cmd, "mac set deveui %s", DEV_EUI);
  if (!loraSendCommand(cmd)) return false;

  // Set AppEUI
  sprintf(cmd, "mac set appeui %s", APP_EUI);
  if (!loraSendCommand(cmd)) return false;

  // Set AppKey
  sprintf(cmd, "mac set appkey %s", APP_KEY);
  if (!loraSendCommand(cmd)) return false;

  // Configure for US915 band (assuming hybrid mode for TTN)
  loraSendCommand("mac set ch status 0 off");  // Disable all channels initially
  for (int i = 8; i < 72; i++) {  // Enable channels 8-15 for US915 (adjust based on sub-band)
    sprintf(cmd, "mac set ch status %d on", i);
    loraSendCommand(cmd);
  }
  loraSendCommand("mac set rx2 3 923300000");  // Set RX2 for US915

  // Join OTAA
  if (!loraSendCommand("mac join otaa", 30000)) return false;

  // Check join response
  loraSerial.setTimeout(30000);
  size_t read = loraSerial.readBytesUntil('\n', response, RESPONSE_LEN);
  if (read > 0) {
    response[read - 1] = '\0';
    debugSerial.print("Join Response: ");
    debugSerial.println(response);
    return (strcmp(response, "accepted") == 0);
  }
  return false;
}

// Function to send data via LoRaWAN (unconfirmed)
bool loraSendData(const uint8_t* data, size_t len) {
  char hexPayload[RESPONSE_LEN * 2];
  char* ptr = hexPayload;
  for (size_t i = 0; i < len; i++) {
    sprintf(ptr, "%02X", data[i]);
    ptr += 2;
  }
  *ptr = '\0';

  char cmd[RESPONSE_LEN * 2 + 20];
  sprintf(cmd, "mac tx uncnf 1 %s", hexPayload);  // Port 1, unconfirmed
  if (!loraSendCommand(cmd, 10000)) return false;

  // Wait for tx response (e.g., mac_tx_ok)
  loraSerial.setTimeout(10000);
  size_t read = loraSerial.readBytesUntil('\n', response, RESPONSE_LEN);
  if (read > 0) {
    response[read - 1] = '\0';
    debugSerial.print("TX Response: ");
    debugSerial.println(response);
    return (strcmp(response, "mac_tx_ok") == 0);
  }
  return false;
}

void setup() {
  pinMode(loraReset, OUTPUT);
  digitalWrite(loraReset, LOW);
  delay(100);
  digitalWrite(loraReset, HIGH);
  delay(1000);

  debugSerial.begin(9600);
  loraSerial.begin(57600);  // Default baud for RN2903
  ram.begin();

  debugSerial.println("EESA-IOT 5.0 LoRaWAN Node Starting...");

  // Reset LoRa module to factory (optional, comment if not needed)
  // loraSendCommand("sys factoryRESET", 10000);

  // Get hardware EUI (DevEUI) if needed
  loraSendCommand("sys get hweui");

  // Set data rate (DR 0 for SF10/125kHz in US915)
  loraSendCommand("mac set dr 0");

  // Attempt to join
  if (loraJoinOTAA()) {
    debugSerial.println("Joined LoRaWAN network successfully!");
  } else {
    debugSerial.println("Join failed. Check keys, gateway, and band.");
    while (true);  // Halt or retry logic
  }

  // Initialize RTC for timing
  rtc.begin();
  rtc.setTime(0, 0, 0);
  rtc.setDate(1, 1, 20);
}

void loop() {
  // Generate dummy data (e.g., temperature)
  float temp = 25.5 + random(-5, 5);  // Simulate sensor

  // Pack into CayenneLPP
  lpp.reset();
  lpp.addTemperature(1, temp);  // Channel 1: Temperature

  // Send the payload
  if (loraSendData(lpp.getBuffer(), lpp.getSize())) {
    debugSerial.println("Data sent successfully!");
  } else {
    debugSerial.println("Send failed.");
  }

  delay(SEND_INTERVAL);  // Wait for next send (consider low power modes)
}
