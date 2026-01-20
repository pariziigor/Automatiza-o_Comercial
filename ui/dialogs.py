import tkinter as tk
from tkinter import ttk

# --- 1. CONFIGURAÇÃO DE TEXTOS E ORDEM ---
LABELS_AMIGAVEIS = {
    # --- GRUPO 1: Dados do Projeto ---
    "NOME_CLIENTE": "Nome do Cliente",
    "NUMERO_PROJETO": "Número do Projeto",
    "TIPO_OBRA": "Tipo de Obra",
    "DESCRICAO_DA_OBRA": "Descrição da Obra",
    "ENDERECO_DA_OBRA": "Endereço da Obra",
    "ARQUIVOS_RECEBIDOS": "Arquivos Recebidos",
    "RESPONSAVEL_TECNICO": "Responsável Técnico/Contato",
    "CREA": "CREA",

    # --- GRUPO 2: Solicitante (Ordem desejada) ---
    "NOME_EMPRESA_SOLICITANTE": "Razão Social (Cliente)",
    "CNPJ_CPF_SOLICITANTE": "CNPJ / CPF",
    "IE_SOLICITANTE": "Inscrição Estadual",
    "ENDERECO_SOLICITANTE": "Endereço Completo",
    "BAIRRO_SOLICITANTE": "Bairro",
    "CIDADE_SOLICITANTE": "Cidade / Município",
    "CEP_SOLICITANTE": "CEP",
    "EMAIL_SOLICITANTE": "E-mail de Contato",
    "CELULAR_SOLICITANTE": "Telefone / Celular",
    
    # --- GRUPO 3: Faturamento ---
    "NOME_EMPRESA_CONTRATANTE": "Razão Social (Faturamento)",
    "CNPJ_CPF_CONTRATANTE": "CNPJ / CPF (Pagador)",
    "ENDERECO_CONTRATANTE": "Endereço de Cobrança",
    "BAIRRO_CONTRATANTE": "Bairro",
    "CIDADE_CONTRATANTE": "Cidade",
    "CEP_CONTRATANTE": "CEP",
    "EMAIL_CONTRATANTE": "E-mail Financeiro",
    "CELULAR_CONTRATANTE": "Celular",
    "ENDERECO_ENTREGA": "Endereço de Entrega",
}

def formatar_label(texto_cru):
    if texto_cru in LABELS_AMIGAVEIS:
        return LABELS_AMIGAVEIS[texto_cru]
    return texto_cru.replace("_", " ").title()

def obter_prioridade(campo):
    chaves = list(LABELS_AMIGAVEIS.keys())
    try:
        return chaves.index(campo)
    except ValueError:
        return 999

# --- JANELA PRINCIPAL ---

