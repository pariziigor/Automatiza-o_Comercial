# 🚀 Gerador de Propostas Comerciais (AULEVI)

> **Versão:** 2.0 (Estável)  
> **Status:** ✅ Concluído  
> **Tema:** 🌙 Dark Mode / 🟠 Laranja Personalizado  

O **Gerador de Propostas Comerciais** é uma aplicação Desktop desenvolvida em **Python** para automatizar a criação, preenchimento e exportação de contratos e orçamentos.

O software elimina o trabalho manual de edição no Word, integrando:

- 🔎 Busca automática de dados via API
- 🧮 Cálculos automáticos
- 📄 Geração de arquivos Word e PDF
- 🎨 Interface moderna e personalizada

---

# 📸 Funcionalidades

## 1️⃣ Automação e Inteligência

- 🔍 **Busca de CNPJ**
  - Integração com a API **ReceitaWS**
  - Preenche automaticamente:
    - Razão Social
    - Endereço
    - Contatos

- 🏢 **Lógica Inteligente de Endereços**
  - Diferencia dados do:
    - **Solicitante**
    - **Faturamento (Contratante)**
  - Preserva locais de obra/entrega corretamente

- 📄 **Modelo Interno Embutido**
  - O sistema já possui um modelo Word interno
  - Não exige arquivos externos para funcionamento

---

## 2️⃣ Interface Moderna (UI/UX)

- 🖥️ **Framework:** CustomTkinter
- 🎨 **Identidade Visual Personalizada**
  - `tema_laranja.json`
  - `icone.ico`
- 🪟 **Janelas Modais com Fluxo Guiado**
  - Revisão → Escopo → Orçamento
- ❌ **Cancelamento Seguro**
  - Permite fechar qualquer janela sem travar a aplicação

---

## 3️⃣ Orçamento e Cálculos

- ➕➖ **Tabelas Dinâmicas**
  - Adição e remoção de itens
- 💰 **Máscara de Moeda Inteligente**
  - Digita: `1000`
  - Sistema formata automaticamente: `1.000,00`
- 🧾 **Somatório Automático**
  - Total atualizado em tempo real

---

## 4️⃣ Engenharia de Software

- ⚡ **Threading**
  - Geração de arquivos em segundo plano
  - Barra de progresso real
  - Interface permanece responsiva

- 📦 **Executável Único**
  - Compilado via PyInstaller
  - Inclui:
    - Bibliotecas
    - Imagens
    - Tema
    - Modelo Word

---

# 📂 Estrutura do Projeto

```
📁 Projeto/
│
├── 📄 main.py               # Ponto de entrada (Boot da aplicação)
├── 📄 main.spec             # Configuração do PyInstaller
├── 📄 utils.py              # Funções utilitárias (Resource Path)
├── 📄 config.json           # Salva última pasta de saída usada
├── 📄 README.md             # Documentação do projeto
│
├── 📂 ui/                   # Interface Gráfica
│   ├── 📄 main_window.py    # Janela Principal
│   └── 📄 dialogs.py        # Janelas Secundárias
│
├── 📂 services/             # Lógica de Negócios
│   ├── 📄 generator.py      # Geração de arquivos (Word/PDF)
│   ├── 📄 parser.py         # Processamento de dados
│   └── 📄 reader.py         # Leitura de arquivos
│
├── 📄 tema_laranja.json     # Tema de cores
├── 📄 icone.ico             # Ícone da aplicação
└── 📄 proposta_modelo.docx  # Modelo Word (Jinja2)
```

---

# 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
|------------|--------|
| Python 3.13 | Linguagem principal |
| CustomTkinter | Interface moderna |
| DocxTpl (Jinja2) | Manipulação do Word |
| Docx2Pdf | Conversão para PDF |
| Requests | Integração API ReceitaWS |
| PyInstaller | Geração do executável |

---

# 🚀 Como Executar (Desenvolvimento)

## 1️⃣ Instalar dependências

```bash
pip install customtkinter docxtpl docx2pdf requests pyinstaller
```

## 2️⃣ Executar aplicação

```bash
python main.py
```

---

# 📦 Como Gerar o Executável (.exe)

Execute:

```bash
python -m PyInstaller --noconsole --onefile --icon="icone.ico" --collect-all customtkinter --collect-all docxtpl --hidden-import requests --add-data "tema_laranja.json;." --add-data "icone.ico;." --add-data "proposta_modelo.docx;." main.py
```

📁 O executável final estará em:

```
dist/main.exe
```

---

# 📝 Configuração do Modelo Word (Jinja2)

O arquivo `proposta_modelo.docx` utiliza tags Jinja2 para receber dados dinâmicos.

---

## 📌 Variáveis Simples

```plaintext
{{ NOME_CLIENTE }}
{{ DATA_HOJE }}
```

---

## 📌 Lista de Orçamento

```plaintext
{% for item in ITENS_ORCAMENTO %}
    Descrição: {{ item.descricao }}  |  Valor: {{ item.valor }}
{% endfor %}
```

---

## 📌 Lista Estrutural

```plaintext
{% for item in ITENS_ESTRUTURAL %}
    - {{ item }}
{% endfor %}
```

---

# 📄 Licença

Desenvolvido para uso interno — **Igor Parizi**.
