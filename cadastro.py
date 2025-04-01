import sqlite3
import json

##
## Objeto responsável por cadastrar, atualizar, remover e procurar novas informações no BD (corujalocal)
##

class InfoRegistro:
    """
    Objeto que registra um tipo de situação.
    """
    def __init__(self, tipo, data, hora, id=None, local=None, fotos=None, pessoas=None, idpessoas=None):
        self.id = id
        self.tipo = tipo
        self.data = data
        self.hora = hora
        self.local = local
        self.fotos = fotos
        self.pessoas = pessoas
        self.idpessoas = idpessoas

    def __str__(self):
        return (f"InfoRegistro(ID={self.id}, Tipo={self.tipo}, Data={self.data}, "
                f"Hora={self.hora}, Local={self.local}, Fotos={self.fotos}, "
                f"Pessoas={self.pessoas})")

    ##Cadastro Banco de  Dados
    def cadastro_no_bd(self):
        # Conecta ao banco de dados (ou cria se não existir)
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para inserir os dados na tabela
        query = """
        INSERT INTO info_table (Tipo, Data, Hora, Local, Fotos, Pessoas, IDPessoas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        # Valores a serem inseridos
        valores = (
            self.tipo,
            self.data,
            self.hora,
            self.local,
            self.fotos,
            self.pessoas,
            self.idpessoas
        )

        try:
            # Executa a query
            cursor.execute(query, valores)
            # Confirma a transação
            conexao.commit()
            print("Dados inseridos com sucesso!")
        except sqlite3.Error as erro:
            print(f"Erro ao inserir dados no banco de dados: {erro}")
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    def update_informacao(self):
        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para atualizar os dados na tabela
        query = """
        UPDATE info_table
        SET Tipo = ?, Data = ?, Hora = ?, Local = ?, Fotos = ?, Pessoas = ?, IDPessoas = ?
        WHERE ID = ?
        """
        # Valores a serem atualizados
        valores = (
            self.tipo,
            self.data,
            self.hora,
            self.local,
            self.fotos,
            self.pessoas,
            self.idpessoas,
            self.id  # ID da linha a ser atualizada
        )

        try:
            # Executa a query
            cursor.execute(query, valores)
            # Confirma a transação
            conexao.commit()
            print("Dados atualizados com sucesso!")
        except sqlite3.Error as erro:
            print(f"Erro ao atualizar dados no banco de dados: {erro}")
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    def deleta_informacao(self):
        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para deletar uma linha da tabela
        query = """
        DELETE FROM info_table
        WHERE ID = ?
        """
        # Valor do ID da linha a ser deletada
        valor = (self.id,)

        try:
            # Executa a query
            cursor.execute(query, valor)
            # Confirma a transação
            conexao.commit()
            print("Dados deletados com sucesso!")
        except sqlite3.Error as erro:
            print(f"Erro ao deletar dados no banco de dados: {erro}")
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    @staticmethod
    def consultar_por_tipo(tipo):
        """
        Consulta registros no banco de dados com base no tipo.
        Retorna os dados no formato JSON.
        """
        if not tipo:
            print("Erro: Tipo não definido. É necessário um tipo para consultar registros.")
            return json.dumps([])  # Retorna uma lista vazia em JSON

        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para consultar registros por tipo
        query = """
            SELECT ID, Tipo, Data, Hora, Local, Fotos, Pessoas, IDPessoas
            FROM info_table
            WHERE Tipo = ?
            """
        valor = (tipo,)

        try:
            # Executa a query
            cursor.execute(query, valor)
            resultados = cursor.fetchall()  # Recupera todas as linhas encontradas

            if resultados:
                # Converte os resultados para uma lista de dicionários
                colunas = ["ID", "Tipo", "Data", "Hora", "Local", "Fotos", "Pessoas", "IDPessoas"]
                dados = [dict(zip(colunas, linha)) for linha in resultados]
                return json.dumps(dados, indent=4)  # Retorna os dados em formato JSON
            else:
                print("Nenhum registro encontrado com o tipo fornecido.")
                return json.dumps([])  # Retorna uma lista vazia em JSON
        except sqlite3.Error as erro:
            print(f"Erro ao consultar dados no banco de dados: {erro}")
            return json.dumps([])  # Retorna uma lista vazia em JSON
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    @staticmethod
    def listar_todos():
        """
        Lista todos os registros da tabela info_table.
        Retorna os dados no formato JSON.
        """
        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para selecionar todos os registros
        query = """
        SELECT ID, Tipo, Data, Hora, Local, Fotos, Pessoas, IDPessoas
        FROM info_table
        """

        try:
            # Executa a query
            cursor.execute(query)
            resultados = cursor.fetchall()  # Recupera todas as linhas

            if resultados:
                # Converte os resultados para uma lista de dicionários
                colunas = ["ID", "Tipo", "Data", "Hora", "Local", "Fotos", "Pessoas", "IDPessoas"]
                dados = [dict(zip(colunas, linha)) for linha in resultados]
                return json.dumps(dados, indent=4)  # Retorna os dados em formato JSON
            else:
                print("Nenhum registro encontrado.")
                return json.dumps([])  # Retorna uma lista vazia em JSON
        except sqlite3.Error as erro:
            print(f"Erro ao consultar dados no banco de dados: {erro}")
            return json.dumps([])  # Retorna uma lista vazia em JSON
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    @staticmethod
    def consultar_com_filtros(**filtros):
        """
        Consulta registros no banco de dados com base em filtros.
        filtros: Dicionário com os campos e valores para filtrar.
        Retorna uma lista de dicionários com os registros encontrados.
        """
        if not filtros:
            print("Erro: Nenhum filtro fornecido.")
            return []

        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Cria a query dinamicamente com base nos filtros
        campos = " AND ".join([f"{campo} = ?" for campo in filtros.keys()])
        query = f"""
        SELECT ID, Tipo, Data, Hora, Local, Fotos, Pessoas, IDPessoas
        FROM info_table
        WHERE {campos}
        """
        valores = tuple(filtros.values())

        try:
            # Executa a query
            cursor.execute(query, valores)
            resultados = cursor.fetchall()  # Recupera todas as linhas encontradas

            if resultados:
                # Retorna os dados como uma lista de dicionários
                colunas = ["ID", "Tipo", "Data", "Hora", "Local", "Fotos", "Pessoas", "IDPessoas"]
                return [dict(zip(colunas, linha)) for linha in resultados]
            else:
                print("Nenhum registro encontrado com os filtros fornecidos.")
                return []
        except sqlite3.Error as erro:
            print(f"Erro ao consultar dados no banco de dados: {erro}")
            return []
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()

    @staticmethod
    def contar_registros():
        """
        Retorna o número total de registros na tabela info_table.
        """
        # Conecta ao banco de dados
        conexao = sqlite3.connect('corujalocal.db')
        cursor = conexao.cursor()

        # Query para contar os registros
        query = """
        SELECT COUNT(*)
        FROM info_table
        """

        try:
            # Executa a query
            cursor.execute(query)
            resultado = cursor.fetchone()  # Recupera o resultado
            return resultado[0]  # Retorna o número de registros
        except sqlite3.Error as erro:
            print(f"Erro ao contar registros no banco de dados: {erro}")
            return 0
        finally:
            # Fecha a conexão com o banco de dados
            cursor.close()
            conexao.close()
