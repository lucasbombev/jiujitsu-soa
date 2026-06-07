import time
import subprocess
import urllib.request
import sys
from lxml import etree

def main():
    # Inicia o servidor em background
    print("Iniciando o servidor SOAP para extrair o WSDL e o XSD...")
    proc = subprocess.Popen([sys.executable, "app.py"])
    time.sleep(3) # Aguarda o servidor inicializar
    
    try:
        # Faz o download do WSDL gerado via GET
        print("Mapeando o WSDL...")
        req = urllib.request.urlopen("http://127.0.0.1:8000/?wsdl")
        wsdl_content = req.read()
        
        # Salva o WSDL
        with open("jiujitsu_service.wsdl", "wb") as f:
            f.write(wsdl_content)
        print("Sucesso! WSDL salvo como 'jiujitsu_service.wsdl'")
        
        # Extrai o XSD
        root = etree.fromstring(wsdl_content)
        ns = {
            'wsdl': 'http://schemas.xmlsoap.org/wsdl/',
            'xs': 'http://www.w3.org/2001/XMLSchema'
        }
        schema_element = root.xpath('//wsdl:types/xs:schema', namespaces=ns)
        if schema_element:
            xsd_content = etree.tostring(schema_element[0], pretty_print=True, xml_declaration=True, encoding='UTF-8')
            with open("jiujitsu_service.xsd", "wb") as f:
                f.write(xsd_content)
            print("Sucesso! XSD extraído e salvo como 'jiujitsu_service.xsd'")
        else:
            print("Erro: Não foi possível encontrar a tag <xs:schema> no WSDL.")
            
    except Exception as e:
        print(f"Erro ao extrair WSDL/XSD: {e}")
    finally:
        # Encerra o servidor local
        proc.terminate()
        proc.wait()
        print("Servidor finalizado.")

if __name__ == "__main__":
    main()
