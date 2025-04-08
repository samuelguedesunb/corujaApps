from flask import Flask, render_template, request, redirect, url_for, flash
from cadastro_mp import InfoMP

app = Flask(__name__)



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


if __name__ == '__main__':
    app.run(debug=True)