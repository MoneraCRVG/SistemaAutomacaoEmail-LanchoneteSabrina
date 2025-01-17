from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
import smtplib
import mysql.connector
import mysql
import os
load_dotenv()
def gerarRelatorio():
    global cursor
    conexao = None
    try:
        conexao =  mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
        )
        cursor = conexao.cursor()

        sql = '''SELECT SUM(ip.quantidade * p.preco) AS total_vendas
FROM item_pedido ip
JOIN produtos p ON ip.codigo_produto = p.codigo
JOIN pedidos ped ON ip.codigo_pedido = ped.numero
WHERE ped.status = 'concluido';
'''
        cursor.execute(sql)
        resultado = cursor.fetchone()
        print("Conectado")
        return resultado
    except mysql.connector.Error as e:
        print(f'Erro ao conectar com o BD: {e}')
    finally:
        cursor.close()
        conexao.close()

def send_email(relatorio):
    destinatario = os.getenv("GERENTE_EMAIL")
    remetente = os.getenv("SMTP_USER")
    senha = os.getenv("SMTP_PASSWORD")
    servidor = os.getenv("SMTP_SERVER")
    porta = os.getenv("SMTP_PORT")
    titulo = "Relatório de Vendas - Total de Vendas"

    corpo = f'''Prezado Nicolas,

Espero que este e-mail o encontre bem.

Estou enviando em anexo o relatório com o valor total das vendas da lanchonete referente ao período do mês de outubro de 2023. O total das vendas foi calculado com base nos pedidos concluídos e inclui todos os itens vendidos.

R$ {relatorio}

Caso tenha alguma dúvida ou precise de informações adicionais, estou à disposição para ajudar.

Agradeço pela atenção e desejo um ótimo dia!

Atenciosamente,

Nelson Oliveira,

Vendedor

+55 (21) 88988-9699

Lanchonete Sabrina'''

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = titulo
    msg.attach(MIMEText(corpo, 'plain'))

    server = None

    try:
        server = smtplib.SMTP(servidor, porta)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
    except Exception as e:
        print("Erro ao enviar: ", e)
    finally:
        if server:
            server.quit()


send_email(gerarRelatorio())
