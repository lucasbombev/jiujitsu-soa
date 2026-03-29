import subprocess
import time
import sys

def main():
    print("Iniciando app.py...")
    proc = subprocess.Popen([sys.executable, "app.py"])
    time.sleep(3)
    
    try:
        from zeep import Client
        client = Client('http://127.0.0.1:8000/?wsdl')
        
        print("\n--- Consultando todos os cursos ---")
        cursos = client.service.consultar_cursos(None)
        # O retorno é um Array, que o zeep empacota em um dict ou list dependendo da versão
        if cursos and hasattr(cursos, 'CursoModel'):
            lista_cursos = cursos.CursoModel
        else:
            lista_cursos = cursos
            
        for c in lista_cursos:
            print(f"Curso {c.id}: {c.nome} ({c.categoria}) - R$ {c.valor}")
            
        print("\n--- Registrando matricula ---")
        matricula_id = client.service.registrar_matricula(
            nome_aluno="Bruce Lee", 
            cpf="111.222.333-44", 
            id_curso=2, 
            plano="ANUAL"
        )
        print(f"Nova Matricula Registrada! ID: {matricula_id}")
        
        print("\n--- Listando Ativas ---")
        ativas = client.service.listar_matriculas_ativas()
        if ativas and hasattr(ativas, 'MatriculaModel'):
            lista_ativas = ativas.MatriculaModel
        else:
            lista_ativas = ativas

        for a in lista_ativas:
            print(f"Matricula {a.id}: {a.nome_aluno} ({a.cpf}) - Curso ID: {a.id_curso} - Status: {a.status}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        proc.terminate()
        proc.wait()
        print("\nTestes OK. Servidor finalizado.")

if __name__ == "__main__":
    main()
