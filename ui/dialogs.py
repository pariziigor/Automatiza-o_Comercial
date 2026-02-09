import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox

# --- CONFIGURAÇÃO DE ESTILO PARA A TABELA (Treeview) ---
def aplicar_estilo_tabela():
    """Aplica um tema escuro/moderno na Treeview padrão do Tkinter."""
    style = ttk.Style()
    style.theme_use("default")
    
    # Cores do Modo Escuro
    bg_color = "#2b2b2b"
    text_color = "white"
    selected_color = "#1f538d"
    
    style.configure("Treeview",
                    background=bg_color,
                    foreground=text_color,
                    fieldbackground=bg_color,
                    borderwidth=0,
                    rowheight=25)
    
    style.configure("Treeview.Heading",
                    background="#1a1a1a",
                    foreground="white",
                    relief="flat")
    
    style.map("Treeview",
              background=[("selected", selected_color)])

# --- JANELA 1: REVISÃO DE DADOS ---
def janela_verificacao_unificada(parent, todos_placeholders, dados_extraidos):
    # Configura janela como Toplevel do CustomTkinter
    win = ctk.CTkToplevel(parent)
    win.title("Conferência Geral dos Dados")
    win.geometry("900x700")
    
    # Garante que a janela fique no topo e em foco
    win.lift()
    win.focus_force()
    
    resultado_final = {}
    widgets_texto = {}
    widgets_servicos = {}
    
    # Variável de Frete
    var_frete = ctk.StringVar(value="CIF - Por conta do destinatário")

    # Cabeçalho
    ctk.CTkLabel(win, text="Revise os dados abaixo", font=("Roboto", 20, "bold")).pack(pady=(20, 5), padx=20, anchor="w")
    ctk.CTkLabel(win, text="Campos vazios serão removidos do documento.", text_color="gray").pack(pady=(0, 10), padx=20, anchor="w")

    # --- ÁREA DE ROLAGEM ---
    scroll_frame = ctk.CTkScrollableFrame(win)
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    # Função auxiliar para títulos de seção
    def add_section_title(texto):
        ctk.CTkLabel(scroll_frame, text=texto, font=("Roboto", 16, "bold"), text_color=("#3B8ED0", "#1f538d")).pack(anchor="w", pady=(20, 10))
        ctk.CTkFrame(scroll_frame, height=2, fg_color="gray30").pack(fill="x", pady=(0, 10))

    # 1. OPÇÕES
    add_section_title("1. OPÇÕES DA PROPOSTA")
    
    f_opcoes = ctk.CTkFrame(scroll_frame, fg_color="transparent")
    f_opcoes.pack(fill="x", pady=5)
    
    ctk.CTkLabel(f_opcoes, text="Tipo de Frete:").pack(side="left", padx=(0, 10))
    opcoes_frete = ["CIF - Por conta do destinatário", "FOB - Por conta do Cliente"]
    
    c_frete = ctk.CTkComboBox(f_opcoes, variable=var_frete, values=opcoes_frete, width=300)
    c_frete.pack(side="left")

    # 2. SERVIÇOS (Checkboxes)
    lista_servicos = sorted([p for p in todos_placeholders if p.startswith("X_")])
    if lista_servicos:
        add_section_title("2. SELEÇÃO DE SERVIÇOS")
        
        # Grid de Checkboxes
        f_servicos = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_servicos.pack(fill="x")
        
        # Configurar grid responsivo
        f_servicos.grid_columnconfigure(0, weight=1)
        f_servicos.grid_columnconfigure(1, weight=1)
        f_servicos.grid_columnconfigure(2, weight=1)

        col = 0
        row = 0
        for servico in lista_servicos:
            nome_bonito = servico.replace("X_", "").replace("_", " ").title()
            # CTkCheckBox
            chk = ctk.CTkCheckBox(f_servicos, text=nome_bonito)
            chk.grid(row=row, column=col, sticky="w", padx=10, pady=10)
            widgets_servicos[servico] = chk
            
            col += 1
            if col > 2: # 3 colunas
                col = 0
                row += 1

    # 3. CAMPOS DE TEXTO
    # Lista Negra (Campos para ignorar nesta tela)
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
    
    # Grupos
    grupo_solicitante = [p for p in todos_campos_texto if p.endswith("_SOLICITANTE")]
    grupo_contratante = [p for p in todos_campos_texto if p.endswith("_CONTRATANTE")]
    grupo_outros = [p for p in todos_campos_texto if p not in grupo_solicitante and p not in grupo_contratante]

    # Função para desenhar campos (Input Moderno)
    def desenhar_campos(lista, titulo):
        if not lista: return
        add_section_title(titulo)
        
        f_campos = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        f_campos.pack(fill="x")
        f_campos.grid_columnconfigure(1, weight=1) # Input da esq estica
        f_campos.grid_columnconfigure(3, weight=1) # Input da dir estica

        for i, campo in enumerate(lista):
            valor_auto = dados_extraidos.get(campo, "")
            texto_label = campo.replace("_SOLICITANTE", "").replace("_CONTRATANTE", "").replace("_", " ").title()
            
            # Input
            ent = ctk.CTkEntry(f_campos)
            if valor_auto:
                ent.insert(0, valor_auto)
                # Destaque sutil para campos preenchidos automaticamente
                ent.configure(placeholder_text="Automático")
            
            widgets_texto[campo] = ent

            # Layout 2 colunas
            row = i // 2
            col_start = (i % 2) * 2 # 0 ou 2
            
            ctk.CTkLabel(f_campos, text=texto_label).grid(row=row, column=col_start, sticky="w", padx=5, pady=5)
            ent.grid(row=row, column=col_start+1, sticky="ew", padx=(0, 20), pady=5)

    desenhar_campos(grupo_outros, "3. DADOS GERAIS")
    desenhar_campos(grupo_solicitante, "4. DADOS DO SOLICITANTE")
    desenhar_campos(grupo_contratante, "5. DADOS DE FATURAMENTO")

    # --- RODAPÉ ---
    def confirmar():
        resultado_final["TIPO_FRETE"] = var_frete.get()
        
        for k, chk in widgets_servicos.items():
            resultado_final[k] = "X" if chk.get() == 1 else "" # CTk checkbox retorna 1/0
        
        for k, entry in widgets_texto.items():
            resultado_final[k] = entry.get()
            
        win.destroy()

    btn_confirma = ctk.CTkButton(win, text="CONFIRMAR E CONTINUAR", command=confirmar, height=50, fg_color="green", hover_color="darkgreen")
    btn_confirma.pack(fill="x", padx=20, pady=20)

    parent.wait_window(win)
    return resultado_final


