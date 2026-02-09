import tkinter as tk
from tkinter import ttk

# --- CONFIGURAÇÃO DE TEXTOS E ORDEM ---
LABELS_AMIGAVEIS = {
    # --- GRUPO 1: Dados do Projeto ---
    "NUMERO_PROJETO": "Número Projeto",
    "TIPO_OBRA": "Tipo de Obra",
    "DESCRICAO_DA_OBRA": "Descrição da Obra",
    "ENDERECO_DA_OBRA": "Endereço da Obra",
    "ARQUIVOS_RECEBIDOS": "Arquivos Recebidos",
    "RESPONSAVEL_TECNICO":  "Responsável Técnico",
    "CREA": "CREA",

    # --- GRUPO 2: Dados do Solicitante ---
    "NOME_EMPRESA_SOLICITANTE": "Nome / Empresa",
    "CNPJ_CPF_SOLICITANTE": "CNPJ/CPF",
    "IE_SOLICITANTE": "IE",
    "ENDERECO_SOLICITANTE": " Endereço",
    "BAIRRO_SOLICITANTE": "Bairro",
    "CIDADE_SOLICITANTE": "Cidade",
    "CEP_SOLICITANTE": "CEP",
    "EMAIL_SOLICITANTE": "E-mail",
    "CELULAR_SOLICITANTE": "Celular",
    
    # --- GRUPO 3: Dados do faturamento ---
    "NOME_EMPRESA_CONTRATANTE": "Nome / Empresa",
    "CNPJ_CPF_CONTRATANTE": "CNPJ/CPF",
    "ENDERECO_CONTRATANTE":  "Endereço", 
    "BAIRRO_CONTRATANTE": "Bairro",
    "CIDADE_CONTRATANTE": "Cidade",
    "CEP_CONTRATANTE": "CEP",
    "EMAIL_CONTRATANTE": "E-mail", 
    "CELULAR_CONTRATANTE": "Celular", 
    "ENDERECO_ENTREGA": "Endereço de entrega",

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

def janela_verificacao_unificada(parent, todos_placeholders, dados_extraidos):
    
    win = tk.Toplevel(parent)
    win.title("Conferência Geral dos Dados")
    win.geometry("1100x750")
    win.minsize(800, 600)
    
    resultado_final = {}
    widgets_texto = {}
    widgets_servicos = {}
    
    # --- CRIAÇÃO LOCAL DA VARIÁVEL DE FRETE ---
    var_frete = tk.StringVar(value="CIF - Por conta do destinatário")

    # --- CABEÇALHO ---
    f_header = ttk.Frame(win, padding=15)
    f_header.pack(fill="x")
    ttk.Label(f_header, text="Revise os dados", font=("Arial", 14, "bold")).pack(anchor="w")

    # --- SCROLL ---
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

    scrollable_frame.columnconfigure(1, weight=1)
    scrollable_frame.columnconfigure(4, weight=1)

    row_idx = [0]

    def add_separator(titulo, cor="#333"):
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=row_idx[0], column=0, columnspan=5, sticky="ew", pady=(20, 10))
        row_idx[0] += 1
        lbl = ttk.Label(scrollable_frame, text=titulo, font=("Arial", 11, "bold"), foreground=cor)
        lbl.grid(row=row_idx[0], column=0, columnspan=5, sticky="w", pady=(0, 10))
        row_idx[0] += 1

    # 1. OPÇÕES
    add_separator("1. OPÇÕES DA PROPOSTA", "#444")
    
    ttk.Label(scrollable_frame, text="Tipo de Frete:").grid(row=row_idx[0], column=0, sticky="w", padx=5)
    opcoes_frete = ["CIF - Por conta do destinatário", "FOB - Por conta do Cliente"]
    c_frete = ttk.Combobox(scrollable_frame, textvariable=var_frete, values=opcoes_frete, state="readonly")
    c_frete.grid(row=row_idx[0], column=1, sticky="ew", padx=5)
    row_idx[0] += 1

    # 2. SERVIÇOS
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
    # Mantém TIPO_FRETE na lista negra para não duplicar
    campos_ignorados = [
        "TIPO_FRETE", "VALOR_TOTAL_PROPOSTA", 
        "ITENS_ORCAMENTO", "ITENS_ESTRUTURAL",
        "item", "item.descricao", "item.valor", "item.qtd", "item.subtotal",
        "DATA_HOJE"
    ]

    todos_campos_texto = [
        p for p in todos_placeholders 
        if not p.startswith("X_") 
        and p not in campos_ignorados
        and not p.startswith("item.")
    ]
    
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

            if i % 2 == 0:
                l.grid(row=row_idx[0], column=0, sticky="w", padx=(5, 5), pady=5)
                ent.grid(row=row_idx[0], column=1, sticky="ew", padx=(0, 20), pady=5)
                if i == len(lista_campos) - 1: row_idx[0] += 1
            else:
                ttk.Frame(scrollable_frame, width=20).grid(row=row_idx[0], column=2)
                l.grid(row=row_idx[0], column=3, sticky="w", padx=(5, 5), pady=5)
                ent.grid(row=row_idx[0], column=4, sticky="ew", padx=(0, 5), pady=5)
                row_idx[0] += 1

    desenhar_campos_lado_a_lado(grupo_outros, "3. DADOS DO PROJETO / GERAIS", "#333")
    desenhar_campos_lado_a_lado(grupo_solicitante, "4. DADOS DO SOLICITANTE", "#0055cc")
    desenhar_campos_lado_a_lado(grupo_contratante, "5. DADOS DE FATURAMENTO", "#cc5500")

    def confirmar():
        # Salva o valor do frete escolhido nesta janela
        resultado_final["TIPO_FRETE"] = var_frete.get()
        
        for k, v in widgets_servicos.items():
            resultado_final[k] = "X" if v.get() else ""
        for k, entry in widgets_texto.items():
            resultado_final[k] = entry.get()
        win.destroy()

    f_footer = ttk.Frame(win, padding=15)
    f_footer.pack(fill="x")
    ttk.Button(f_footer, text="CONFIRMAR E CONTINUAR", command=confirmar).pack(fill="x", ipady=10)

    parent.wait_window(win)
    return resultado_final

