import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from services import reader, parser, generator

class GeradorPropostasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador Automático de Propostas - v3.1")
        self.root.geometry("600x650") # Aumentei um pouco a altura para caber o campo novo
        
        # Variáveis de Caminho
        self.path_modelo = tk.StringVar()
        self.path_solicitante = tk.StringVar()
        self.path_faturamento = tk.StringVar()
        
        # --- NOVO: Variável para o Frete ---
        self.var_frete = tk.StringVar(value="CIF - Por conta do destinatário") # Valor padrão
        
        self.dados_finais = {}
        
        self._setup_ui()

    def _setup_ui(self):
        # Frame Arquivos
        f_arquivos = ttk.LabelFrame(self.root, text="Arquivos de Entrada", padding=10)
        f_arquivos.pack(fill="x", padx=10, pady=10)
        
        # 1. Modelo
        self._criar_seletor(f_arquivos, "Modelo Word:", self.path_modelo, 0)
        
        # 2. Doc Solicitante
        self._criar_seletor(f_arquivos, "Ficha Solicitante:", self.path_solicitante, 1)
        
        # 3. Doc Faturamento
        self._criar_seletor(f_arquivos, "Ficha Faturamento (Opcional):", self.path_faturamento, 2)
        ttk.Label(f_arquivos, text="(Deixe vazio caso não seja utilizado um anexo)", font=("Arial", 8, "italic")).grid(row=3, column=1, sticky="w", padx=5)

        
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
            
            # --- EXTRAÇÃO AUTOMÁTICA ---
            self.log("2. Extraindo dados dos arquivos...")
            
            # Lê Solicitante
            txt_solicitante = reader.ler_documento_cliente(self.path_solicitante.get())
            dados_auto = parser.processar_dados(placeholders, txt_solicitante)

            # Lê Faturamento (se houver) e mescla
            path_fat = self.path_faturamento.get()
            if path_fat:
                txt_fat = reader.ler_documento_cliente(path_fat)
                dados_fat = parser.processar_dados(placeholders, txt_fat, sufixo_filtro="_CONTRATANTE")
                dados_auto.update(dados_fat)

            # --- NOVA JANELA UNIFICADA ---
            # Aqui passamos o valor do Frete selecionado na tela principal para dentro da revisão
            from ui.dialogs import janela_verificacao_unificada
            
            self.log("3. Aguardando verificação do usuário...")
            
            # Esta função vai abrir a janela e só retorna quando o usuário clicar em Confirmar
            # Ela devolve um dicionário COMPLETO (Texto + Serviços + Frete)
            dados_revisados = janela_verificacao_unificada(
                self.root, 
                placeholders, 
                dados_auto, 
                self.var_frete.get() # Passa o valor atual do dropdown da tela principal
            )
            
            # Se o usuário fechou a janela sem confirmar, o dicionário vem vazio
            if not dados_revisados:
                self.log("Processo cancelado pelo usuário.")
                return

            # --- GERAÇÃO FINAL ---
            self.log("4. Gerando documentos finais...")
            docx, pdf = generator.gerar_arquivos(self.path_modelo.get(), dados_revisados)
            
            messagebox.showinfo("Sucesso", f"Arquivos gerados!\nWord: {docx}\nPDF: {pdf}")
            self.log("Processo concluído com sucesso.")

        except Exception as e:
            self.log(f"ERRO: {e}")
            messagebox.showerror("Erro Crítico", str(e))