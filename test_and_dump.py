import time
import subprocess
import urllib.request
import sys

def main():
    # Inicia o servidor em background
    print("Iniciando o servidor SOAP para extrair o WSDL...")
    proc = subprocess.Popen([sys.executable, "app.py"])
    time.sleep(2) # Aguarda o servidor inicializar
    
    try:
        # Faz o download do WSDL gerado via GET
        print("Mapeando o WSDL...")
        req = urllib.request.urlopen("http://127.0.0.1:8000/?wsdl")
        wsdl_content = req.read()
        
        # O XSD já está embutido (<wsdl:types><xs:schema...>)
        with open("jiujitsu_service.wsdl", "wb") as f:
            f.write(wsdl_content)
        print("Sucesso! WSDL salvo como 'jiujitsu_service.wsdl'")
        
    except Exception as e:
        print(f"Erro ao extrair WSDL: {e}")
    finally:
        # Encerra o servidor local
        proc.terminate()
        proc.wait()
        print("Servidor finalizado.")

if __name__ == "__main__":
    main()
