from flask import Flask, render_template, request, redirect, url_for, flash
from cadastro_mp import InfoMP
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, URL, Length
from datetime import date, datetime
from cadastro_mp import InfoMP
from flask_wtf.file import FileField, FileAllowed, FileRequired
from werkzeug.utils import secure_filename
import os
import uuid


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
UPLOAD_FOLDER = os.path.join('static', 'images', 'uploads')
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

## Pasta de uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return new_filename

# CRIA O FORMULARIO
class TarefaForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired()])
    data = DateField("Data", validators=[DataRequired()], default=date.today, format='%Y-%m-%d')
    endereco = StringField("Endereço", validators=[DataRequired()])
    situacao = SelectField("Situação", choices=[("Pendente", "Pendente"), ("Cumprido", "Cumprido")], validators=[DataRequired()])
    local = SelectField("Local", choices=[
        ("Setor Norte", "Setor Norte"),
        ("Setor Sul", "Setor Sul"),
        ("Setor Central", "Setor Central"),
        ("Setor Oeste", "Setor Oeste"),
        ("Setor Leste", "Setor Leste"),
        ("Sem Setor", "Sem Setor")
    ], validators=[Length(max=200)])
    nome_mae = StringField("Nome da Mãe", validators=[DataRequired()])
    nome_pai = StringField("Nome do Pai", validators=[DataRequired()])
    cpf = StringField("CPF", validators=[DataRequired()])
    numero_mp = StringField("Número MP", validators=[DataRequired()])
    artigo_crime = StringField("Artigo do Crime", validators=[DataRequired()])
    info_aguia = StringField("Informações", validators=[DataRequired()])
    foto = FileField('Foto Procurado', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Apenas imagens no formato JPG, JPEG e PNG permitidas')
    ])
    submit = SubmitField("Salvar")


@app.route("/mp")
def mp_pagina():
    registros = InfoMP.listar_todos(formatar_json=False)
    return render_template('index_mp.html', posts=registros)

@app.route("/mp/<int:procurado_id>/")
def mp_pagina_procurado(procurado_id):
    mp_busca = InfoMP.buscar_por_id(procurado_id)
    if mp_busca is None:
        return "Post não encontrado", 404

    return render_template('procurado.html', procurado=mp_busca)


@app.route("/mp/new-mp", methods=["GET", "POST"])
def new_mp():
    form = TarefaForm()
    if form.validate_on_submit():
        if 'foto' in request.files:
            file = request.files['foto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                random_name = random_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
                file.save(filepath)

                # Aqui você pode salvar o caminho no banco de dados
                foto_path = os.path.join('images', 'uploads', random_name).replace('\\', '/')
                print(foto_path)

        novo_mp = InfoMP(
            nome=form.nome.data,
            data=form.data.data,
            endereco=form.endereco.data,
            situacao=form.situacao.data,
            local=form.local.data,
            fotos=foto_path,
            nome_mae=form.nome_mae.data,
            nome_pai=form.nome_pai.data,
            cpf=form.cpf.data,
            status_mp=form.info_aguia.data, ## STATUS MP SÃO AS OBSERVAÇÕES.
            numero_mp=form.numero_mp.data,
            emissao_mp=form.data.data,
            artigos_mp=form.artigo_crime.data
        )
        novo_mp.cadastro_mp_bd()
        flash('Cadastro realizado com sucesso!', 'success')
        return redirect('/mp')
    return render_template("new-mp.html", form=form)


@app.route("/edit-mp/<int:mp_id>", methods=["GET", "POST"])
def edit_mp(mp_id):
    mp = InfoMP.buscar_por_id(mp_id)

    if not mp:
        flash("MP não encontrado", "error")
        return redirect(url_for('mp_pagina'))

    form = TarefaForm()

    if form.validate_on_submit():
        # Processar upload da nova foto se fornecida
        foto_path = mp.fotos  # Mantém a foto existente por padrão

        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename != '' and allowed_file(file.filename):
                # Remove a foto antiga se existir
                if mp.fotos:
                    try:
                        old_file = os.path.join(app.config['UPLOAD_FOLDER'], mp.fotos.split('/')[-1])
                        if os.path.exists(old_file):
                            os.remove(old_file)
                    except Exception as e:
                        flash(f"Erro ao remover foto antiga: {str(e)}", "warning")

                # Salva a nova foto
                filename = secure_filename(file.filename)
                random_name = random_filename(filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], random_name)
                file.save(filepath)
                foto_path = os.path.join('images', 'uploads', random_name).replace('\\', '/')

        # Atualiza os atributos do objeto
        mp.nome = form.nome.data
        mp.data = form.data.data
        mp.endereco = form.endereco.data
        mp.situacao = form.situacao.data
        mp.local = form.local.data
        mp.fotos = foto_path
        mp.nome_mae = form.nome_mae.data
        mp.nome_pai = form.nome_pai.data
        mp.cpf = form.cpf.data
        mp.status_mp = form.situacao.data
        mp.numero_mp = form.numero_mp.data
        mp.emissao_mp = form.data.data
        mp.artigos_mp = form.artigo_crime.data
        mp.informe_equipe_aguia = form.info_aguia.data

        # Metodo que atualiza
        success, message = mp.atualizar_mp_bd(mp_id)

        if success:
            flash('MP atualizado com sucesso!', 'success')
            return redirect(url_for('mp_pagina'))
        else:
            flash(f'Erro ao atualizar: {message}', 'error')

    elif request.method == 'GET':
        # Converter a string de data para objeto date
        try:
            if isinstance(mp.data, str):
                # Assume formato YYYY-MM-DD (ajuste conforme seu banco)
                data_obj = datetime.strptime(mp.data, '%Y-%m-%d').date()
            else:
                data_obj = mp.data
        except (ValueError, AttributeError):
            data_obj = date.today()  # Valor padrão se houver erro

        # Preenche o formulário com os dados existentes
        form.nome.data = mp.nome
        form.data.data = data_obj  # Agora é um objeto date
        form.endereco.data = mp.endereco
        form.situacao.data = mp.situacao
        form.local.data = mp.local
        form.nome_mae.data = mp.nome_mae
        form.nome_pai.data = mp.nome_pai
        form.cpf.data = mp.cpf
        form.numero_mp.data = mp.numero_mp
        form.artigo_crime.data = mp.artigos_mp
        form.info_aguia.data = getattr(mp, 'informe_equipe_aguia', '')  # Usando getattr por segurança


    # Tratamento simplificado da foto
    foto_atual = None
    if hasattr(mp, 'fotos') and mp.fotos:
        # Remove a parte '/static/' se existir (pois o url_for já adiciona)
        foto_path = mp.fotos[0]
        foto_atual = url_for('static', filename=foto_path)


    return render_template("new-mp.html", form=form, mp=mp, foto_atual=foto_atual, edicao=True)


if __name__ == '__main__':
    app.run(debug=True)