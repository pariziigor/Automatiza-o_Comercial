# Gerador Automático de Propostas

Ferramenta desktop desenvolvida em Python para automatizar a criação de propostas comerciais e orçamentos. O sistema lê dados de fichas cadastrais (PDF ou DOCX), permite validação e edição via Interface Gráfica e gera os documentos finais baseados em um modelo Word.

## 🚀 Funcionalidades

- **Leitura Inteligente de Arquivos:** Extrai dados de documentos do cliente (Solicitante) e de Faturamento.
- **Parser com Regex e Stopwords:** Algoritmo robusto que identifica CNPJ, CPF, CEP e Datas ignorando títulos e formatações variadas.
- **Interface Gráfica Responsiva (Tkinter):**
  - Grid dinâmico que se ajusta ao tamanho da janela.
  - Seleção de serviços via Checkboxes.
  - Opção de Frete (CIF/FOB).
  - Campos de edição para conferência de dados extraídos.
- **Geração de Documentos:**
  - Preenchimento de templates `.docx` usando tags (Jinja2).
  - Conversão automática para PDF final.

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **Interface:** `tkinter` (Nativo) e `ttk`
- **Manipulação de Arquivos:** `pdfplumber`, `python-docx`
- **Geração de Propostas:** `docxtpl`, `docx2pdf`
- **Lógica:** Expressões Regulares (Regex)

## 📦 Como Usar

1. Execute o arquivo principal:
   ```bash
   python main_window.py
   Selecione o Modelo Word (Template).

Selecione o arquivo do Cliente (PDF/DOCX).

(Opcional) Selecione arquivo de Faturamento.

Clique em Iniciar Processo.

Na janela de conferência, revise os dados, escolha o frete e os serviços.

Confirme para gerar o PDF e o DOCX finais.
