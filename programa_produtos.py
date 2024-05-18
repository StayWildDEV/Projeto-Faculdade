# aqui vão ficar os comandos da aplicação

# pip install flask

from flask import Flask, render_template, request, redirect, flash, session, url_for
import sys

from flask_sqlalchemy import SQLAlchemy

# abaixo é criada a variavel de aplicação
app = Flask(__name__)

# a linha abaixo é a chave de segurança da aplicação
app.secret_key = 'aprendendodoiniciocomdaniel'

app.config['SQLALCHEMY_DATABASE_URI'] = \
    '{SGBD}://{usuario}:{senha}@{servidor}/{database}'.format(
        SGBD='mysql+mysqlconnector',
        usuario='root',
        senha='baladar1',
        servidor='localhost',
        database='loja'
    )

db = SQLAlchemy(app)


class Produto(db.Model):
    id_produto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_produto = db.Column(db.String(50), nullable=False)
    marca_produto = db.Column(db.String(30), nullable=True)
    preco_produto = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name


class Usuarios(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome_usuario = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    senha = db.Column(db.String(120), nullable=False)


# a linha abaixo eu crio uma rota
@app.route("/inicio")
def ola():
    return "<h2>iniciando com o flask</h2>"


# a rota abaixo chama a lista de produtos
@app.route("/lista")
def lista_produtos():
    try:
        # A Linha abaixo valida se o usuario tem permissão Acessar ou não .
        if 'usuario_logado' not in session or session['usuario_logado'] == None:
            return redirect('/login')
        prod_cadastrados = Produto.query.order_by(Produto.id_produto)
        return render_template("lista.html", descricao_pagina="Aqui estão todos os produtos de dados",
                               todos_produtos=prod_cadastrados)
    except:
        return redirect('/login')


@app.route('/cadastrar')
def cadastrar_produto():
    try:
        if session['usuario_logado'] != None:
            return render_template('cad_produto.html')

        if 'usuario_logado' not in session or session['usuario_logado'] == None:
            return redirect('/login')
    except:
        return redirect('/login')


# Aqui inicia a parte dde edição do produto
# Ele está como INT pois dentro do DB está int | quando está dentro de <> estou dizendo que esta variável é rotativa
@app.route('/editar/<int:id>')
def editar_produto(id):
    produto_selecionado = Produto.query.filter_by(
        id_produto=id).first()

    return render_template('editar.html', produto=produto_selecionado)


# a rota abaixo é responsavel por adicionar
@app.route('/adicionar', methods=['POST', ])
def adicionar_produto():
    # as linhas abaixo fazem a captação dos dados dos formularios
    nome_recebido = request.form['txtNome']
    marca_recebido = request.form['txtMarca']

    preco_recebido = request.form['txtPreco'].replace(',', '.')
    preco_recebido = float(preco_recebido)

    # linha abaixo é a variavel que prepara os dados para enviar para o banco de dados
    add_produto = Produto(nome_produto=nome_recebido, marca_produto=marca_recebido, preco_produto=preco_recebido)

    # a linha abaixo adiciona a variavel para ser inserida na tabela
    db.session.add(add_produto)

    # a linha abaixo envia as informacoes para o banco de dados
    db.session.commit()

    # a linha abaixo envia a mensagem para apresentar para o usuario
    flash("Produto cadastrado com sucesso!!!")

    return redirect('/lista')


@app.route('/atualizar', methods={"POST", })
def atualizar():
    produto_selecionado = Produto.query.filter_by(
        id_produto=request.form["txtId"]).first()

    # As linhas abaixo atualiza cada campo na tabela do Banco
    # com base nas informações passadas pelo usuario
    produto_selecionado.nome_produto = request.form["txtNome"]
    produto_selecionado.marca_produto = request.form["txtMarca"]
    produto_selecionado.preco_produto = float(request.form["txtPreco"])

    # A Linha abaixo adiciona as informações na camada para enviar
    # Para o banco de dados
    db.session.add(produto_selecionado)

    # A Linha abaixo manda as informações para o banco de dados
    db.session.commit()
    return redirect('/lista')


# **** A ROTA ABAIXOSE TRATA DE EXCLUIR O PRODUTO
@app.route('/excluir/<int:id>')
def excluir_produto(id):
    # a linha abaixo exclui o registro do banco de dados
    Produto.query.filter_by(id_produto=id).delete()

    # a linha abaixo commita as informções para a base de dados
    db.session.commit()

    return redirect('/lista')


@app.route('/login')
def login_usuario():
    try:
        print('oi')
        alerta = request.args['alerta']
        if session['usuario_logado'] == None:
            print('oi2')
            if alerta:
                print('oi3')
                return render_template('login.html', alerta=alerta)
    except:
            return render_template('login.html')

        # A Linha abaixo valida se o usuario tem permissão Acessar ou não .


# essa é a rota miassensivel da aplicação

@app.route('/autenticar', methods=['POST', ])
def autenticar_usuario():
    # A Linha abaixo verifica se a senha e login são "admin"
    login = request.form['txtLogin']
    senha = request.form['txtSenha']
    usuarios_cadastrados = Usuarios.query.filter_by(email=login).first()
    print('Usuario logado: ', usuarios_cadastrados.email)
    if usuarios_cadastrados != None and login == usuarios_cadastrados.email and senha == usuarios_cadastrados.senha:
        # Session -> é necessario importar
        # *** IMPORTANTE:  PARA UTILIZAR O SESSION DEVE SE POR OBRIGAÇÃO
        # *** TER REFERENCIADO O COMANDO SECRET_KEY
        # PARA QUE TENHA UMA SESSÃO ONE NÃO SEJA APENAS O LOGIN CRIPTOGRAFADO
        session['usuario_logado'] = request.form['txtLogin']
        return redirect('/lista')


    else:
        # a Linha abaixa retorna para a tela de login caso o usuario
        # erre o login ou senha

        return redirect('/login')


@app.route('/sair')
def sair_usuario():
    session.clear()
    # return render_template('login.html', alerta = 'Usuario Desconectado')
    return redirect(url_for('.login_usuario', alerta='Usuario Desconectado'))


app.run(debug=True)