# --- JANELA 2: ESCOPO ESTRUTURAL ---
def janela_projeto_estrutural(parent, dados_anteriores):
    win = ctk.CTkToplevel(parent)
    win.title("Passo 2: Escopo Estrutural")
    win.geometry("900x700")
    win.lift()
    win.focus_force()

    lista_itens_estrutural = []
    
    # Aplica estilo na tabela
    aplicar_estilo_tabela()

    ctk.CTkLabel(win, text="Definição do Escopo Estrutural", font=("Roboto", 20, "bold")).pack(pady=(20, 5))
    ctk.CTkLabel(win, text="Insira os itens de texto livre (ex: ART, Memória de Cálculo).", text_color="gray").pack()

    # Área de Inserção
    f_input = ctk.CTkFrame(win)
    f_input.pack(fill="x", padx=20, pady=10)

    ctk.CTkLabel(f_input, text="Descrição do Item:").pack(anchor="w", padx=10, pady=(10,0))
    
    # Caixa de Texto Grande (Multi-line)
    txt_desc = ctk.CTkTextbox(f_input, height=80)
    txt_desc.pack(fill="x", padx=10, pady=5)
    ctk.CTkLabel(f_input, text="Dica: Use Enter para criar sub-itens ou listas com bolinhas.", font=("Arial", 10), text_color="gray").pack(anchor="w", padx=10)

    # Tabela 
    f_lista = ctk.CTkFrame(win, fg_color="transparent") # Frame transparente para conter a tabela
    f_lista.pack(fill="both", expand=True, padx=20, pady=5)

    columns = ("desc",)
    tree = ttk.Treeview(f_lista, columns=columns, show="headings", selectmode="browse")
    tree.heading("desc", text="Itens Adicionados")
    tree.column("desc", anchor="w")
    
    # Scrollbar do CTk conectada ao Treeview
    scrollbar = ctk.CTkScrollbar(f_lista, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Lógica
    def adicionar_item():
        desc = txt_desc.get("1.0", "end-1c").strip()
        if not desc: return

        primeira_linha = desc.split("\n")[0]
        if len(desc.split("\n")) > 1: primeira_linha += " (...)"
            
        tree.insert("", "end", values=(primeira_linha,), tags=(desc,)) # Guarda texto completo na tag
        lista_itens_estrutural.append(desc)
        txt_desc.delete("1.0", "end")
        txt_desc.focus()

    def remover_item():
        selected = tree.selection()
        if not selected: return
        for item_id in selected:
            idx = tree.index(item_id)
            if idx < len(lista_itens_estrutural):
                lista_itens_estrutural.pop(idx)
            tree.delete(item_id)

    def finalizar():
        dados_anteriores["ITENS_ESTRUTURAL"] = lista_itens_estrutural
        win.destroy()

    # Botões
    btn_add = ctk.CTkButton(f_input, text="Adicionar Item", command=adicionar_item)
    btn_add.pack(anchor="e", padx=10, pady=10)
    
    f_footer = ctk.CTkFrame(win, height=50, fg_color="transparent")
    f_footer.pack(fill="x", padx=20, pady=20)
    
    ctk.CTkButton(f_footer, text="Remover Selecionado", command=remover_item, fg_color="firebrick", hover_color="darkred").pack(side="left")
    ctk.CTkButton(f_footer, text="CONCLUIR", command=finalizar, fg_color="green", hover_color="darkgreen").pack(side="right")

    parent.wait_window(win)
    return dados_anteriores

# --- JANELA 3: ORÇAMENTO ---
def janela_itens_orcamento(parent, dados_anteriores):
    win = ctk.CTkToplevel(parent)
    win.title("Passo 3: Orçamento")
    win.geometry("900x700")
    win.lift()
    win.focus_force()

    lista_itens = []
    total_geral_float = 0.0
    
    aplicar_estilo_tabela()

    # Header
    ctk.CTkLabel(win, text="Composição do Orçamento", font=("Roboto", 20, "bold")).pack(pady=(20, 10))

    # Área de Input
    f_input = ctk.CTkFrame(win)
    f_input.pack(fill="x", padx=20, pady=10)
    
    f_input.grid_columnconfigure(0, weight=1) # Descrição estica

    ctk.CTkLabel(f_input, text="Descrição:").grid(row=0, column=0, sticky="w", padx=10, pady=(10,0))
    ctk.CTkLabel(f_input, text="Valor (R$):").grid(row=0, column=1, sticky="w", padx=10, pady=(10,0))

    entry_desc = ctk.CTkEntry(f_input)
    entry_desc.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    entry_valor = ctk.CTkEntry(f_input, width=150)
    entry_valor.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
    
    # Tabela
    f_lista = ctk.CTkFrame(win, fg_color="transparent")
    f_lista.pack(fill="both", expand=True, padx=20, pady=5)

    columns = ("desc", "valor")
    tree = ttk.Treeview(f_lista, columns=columns, show="headings")
    tree.heading("desc", text="Descrição")
    tree.heading("valor", text="Valor")
    tree.column("desc", width=500)
    tree.column("valor", width=150, anchor="e")

    scrollbar = ctk.CTkScrollbar(f_lista, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Rodapé Total
    lbl_total = ctk.CTkLabel(win, text="TOTAL GERAL: R$ 0,00", font=("Roboto", 24, "bold"), text_color="green")
    lbl_total.pack(pady=10)

    # Lógica
    def formatar_moeda(valor_float):
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def converter_brl_para_float(texto):
        limpo = texto.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        try: return float(limpo)
        except: return 0.0

    def adicionar_item():
        nonlocal total_geral_float
        desc = entry_desc.get().strip()
        valor_txt = entry_valor.get().strip()

        if not desc or not valor_txt: return

        try:
            valor_float = converter_brl_para_float(valor_txt)
            valor_fmt = formatar_moeda(valor_float)

            tree.insert("", "end", values=(desc, valor_fmt))
            lista_itens.append({"descricao": desc, "valor": valor_fmt})

            total_geral_float += valor_float
            lbl_total.configure(text=f"TOTAL GERAL: {formatar_moeda(total_geral_float)}")

            entry_desc.delete(0, "end")
            entry_valor.delete(0, "end")
            entry_desc.focus()
        except:
            messagebox.showerror("Erro", "Valor inválido.")

    def remover_item():
        nonlocal total_geral_float
        selected = tree.selection()
        if not selected: return

        for item_id in selected: tree.delete(item_id)
        
        lista_itens.clear()
        total_geral_float = 0.0
        
        for child in tree.get_children():
            vals = tree.item(child)['values']
            val_float = converter_brl_para_float(str(vals[1]))
            lista_itens.append({"descricao": vals[0], "valor": vals[1]})
            total_geral_float += val_float

        lbl_total.configure(text=f"TOTAL GERAL: {formatar_moeda(total_geral_float)}")

    def finalizar():
        dados_anteriores["ITENS_ORCAMENTO"] = lista_itens
        dados_anteriores["VALOR_TOTAL_PROPOSTA"] = formatar_moeda(total_geral_float)
        win.destroy()

    # Botões Finais
    btn_add = ctk.CTkButton(f_input, text="Adicionar (+)", command=adicionar_item, width=120)
    btn_add.grid(row=1, column=2, padx=10, pady=(0, 10))

    f_footer = ctk.CTkFrame(win, fg_color="transparent")
    f_footer.pack(fill="x", padx=20, pady=20)

    ctk.CTkButton(f_footer, text="Remover Item", command=remover_item, fg_color="firebrick", hover_color="darkred").pack(side="left")
    ctk.CTkButton(f_footer, text="GERAR PROPOSTA", command=finalizar, fg_color="green", hover_color="darkgreen", height=40).pack(side="right", fill="x", expand=True, padx=(20, 0))

    parent.wait_window(win)
    return dados_anteriores