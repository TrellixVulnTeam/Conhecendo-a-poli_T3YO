from flask import Flask, request, render_template, redirect, url_for, session
import os
from db_create import Banco
from pessoas import Pessoa, Usuario, Coordenador, Adm

app = Flask(__name__)

#print(exemplo_usr.get_classe())

@app.route("/")
def inicio():
    banco = Banco()
    return render_template('inicio.html', eventos = banco.listarEventos2("04/11", "30/12","05","22"))

@app.route("/sugerir", methods = ['POST'])
def sugerir():
    nome = str(request.form["nome"])
    descricao = str(request.form["descricao"])
    local = str(request.form["local"])
    dataIn = str(request.form["data_inicio"])
    horarioIn = str(request.form["hora_inicio"])
    horarioFim = str(request.form["hora_fim"])
    tipo = str(request.form["tipo"])
    assunto = []
    try:
        assunto.append(str(request.form["assunto1"]))
        assunto.append(str(request.form["assunto2"]))
        assunto.append(str(request.form["assunto3"]))
    except:
        print("Erro")
    assunto = ", ".join(assunto)
    print(assunto)
    banco = Banco()
    banco.adicionarEvento(nome, descricao, local, dataIn, horarioIn, horarioFim, tipo, assunto)
    
    return render_template('sugerir_topicos.html', teste = ["Enviado"])

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/logar", methods = ['POST'])
def logar():
    
    usr = str(request.form["usuario"]).title()
    senha = str(request.form["senha"])
    visitante = Pessoa()

    banco = Banco()
    busca =  banco.buscar_pessoa(usr, senha)
    print(busca)
    if len(busca) > 0:    
        x = busca[0]
        usuario = x[1]
        email = x[2]
        classe = x[4]

        session['logged_in'] = True
        if classe == "usuario":
            visitante = Usuario(usuario, senha, email)
        elif classe == "coordenador":
            visitante = Coordenador(usuario, senha, email)
        elif classe == "adm":
            visitante = Adm(usuario, senha, email)
        else:
            print("Um erro com as classes")
            session['logged_in'] = False
    
    visitante.validar()
    try:
        if session['logged_in']:
            return redirect('/')
        else:
            return render_template('login.html', erro_log = True)
    except:
        return "Concerte isso"

@app.route("/sair")
def sair():
    session['logged_in'] = False
    session['user'] = ""
    return redirect('/')

@app.route("/cadastro")
def cadastro():
    return render_template('cadastro.html')

@app.route("/cadastrar", methods = ['POST'])
def cadastrar():
    usr = str(request.form["usuario"]).title()
    email = str(request.form["email"]).title()
    senha = str(request.form["senha"])
    
    banco = Banco()
    if (banco.buscar_pessoa(usr, senha) == []):
        cadastrado =  banco.cadastrar_pessoa(usr, senha, email)
        print(cadastrado)
    else:
        return 'usuário já existente'
    if cadastrado:
        return redirect('/')
    else:
        return render_template('cadastro.html', erro_cad = True)

@app.route("/encontrar_atividades")
def encontrar_atividades():
    banco = Banco()
    return render_template('encontrar_atividades.html', eventos = banco.listarEventos2("04/11", "30/12","05","22"))

@app.route("/grade")
def grade():
    return render_template('grade.html')

@app.route("/sugerir_topicos")
def sugerir_topicos():
    return render_template('sugerir_topicos.html')

@app.route("/aceitar_topicos")
def aceitar_topicos():
    return render_template('aceitar_topicos.html')

@app.route("/gerenciar_colaboradores")
def gerenciar_colaboradores():
    return render_template('gerenciar_colaboradores.html')

app.secret_key = os.urandom(12)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True, debug=True)