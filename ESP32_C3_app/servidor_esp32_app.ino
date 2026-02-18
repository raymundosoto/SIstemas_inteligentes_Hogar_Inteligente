#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

//  Credenciales de Red 
const char* ssid = "Totalplay-319F_2.4Gnormal";
const char* password = "319FEF5D88K2kS97";

// URLs de Servicios 
const char* url_nube = "https://raymundoss.pythonanywhere.com/update";
const char* url_clima = "http://api.open-meteo.com/v1/forecast?latitude=19.60&longitude=-99.04&current_weather=true&relative_humidity_2m=true";

WebServer server(80);

//  Configuracion de Hardware 
int actuadores[] = {5, 6, 7}; 
int botones[] = {2, 3, 4};    
bool estados[] = {false, false, false};

// Variables de Logica e IA 
float temp = 0, hum = 0, viento = 0;
String id_dispositivo = "AGENTE_MAESTRO";

// Variables para el "Manual Override"
bool bloqueoAuto[] = {false, false, false};
unsigned long tiempoBloqueo[] = {0, 0, 0};
const unsigned long DURACION_BLOQUEO = 60000; // 1 minuto de preferencia manual

void manejarRaiz() {
  String html = "<!DOCTYPE html><html lang='es'><head><meta charset='UTF-8'>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>";
  html += "<style>body{background:#0f0f0f; color:white; font-family:sans-serif; text-align:center; padding:20px;}";
  html += ".btn{background:#004b93; color:white; padding:20px; margin:10px; border-radius:10px; display:block; text-decoration:none; font-weight:bold;}";
  html += ".on{background:#f39200; box-shadow: 0 0 15px #f39200; border: 2px solid white;}";
  html += ".status-ia{font-size:0.7rem; color:#888;}</style></head><body>";
  
  html += "<h2>Agente Maestro</h2><p>Ecatepec: " + String(temp) + "°C</p>";
  
  for(int i=0; i<3; i++){
    String modo = bloqueoAuto[i] ? " (MANUAL)" : " (AUTO)";
    html += "<a href='/t" + String(i) + "' class='btn " + String(estados[i]?"on":"") + "'>";
    html += (i==0?"Ventilador":i==1?"Humidificador":"Iluminacion") + modo + "</a>";
  }
  
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void activarBloqueo(int index) {
  bloqueoAuto[index] = true;
  tiempoBloqueo[index] = millis();
  Serial.print("Preferencia Manual activada para actuador ");
  Serial.println(index);
}

void setup() {
  Serial.begin(115200);
  for(int i=0; i<3; i++) {
    pinMode(actuadores[i], OUTPUT);
    pinMode(botones[i], INPUT_PULLUP);
  }

  WiFi.begin(ssid, password);
  while(WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  
  Serial.println("\nWiFi Conectado!");
  Serial.print("IP: "); Serial.println(WiFi.localIP());

  server.on("/", manejarRaiz);
  server.on("/t0", []() { estados[0] = !estados[0]; activarBloqueo(0); server.sendHeader("Location", "/"); server.send(303); });
  server.on("/t1", []() { estados[1] = !estados[1]; activarBloqueo(1); server.sendHeader("Location", "/"); server.send(303); });
  server.on("/t2", []() { estados[2] = !estados[2]; activarBloqueo(2); server.sendHeader("Location", "/"); server.send(303); });
  server.begin();
}

void loop() {
  server.handleClient();

  // 1. REVISAR EXPIRACIÓN DE BLOQUEOS MANUALES
  for(int i=0; i<3; i++) {
    if(bloqueoAuto[i] && (millis() - tiempoBloqueo[i] > DURACION_BLOQUEO)) {
      bloqueoAuto[i] = false;
      Serial.print("Control automatico recuperado para actuador ");
      Serial.println(i);
    }
  }

  // 2. REGLAS AUTOMÁTICAS (IA)
  static unsigned long t_clima = 0;
  if(millis() - t_clima > 30000 || t_clima == 0) {
    HTTPClient http;
    http.begin(url_clima);
    if(http.GET() == 200) {
      DynamicJsonDocument doc(1024);
      deserializeJson(doc, http.getString());
      temp = doc["current_weather"]["temperature"];
      viento = doc["current_weather"]["windspeed"];
      hum = 25.0; // Simulando humedad baja para probar humidificador

      // Solo actúa si NO hay bloqueo manual
      if(!bloqueoAuto[0]) estados[0] = (temp > 28.0);
      if(!bloqueoAuto[1]) estados[1] = (hum < 30.0);
      if(!bloqueoAuto[2]) estados[2] = (viento > 20.0);
    }
    http.end();
    t_clima = millis();
  }

  // 3. CONTROL POR BOTONES FÍSICOS (Manual Override)
  for(int i=0; i<3; i++) {
    if(digitalRead(botones[i]) == LOW) {
      estados[i] = !estados[i];
      activarBloqueo(i);
      delay(300);
    }
    digitalWrite(actuadores[i], estados[i]);
  }

  // 4. ACTUALIZAR NUBE (Cada 5 seg)
  static unsigned long t_nube = 0;
  if(millis() - t_nube > 5000) {
    HTTPClient http;
    http.begin(url_nube);
    http.addHeader("Content-Type", "application/json");
    StaticJsonDocument<256> doc;
    doc["id_dispositivo"] = id_dispositivo;
    doc["temp"] = temp; doc["hum"] = hum; doc["viento"] = viento;
    doc["act1"] = estados[0]; doc["act2"] = estados[1]; doc["act3"] = estados[2];
    String json;
    serializeJson(doc, json);
    http.POST(json);
    http.end();
    t_nube = millis();
  }
}