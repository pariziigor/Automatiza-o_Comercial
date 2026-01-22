import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from services import reader, parser, generator
from ui.dialogs import janela_verificacao_unificada
class GeradorPropostasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador Automático de Propostas - v3.2")
        self.root.geometry("600x700") # Aumentei um pouco mais
        
        # Variáveis de Caminho
        self.path_modelo = tk.StringVar()
        self.path_solicitante = tk.StringVar()
        self.path_faturamento = tk.StringVar()
        
        # --- VARIÁVEIS DE OPÇÃO ---
        self.var_frete = tk.StringVar(value="CIF - Por conta do destinatário")
        self.var_pagamento = tk.StringVar(value="À vista") # NOVA VARIÁVEL
        
        self.dados_finais = {}
        
        self._setup_ui()

    def _setup_ui(self):
        # Frame Arquivos
        f_arquivos = ttk.LabelFrame(self.root, text="Arquivos de Entrada", padding=10)
        f_arquivos.pack(fill="x", padx=10, pady=10)
        
        self._criar_seletor(f_arquivos, "Modelo Word:", self.path_modelo, 0)
        self._criar_seletor(f_arquivos, "Ficha Solicitante:", self.path_solicitante, 1)
        self._criar_seletor(f_arquivos, "Ficha Faturamento (Opcional):", self.path_faturamento, 2)
        ttk.Label(f_arquivos, text="(Deixe vazio se for o mesmo)", font=("Arial", 8, "italic")).grid(row=3, column=1, sticky="w", padx=5)

        # --- FRAME DE OPÇÕES (Frete + Pagamento) ---
        f_opcoes = ttk.LabelFrame(self.root, text="Opções da Proposta", padding=10)
        f_opcoes.pack(fill="x", padx=10, pady=5)
        
        # 1. Frete
        ttk.Label(f_opcoes, text="Tipo de Frete:").grid(row=0, column=0, sticky="w", pady=5)
        opcoes_frete = ["CIF - Por conta do destinatário", "FOB - Por conta do Cliente"]
        c_frete = ttk.Combobox(f_opcoes, textvariable=self.var_frete, values=opcoes_frete, state="readonly", width=35)
        c_frete.grid(row=0, column=1, padx=10, pady=5)
        
        # 2. Pagamento (NOVO)
        ttk.Label(f_opcoes, text="Cond. Pagamento:").grid(row=1, column=0, sticky="w", pady=5)
        # Edite esta lista conforme suas necessidades
        opcoes_pag = ["À vista", "15 DD", "15 / 30 DD", "15 / 30 / 45 DD", "15 / 30 / 45 / 60 DD", "1X Cartão", "2X Catão", "3X Cartão", "4X Cartão"]
        c_pag = ttk.Combobox(f_opcoes, textvariable=self.var_pagamento, values=opcoes_pag, state="readonly", width=35)
        c_pag.grid(row=1, column=1, padx=10, pady=5)
        
        # Botão Ação
        self.btn_processar = ttk.Button(self.root, text="INICIAR PROCESSO", command=self.fluxo_principal, state="disabled")
        self.btn_processar.pack(fill="x", padx=20, pady=20, ipady=10)
        
        # Log
        self.log_text = tk.Text(self.root, height=10, bg="#f4f4f4", state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)

    def _criar_seletor(self, parent, label, var, row):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
        ttk.Entry(parent, textvariable=var, width=45).grid(row=row, column=1, padx=5, pady=5)
        ttk.Button(parent, text="...", command=lambda: self._buscar_arquivo(var)).grid(row=row, column=2, pady=5)

    def _buscar_arquivo(self, var_target):
        path = filedialog.askopenfilename()
        if path:
            var_target.set(path)
            if self.path_modelo.get() and self.path_solicitante.get():
                self.btn_processar.config(state="normal")

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()

    # --- FLUXO PRINCIPAL ATUALIZADO ---
    def fluxo_principal(self):
        try:
            self.log("1. Analisando Modelo Word...")
            placeholders = reader.extrair_placeholders_modelo(self.path_modelo.get())
            
            self.log("2. Extraindo dados dos arquivos...")
            txt_solicitante = reader.ler_documento_cliente(self.path_solicitante.get())
            dados_auto = parser.processar_dados(placeholders, txt_solicitante)

            path_fat = self.path_faturamento.get()
            if path_fat:
                txt_fat = reader.ler_documento_cliente(path_fat)
                dados_fat = parser.processar_dados(placeholders, txt_fat, sufixo_filtro="_CONTRATANTE")
                dados_auto.update(dados_fat)

            self.log("3. Aguardando verificação do usuário...")
            
            # --- ATENÇÃO AQUI: PASSAMOS OS DOIS VALORES AGORA ---
            dados_revisados = janela_verificacao_unificada(
                self.root, 
                placeholders, 
                dados_auto, 
                self.var_frete.get(),      # Passa valor do Frete
                self.var_pagamento.get()   # Passa valor do Pagamento
            )
            
            if not dados_revisados:
                self.log("Processo cancelado pelo usuário.")
                return

            self.log("4. Gerando documentos finais...")
            docx, pdf = generator.gerar_arquivos(self.path_modelo.get(), dados_revisados)
            
            messagebox.showinfo("Sucesso", f"Arquivos gerados!\nWord: {docx}\nPDF: {pdf}")
            self.log("Processo concluído com sucesso.")

        except Exception as e:
            self.log(f"ERRO: {e}")
            messagebox.showerror("Erro Crítico", str(e))