# app.py - Aplicação principal
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

def obter_estado_rele():
    """Retorna a string baseada no estado físico do pino."""
    return "ON" if rele.value() == 1 else "OFF"

def enviar_descoberta(cliente):
    gc.collect()
    
    # 1. Envia o Discovery da Lâmpada
    try:
        payload_sw = ujson.dumps(config.CONFIG_PAYLOAD)
        cliente.publish(config.TOPICO_CONFIG, payload_sw, qos=0, retain=True)
        print("Discovery da Lâmpada enviado.")
    except Exception as e:
        print("Erro ao enviar discovery da lâmpada:", e)
        
    time.sleep_ms(300)
    
    # 2. Envia o Discovery do Botão OTA
    try:
        payload_ota = ujson.dumps(config.CONFIG_OTA_BTN_PAYLOAD)
        cliente.publish(config.TOPICO_CONFIG_OTA_BTN, payload_ota, qos=0, retain=True)
        print("Discovery do Botão OTA enviado.")
    except Exception as e:
        print("Erro ao enviar discovery do OTA:", e)
        
    time.sleep_ms(300)
    
    # 3. Publica o estado inicial do relé
    try:
        cliente.publish(config.TOPICO_ESTADO, obter_estado_rele(), qos=0, retain=True)
        print("Estado inicial enviado!")
    except Exception as e:
        print("Erro ao enviar estado inicial:", e)
        
def executar_atualizacao_ota():
    """Executa o Senko sob demanda liberando o máximo de memória possível."""
    global client
    print("Iniciando verificação OTA sob demanda...")
    try:
        if client:
            client.disconnect()
            print("Cliente MQTT desconectado temporariamente para liberar RAM.")
    except Exception:
        pass
        
    gc.collect()
    time.sleep_ms(500)

    try:
        import senko
        
        ota = senko.Senko(
            user=config.GITHUB_USER,
            repo=config.GITHUB_REPO,
            branch=config.GITHUB_BRANCH,
            files=config.ARQUIVOS_OTA
        )
        
        if ota.update():
            print("Atualização realizada com sucesso! Reiniciando o dispositivo...")
            time.sleep(2)
            machine.reset()
        else:
            print("Firmware já está atualizado. Reiniciando para restaurar conexões...")
            time.sleep(1)
            machine.reset()
            
    except Exception as e:
        print("Falha ao executar verificação OTA:", e)
        time.sleep(2)
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
                return
            
            estado = obter_estado_rele()
            client.publish(config.TOPICO_ESTADO, estado, retain=True)
            print(f"Comando executado. Relé: {estado}")

        elif topico == config.TOPICO_OTA and mensagem == "CHECK":
            print("Comando de OTA manual recebido via MQTT!")
            executar_atualizacao_ota()

    except Exception as e:
        print("Erro no callback MQTT:", e)

def main():
    global client
    print("Iniciando aplicação principal...")
    time.sleep(1)
    
    client = MQTTClient(
        config.CLIENT_ID, 
        config.MQTT_BROKER, 
        port=config.MQTT_PORT,
        user=config.MQTT_USER, 
        password=config.MQTT_PASS,
        keepalive=60
    )
    client.set_callback(callback_mqtt)
    
    tentativas = 0
    while tentativas < 5:
        try:
            client.connect()
            print("Conectado ao Broker MQTT com sucesso.")
            break
        except Exception as e:
            print(f"Falha na conexão MQTT ({tentativas+1}/5):", e)
            time.sleep(2)
            tentativas += 1
    
    if tentativas == 5:
        print("Falha permanente no MQTT. Reiniciando...")
        machine.reset()

    try:
        client.subscribe(config.TOPICO_COMANDO)
        client.subscribe(config.TOPICO_OTA)
        print("Inscrito nos tópicos MQTT com sucesso.")
        
        enviar_descoberta(client)
        print("ESP8266 Pronto e operacional!")
        
        ultimo_ping = time.time()
        
        # Loop principal
        while True:
            client.check_msg()
            
            # Envia Ping PINGREQ a cada 30 segundos para manter a conexão viva no broker
            if time.time() - ultimo_ping > 30:
                client.ping()
                ultimo_ping = time.time()
                
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro no loop principal:", e)
        time.sleep(3)
        machine.reset()

if __name__ == "__main__":
    main()