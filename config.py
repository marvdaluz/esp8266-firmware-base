# config.py - ESP8266 NodeMCU v3

# --- CREDENCIAIS WI-FI ---
WIFI_SSID = "Ubuntu"
WIFI_PASS = "27734056"

# --- CONFIGURAÇÃO GITHUB / SENKO OTA ---
GITHUB_USER = "marvdaluz"
GITHUB_REPO = "esp8266-firmware-base"
GITHUB_BRANCH = "main"

# IMPORTANTE: "config.py" NÃO deve estar nesta lista!
ARQUIVOS_OTA = ["boot.py", "app.py", "senko.py", "main.py"]

# --- CREDENCIAIS MQTT ---
MQTT_BROKER = "10.103.1.30"
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASS = "p300b795"
CLIENT_ID = "esp8266_lampada_01"

# --- HARDWARE ---
# GPIO 5 (pino D1 no NodeMCU v3)
PIN_RELE = 5

# --- TÓPICOS MQTT ---
# Usando 'light' para o Home Assistant reconhecer nativamente como iluminação
TOPICO_CONFIG = "homeassistant/light/esp8266_lampada_01/config"
TOPICO_ESTADO = "casa/lampada_01/state"
TOPICO_COMANDO = "casa/lampada_01/set"
TOPICO_OTA = "casa/lampada/ota"

# --- PAYLOAD HOME ASSISTANT DISCOVERY ---
CONFIG_PAYLOAD = {
    "name": "Lampada Sala 01",
    "unique_id": "esp8266_lampada_01_light",
    "state_topic": TOPICO_ESTADO,
    "command_topic": TOPICO_COMANDO,
    "payload_on": "ON",
    "payload_off": "OFF",
    "qos": 1,
    "retain": True,
    "device": {
        "identifiers": ["esp8266_lampada_01"],
        "name": "Modulo Rele Sala (ESP8266)",
        "model": "NodeMCU v3 (ESP-12E)",
        "manufacturer": "Espressif",
        "sw_version": "MicroPython v1.28 OTA"
    }
}