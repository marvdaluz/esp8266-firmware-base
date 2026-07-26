# app.py - ESP8266 NodeMCU v3 (Correção Final de Tópicos)
from umqtt.simple import MQTTClient
from machine import Pin
import ujson
import time
import gc
import config
import machine

rele = Pin(config.PIN_RELE, Pin.OUT, value=0)
client = None

def enviar_descoberta(cliente):
    try:
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        
        # GARANTIA: Publicar APENAS no tópico de CONFIG
        print(f"Publicando CONFIG em: {config.TOPICO_CONFIG}")
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        
        time.sleep(2) # Aguarda processamento
        
        # GARANTIA: Publicar APENAS no tópico de ESTADO
        print(f"Publicando ESTADO em: {config.TOPICO_ESTADO}")
        cliente.publish(config.TOPICO_ESTADO, "OFF", qos=1, retain=True)
        
        print("Descoberta enviada corretamente.")
    except Exception as e:
        print("Erro na descoberta:", e)
        machine.reset()

def callback_mqtt(topic, msg):
    try:
        topico = topic.decode('utf-8')
        mensagem = msg.decode('utf-8')
        
        # Verifica EXATAMENTE o tópico de comando definido no config
        if topico == config.TOPICO_COMANDO:
            if mensagem == "ON":
                rele.value(1)
                estado = "ON"
            elif mensagem == "OFF":
                rele.value(0)
                estado = "OFF"
            else:
                return # Ignora outros payloads
            
            # Publica o estado APENAS no tópico de estado
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando: {estado} -> Publicado em {config.TOPICO_ESTADO}")
    except Exception as e:
        print("Erro callback:", e)

def main():
    global client
    time.sleep(2)
    
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    client.set_callback(callback_mqtt)
    
    try:
        client.connect()
        time.sleep(1)
        client.subscribe(config.TOPICO_COMANDO)
        
        # Reenvia a descoberta a cada boot para garantir
        enviar_descoberta(client)
        
        print("Sistema Online. IP:", client.ifconfig()[0])
        
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
    except Exception as e:
        print("Erro:", e)
        machine.reset()

if __name__ == "__main__":
    main()   