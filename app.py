# app.py - ESP8266 NodeMCU v3 tedte
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

# ... (imports)

def enviar_descoberta(cliente):
    try:
        # 1. Publica a configuração (Discovery)
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        # QoS 1 garante que o broker recebeu
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        print("Payload de descoberta enviado.")
        
        # 2. Aguarda o broker processar
        time.sleep(1) 
        
        # 3. Publica o estado inicial
        cliente.publish(config.TOPICO_ESTADO, "OFF", qos=1, retain=True)
        print("Estado inicial enviado. Home Assistant deve reconhecer.")
    except Exception as e:
        print("Erro na descoberta:", e)

def main():
    global client
    time.sleep(2) 
    
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    client.set_callback(callback_mqtt)
    
    try:
        client.connect()
        # Pequeno delay após conectar para garantir estabilidade da rede
        time.sleep(1) 
        
        # Assina primeiro para garantir que está pronto para receber comandos
        client.subscribe(config.TOPICO_COMANDO)
        
        # Envia a descoberta
        enviar_descoberta(client)
        
        print("ESP8266 Pronto! IP:", client.ifconfig()[0])
        
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro:", e)
        time.sleep(5)
        machine.reset()
# ...   

if __name__ == "__main__":
    main()