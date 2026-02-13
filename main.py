import os
import sys
import customtkinter as ctk
from ui.main_window import GeradorPropostasApp

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Configuração do tema antes de criar a janela
    ctk.set_appearance_mode("Dark") 
    ctk.set_default_color_theme(resource_path("tema_laranja.json"))

    root = ctk.CTk() # <--- Mudou aqui
    app = GeradorPropostasApp(root)
    root.mainloop()