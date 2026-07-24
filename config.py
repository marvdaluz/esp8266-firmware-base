# config.py - ESP8266 NodeMCU v3
MQTT_BROKER = "10.103.1.30"
MQTT_USER = "mqtt_user"
MQTT_PASS = "p300b795"
CLIENT_ID = "esp8266_lampada_01"

# GPIO 5 (D1 no NodeMCU)
PIN_RELE = 5

# Tópicos MQTT
TOPICO_CONFIG = "homeassistant/light/esp8266_lampada/config"
TOPICO_ESTADO = "casa/lampada/state"
TOPICO_COMANDO = "casa/lampada/set"
# Removido tópico OTA complexo, pois usaremos WebREPL para atualizar

# Payload Home Assistant
CONFIG_PAYLOAD = {
    "name": "Lâmpada ESP8266",
    "unique_id": "esp8266_rele_01",
    "state_topic": TOPICO_ESTADO,
    "command_topic": TOPICO_COMANDO,
    "payload_on": "ON",
    "payload_off": "OFF",
    "qos": 1,
    "device": {
        "identifiers": ["esp8266_nodemcu_v3"],
        "name": "Módulo Relé Sala",
        "model": "NodeMCU v3 (ESP-12E)",
        "manufacturer": "Espressif",
        "sw_version": "MicroPython WebREPL"
    }
}   