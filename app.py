# app.py - Aplicação principal
from umqtt.simple import MQTTClient
from machine import Pin
import ujson
import time
import gc
import config
import machine
# --- HARDWARE ---
# Se o seu relé for Active Low (liga em 0, desliga em 1), altere o valor inicial
rele = Pin(config.PIN_RELE, Pin.OUT, value=0)
client = None
def obter_estado_rele():
    """Retorna a string baseada no estado físico do pino."""
    return "ON" if rele.value() == 1 else "OFF"
def enviar_descoberta(cliente):
    try:
        gc.collect()
        # Envia o Discovery do Switch do Relé
        payload_sw = ujson.dumps(config.CONFIG_PAYLOAD)
        cliente.publish(config.TOPICO_CONFIG, payload_sw, qos=0, retain=True)
        
        time.sleep_ms(200)
        
        # Envia o Discovery do Botão de Atualização OTA
        payload_ota = ujson.dumps(config.CONFIG_OTA_BTN_PAYLOAD)
        cliente.publish(config.TOPICO_CONFIG_OTA_BTN, payload_ota, qos=0, retain=True)
        
        time.sleep_ms(200)
        
        # Publica o estado inicial real do relé
        cliente.publish(config.TOPICO_ESTADO, obter_estado_rele(), qos=0, retain=True)
        print("Discovery do HA e estado inicial enviados!")
    except Exception as e:
        print("Erro ao enviar discovery:", e)
def executar_atualizacao_ota():
    """Executa o Senko sob demanda liberando o máximo de memória possível."""
    global client
    print("Iniciando verificação OTA sob demanda...")
    # 1. Desconecta temporariamente do MQTT para liberar a memória do socket/buffer
    try:
        if client:
            client.disconnect()
            print("Cliente MQTT desconectado temporariamente para liberar RAM.")
    except Exception:
        pass
    # 2. Força a limpeza completa do Garbage Collector
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
            print("Firmware já está atualizado. Nenhuma ação tomada.")
            # Reiniciamos o ESP mesmo se não houver atualização para reestabelecer o estado limpo
            print("Reiniciando para restaurar conexões limpas...")
            time.sleep(1)
            machine.reset()
            
    except Exception as e:
        print("Falha ao executar verificação OTA:", e)
        print("Reiniciando devido a erro no OTA...")
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
        # Inscreve nos tópicos de comando e acionamento OTA
        client.subscribe(config.TOPICO_COMANDO)
        client.subscribe(config.TOPICO_OTA)
        print("Inscrito nos tópicos MQTT com sucesso.")
        
        enviar_descoberta(client)
        print("ESP8266 Pronto e operacional!")
        
        # Loop principal
        while True:
            client.check_msg()
            gc.collect()
            time.sleep(0.1)
            
    except Exception as e:
        print("Erro no loop principal:", e)
        time.sleep(3)
        machine.reset()

if __name__ == "__main__":
    main()