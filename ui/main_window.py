import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
from services import reader, parser, generator
import json  
import os    

class GeradorPropostasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador Automático de Propostas - v3.5")
        self.root.geometry("650x550")
        
        # 1. Carrega configuração existente
        config = self._carregar_config()

        # 2. Define as variáveis JÁ COM OS VALORES SALVOS
        # O segundo argumento do .get() é o valor padrão (vazio) se não tiver nada salvo
        self.path_modelo = tk.StringVar(value=config.get("modelo", ""))
        self.path_solicitante = tk.StringVar(value=config.get("solicitante", ""))
        self.path_faturamento = tk.StringVar(value=config.get("faturamento", ""))
        self.path_saida = tk.StringVar(value=config.get("saida", "")) # <--- AQUI A MÁGICA
        
        self.dados_finais = {}
        
        self._setup_ui()
    def _setup_ui(self):
        # Frame Arquivos
        f_arquivos = ttk.LabelFrame(self.root, text="Arquivos e Pastas", padding=10)
        f_arquivos.pack(fill="x", padx=10, pady=10)
        
        # Seletores de Arquivos
        self._criar_seletor(f_arquivos, "Modelo Word:", self.path_modelo, 0)
        self._criar_seletor(f_arquivos, "Ficha Solicitante:", self.path_solicitante, 1)
        self._criar_seletor(f_arquivos, "Ficha Faturamento (Opcional):", self.path_faturamento, 2)
        ttk.Label(f_arquivos, text="(Deixe vazio se for o mesmo)", font=("Arial", 8, "italic")).grid(row=3, column=1, sticky="w", padx=5)

        # --- NOVO: Seletor de Pasta de Saída ---
        ttk.Separator(f_arquivos, orient='horizontal').grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Label(f_arquivos, text="Salvar em:").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Entry(f_arquivos, textvariable=self.path_saida, width=45).grid(row=5, column=1, padx=5, pady=5)
        ttk.Button(f_arquivos, text="Selecionar Pasta", command=self._buscar_pasta).grid(row=5, column=2, pady=5)
        # ---------------------------------------

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
            self._salvar_config() # <--- SALVA AUTOMATICAMENTE
            
            if self.path_modelo.get() and self.path_solicitante.get():
                self.btn_processar.config(state="normal")
    
    def _buscar_pasta(self):
        path = filedialog.askdirectory()
        if path:
            self.path_saida.set(path)
            self._salvar_config() # <--- SALVA AUTOMATICAMENTE

    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"> {msg}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update()

    # --- NOVOS MÉTODOS DE CONFIGURAÇÃO ---
    def _carregar_config(self):
        """Lê o arquivo config.json e retorna os dados ou um dicionário vazio."""
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _salvar_config(self):
        """Salva os caminhos atuais no arquivo config.json."""
        dados = {
            "modelo": self.path_modelo.get(),
            "solicitante": self.path_solicitante.get(),
            "faturamento": self.path_faturamento.get(),
            "saida": self.path_saida.get()
        }
        with open("config.json", "w") as f:
            json.dump(dados, f, indent=4)

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

            # 1. Revisão
            self.log("3. Aguardando verificação do usuário (Passo 1/3)...")
            from ui.dialogs import janela_verificacao_unificada, janela_itens_orcamento, janela_projeto_estrutural
            
            dados_revisados = janela_verificacao_unificada(self.root, placeholders, dados_auto)
            if not dados_revisados: return

            # 2. Estrutural
            self.log("4. Aguardando escopo estrutural (Passo 2/3)...")
            dados_com_estrutural = janela_projeto_estrutural(self.root, dados_revisados)
            if "ITENS_ESTRUTURAL" not in dados_com_estrutural: dados_com_estrutural["ITENS_ESTRUTURAL"] = []

            # 3. Orçamento
            self.log("5. Aguardando composição do orçamento (Passo 3/3)...")
            dados_finais = janela_itens_orcamento(self.root, dados_com_estrutural)
            
            if "ITENS_ORCAMENTO" not in dados_finais:
                 dados_finais["ITENS_ORCAMENTO"] = []
                 dados_finais["VALOR_TOTAL_PROPOSTA"] = "R$ 0,00"

            # Data Automática
            agora = datetime.now()
            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            dados_finais["DATA_HOJE"] = f"{agora.day} de {meses[agora.month - 1]} de {agora.year}"
            
            # Geração (AGORA PASSANDO A PASTA DE SAÍDA)
            self.log("6. Gerando documentos finais...")
            
            pasta_destino = self.path_saida.get() # Pega o valor do campo
            
            docx, pdf = generator.gerar_arquivos(
                self.path_modelo.get(), 
                dados_finais,
                pasta_destino # <--- Passa como argumento novo
            )
            
            messagebox.showinfo("Sucesso", f"Arquivos salvos em:\n{pasta_destino if pasta_destino else 'Pasta do Programa'}\n\nArquivos:\n{docx}\n{pdf}")
            self.log("Processo concluído com sucesso.")

        except Exception as e:
            self.log(f"ERRO: {e}")
            messagebox.showerror("Erro Crítico", str(e))