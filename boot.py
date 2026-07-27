# boot.py - ESP8266 com Senko OTA
import network
import time
import machine
import gc
import config

gc.collect()

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando ao Wi-Fi...')
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
        
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            
    if wlan.isconnected():
        print('Wi-Fi Conectado! IP:', wlan.ifconfig()[0])
        return True
    else:
        print('Falha na conexão Wi-Fi.')
        return False

def verificar_ota():
    if config.GITHUB_USER == "SEU_USUARIO_GITHUB":
        print("Aviso OTA: Atualize o GITHUB_USER no config.py com seu usuário real.")
        return

    try:
        gc.collect() # Libera RAM antes de abrir socket HTTPS
        import senko
        print("Verificando atualizações no GitHub...")
        
        ota = senko.Senko(
            user=config.GITHUB_USER,
            repo=config.GITHUB_REPO,
            branch=config.GITHUB_BRANCH,
            files=config.ARQUIVOS_OTA
        )
        
        if ota.update():
            print("Atualização realizada! Reiniciando...")
            time.sleep(2)
            machine.reset()
        else:
            print("Sistema atualizado.")
            
    except Exception as e:
        print("Erro no OTA Senko:", e)
    finally:
        gc.collect()

# Fluxo de Inicialização
if conectar_wifi():
    verificar_ota()
    print("Iniciando aplica��ão principal...")
else:
    print("Iniciando sem Wi-Fi/OTA...")

gc.collect()