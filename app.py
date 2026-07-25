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

# Define a função de callback ANTES de qualquer uso
def callback_mqtt(topic, msg):
    try:
        topico = topic.decode('utf-8')
        mensagem = msg.decode('utf-8')
        
        if topico == config.TOPICO_COMANDO:
            if mensagem == "ON":
                rele.value(1)
                estado = "ON"
            elif mensagem == "OFF":
                rele.value(0)
                estado = "OFF"
            else:
                return # Ignora mensagens inválidas
            
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando recebido: {estado}")
    except Exception as e:
        print("Erro no callback:", e)

def enviar_descoberta(cliente):
    try:
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        # QoS 1 garante entrega
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        time.sleep(1) # Aguarda o broker processar
        cliente.publish(config.TOPICO_ESTADO, "OFF", qos=1, retain=True)
        print("Home Assistant configurado (Discovery enviado).")
    except Exception as e:
        print("Erro na descoberta:", e)

def main():
    global client
    # Aguarda Wi-Fi estar pronto
    time.sleep(2) 
    
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    
    # Registra o callback explicitamente
    client.set_callback(callback_mqtt)
    
    try:
        client.connect()
        time.sleep(1) # Estabiliza conexão
        
        client.subscribe(config.TOPICO_COMANDO)
        print("Subscrito em:", config.TOPICO_COMANDO)
        
        # Envia descoberta após subscrever
        enviar_descoberta(client)
        
        print("ESP8266 Pronto! IP:", client.ifconfig()[0])
        
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro crítico:", e)
        time.sleep(5)
        machine.reset()

if __name__ == "__main__":
    main()   