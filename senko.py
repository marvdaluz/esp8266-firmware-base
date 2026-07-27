# senko.py - Biblioteca OTA leve para MicroPython no ESP8266
import urequests
import os
import gc

class Senko:
    def __init__(self, user, repo, url=None, branch="main", files=None):
        self.user = user
        self.repo = repo
        self.url = url
        self.branch = branch
        self.files = files if files else []
        self.headers = {"User-Agent": "MicroPython-ESP8266-OTA"}
        
        # Define a URL base para buscar arquivos Raw no GitHub
        if not self.url:
            self.url = f"https://raw.githubusercontent.com/{self.user}/{self.repo}/{self.branch}"

    def _get_file(self, filename):
        """Baixa o arquivo do GitHub de forma otimizada para economizar RAM."""
        url = f"{self.url}/{filename}"
        response = None
        try:
            gc.collect()
            response = urequests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erro ao buscar {filename}: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Exceção ao baixar {filename}:", e)
            return None
        finally:
            if response:
                response.close()
            gc.collect()

    def update(self):
        """Verifica, baixa e substitui apenas os arquivos que sofreram alteração (1 requisição por arquivo)."""
        updated_any = False
        
        for file in self.files:
            print(f"Verificando {file}...")
            github_code = self._get_file(file)
            
            if github_code is None:
                print(f"Pulado {file} por erro de download.")
                continue

            # Tenta ler o arquivo local
            local_code = ""
            try:
                with open(file, "r") as f:
                    local_code = f.read()
            except OSError:
                # Se não existir localmente, força a gravação
                pass

            # Compara e atualiza apenas se o código mudou
            if github_code != local_code:
                print(f"Atualizações encontradas para {file}. Gravando na flash...")
                try:
                    with open(file, "w") as f:
                        f.write(github_code)
                    print(f"{file} atualizado com sucesso!")
                    updated_any = True
                except Exception as e:
                    print(f"Erro ao gravar {file}:", e)
            else:
                print(f"{file} já está atualizado.")

        return updated_any