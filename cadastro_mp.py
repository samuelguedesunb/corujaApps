import sqlite3
from datetime import datetime
import json
from typing import List, Dict, Union, Optional

class InfoMP:
    """
    Objeto que registra um Mandado de Prisãa
    """
    def __init__(self, nome, data, endereco, situacao, id_mp=None, local=None, fotos=None):
        self.id_mp = id_mp
        self.nome = nome
        self.data = data
        self.endereco = endereco
        self.situacao = situacao
        self.local = local
        self.fotos = fotos

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
        """
        try:
            # Conecta ao banco de dados (cria se não existir)
            conn = sqlite3.connect('corujalocal.db')
            cursor = conn.cursor()

            # Cria a tabela se não existir
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mp_table (
                    id_mp INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data TEXT NOT NULL,
                    endereco TEXT,
                    situacao TEXT NOT NULL,
                    local TEXT,
                    fotos TEXT,
                    data_cadastro TEXT
                )
            ''')

            # Converte a lista de fotos para string JSON se existir
            fotos_str = None
            if self.fotos is not None:
                if isinstance(self.fotos, list):
                    fotos_str = ','.join(self.fotos)
                else:
                    fotos_str = str(self.fotos)

            # Data e hora atual para registro do cadastro
            data_cadastro = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Insere os dados
            cursor.execute('''
                INSERT INTO mp_table (nome, data, endereco, situacao, local, fotos, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (self.nome, self.data, self.endereco, self.situacao, self.local, fotos_str, data_cadastro))

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

    def atualizar_mp_bd(self):
        """
        Atualiza os dados do mandado de prisão no banco de dados corujalocal.db

        Parâmetros:
            Utiliza os atributos atuais do objeto para atualização

        Retorno:
            Tuple (bool, str): (sucesso, mensagem)
            - sucesso: True se a atualização foi bem-sucedida, False caso contrário
            - mensagem: Descrição do resultado da operação

        Requisitos:
            - O objeto deve ter um id_mp válido (já existente no banco)
            - Pelo menos um campo além do id_mp deve ser modificado

        Exceções:
            - sqlite3.Error se ocorrer algum problema com o banco de dados
            - AttributeError se o id_mp não estiver definido

        Exemplo de uso:
            >>> mp = InfoMP(...)
            >>> mp.id_mp = 1  # ID existente
            >>> mp.situacao = "Cancelado"
            >>> sucesso, msg = mp.atualizar_mp_bd()
        """
        if not self.id_mp:
            return False, "ID do MP não especificado para atualização"

        try:
            conn = sqlite3.connect('corujalocal.db')
            cursor = conn.cursor()

            # Converte fotos para string se for lista
            fotos_str = ','.join(self.fotos) if isinstance(self.fotos, list) else self.fotos

            cursor.execute('''
                UPDATE mp_table 
                SET nome = ?, 
                    data = ?, 
                    endereco = ?, 
                    situacao = ?, 
                    local = ?, 
                    fotos = ?
                WHERE id_mp = ?
            ''', (self.nome, self.data, self.endereco, self.situacao,
                  self.local, fotos_str, self.id_mp))

            if cursor.rowcount == 0:
                return False, "Nenhum registro encontrado com o ID especificado"

            conn.commit()
            return True, "Registro atualizado com sucesso"

        except sqlite3.Error as e:
            return False, f"Erro ao atualizar no banco de dados: {str(e)}"

        finally:
            if conn:
                conn.close()

    @staticmethod
    def excluir_mp_bd(id_mp):
        """
        Exclui um mandado de prisão do banco de dados pelo ID

        Parâmetros:
            id_mp (int): ID do registro a ser excluído

        Retorno:
            Tuple (bool, str): (sucesso, mensagem)
            - sucesso: True se a exclusão foi bem-sucedida, False caso contrário
            - mensagem: Descrição do resultado da operação

        Exceções:
            - sqlite3.Error se ocorrer algum problema com o banco de dados

        Exemplo de uso:
            >>> sucesso, msg = InfoMP.excluir_mp_bd(1)
            >>> if sucesso:
            ...     print("MP excluído com sucesso")
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
            if conn:
                conn.close()

    @staticmethod
    def listar_todos(formatar_json: bool = True) -> Union[List[Dict], str]:
        """
        Lista todos os registros da tabela mp_table com opção de retorno formatado.

        Parâmetros:
            formatar_json (bool): Se True, retorna os dados em formato JSON.
                                Se False, retorna uma lista de dicionários.
                                Default: True

        Retorno:
            Se formatar_json=True:
                str: JSON contendo todos os registros ou lista vazia se não houver dados
            Se formatar_json=False:
                List[Dict]: Lista de dicionários com os registros ou lista vazia

        Exceções:
            sqlite3.Error: Se ocorrer erro na conexão ou consulta ao banco de dados

        Exemplo de uso:
            # Como JSON
            mps_json = InfoMP.listar_todos()
            print(mps_json)

            # Como lista de dicionários
            mps_lista = InfoMP.listar_todos(formatar_json=False)
            for mp in mps_lista:
                print(mp['nome'], mp['situacao'])
        """
        conn = None
        try:
            conn = sqlite3.connect('corujalocal.db')
            conn.row_factory = sqlite3.Row  # Permite acesso aos campos por nome
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_mp, nome, data, endereco, situacao, local, fotos, data_cadastro
                FROM mp_table
                ORDER BY data DESC, nome ASC
            """)

            resultados = cursor.fetchall()

            if not resultados:
                return json.dumps([]) if formatar_json else []

            # Converte para lista de dicionários
            registros = [dict(linha) for linha in resultados]

            # Converte fotos de string para lista se necessário
            for registro in registros:
                if registro['fotos'] and isinstance(registro['fotos'], str):
                    registro['fotos'] = registro['fotos'].split(',')

            return json.dumps(registros, indent=4, ensure_ascii=False) if formatar_json else registros

        except sqlite3.Error as e:
            print(f"Erro ao consultar MP's: {str(e)}")
            return json.dumps({"erro": str(e)}) if formatar_json else []

        finally:
            if conn:
                conn.close()

    @staticmethod
    def buscar_por_id(id_mp: int) -> Optional['InfoMP']:
        """
        Busca um Mandado de Prisão pelo ID e retorna um objeto InfoMP

        Parâmetros:
            id_mp (int): ID do registro a ser buscado

        Retorno:
            Optional[InfoMP]: Retorna o objeto InfoMP se encontrado, None caso contrário

        Exemplo de uso:
            mp = InfoMP.buscar_por_id(1)
            if mp:
                print(f"Encontrado MP: {mp.nome}")
                mp.situacao = "Atualizado"
                mp.atualizar_mp_bd()
            else:
                print("MP não encontrado")
        """
        conn = None
        try:
            conn = sqlite3.connect('corujalocal.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id_mp, nome, data, endereco, situacao, local, fotos
                FROM mp_table
                WHERE id_mp = ?
            """, (id_mp,))

            resultado = cursor.fetchone()

            if not resultado:
                return None

            # Converte a string de fotos para lista se existir
            fotos = resultado['fotos'].split(',') if resultado['fotos'] else None

            return InfoMP(
                id_mp=resultado['id_mp'],
                nome=resultado['nome'],
                data=resultado['data'],
                endereco=resultado['endereco'],
                situacao=resultado['situacao'],
                local=resultado['local'],
                fotos=fotos
            )

        except sqlite3.Error as e:
            print(f"Erro ao buscar MP: {str(e)}")
            return None

        finally:
            if conn:
                conn.close()