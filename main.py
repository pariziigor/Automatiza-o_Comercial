import customtkinter as ctk
from ui.main_window import GeradorPropostasApp

if __name__ == "__main__":
    # Configuração do tema antes de criar a janela
    ctk.set_appearance_mode("Dark") 
    ctk.set_default_color_theme("blue")

    root = ctk.CTk() # <--- Mudou aqui
    app = GeradorPropostasApp(root)
    root.mainloop()