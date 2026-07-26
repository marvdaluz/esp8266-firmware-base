# app.py - ESP8266 NodeMCU v3 (Versão Blindada)
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
        # 1. Gerar JSON
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        
        # 2. Validação de Segurança
        if not payload_json or len(payload_json) < 20:
            print("ERRO CRÍTICO: JSON inválido ou vazio!")
            print("Conteúdo gerado:", payload_json)
            return

        # 3. Publicar Configuração (Discovery)
        print(">>> Enviando Discovery (Tamanho:", len(payload_json), "bytes)")
        # QoS 1 e Retain True são obrigatórios para descoberta
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        
        # 4. Aguarda o Broker processar (Essencial no ESP8266)
        time.sleep(2) 
        
        # 5. Publicar Estado Inicial
        cliente.publish(config.TOPICO_ESTADO, "OFF", qos=1, retain=True)
        print(">>> Discovery e Estado enviados com sucesso!")
        
    except Exception as e:
        print("Erro fatal na descoberta:", e)
        # Reinicia se falhar para tentar novamente no próximo boot
        time.sleep(2)
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
                print("Comando desconhecido:", mensagem)
                return
            
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando executado: {estado}")
    except Exception as e:
        print("Erro no callback:", e)

def main():
    global client
    print("Iniciando sistema...")
    time.sleep(2) # Aguarda Wi-Fi do boot.py
    
    # Tenta conectar
    client = MQTTClient(config.CLIENT_ID, config.MQTT_BROKER, 
                        user=config.MQTT_USER, password=config.MQTT_PASS)
    client.set_callback(callback_mqtt)
    
    try:
        client.connect()
        print("Conectado ao Broker MQTT.")
        time.sleep(1) # Estabiliza socket
        
        # Assina o tópico de comando
        client.subscribe(config.TOPICO_COMANDO)
        print("Subscrito em:", config.TOPICO_COMANDO)
        
        # Envia a descoberta
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