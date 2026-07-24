# app.py - ESP8266 NodeMCU v3
from umqtt.simple import MQTTClient
from machine import Pin
import ujson
import time
import gc
import config
import machine

# --- HARDWARE ---
rele = Pin(config.PIN_RELE, Pin.OUT, value=0)
client = None

def enviar_descoberta(cliente):
    try:
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        cliente.publish(config.TOPICO_CONFIG, payload_json, retain=True)
        time.sleep(0.5)
        cliente.publish(config.TOPICO_ESTADO, "OFF", retain=True)
        print("Home Assistant configurado.")
    except Exception as e:
        print("Erro na descoberta:", e)

def callback_mqtt(topic, msg):
    topico = topic.decode('utf-8')
    mensagem = msg.decode('utf-8')
    
    if topico == config.TOPICO_COMANDO:
        if mensagem == "ON":
            rele.value(1)
            estado = "ON"
        else:
            rele.value(0)
            estado = "OFF"
        client.publish(config.TOPICO_ESTADO, estado, retain=True)

def main():
    global client
    # Aguarda Wi-Fi estar pronto (iniciado no boot.py)
    time.sleep(2) 
    
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    client.set_callback(callback_mqtt)
    
    try:
        client.connect()
        enviar_descoberta(client)
        client.subscribe(config.TOPICO_COMANDO)
        print("ESP8266 Pronto! IP:", client.ifconfig()[0])
        
        while True:
            client.check_msg()
            gc.collect() # Limpeza crítica no ESP8266
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro:", e)
        time.sleep(5)
        machine.reset()

if __name__ == "__main__":
    main()   