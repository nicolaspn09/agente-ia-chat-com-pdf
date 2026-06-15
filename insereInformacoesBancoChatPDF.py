import requests
import os
import locale
import mysql.connector
import time
from datetime import datetime

def conecta_sql():
    host = 'REMOVED'  # Endereço do servidor MySQL
    database = 'REMOVED'  # Nome do banco de dados
    user = 'REMOVED'  # Nome de usuário para acessar o banco de dados
    password = 'REMOVED_FOR_GITHUB'  # Senha do usuário para acessar o banco de dados

    try:
        # Estabelece a conexão com o banco de dados
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return connection
        
    except mysql.connector.Error as error:
        print('Erro ao conectar-se ao banco de dados:', error)


def acessa_pdf():
    locale.setlocale(locale.LC_ALL, "pt_BR")
    data_atual = datetime.now()
    data_convertida = data_atual.strftime("%m/%Y")

    diretorio = r"C:\rpa\contabilidade\Notas Representantes\PDFs"

    for caminho_arquivo in os.listdir(diretorio):
        conexao = conecta_sql()
        cursor = conexao.cursor()

        sql_select = f"SELECT * FROM FISCAL.NOTAS_FISCAIS_REPRESENTANTES WHERE DATA_PESQUISA = '{data_convertida}' AND NOME_ARQUIVO = '{caminho_arquivo}'"

        cursor.execute(sql_select)
        rows = cursor.fetchall()

        quantidade_linhas_mysql = len(rows)

        cursor.close()                                
        conexao.close()

        if quantidade_linhas_mysql == 0:

            files = [
                ('file', ('file', open(r"{}\{}".format(diretorio, caminho_arquivo), 'rb'), 'application/octet-stream'))
            ]
            headers = {
                'x-api-key': 'REMOVED_FOR_GITHUB'
            }

            response = requests.post(
                'https://api.chatpdf.com/v1/sources/add-file', headers=headers, files=files)

            if response.status_code == 200:
                source_id = response.json()['sourceId']

                data = {
                    'sourceId': str(source_id),
                    'messages': [
                        {
                            'role': "user",
                            'content': "Me retorne, de forma organizada, tendo como nome da informação os seguintes dados da nota fiscal: o número da NF, data de emissão, todos os CNPJs presentes na nota fiscal (dividindo-os em linhas), o valor total da NF, a alíquota do IR, o valor do IR, a alíquota do ISS, o valor do ISS e o valor líquido da NF. Caso você não encontre alguma informação, me retorne o número zero. Iniciando cada linha com informação pelo hashtag"
                        }
                    ]
                }

                response = requests.post(
                    'https://api.chatpdf.com/v1/chats/message', headers=headers, json=data)

                if response.status_code == 200:
                    conexao = conecta_sql()
                    cursor = conexao.cursor()

                    sql_insert = f"INSERT INTO fiscal.notas_fiscais_representantes (informacao_ia, data_pesquisa, nome_arquivo) VALUES('{response.json()['content']}', '{data_convertida}', '{caminho_arquivo}')"

                    cursor.execute(sql_insert)
                    conexao.commit()

                    cursor.close()                                
                    conexao.close()

                else:
                    conexao = conecta_sql()
                    cursor = conexao.cursor()

                    sql_insert = f"INSERT INTO fiscal.notas_fiscais_representantes (informacao_ia, data_pesquisa, nome_arquivo) VALUES('Erro ao conectar na API da IA', '{data_convertida}', '{caminho_arquivo}')"

                    cursor.execute(sql_insert)
                    conexao.commit()

                    cursor.close()                                
                    conexao.close()

        time.sleep(6)

acessa_pdf()