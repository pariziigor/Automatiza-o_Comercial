from docxtpl import DocxTemplate
from docx2pdf import convert
from datetime import datetime
import os
import sys
import re

def gerar_arquivos(path_modelo, dados, pasta_saida, callback_progresso=None):
    
    def reportar(pct, msg):
        if callback_progresso:
            callback_progresso(pct, msg)

    reportar(10, "Carregando modelo Word...")
    try:
        doc = DocxTemplate(path_modelo)
    except Exception as e:
        raise Exception(f"Erro ao abrir o modelo Word: {str(e)}")

    reportar(30, "Processando dados...")
    
    # Não podemos converter LISTAS para STRING, senão o Word soletra letra por letra.
    dados_limpos = {}
    for chave, valor in dados.items():
        if valor is None:
            dados_limpos[chave] = ""
        elif isinstance(valor, list):
            # Se for lista (Orçamento ou Estrutural), mantém como lista!
            dados_limpos[chave] = valor
        else:
            # Se for texto ou número, converte para string segura
            dados_limpos[chave] = str(valor)
    
    # Renderiza o documento
    try:
        doc.render(dados_limpos)
    except Exception as e:
        raise Exception(f"Erro ao preencher o Word (Tags incorretas?): {str(e)}")

    # --- Lógica de Nome do Arquivo ---
    nome_cliente = dados.get("NOME_EMPRESA_SOLICITANTE") or \
                   dados.get("NOME_EMPRESA") or \
                   dados.get("RAZAO_SOCIAL") or \
                   dados.get("NOME_CLIENTE") or \
                   "Cliente"
                   
    num_projeto = dados.get("NUMERO_PROJETO") or "000"
    data_hoje = datetime.now().strftime("%d-%m-%Y")
    
    nome_base = f"Proposta {num_projeto} - {nome_cliente} - {data_hoje}"
    nome_final = re.sub(r'[<>:"/\\|?*]', '', str(nome_base)).strip()

    path_word = os.path.join(pasta_saida, f"{nome_final}.docx")
    path_pdf = os.path.join(pasta_saida, f"{nome_final}.pdf")

    reportar(50, f"Salvando DOCX...")
    doc.save(path_word)

    reportar(70, "Convertendo para PDF...")
    try:
        if sys.platform == "win32":
            convert(path_word, path_pdf)
        else:
            pass 
    except Exception as e:
        print(f"Erro PDF (Ignorado): {e}")
    
    reportar(100, "Concluído!")
    
    return path_word, path_pdf