# --- FUNÇÃO: JANELA DE ORÇAMENTO (SIMPLIFICADA - SEM QUANTIDADE) ---
def janela_itens_orcamento(parent, dados_anteriores):
    """
    Janela para inserir itens e valores (Simplificada).
    """
    win = tk.Toplevel(parent)
    win.title("Passo 3: Composição do Orçamento")
    win.geometry("900x600")
    win.minsize(800, 500)

    lista_itens = []
    total_geral_float = 0.0

    # --- LAYOUT ---
    
    # 1. Área de Inserção
    f_input = ttk.LabelFrame(win, text="Adicionar", padding=10) # Simplifiquei o título do quadro também
    f_input.pack(fill="x", padx=10, pady=10)

    f_input.columnconfigure(0, weight=1)

    # Linha 1: Labels
    ttk.Label(f_input, text="Descrição:").grid(row=0, column=0, sticky="w")
    
    ttk.Label(f_input, text="Valor (R$):").grid(row=0, column=1, sticky="w", padx=10)

    # Linha 2: Inputs
    entry_desc = ttk.Entry(f_input)
    entry_desc.grid(row=1, column=0, sticky="ew")

    entry_valor = ttk.Entry(f_input, width=20)
    entry_valor.grid(row=1, column=1, sticky="ew", padx=10)

    # 2. Lista de Itens (Treeview)
    f_lista = ttk.Frame(win)
    f_lista.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("desc", "valor")
    tree = ttk.Treeview(f_lista, columns=columns, show="headings", height=10)
    
    tree.heading("desc", text="Descrição")
    tree.heading("valor", text="Valor")

    tree.column("desc", width=600)
    tree.column("valor", width=150, anchor="e")

    scrollbar = ttk.Scrollbar(f_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 3. Rodapé
    f_footer = ttk.Frame(win, padding=15)
    f_footer.pack(fill="x")

    lbl_total = ttk.Label(f_footer, text="TOTAL GERAL: R$ 0,00", font=("Arial", 14, "bold"), foreground="#006600")
    lbl_total.pack(side="left")

    # --- LÓGICA INTERNA ---

    def formatar_moeda(valor_float):
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def converter_brl_para_float(texto):
        limpo = texto.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try:
            return float(limpo)
        except ValueError:
            return 0.0

    def adicionar_item():
        nonlocal total_geral_float
        
        desc = entry_desc.get().strip()
        valor_txt = entry_valor.get().strip()

        if not desc or not valor_txt:
            return

        try:
            valor_float = converter_brl_para_float(valor_txt)
            valor_fmt = formatar_moeda(valor_float)

            tree.insert("", "end", values=(desc, valor_fmt))
            
            lista_itens.append({
                "descricao": desc,
                "valor": valor_fmt
            })

            total_geral_float += valor_float
            lbl_total.config(text=f"TOTAL GERAL: {formatar_moeda(total_geral_float)}")

            entry_desc.delete(0, tk.END)
            entry_valor.delete(0, tk.END)
            entry_desc.focus()

        except ValueError:
            tk.messagebox.showerror("Erro", "Valor inválido.")

    def remover_item():
        nonlocal total_geral_float
        selected = tree.selection()
        if not selected: return

        for item_id in selected:
            tree.delete(item_id)
        
        lista_itens.clear()
        total_geral_float = 0.0
        
        for child in tree.get_children():
            vals = tree.item(child)['values']
            val_float = converter_brl_para_float(str(vals[1]))
            
            lista_itens.append({
                "descricao": vals[0],
                "valor": vals[1]
            })
            total_geral_float += val_float

        lbl_total.config(text=f"TOTAL GERAL: {formatar_moeda(total_geral_float)}")

    def finalizar():
        dados_anteriores["ITENS_ORCAMENTO"] = lista_itens
        dados_anteriores["VALOR_TOTAL_PROPOSTA"] = formatar_moeda(total_geral_float)
        win.destroy()

    # Botões
    btn_add = ttk.Button(f_input, text="Adicionar (+)", command=adicionar_item)
    btn_add.grid(row=1, column=2, padx=10, sticky="ew")
    
    btn_remove = ttk.Button(f_lista, text="Remover Item Selecionado", command=remover_item)
    btn_remove.pack(pady=5, anchor="e")

    ttk.Button(f_footer, text="CONCLUIR E GERAR DOCUMENTO", command=finalizar).pack(side="right", ipady=10, padx=5)

    parent.wait_window(win)
    return dados_anteriores
    # --- NOVA FUNÇÃO: JANELA DE ESCOPO ESTRUTURAL ---
def janela_projeto_estrutural(parent, dados_anteriores):
    """
    Janela para inserir os itens do Escopo do Projeto (Texto livre).
    """
    win = tk.Toplevel(parent)
    win.title("Passo 3: Escopo do Projeto Estrutural")
    win.geometry("900x650")
    win.minsize(800, 500)

    lista_itens_estrutural = []

    # --- CABEÇALHO ---
    ttk.Label(win, text="Definição do Escopo Estrutural", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(win, text="Adicione os itens que farão parte da proposta comercial.", font=("Arial", 9)).pack()

    # --- ÁREA DE INSERÇÃO ---
    f_input = ttk.LabelFrame(win, text="Novo Item do Escopo", padding=10)
    f_input.pack(fill="x", padx=10, pady=10)

    ttk.Label(f_input, text="Descrição do Item:").pack(anchor="w")
    
    # Usamos Text em vez de Entry para permitir múltiplas linhas (sub-itens com bolinhas)
    txt_desc = tk.Text(f_input, height=5, width=80) 
    txt_desc.pack(fill="x", pady=5)
    ttk.Label(f_input, text="Dica: Você pode colar textos com quebras de linha aqui.", font=("Arial", 8, "italic"), foreground="gray").pack(anchor="w")

    # --- LISTA VISUAL (TREEVIEW) ---
    f_lista = ttk.Frame(win)
    f_lista.pack(fill="both", expand=True, padx=10, pady=5)

    columns = ("desc",)
    tree = ttk.Treeview(f_lista, columns=columns, show="headings", height=10)
    
    tree.heading("desc", text="Itens Adicionados")
    tree.column("desc", width=800, anchor="w") # Coluna larga

    scrollbar = ttk.Scrollbar(f_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # --- LÓGICA ---
    def adicionar_item():
        # Pega o texto do widget Text (do inicio '1.0' até o fim 'end-1c')
        desc = txt_desc.get("1.0", "end-1c").strip()

        if not desc:
            return

        # Adiciona na visualização (mostra apenas a primeira linha para não poluir)
        primeira_linha = desc.split("\n")[0]
        if len(desc.split("\n")) > 1:
            primeira_linha += " (...)"
            
        tree.insert("", "end", values=(primeira_linha,), tags=(desc,)) # Guardamos o texto completo na tag
        
        # Adiciona na lista de dados real
        lista_itens_estrutural.append(desc)

        # Limpa o campo
        txt_desc.delete("1.0", tk.END)
        txt_desc.focus()

    def remover_item():
        selected = tree.selection()
        if not selected: return

        # Remove da lista de dados e da árvore
        for item_id in selected:
            # Precisamos achar o índice para remover da lista 'lista_itens_estrutural'
            # Como a Treeview insere em ordem, o índice visual (index) geralmente bate com o da lista
            idx = tree.index(item_id)
            if idx < len(lista_itens_estrutural):
                lista_itens_estrutural.pop(idx)
            
            tree.delete(item_id)

    def finalizar():
        dados_anteriores["ITENS_ESTRUTURAL"] = lista_itens_estrutural
        win.destroy()

    # --- BOTÕES ---
    btn_add = ttk.Button(f_input, text="Adicionar Item à Lista", command=adicionar_item)
    btn_add.pack(anchor="e", pady=5)
    
    f_footer = ttk.Frame(win, padding=15)
    f_footer.pack(fill="x")
    
    ttk.Button(f_footer, text="Remover Selecionado", command=remover_item).pack(side="left")
    ttk.Button(f_footer, text="CONCLUIR TUDO E GERAR PDF", command=finalizar).pack(side="right", ipady=10)

    parent.wait_window(win)
    return dados_anteriores