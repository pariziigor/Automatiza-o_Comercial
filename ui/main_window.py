import customtkinter as ctk  # <--- A GRANDE MUDANÇA
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import json
import os
from services import reader, parser, generator
from ui.dialogs import janela_verificacao_unificada, janela_itens_orcamento, janela_projeto_estrutural

# Configuração Global do Tema
ctk.set_appearance_mode("Dark")  # Modos: "System" (padrão), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Temas: "blue" (padrão), "green", "dark-blue"

class GeradorPropostasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Propostas Moderno")
        self.root.geometry("700x600")
        
        # Configuração inicial
        config = self._carregar_config()

        # Variáveis (Tkinter padrão continua sendo usado para variáveis)
        self.path_modelo = tk.StringVar() 
        self.path_solicitante = tk.StringVar()
        self.path_faturamento = tk.StringVar()
        self.path_saida = tk.StringVar(value=config.get("saida", ""))
        
        self.dados_finais = {}
        
        self._setup_ui()

    def _setup_ui(self):
        # Configuração do Grid da Janela Principal (para garantir que tudo estique)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1) # A linha do Log vai crescer

        # Título Principal
        lbl_titulo = ctk.CTkLabel(self.root, text="Gerador de Propostas", font=("Roboto", 24, "bold"))
        lbl_titulo.pack(pady=(20, 10))

        # --- FRAME DE ARQUIVOS ---
        f_arquivos = ctk.CTkFrame(self.root)
        f_arquivos.pack(fill="x", padx=20, pady=10)
        
        # A MÁGICA DA RESPONSIVIDADE ACONTECE AQUI:
        # Coluna 0: Labels (fixo)
        # Coluna 1: Inputs (ESTICA - weight=1)
        # Coluna 2: Botões (fixo)
        f_arquivos.grid_columnconfigure(1, weight=1) 

        # Label descritiva
        ctk.CTkLabel(f_arquivos, text="Arquivos de Entrada", font=("Roboto", 14, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=10)

        # Seletores
        self._criar_seletor(f_arquivos, "Modelo Word:", self.path_modelo, 1)
        self._criar_seletor(f_arquivos, "Ficha Solicitante:", self.path_solicitante, 2)
        self._criar_seletor(f_arquivos, "Ficha Faturamento:", self.path_faturamento, 3)
        
        ctk.CTkLabel(f_arquivos, text="(Opcional)", text_color="gray").grid(row=3, column=3, sticky="w", padx=(0, 10))

        # Divisória
        div = ctk.CTkFrame(f_arquivos, height=2, fg_color="gray30")
        div.grid(row=4, column=0, columnspan=4, sticky="ew", pady=15, padx=10)
        
        # Seletor de Pasta de Saída
        ctk.CTkLabel(f_arquivos, text="Salvar em:").grid(row=5, column=0, sticky="w", padx=15)
        
        entry_saida = ctk.CTkEntry(f_arquivos, textvariable=self.path_saida)
        entry_saida.grid(row=5, column=1, sticky="ew", padx=5, pady=5) # sticky="ew" estica horizontalmente
        
        ctk.CTkButton(f_arquivos, text="Selecionar", width=100, command=self._buscar_pasta).grid(row=5, column=2, padx=15)

        # --- BOTÃO DE AÇÃO ---
        self.btn_processar = ctk.CTkButton(
            self.root, 
            text="INICIAR PROCESSO", 
            command=self.fluxo_principal, 
            state="disabled",
            height=50,
            font=("Roboto", 16, "bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_processar.pack(fill="x", padx=20, pady=20)
        
        # --- LOG ---
        self.log_text = ctk.CTkTextbox(self.root)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_text.configure(state="disabled")

    def _criar_seletor(self, parent, label, var, row):
        # Label
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=15, pady=5)
        
        # Entry (Input) - Agora com sticky="ew" para esticar
        # Remoção do width fixo para ele obedecer o layout
        ctk.CTkEntry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Botão
        ctk.CTkButton(parent, text="Arquivo...", width=100, command=lambda: self._buscar_arquivo(var)).grid(row=row, column=2, padx=15, pady=5)

    # --- MÉTODOS DE LÓGICA ---
    def _buscar_arquivo(self, var_target):
        path = filedialog.askopenfilename()
        if path:
            var_target.set(path)
            if self.path_modelo.get() and self.path_solicitante.get():
                self.btn_processar.configure(state="normal") 
    
    def _buscar_pasta(self):
        path = filedialog.askdirectory()
        if path:
            self.path_saida.set(path)
            self._salvar_config()

    def log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")
        self.root.update()

    def _carregar_config(self):
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _salvar_config(self):
        dados = {"saida": self.path_saida.get()}
        try:
            with open("config.json", "w") as f:
                json.dump(dados, f, indent=4)
        except: pass

    # --- FLUXO PRINCIPAL (CÓDIGO IGUAL AO ANTERIOR) ---
    def fluxo_principal(self):
        try:
            self.log("1. Analisando Modelo...")
            placeholders = reader.extrair_placeholders_modelo(self.path_modelo.get())
            
            self.log("2. Lendo dados...")
            txt_solicitante = reader.ler_documento_cliente(self.path_solicitante.get())
            dados_auto = parser.processar_dados(placeholders, txt_solicitante)

            path_fat = self.path_faturamento.get()
            if path_fat:
                txt_fat = reader.ler_documento_cliente(path_fat)
                dados_fat = parser.processar_dados(placeholders, txt_fat, sufixo_filtro="_CONTRATANTE")
                dados_auto.update(dados_fat)

            # --- PASSO 1: REVISÃO ---
            self.log("3. Revisão (Passo 1/3)...")
            dados_revisados = janela_verificacao_unificada(self.root, placeholders, dados_auto)
            
            # VERIFICAÇÃO 1: Se fechou a janela de revisão
            if not dados_revisados:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa de Revisão.")
                self.log("Processo cancelado pelo usuário.")
                return

            # --- PASSO 2: ESTRUTURAL ---
            self.log("4. Estrutural (Passo 2/3)...")
            dados_com_estrutural = janela_projeto_estrutural(self.root, dados_revisados)
            
            # VERIFICAÇÃO 2: Se fechou a janela estrutural (não salvou a chave ITENS_ESTRUTURAL)
            if "ITENS_ESTRUTURAL" not in dados_com_estrutural:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa de Escopo Estrutural.")
                self.log("Processo cancelado pelo usuário.")
                return

            # --- PASSO 3: ORÇAMENTO ---
            self.log("5. Orçamento (Passo 3/3)...")
            dados_finais = janela_itens_orcamento(self.root, dados_com_estrutural)
            
            # VERIFICAÇÃO 3: Se fechou a janela de orçamento (não salvou a chave ITENS_ORCAMENTO)
            if "ITENS_ORCAMENTO" not in dados_finais:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa de Orçamento.")
                self.log("Processo cancelado pelo usuário.")
                return

            # --- FINALIZAÇÃO ---
            agora = datetime.now()
            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            dados_finais["DATA_HOJE"] = f"{agora.day} de {meses[agora.month - 1]} de {agora.year}"
            
            self.log("6. Gerando arquivos...")
            docx, pdf = generator.gerar_arquivos(self.path_modelo.get(), dados_finais, self.path_saida.get())
            
            messagebox.showinfo("Sucesso", f"Arquivos gerados com sucesso!")
            self.log("Concluído.")

        except Exception as e:
            self.log(f"ERRO: {e}")
            messagebox.showerror("Erro", str(e))