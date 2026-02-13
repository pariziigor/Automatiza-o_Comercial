import os
import sys
import customtkinter as ctk
from ui.main_window import GeradorPropostasApp
from services.utils import resource_path

if __name__ == "__main__":
    # Configuração do tema antes de criar a janela
    
    ctk.set_appearance_mode("Dark") 
    ctk.set_default_color_theme(resource_path("tema_laranja.json"))

    root = ctk.CTk() # <--- Mudou aqui
    app = GeradorPropostasApp(root)
    root.mainloop()