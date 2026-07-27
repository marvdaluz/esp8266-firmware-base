# app.py - ESP8266 NodeMCU v3
from umqtt.simple import MQTTClient
from machine import Pin
import ujson
import time
import gc
import config
import machine
import senko  # Import do atualizador OTA

# --- HARDWARE ---
# Se o seu relé for Active Low (liga em 0, desliga em 1), altere initial value para 1
rele = Pin(config.PIN_RELE, Pin.OUT, value=0)
client = None

def obter_estado_rele():
    """Retorna a string baseada no estado físico do pino."""
    return "ON" if rele.value() == 1 else "OFF"

def enviar_descoberta(cliente):
    try:
        payload_json = ujson.dumps(config.CONFIG_PAYLOAD)
        
        if len(payload_json) < 10:
            print("ERRO: Payload JSON muito curto ou inválido!")
            return

        print("Enviando Auto-Discovery do Home Assistant...")
        cliente.publish(config.TOPICO_CONFIG, payload_json, qos=1, retain=True)
        
        time.sleep(1)
        # Envia o estado REAL do relé em vez de forçar OFF
        estado_atual = obter_estado_rele()
        cliente.publish(config.TOPICO_ESTADO, estado_atual, qos=1, retain=True)
        print(f"Discovery enviado. Estado publicado: {estado_atual}")
    except Exception as e:
        print("Erro na descoberta:", e)
        machine.reset()   

def callback_mqtt(topic, msg):
    try:
        topico = topic.decode('utf-8')
        mensagem = msg.decode('utf-8').strip()
        
        if topico == config.TOPICO_COMANDO:
            if mensagem == "ON":
                rele.value(1)
            elif mensagem == "OFF":
                rele.value(0)
            else:
                return # Ignora comandos desconhecidos
            
            estado = obter_estado_rele()
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando executado. Relé: {estado}")

        elif topico == config.TOPICO_OTA and mensagem == "CHECK":
            print("Solicitação OTA recebida via MQTT. Verificando atualizações...")
            OTA = senko.Senko(
                user=config.GITHUB_USER,
                repo=config.GITHUB_REPO,
                branch=config.GITHUB_BRANCH,
                files=config.ARQUIVOS_OTA
            )
            if OTA.update():
                print("Atualização encontrada e instalada! Reiniciando...")
                machine.reset()
            else:
                print("Firmware já está na versão mais recente.")

    except Exception as e:
        print("Erro no callback MQTT:", e)

def main():
    global client
    print("Iniciando aplicação...")
    time.sleep(2) # Estabilização
    
    client = MQTTClient(
        config.CLIENT_ID, 
        config.MQTT_BROKER, 
        port=config.MQTT_PORT,
        user=config.MQTT_USER, 
        password=config.MQTT_PASS
    )
    client.set_callback(callback_mqtt)
    
    tentativas = 0
    while tentativas < 5:
        try:
            client.connect()
            print("Conectado ao Broker MQTT.")
            break
        except Exception as e:
            print(f"Falha na conexão MQTT ({tentativas+1}/5):", e)
            time.sleep(2)
            tentativas += 1
    
    if tentativas == 5:
        print("Falha permanente no MQTT. Reiniciando...")
        machine.reset()

    try:
        time.sleep(1) 
        
        # Inscreve nos tópicos de comando e acionamento OTA
        client.subscribe(config.TOPICO_COMANDO)
        client.subscribe(config.TOPICO_OTA)
        print("Subscrito nos tópicos MQTT com sucesso.")
        
        enviar_descoberta(client)
        print("ESP8266 Pronto e operacional!")
        
        # Loop principal
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro fatal no loop principal:", e)
        time.sleep(3)
        machine.reset()

if __name__ == "__main__":
    main()