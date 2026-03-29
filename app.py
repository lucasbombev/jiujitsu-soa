from spyne import Application, rpc, ServiceBase, Integer, Unicode, Array, ComplexModel, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import logging

# Simularemos o banco de dados em memória
CURSOS = [
    {"id": 1, "nome": "Jiu-Jitsu Iniciante", "categoria": "Basico", "valor": 150.0},
    {"id": 2, "nome": "Jiu-Jitsu Competição", "categoria": "Avançado", "valor": 200.0},
    {"id": 3, "nome": "Jiu-Jitsu Kids", "categoria": "Infantil", "valor": 120.0},
]
MATRICULAS = []
_matricula_id_counter = 1

class CursoModel(ComplexModel):
    id = Integer
    nome = Unicode
    categoria = Unicode
    valor = Unicode 

class MatriculaModel(ComplexModel):
    id = Integer
    nome_aluno = Unicode
    cpf = Unicode
    id_curso = Integer
    plano = Unicode
    status = Unicode

class GestorMatriculasService(ServiceBase):
    
    @rpc(Unicode, Unicode, Integer, Unicode, _returns=Integer)
    def registrar_matricula(ctx, nome_aluno, cpf, id_curso, plano):
        global _matricula_id_counter
        curso_existe = any(c['id'] == id_curso for c in CURSOS)
        if not curso_existe:
            raise ValueError("Curso Invalido")
            
        nova_matricula = {
            "id": _matricula_id_counter,
            "nome_aluno": nome_aluno,
            "cpf": cpf,
            "id_curso": id_curso,
            "plano": plano,
            "status": "Ativo"
        }
        MATRICULAS.append(nova_matricula)
        _matricula_id_counter += 1
        return nova_matricula["id"]

    @rpc(Integer, _returns=MatriculaModel)
    def consultar_matricula(ctx, id_matricula):
        for m in MATRICULAS:
            if m["id"] == id_matricula:
                return MatriculaModel(**m)
        return None

    @rpc(_returns=Array(MatriculaModel))
    def listar_matriculas_ativas(ctx):
        ativas = [MatriculaModel(**m) for m in MATRICULAS if m["status"] == "Ativo"]
        return ativas

    @rpc(Unicode, _returns=Array(CursoModel))
    def consultar_cursos(ctx, categoria):
        res = []
        for c in CURSOS:
            if not categoria or c["categoria"].lower() == categoria.lower():
                c_model = CursoModel(id=c["id"], nome=c["nome"], categoria=c["categoria"], valor=str(c["valor"]))
                res.append(c_model)
        return res

application = Application([GestorMatriculasService],
    tns='jiujitsu.escola.services',
    in_protocol=Soap11(),
    out_protocol=Soap11()
)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Iniciando servidor SOAP Gestor de Matrículas em http://127.0.0.1:8000/")
    wsgi_app = WsgiApplication(application)
    server = make_server('127.0.0.1', 8000, wsgi_app)
    server.serve_forever()
