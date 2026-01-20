import tkinter as tk
from ui.main_window import GeradorPropostasApp

if __name__ == "__main__":
    root = tk.Tk()
    # Configuração opcional de ícone ou tema aqui
    app = GeradorPropostasApp(root)
    root.mainloop()