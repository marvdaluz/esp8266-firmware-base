# boot.py - ESP8266 com Senko OTA
import network
import time
import machine
import gc

# --- CONFIGURAÇÃO WI-FI ---
WIFI_SSID = "Ubuntu"
WIFI_PASS = "27734056"

# --- CONFIGURAÇÃO SENKO ---
# Substitua pelos seus dados do GitHub
GITHUB_USER = "SEU_USUARIO_GITHUB"
GITHUB_REPO = "NOME_DO_REPOSITORIO"
GITHUB_BRANCH = "master"  # ou "main"
# Lista de arquivos que serão sincronizados
ARQUIVOS_OTA = ["boot.py", "config.py", "app.py", "main.py"]

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Conectando ao Wi-Fi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1)
            tentativas += 1
            
    if wlan.isconnected():
        print('Wi-Fi OK. IP:', wlan.ifconfig()[0])
        return True
    else:
        print('Falha no Wi-Fi.')
        return False

def verificar_ota():
    try:
        import senko
        print("Verificando atualizações no GitHub...")
        
        # Inicializa o objeto Senko
        ota = senko.Senko(
            user=GITHUB_USER,
            repo=GITHUB_REPO,
            branch=GITHUB_BRANCH,
            files=ARQUIVOS_OTA
        )
        
        # Verifica e atualiza se houver versão nova
        if ota.update():
            print("Atualização realizada! Reiniciando...")
            time.sleep(2)
            machine.reset()
        else:
            print("Sistema atualizado.")
            
    except Exception as e:
        print("Erro no OTA Senko:", e)

# Fluxo de Inicialização
gc.collect()
if conectar_wifi():
    verificar_ota()
    # Se não reiniciou, continua para o main.py
    print("Iniciando aplicação...")
else:
    print("Iniciando sem Wi-Fi/OTA...")   