def janela_verificacao_unificada(parent, todos_placeholders, dados_extraidos, valor_frete_inicial):
    win = tk.Toplevel(parent)
    win.title("Conferência Geral dos Dados")
    win.geometry("1100x750")
    win.minsize(800, 600)
    
    resultado_final = {}
    widgets_texto = {}
    widgets_servicos = {}
    var_frete = tk.StringVar(value=valor_frete_inicial)

    # --- CABEÇALHO ---
    f_header = ttk.Frame(win, padding=15)
    f_header.pack(fill="x")
    ttk.Label(f_header, text="Revise os dados", font=("Arial", 14, "bold")).pack(anchor="w")
    ttk.Label(f_header, text="Redimensione a janela para ajustar os campos.", font=("Arial", 9), foreground="gray").pack(anchor="w")

    # --- ÁREA DE SCROLL RESPONSIVA ---
    container = ttk.Frame(win)
    container.pack(fill="both", expand=True, padx=10, pady=5)
    
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    def on_canvas_configure(event):
        canvas.itemconfig(frame_id, width=event.width)

    frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.bind("<Configure>", on_canvas_configure)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- CONFIGURAÇÃO DO GRID (PESOS) ---
    scrollable_frame.columnconfigure(1, weight=1)
    scrollable_frame.columnconfigure(4, weight=1)

    row_idx = [0]

    def add_separator(titulo, cor="#333"):
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row_idx[0], column=0, columnspan=5, sticky="ew", pady=(20, 10))
        row_idx[0] += 1
        lbl = ttk.Label(scrollable_frame, text=titulo, font=("Arial", 11, "bold"), foreground=cor)
        lbl.grid(row=row_idx[0], column=0, columnspan=5, sticky="w", pady=(0, 10))
        row_idx[0] += 1

    # 1. FRETE
    add_separator("1. OPÇÕES DA PROPOSTA", "#444")
    ttk.Label(scrollable_frame, text="Tipo de Frete:").grid(row=row_idx[0], column=0, sticky="w", padx=5)
    
    # --- CORREÇÃO: Definindo a lista antes de usar ---
    opcoes_frete = ["CIF - Por conta do destinatário", "FOB - Por conta do Cliente"]
    
    combo = ttk.Combobox(scrollable_frame, textvariable=var_frete, values=opcoes_frete, state="readonly")
    combo.grid(row=row_idx[0], column=1, sticky="ew", padx=5)
    row_idx[0] += 1

    # 2. SERVIÇOS (GRID RESPONSIVO)
    lista_servicos = sorted([p for p in todos_placeholders if p.startswith("X_")])
    if lista_servicos:
        add_separator("2. SELEÇÃO DE SERVIÇOS", "#0055cc")
        f_servicos = ttk.Frame(scrollable_frame)
        f_servicos.grid(row=row_idx[0], column=0, columnspan=5, sticky="ew", padx=5)
        row_idx[0] += 1
        
        f_servicos.columnconfigure(0, weight=1)
        f_servicos.columnconfigure(1, weight=1)
        f_servicos.columnconfigure(2, weight=1)
        
        col_chk = 0
        row_chk = 0
        for servico in lista_servicos:
            nome_bonito = servico.replace("X_", "").replace("_", " ").title()
            var_chk = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(f_servicos, text=nome_bonito, variable=var_chk)
            chk.grid(row=row_chk, column=col_chk, sticky="w", padx=10, pady=5)
            
            widgets_servicos[servico] = var_chk
            
            col_chk += 1
            if col_chk > 2:
                col_chk = 0
                row_chk += 1

    # 3. CAMPOS DE TEXTO
    todos_campos_texto = [p for p in todos_placeholders if not p.startswith("X_") and p != "TIPO_FRETE"]
    
    grupo_solicitante = [p for p in todos_campos_texto if p.endswith("_SOLICITANTE")]
    grupo_contratante = [p for p in todos_campos_texto if p.endswith("_CONTRATANTE")]
    grupo_outros = [p for p in todos_campos_texto if p not in grupo_solicitante and p not in grupo_contratante]

    grupo_solicitante.sort(key=obter_prioridade)
    grupo_contratante.sort(key=obter_prioridade)
    grupo_outros.sort(key=obter_prioridade)

    def desenhar_campos_lado_a_lado(lista_campos, titulo_secao, cor):
        if not lista_campos: return
        add_separator(titulo_secao, cor)
        
        for i, campo in enumerate(lista_campos):
            valor_auto = dados_extraidos.get(campo, "")
            texto_label = formatar_label(campo)
            
            l = ttk.Label(scrollable_frame, text=texto_label, font=("Arial", 9))
            ent = ttk.Entry(scrollable_frame)
            
            if valor_auto:
                ent.insert(0, valor_auto)
                ent.config(background="#d9ffcc")
            widgets_texto[campo] = ent

            if i % 2 == 0: # LADO ESQUERDO
                l.grid(row=row_idx[0], column=0, sticky="w", padx=(5, 5), pady=5)
                ent.grid(row=row_idx[0], column=1, sticky="ew", padx=(0, 20), pady=5)
                
                if i == len(lista_campos) - 1:
                    row_idx[0] += 1
            else: # LADO DIREITO
                ttk.Frame(scrollable_frame, width=20).grid(row=row_idx[0], column=2)
                l.grid(row=row_idx[0], column=3, sticky="w", padx=(5, 5), pady=5)
                ent.grid(row=row_idx[0], column=4, sticky="ew", padx=(0, 5), pady=5)
                row_idx[0] += 1

    desenhar_campos_lado_a_lado(grupo_outros, "3. DADOS DO PROJETO / GERAIS", "#333")
    desenhar_campos_lado_a_lado(grupo_solicitante, "4. DADOS DO SOLICITANTE", "#0055cc")
    desenhar_campos_lado_a_lado(grupo_contratante, "5. DADOS DE FATURAMENTO", "#cc5500")

    # BOTÃO FINAL
    def confirmar():
        resultado_final["TIPO_FRETE"] = var_frete.get()
        for k, v in widgets_servicos.items():
            resultado_final[k] = "X" if v.get() else ""
        for k, entry in widgets_texto.items():
            resultado_final[k] = entry.get()
        win.destroy()

    f_footer = ttk.Frame(win, padding=15)
    f_footer.pack(fill="x")
    ttk.Button(f_footer, text="CONFIRMAR E GERAR ARQUIVOS", command=confirmar).pack(fill="x", ipady=10)

    parent.wait_window(win)
    return resultado_final