import os
from docxtpl import DocxTemplate
from docx2pdf import convert

def gerar_arquivos(template_path, dados, output_folder=None):
    """Gera o .docx e o .pdf finais."""
    
    if not output_folder:
        output_folder = os.path.dirname(template_path)
        
    doc = DocxTemplate(template_path)
    doc.render(dados)
    
    base_name = os.path.splitext(template_path)[0] + "_FINAL"
    path_docx = f"{base_name}.docx"
    path_pdf = f"{base_name}.pdf"
    
    # Salva Docx
    doc.save(path_docx)
    
    # Converte PDF
    try:
        convert(path_docx, path_pdf)
        return path_docx, path_pdf
    except Exception as e:
        # Retorna o docx mas avisa do erro no PDF
        raise Exception(f"Word gerado, mas erro no PDF: {str(e)}")