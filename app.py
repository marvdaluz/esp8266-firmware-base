# app.py - ESP8266 NodeMCU v3 (Versão Corrigida)
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
        
        # Debug: Verifica se o JSON foi gerado
        if len(payload_json) < 10:
            print("ERRO: Payload JSON muito curto ou inválido!")
            return

        print("Enviando Discovery:", payload_json) # Imprime no console serial
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        
        time.sleep(2)
        cliente.publish(config.TOPICO_ESTADO, "OFF", qos=1, retain=True)
        print("Discovery e Estado enviados com sucesso.")
    except Exception as e:
        print("Erro fatal na descoberta:", e)
        machine.reset()   

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
                return # Ignora payloads inválidos
            
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando executado: {estado}")
    except Exception as e:
        print("Erro no callback:", e)

def main():
    global client
    print("Iniciando conexão...")
    time.sleep(2) # Aguarda Wi-Fi do boot.py estabilizar
    
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    client.set_callback(callback_mqtt)
    
    tentativas = 0
    while tentativas < 5:
        try:
            client.connect()
            print("Conectado ao Broker MQTT.")
            break
        except Exception as e:
            print(f"Falha na conexão MQTT ({tentativas}):", e)
            time.sleep(2)
            tentativas += 1
    
    if tentativas == 5:
        print("Falha permanente no MQTT. Reiniciando...")
        machine.reset()

    try:
        # Pequeno delay pós-conexão para garantir estabilidade do socket
        time.sleep(1) 
        
        client.subscribe(config.TOPICO_COMANDO)
        print("Subscrito em:", config.TOPICO_COMANDO)
        
        # Envia a descoberta APÓS subscrever e estabilizar
        enviar_descoberta(client)
        
        print("ESP8266 Pronto! IP:", client.ifconfig()[0])
        
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro fatal no loop:", e)
        time.sleep(5)
        machine.reset()

if __name__ == "__main__":
    main()   