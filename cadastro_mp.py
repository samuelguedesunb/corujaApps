import sqlite3
from datetime import datetime
import json
from typing import List, Dict, Union, Optional

class InfoMP:
    """
    Objeto que registra um Mandado de Prisão
    """
    def __init__(self, nome, data, endereco, situacao, id_mp=None, local=None, fotos=None,
                 nome_mae=None, nome_pai=None, cpf=None, status_mp=None,
                 numero_mp=None, emissao_mp=None, artigos_mp=None, informe_equipe_aguia=None):
        self.id_mp = id_mp
        self.nome = nome
        self.data = data
        self.endereco = endereco
        self.situacao = situacao
        self.local = local
        self.fotos = fotos
        self.nome_mae = nome_mae
        self.nome_pai = nome_pai
        self.cpf = cpf
        self.status_mp = status_mp
        self.numero_mp = numero_mp
        self.emissao_mp = emissao_mp
        self.artigos_mp = artigos_mp
        self.informe_equipe_aguia = informe_equipe_aguia

    def cadastro_mp_bd(self):
        """
        Insere os dados do mandado de prisão no banco de dados corujalocal.db
        na tabela mp_table.

        Estrutura da tabela:
        - id_mp: INTEGER PRIMARY KEY AUTOINCREMENT
        - nome: TEXT NOT NULL
        - data: TEXT NOT NULL
        - endereco: TEXT
        - situacao: TEXT NOT NULL
        - local: TEXT
        - fotos: TEXT (armazenará caminhos ou JSON se múltiplas fotos)
        - data_cadastro: TEXT (data/hora do cadastro no sistema)
        - nome_mae: TEXT
        - nome_pai: TEXT
        - cpf: TEXT
        - status_mp: TEXT
        - numero_mp: TEXT
        - emissao_mp: TEXT
        - artigos_mp: TEXT
        - informe_equipe_aguia: TEXT
        """
        try:
            # Conecta ao banco de dados (cria se não existir)
            conn = sqlite3.connect('corujalocal.db')
            cursor = conn.cursor()

            # Cria a tabela se não existir com as novas colunas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mp_table (
                    id_mp INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data TEXT NOT NULL,
                    endereco TEXT,
                    situacao TEXT NOT NULL,
                    local TEXT,
                    fotos TEXT,
                    data_cadastro TEXT,
                    nome_mae TEXT,
                    nome_pai TEXT,
                    cpf TEXT,
                    status_mp TEXT,
                    numero_mp TEXT,
                    emissao_mp TEXT,
                    artigos_mp TEXT,
                    informe_equipe_aguia TEXT
                )
            ''')

            # --- Alteração Principal Aqui ---
            # Processa o campo 'fotos' para garantir que seja uma string simples
            fotos_str = None
            if self.fotos:
                if isinstance(self.fotos, list):
                    # Pega o primeiro elemento da lista (se for uma lista de caminhos)
                    fotos_str = self.fotos[0] if self.fotos else None
                else:
                    # Assume que já é uma string (caminho único)
                    fotos_str = self.fotos

                # Remove caracteres indesejados (ex: '[', ']', ou aspas extras)
                if fotos_str:
                    fotos_str = fotos_str.strip("[]'\"")  # Limpa a string
            # --- Fim da Alteração ---

            # Data e hora atual para registro do cadastro
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            values = (
                self.nome,
                self.data,
                self.endereco or None,
                self.situacao,
                self.local or None,
                fotos_str or None,
                data_cadastro,
                self.nome_mae or None,
                self.nome_pai or None,
                self.cpf or None,
                self.status_mp or None,
                self.numero_mp or None,
                self.emissao_mp or None,
                self.artigos_mp or None,
                self.informe_equipe_aguia or None
            )

            cursor.execute('''
                INSERT INTO mp_table (
                    nome, data, endereco, situacao, local, fotos, data_cadastro,
                    nome_mae, nome_pai, cpf, status_mp, numero_mp, emissao_mp,
                    artigos_mp, informe_equipe_aguia
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', values)

            # Confirma a transação
            conn.commit()

            # Obtém o ID gerado
            self.id_mp = cursor.lastrowid

            return True, "Cadastro realizado com sucesso!"

        except sqlite3.Error as e:
            return False, f"Erro ao cadastrar no banco de dados: {str(e)}"

        finally:
            # Fecha a conexão
            if conn:
                conn.close()

    def atualizar_mp_bd(self, id_mp=None):
        """
        Atualiza os dados do mandado de prisão no banco de dados com base no ID fornecido.

        Parâmetros:
            id_mp (int, opcional): ID do registro a ser atualizado. Se não fornecido, usa self.id_mp

        Retorna:
            Tuple (bool, str): (sucesso, mensagem)
        """
        # Determina qual ID usar (parâmetro ou atributo do objeto)
        target_id = id_mp if id_mp is not None else self.id_mp

        if not target_id:
            return False, "ID do MP não especificado para atualização"

        try:
            conn = sqlite3.connect('corujalocal.db')
            cursor = conn.cursor()

            # Tratamento das fotos (convertendo lista para string se necessário)
            fotos_str = json.dumps(self.fotos) if isinstance(self.fotos, list) else self.fotos

            # Prepara os valores para atualização
            update_values = (
                self.nome, self.data, self.endereco, self.situacao,
                self.local, fotos_str, self.nome_mae, self.nome_pai,
                self.cpf, self.status_mp, self.numero_mp, self.emissao_mp,
                self.artigos_mp, self.informe_equipe_aguia, target_id
            )

            cursor.execute('''
                UPDATE mp_table 
                SET nome = ?, 
                    data = ?, 
                    endereco = ?, 
                    situacao = ?, 
                    local = ?, 
                    fotos = ?,
                    nome_mae = ?,
                    nome_pai = ?,
                    cpf = ?,
                    status_mp = ?,
                    numero_mp = ?,
                    emissao_mp = ?,
                    artigos_mp = ?,
                    informe_equipe_aguia = ?
                WHERE id_mp = ?
            ''', update_values)

            if cursor.rowcount == 0:
                return False, "Nenhum registro encontrado com o ID especificado"

            conn.commit()

            # Atualiza o id_mp do objeto se foi usado um ID diferente
            if id_mp is not None and id_mp != self.id_mp:
                self.id_mp = id_mp

            return True, "Registro atualizado com sucesso"

        except sqlite3.Error as e:
            return False, f"Erro ao atualizar no banco de dados: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def excluir_mp_bd(id_mp):
        """
        Exclui um mandado de prisão do banco de dados pelo ID.

        Parâmetros:
            id_mp (int): ID do registro a ser excluído

        Retorno:
            Tuple (bool, str): (sucesso, mensagem)
        """
        try:
            conn = sqlite3.connect('corujalocal.db')
            cursor = conn.cursor()

            cursor.execute('DELETE FROM mp_table WHERE id_mp = ?', (id_mp,))

            if cursor.rowcount == 0:
                return False, "Nenhum registro encontrado com o ID especificado"

            conn.commit()
            return True, "Registro excluído com sucesso"

        except sqlite3.Error as e:
            return False, f"Erro ao excluir do banco de dados: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def listar_todos(formatar_json: bool = True) -> Union[List[Dict], str]:
        """
        Lista todos os registros da tabela mp_table com opção de retorno formatado.
        Atualizado para incluir todos os campos.
        """
        conn = None
        try:
            conn = sqlite3.connect('corujalocal.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_mp, nome, data, endereco, situacao, local, fotos, data_cadastro,
                       nome_mae, nome_pai, cpf, status_mp, numero_mp, emissao_mp,
                       artigos_mp, informe_equipe_aguia
                FROM mp_table
                ORDER BY data DESC, nome ASC
            """)

            resultados = cursor.fetchall()

            if not resultados:
                return json.dumps([]) if formatar_json else []

            # Converte para lista de dicionários (mantendo o tratamento existente de fotos)
            registros = []
            for linha in resultados:
                registro = dict(linha)
                # Mantém o mesmo tratamento de fotos do original
                if registro['fotos'] and isinstance(registro['fotos'], str):
                    registro['fotos'] = registro['fotos'].split(',')
                registros.append(registro)

            return json.dumps(registros, indent=4, ensure_ascii=False) if formatar_json else registros

        except sqlite3.Error as e:
            print(f"Erro ao consultar MPs: {str(e)}")
            return json.dumps({"erro": str(e)}) if formatar_json else []
        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(id_mp: int) -> Optional['InfoMP']:
        """
        Busca um Mandado de Prisão pelo ID e retorna um objeto InfoMP completo.
        Atualizado para incluir todos os campos.
        """
        conn = None
        try:
            conn = sqlite3.connect('corujalocal.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_mp, nome, data, endereco, situacao, local, fotos,
                       nome_mae, nome_pai, cpf, status_mp, numero_mp, emissao_mp,
                       artigos_mp, informe_equipe_aguia
                FROM mp_table
                WHERE id_mp = ?
            """, (id_mp,))

            resultado = cursor.fetchone()

            if not resultado:
                return None

            # Mantém o mesmo tratamento de fotos do original
            fotos = resultado['fotos'].split(',') if resultado['fotos'] else None

            return InfoMP(
                id_mp=resultado['id_mp'],
                nome=resultado['nome'],
                data=resultado['data'],
                endereco=resultado['endereco'],
                situacao=resultado['situacao'],
                local=resultado['local'],
                fotos=fotos,
                nome_mae=resultado['nome_mae'],
                nome_pai=resultado['nome_pai'],
                cpf=resultado['cpf'],
                status_mp=resultado['status_mp'],
                numero_mp=resultado['numero_mp'],
                emissao_mp=resultado['emissao_mp'],
                artigos_mp=resultado['artigos_mp'],
                informe_equipe_aguia=resultado['informe_equipe_aguia']
            )

        except sqlite3.Error as e:
            print(f"Erro ao buscar MP: {str(e)}")
            return None
        finally:
            if conn:
                conn.close()