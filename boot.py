# boot.py - ESP8266 com conexão Wi-Fi
import network
import time
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

# Fluxo de Inicialização
if conectar_wifi():
    print("Wi-Fi pronto. Iniciando aplicação...")
else:
    print("Iniciando sem Wi-Fi...")

gc.collect()