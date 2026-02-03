import os
from datetime import datetime
from docxtpl import DocxTemplate
from docx2pdf import convert
import pythoncom

# Adicionado argumento opcional 'output_folder'
def gerar_arquivos(template_path, context, output_folder=""):
    try:
        doc = DocxTemplate(template_path)
        doc.render(context)

        # --- NOMEAÇÃO ---
        raw_cliente = context.get("NOME_EMPRESA_SOLICITANTE", "Cliente")
        raw_obra = context.get("NUMERO_PROJETO", context.get("NUMERO_PROJETO", "SN"))
        data_arquivo = datetime.now().strftime("%d-%m-%Y")

        def limpar_nome_arquivo(texto):
            if not texto: return ""
            texto = str(texto)
            caracteres_proibidos = '<>:"/\\|?*'
            for char in caracteres_proibidos:
                texto = texto.replace(char, "")
            return texto.replace("\n", "").replace("\r", "").strip()

        cliente_limpo = limpar_nome_arquivo(raw_cliente)
        obra_limpa = limpar_nome_arquivo(raw_obra)
        nome_base = f"{cliente_limpo} - Obra {obra_limpa} - {data_arquivo}"
        
        # Se o usuário escolheu uma pasta, usamos ela. Se não, salva na pasta atual.
        if output_folder:
            # Cria a pasta se ela não existir 
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
                
            output_docx = os.path.join(output_folder, f"{nome_base}.docx")
            output_pdf = os.path.join(output_folder, f"{nome_base}.pdf")
        else:
            output_docx = f"{nome_base}.docx"
            output_pdf = f"{nome_base}.pdf"

        # Salva
        doc.save(output_docx)

        # Converte
        pythoncom.CoInitialize()
        convert(output_docx, output_pdf)
        
        # Retorna apenas o nome do arquivo (ou caminho completo se preferir)
        return os.path.basename(output_docx), os.path.basename(output_pdf)

    except Exception as e:
        raise Exception(f"Erro ao gerar arquivos: {str(e)}")