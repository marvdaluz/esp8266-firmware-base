# config.py - Configurações do dispositivo
import network
# --- CREDENCIAIS WI-FI ---
WIFI_SSID = "Ubuntu"
WIFI_PASS = "27734056"
# --- CONFIGURAÇÃO GITHUB / SENKO OTA ---
GITHUB_USER = "marvdaluz"
GITHUB_REPO = "esp8266-firmware-base"
GITHUB_BRANCH = "main"
# Atualizamos apenas os arquivos de aplicação via OTA
ARQUIVOS_OTA = ["app.py", "main.py", "config.py"]
# --- CREDENCIAIS MQTT ---
MQTT_BROKER = "10.103.1.30"
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASS = "p300b795"
CLIENT_ID = "esp8266_lampada_01"
# --- HARDWARE ---
PIN_RELE = 5
# --- TÓPICOS MQTT ---
TOPICO_CONFIG = "homeassistant/light/esp8266_lampada_01/config"
TOPICO_CONFIG_OTA_BTN = "homeassistant/button/esp8266_lampada_01_ota/config"
TOPICO_ESTADO = "casa/lampada_01/state"
TOPICO_COMANDO = "casa/lampada_01/set"
TOPICO_OTA = "casa/lampada/ota"

CONFIG_PAYLOAD = {
    "name": "Lampada Sala",
    "uniq_id": "esp8266_lampada_01_light",
    "stat_t": TOPICO_ESTADO,
    "cmd_t": TOPICO_COMANDO,
    "pl_on": "ON",
    "pl_off": "OFF",
    "dev": {
        "ids": ["esp8266_lampada_01"],
        "name": "Lampada da Sala"
    }
}
# --- PAYLOAD DISCOVERY (BOTÃO OTA) ---
CONFIG_OTA_BTN_PAYLOAD = {
    "name": "Atualizar Firmware OTA",
    "unique_id": "esp8266_lampada_01_ota_btn",
    "command_topic": TOPICO_OTA,
    "payload_press": "CHECK",
    "icon": "mdi:system-update",
    "device": {
        "identifiers": ["esp8266_lampada_01"],
        "name": "Lampada da Sala"
    }
}