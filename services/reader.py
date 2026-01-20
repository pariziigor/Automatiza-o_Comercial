import os
import pdfplumber
from docx import Document

def ler_documento_cliente(filepath):
    """Lê o arquivo do cliente (PDF ou DOCX) e retorna texto puro."""
    if not filepath:
        return ""
        
    ext = os.path.splitext(filepath)[1].lower()
    texto = ""
    
    try:
        if ext == '.pdf':
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    texto += (page.extract_text() or "") + "\n"
        elif ext == '.docx':
            doc = Document(filepath)
            # Texto dos parágrafos
            for para in doc.paragraphs:
                texto += para.text + "\n"
            # Texto das tabelas (importante para orçamentos)
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        texto += cell.text + " "
                    texto += "\n"
    except Exception as e:
        raise Exception(f"Erro ao ler arquivo: {str(e)}")
            
    return texto

def extrair_placeholders_modelo(doc_path):
    """Lê o template Word e identifica {{Variaveis}}."""
    import re
    doc = Document(doc_path)
    texto_completo = ""
    
    for para in doc.paragraphs:
        texto_completo += para.text + "\n"
        
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                texto_completo += cell.text + "\n"
    
    pattern = r"\{\{(.*?)\}\}"
    matches = re.findall(pattern, texto_completo)
    return set([m.strip() for m in matches])