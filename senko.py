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
        
        # Define a URL base para buscar arquivos Raw no GitHub
        if not self.url:
            self.url = f"https://raw.githubusercontent.com/{self.user}/{self.repo}/{self.branch}"

    def _get_file(self, filename):
        """Baixa o arquivo do GitHub de forma otimizada para economizar RAM."""
        url = f"{self.url}/{filename}"
        response = None
        try:
            gc.collect()
            response = urequests.get(url)
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

    def _check_hash(self, filename):
        """Verifica se há diferença entre o arquivo local e o do GitHub."""
        # Se o arquivo local não existir na flash, considera como precisando de atualização
        try:
            os.stat(filename)
        except OSError:
            return True

        github_code = self._get_file(filename)
        if github_code is None:
            return False

        try:
            with open(filename, "r") as f:
                local_code = f.read()
            return github_code != local_code
        except Exception as e:
            print(f"Erro ao ler arquivo local {filename}:", e)
            return False

    def fetch(self):
        """Verifica quais arquivos precisam de atualização."""
        changes = []
        for file in self.files:
            if self._check_hash(file):
                changes.append(file)
        return changes

    def update(self):
        """Baixa e substitui os arquivos desatualizados."""
        changes = self.fetch()
        if not changes:
            return False

        print(f"Arquivos com atualizações pendentes: {changes}")
        
        for file in changes:
            print(f"Atualizando {file}...")
            new_code = self._get_file(file)
            if new_code is not None:
                try:
                    # Sobreve o arquivo na memória Flash
                    with open(file, "w") as f:
                        f.write(new_code)
                    print(f"{file} atualizado com sucesso!")
                except Exception as e:
                    print(f"Erro ao gravar {file}:", e)
                    return False
            else:
                print(f"Falha ao obter código de {file}")
                return False

        return True