from docxtpl import DocxTemplate
from docx2pdf import convert
from datetime import datetime  # <--- IMPORTANTE: Importamos a biblioteca de data
import os
import sys
import re

def gerar_arquivos(path_modelo, dados, pasta_saida, callback_progresso=None):
    
    def reportar(pct, msg):
        if callback_progresso:
            callback_progresso(pct, msg)

    reportar(10, "Carregando modelo...")
    doc = DocxTemplate(path_modelo)

    reportar(30, "Preenchendo dados no Word...")
    
    # Prepara os dados (converte tudo para string)
    dados_limpos = {k: (str(v) if v is not None else "") for k, v in dados.items()}
    doc.render(dados_limpos)

    # --- DEFINIÇÃO DO NOME DO ARQUIVO ---
    
    # 1. Pega o nome do cliente (com várias tentativas para garantir)
    nome_cliente = dados.get("NOME_EMPRESA_SOLICITANTE") or \
                   dados.get("NOME_EMPRESA") or \
                   dados.get("RAZAO_SOCIAL") or \
                   dados.get("NOME_CLIENTE") or \
                   dados.get("CLIENTE") or \
                   "Cliente"

    # 2. Pega número do projeto e a DATA DE HOJE
    num_projeto = dados.get("NUMERO_PROJETO") or dados.get("PROJETO")
    
    # Formata a data: Dia-Mês-Ano (Ex: 25-10-2023)
    data_hoje = datetime.now().strftime("%d-%m-%Y") 

    # 3. Monta o nome base: "Proposta [Num] - [Cliente] - [Data]"
    if num_projeto:
        nome_base = f"Proposta AULEVI {num_projeto} - {nome_cliente} - {data_hoje}"
    else:
        nome_base = f"Proposta AULEVI - {nome_cliente} - {data_hoje}"

    # 4. Remove caracteres proibidos no Windows para evitar erro
    nome_final = re.sub(r'[<>:"/\\|?*]', '', str(nome_base)).strip()

    # Caminhos finais
    path_word = os.path.join(pasta_saida, f"{nome_final}.docx")
    path_pdf = os.path.join(pasta_saida, f"{nome_final}.pdf")

    reportar(50, f"Salvando: {nome_final}.docx...")
    doc.save(path_word)

    reportar(70, "Convertendo para PDF (Aguarde)...")
    try:
        if sys.platform == "win32":
            convert(path_word, path_pdf)
        else:
            pass 
    except Exception as e:
        print(f"Erro PDF: {e}")

    reportar(100, "Concluído!")
    
    return path_word, path_pdf