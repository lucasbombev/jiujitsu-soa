import subprocess
import time
import sys
import os
import sys

def main():
    # Remover o banco de dados antigo para garantir um teste limpo
    if os.path.exists("jiujitsu.db"):
        try:
            os.remove("jiujitsu.db")
            print("Banco de dados jiujitsu.db removido para iniciar os testes do zero.")
        except Exception as e:
            print(f"Aviso ao remover banco de dados: {e}")

    # Remover o arquivo de logs anterior
    if os.path.exists("jiujitsu_service.log"):
        try:
            os.remove("jiujitsu_service.log")
            print("Log do servidor anterior limpo.")
        except Exception as e:
            print(f"Aviso ao remover log antigo: {e}")

    print("Iniciando o servidor SOAP (app.py) em background...")
    proc = subprocess.Popen([sys.executable, "app.py"])
    time.sleep(3) # Aguarda o servidor inicializar
    
    try:
        from zeep import Client
        from zeep.wsse import UsernameToken
        
        # Cliente 1: Público (sem headers de segurança)
        client_public = Client('http://127.0.0.1:8000/?wsdl')
        
        # Cliente 2: Autenticado com credenciais corretas
        client_secure = Client('http://127.0.0.1:8000/?wsdl', wsse=UsernameToken('admin', 'senha_jiujitsu_123'))
        
        # Cliente 3: Autenticado com credenciais incorretas
        client_bad_auth = Client('http://127.0.0.1:8000/?wsdl', wsse=UsernameToken('admin', 'senha_errada'))
        
        print("\n==================================================")
        print("INICIANDO SUÍTE DE TESTES DO SERVIÇO SOAP DE JIU-JITSU")
        print("==================================================")
        
        # --------------------------------------------------
        # TESTE 1: Consultar Cursos (Operação Pública)
        # --------------------------------------------------
        print("\nTESTE 1: Consultar Cursos (Público, sem cabeçalho de segurança)...")
        try:
            cursos = client_public.service.consultar_cursos(None)
            lista_cursos = cursos.CursoModel if cursos and hasattr(cursos, 'CursoModel') else cursos
            print(f"Sucesso! Cursos cadastrados encontrados: {len(lista_cursos)}")
            for c in lista_cursos:
                print(f" - Curso ID {c.id}: {c.nome} ({c.categoria}) - R$ {c.valor}")
        except Exception as e:
            print(f"FALHA NO TESTE 1: {e}")
            
        # --------------------------------------------------
        # TESTE 2: Registrar Matrícula Sem Autenticação (Operação Protegida)
        # --------------------------------------------------
        print("\nTESTE 2: Registrar Matrícula Sem Autenticação (Deve falhar)...")
        try:
            client_public.service.registrar_matricula(
                nome_aluno="Rickson Gracie",
                cpf="222.333.444-55",
                id_curso=2,
                plano="SEMESTRAL"
            )
            print("FALHA: A operação deveria ter sido bloqueada por falta de credenciais!")
        except Exception as e:
            print(f"Sucesso! Operação bloqueada como esperado. Erro retornado: {e}")
            
        # --------------------------------------------------
        # TESTE 3: Registrar Matrícula Com Senha Incorreta (Operação Protegida)
        # --------------------------------------------------
        print("\nTESTE 3: Registrar Matrícula Com Senha Incorreta (Deve falhar)...")
        try:
            client_bad_auth.service.registrar_matricula(
                nome_aluno="Rickson Gracie",
                cpf="222.333.444-55",
                id_curso=2,
                plano="SEMESTRAL"
            )
            print("FALHA: A operação deveria ter sido bloqueada por credenciais incorretas!")
        except Exception as e:
            print(f"Sucesso! Operação bloqueada como esperado. Erro retornado: {e}")
            
        # --------------------------------------------------
        # TESTE 4: Registrar Matrícula Com Credenciais Corretas (Operação Protegida)
        # --------------------------------------------------
        print("\nTESTE 4: Registrar Matrícula Com Credenciais Corretas (Deve funcionar)...")
        matricula_id = None
        try:
            matricula_id = client_secure.service.registrar_matricula(
                nome_aluno="Rickson Gracie",
                cpf="222.333.444-55",
                id_curso=2,
                plano="SEMESTRAL"
            )
            print(f"Sucesso! Matrícula registrada no banco de dados. ID Gerado: {matricula_id}")
        except Exception as e:
            print(f"FALHA NO TESTE 4: {e}")
            
        # --------------------------------------------------
        # TESTE 5: Consultar Matrícula Recém Criada (Operação Pública)
        # --------------------------------------------------
        if matricula_id:
            print(f"\nTESTE 5: Consultar Matrícula ID {matricula_id} (Público)...")
            try:
                m = client_public.service.consultar_matricula(matricula_id)
                if m:
                    print("Sucesso! Detalhes da matrícula:")
                    print(f" - Aluno: {m.nome_aluno}")
                    print(f" - CPF: {m.cpf}")
                    print(f" - Curso ID: {m.id_curso}")
                    print(f" - Plano: {m.plano}")
                    print(f" - Status: {m.status}")
                else:
                    print(f"FALHA: Matrícula ID {matricula_id} não encontrada.")
            except Exception as e:
                print(f"FALHA NO TESTE 5: {e}")
                
        # --------------------------------------------------
        # TESTE 6: Listar Matrículas Ativas (Operação Protegida)
        # --------------------------------------------------
        print("\nTESTE 6: Listar Matrículas Ativas com Autenticação...")
        try:
            ativas = client_secure.service.listar_matriculas_ativas()
            lista_ativas = ativas.MatriculaModel if ativas and hasattr(ativas, 'MatriculaModel') else ativas
            print(f"Sucesso! Matrículas ativas encontradas: {len(lista_ativas)}")
            for a in lista_ativas:
                print(f" - Inscrição {a.id}: {a.nome_aluno} - Status: {a.status}")
        except Exception as e:
            print(f"FALHA NO TESTE 6: {e}")
            
        # --------------------------------------------------
        # TESTE 7: Atualizar Status da Matrícula (Operação Protegida)
        # --------------------------------------------------
        if matricula_id:
            print(f"\nTESTE 7: Atualizar Status da Matrícula ID {matricula_id} para 'Inativo'...")
            try:
                sucesso = client_secure.service.atualizar_status_matricula(matricula_id, "Inativo")
                if sucesso:
                    print("Sucesso! Status da matrícula alterado no banco de dados.")
                    # Verificar se o status realmente mudou
                    m = client_public.service.consultar_matricula(matricula_id)
                    print(f" - Novo status confirmado no banco: {m.status}")
                else:
                    print("FALHA: Retornou falso ao tentar atualizar.")
            except Exception as e:
                print(f"FALHA NO TESTE 7: {e}")
                
        # --------------------------------------------------
        # TESTE 8: Deletar Matrícula (Operação Protegida)
        # --------------------------------------------------
        if matricula_id:
            print(f"\nTESTE 8: Deletar Matrícula ID {matricula_id} (CRUD - Delete)...")
            try:
                sucesso = client_secure.service.deletar_matricula(matricula_id)
                if sucesso:
                    print("Sucesso! Matrícula deletada fisicamente do banco de dados.")
                    # Confirmar que não existe mais
                    m = client_public.service.consultar_matricula(matricula_id)
                    if m is None:
                        print(" - Confirmação: Matrícula não foi mais localizada (sucesso).")
                    else:
                        print(" - FALHA: Matrícula ainda existe após exclusão.")
                else:
                    print("FALHA: Retornou falso ao deletar.")
            except Exception as e:
                print(f"FALHA NO TESTE 8: {e}")

        print("\n==================================================")
        print("SUÍTE DE TESTES CONCLUÍDA COM SUCESSO!")
        print("==================================================")

    except Exception as e:
        print(f"\nErro geral na execução do script de teste: {e}")
    finally:
        # Finaliza o servidor
        print("\nFinalizando o servidor local...")
        proc.terminate()
        proc.wait()
        print("Servidor finalizado. Testes concluídos.")

if __name__ == "__main__":
    main()
