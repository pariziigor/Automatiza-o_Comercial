import customtkinter as ctk  # <--- A GRANDE MUDANÇA
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import json
import os
from services.utils import resource_path
import threading
from services import reader, parser, generator
from ui.dialogs import janela_verificacao_unificada, janela_itens_orcamento, janela_projeto_estrutural

class GeradorPropostasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Propostas Comerciais - AULEVI")
        self.root.geometry("700x600")

        try:
            self.root.iconbitmap(resource_path("icone.ico"))
        except:
            pass
        
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
        # Configuração do Grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        # Título
        lbl_titulo = ctk.CTkLabel(self.root, text="Gerador de Propostas - AULEVI", font=("Roboto", 24, "bold"))
        lbl_titulo.pack(pady=(20, 10))

        # --- FRAME DE ARQUIVOS ---
        f_arquivos = ctk.CTkFrame(self.root)
        f_arquivos.pack(fill="x", padx=20, pady=10)
        
        f_arquivos.grid_columnconfigure(1, weight=1) 

        # Inputs
        ctk.CTkLabel(f_arquivos, text="Arquivos de Entrada", font=("Roboto", 14, "bold")).grid(row=0, column=0, sticky="w", padx=15, pady=10)

        self._criar_seletor(f_arquivos, "Modelo Word:", self.path_modelo, 1)
        
        self._criar_seletor(f_arquivos, "Ficha Solicitante:", self.path_solicitante, 2)
        ctk.CTkLabel(f_arquivos, text="(Opcional)", text_color="gray").grid(row=2, column=3, sticky="w", padx=(0, 10))

        self._criar_seletor(f_arquivos, "Ficha Faturamento:", self.path_faturamento, 3)
        ctk.CTkLabel(f_arquivos, text="(Opcional)", text_color="gray").grid(row=3, column=3, sticky="w", padx=(0, 10))

        # Divisória e Saída
        div = ctk.CTkFrame(f_arquivos, height=2, fg_color="gray30")
        div.grid(row=4, column=0, columnspan=4, sticky="ew", pady=15, padx=10)
        
        ctk.CTkLabel(f_arquivos, text="Salvar em:").grid(row=5, column=0, sticky="w", padx=15)
        entry_saida = ctk.CTkEntry(f_arquivos, textvariable=self.path_saida)
        entry_saida.grid(row=5, column=1, sticky="ew", padx=5, pady=5)
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
        
        # --- 1. CRIAMOS O LOG PRIMEIRO (CORREÇÃO AQUI) ---
        self.log_text = ctk.CTkTextbox(self.root)
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_text.configure(state="disabled")

        # --- 2. CRIAMOS A BARRA E POSICIONAMOS 'BEFORE' O LOG ---
        # Label de Porcentagem
        self.lbl_progresso = ctk.CTkLabel(self.root, text="", text_color="orange")
        self.lbl_progresso.pack(before=self.log_text, pady=(0, 5)) # 'before' agora funciona porque log_text existe
        
        # Barra Determinada
        self.bar_progresso = ctk.CTkProgressBar(self.root, mode="determinate", height=15)
        self.bar_progresso.set(0)
        self.bar_progresso.pack(before=self.log_text, fill="x", padx=50, pady=(0, 20))
        
        # Esconde inicialmente
        self.lbl_progresso.pack_forget()
        self.bar_progresso.pack_forget()

    def _criar_seletor(self, parent, label, var, row):
        # Label
        ctk.CTkLabel(parent, text=label).grid(row=row, column=0, sticky="w", padx=15, pady=5)
        
        # Remoção do width fixo para ele obedecer o layout
        ctk.CTkEntry(parent, textvariable=var).grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        # Botão
        ctk.CTkButton(parent, text="Arquivo...", width=100, command=lambda: self._buscar_arquivo(var)).grid(row=row, column=2, padx=15, pady=5)

    # --- MÉTODOS DE LÓGICA ---
    def _buscar_arquivo(self, var_target):
        path = filedialog.askopenfilename()
        if path:
            var_target.set(path)
            
            if self.path_modelo.get():
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

    # --- FLUXO PRINCIPAL ---
    def fluxo_principal(self):
        try:
            # --- PREPARAÇÃO (RÁPIDA) ---
            self.log("1. Analisando Modelo...")
            placeholders = reader.extrair_placeholders_modelo(self.path_modelo.get())
            
            dados_auto = {}
            path_sol = self.path_solicitante.get()
            if path_sol:
                self.log("2. Lendo dados do Solicitante...")
                txt_solicitante = reader.ler_documento_cliente(path_sol)
                dados_auto = parser.processar_dados(placeholders, txt_solicitante)
            else:
                self.log("2. Ficha Solicitante não informada. Preenchimento manual...")

            path_fat = self.path_faturamento.get()
            if path_fat:
                self.log("Lendo dados de Faturamento...")
                txt_fat = reader.ler_documento_cliente(path_fat)
                dados_fat = parser.processar_dados(placeholders, txt_fat, sufixo_filtro="_CONTRATANTE")
                dados_auto.update(dados_fat)

            # --- ETAPAS VISUAIS (JANELAS) ---
            self.log("3. Revisão (Passo 1/3)...")
            dados_revisados = janela_verificacao_unificada(self.root, placeholders, dados_auto)
            if not dados_revisados:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa de Revisão.")
                return

            self.log("4. Estrutural (Passo 2/3)...")
            dados_com_estrutural = janela_projeto_estrutural(self.root, dados_revisados)
            if "ITENS_ESTRUTURAL" not in dados_com_estrutural:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa estrutural.")
                return

            self.log("5. Orçamento (Passo 3/3)...")
            dados_finais = janela_itens_orcamento(self.root, dados_com_estrutural)
            if "ITENS_ORCAMENTO" not in dados_finais:
                messagebox.showinfo("Cancelado", "Operação cancelada na etapa de orçamento.")
                return

            # Data final
            agora = datetime.now()
            meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
            dados_finais["DATA_HOJE"] = f"{agora.day} de {meses[agora.month - 1]} de {agora.year}"
            
            # --- FASE DE GERAÇÃO (COM PORCENTAGEM) ---
            self.log("6. Iniciando geração...")
            
            # Mostra a barra e o texto
            self.lbl_progresso.configure(text="0% - Iniciando...")
            self.lbl_progresso.pack(before=self.log_text, pady=(0, 5))
            self.bar_progresso.pack(before=self.log_text, fill="x", padx=50, pady=(0, 20))
            
            self.bar_progresso.set(0)
            self.btn_processar.configure(state="disabled") 

            # --- FUNÇÃO QUE O GERADOR VAI CHAMAR ---
            def atualizar_gui(pct, mensagem):
                # O CustomTkinter espera valor entre 0.0 e 1.0
                valor_float = pct / 100
                self.bar_progresso.set(valor_float)
                self.lbl_progresso.configure(text=f"{pct}% - {mensagem}")
                # Força atualização visual
                self.root.update_idletasks()

            def tarefa_pesada():
                try:
                    # Passamos a função 'atualizar_gui' para dentro do gerador!
                    generator.gerar_arquivos(
                        self.path_modelo.get(), 
                        dados_finais, 
                        self.path_saida.get(),
                        callback_progresso=atualizar_gui  # <--- AQUI É O PULO DO GATO
                    )
                    self.root.after(0, finalizar_sucesso)
                except Exception as e:
                    self.root.after(0, lambda: finalizar_erro(str(e)))

            def finalizar_sucesso():
                # Esconde a barra depois de um tempo ou deixa lá cheia
                self.lbl_progresso.configure(text="100% - Concluído!")
                self.bar_progresso.set(1)
                self.btn_processar.configure(state="normal")
                self.log("Concluído com sucesso.")
                messagebox.showinfo("Sucesso", "Arquivos gerados com sucesso!")
                
                # Opcional: Esconder depois de 2 segundos
                self.root.after(2000, lambda: self.bar_progresso.pack_forget())
                self.root.after(2000, lambda: self.lbl_progresso.pack_forget())

            def finalizar_erro(msg_erro):
                self.lbl_progresso.configure(text="Erro!")
                self.bar_progresso.pack_forget()
                self.lbl_progresso.pack_forget()
                self.btn_processar.configure(state="normal")
                self.log(f"ERRO: {msg_erro}")
                messagebox.showerror("Erro", msg_erro)

            threading.Thread(target=tarefa_pesada, daemon=True).start()

        except Exception as e:
            self.log(f"ERRO GERAL: {e}")
            messagebox.showerror("Erro", str(e))

        except Exception as e:
            self.bar_progresso.stop()
            self.bar_progresso.pack_forget()
        
            self.log(f"ERRO: {e}")
            messagebox.showerror("Erro", str(e))