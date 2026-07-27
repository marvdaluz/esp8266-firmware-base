# --- CREDENCIAIS WI-FI ---
WIFI_SSID = "Ubuntu"
WIFI_PASS = "27734056"
# --- CONFIGURAÇÃO GITHUB / SENKO OTA ---
GITHUB_USER = "marvdaluz"
GITHUB_REPO = "esp8266-firmware-base"
GITHUB_BRANCH = "main"
ARQUIVOS_OTA = ["boot.py", "app.py", "senko.py", "main.py"]
# --- CREDENCIAIS MQTT ---
MQTT_BROKER = "10.103.1.30"
MQTT_PORT = 1883
MQTT_USER = "mqtt_user"
MQTT_PASS = "p300b795"
CLIENT_ID = "esp8266_lampada_01"
# --- HARDWARE ---
PIN_RELE = 5
# --- TÓPICOS MQTT ---
TOPICO_CONFIG = "homeassistant/switch/esp8266_lampada_01/config"
TOPICO_ESTADO = "casa/lampada_01/state"
TOPICO_COMANDO = "casa/lampada_01/set"
TOPICO_OTA = "casa/lampada/ota"
# --- PAYLOAD MINIMALISTA ---
CONFIG_PAYLOAD = {
    "name": "Lampada Sala",
    "unique_id": "esp8266_lampada_01_sw",
    "state_topic": TOPICO_ESTADO,
    "command_topic": TOPICO_COMANDO,
    "payload_on": "ON",
    "payload_off": "OFF",
    "device": {
        "identifiers": ["esp8266_lampada_01"],
        "name": "Rele Sala"
    }
}
    }
}