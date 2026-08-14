import tkinter as tk
from tkinter import ttk

def window():
    root = tk.Tk()
    root.title("trabalho de CG")
    root.geometry("2400x1600")

    janela = ttk.Frame(root, padding=50)

    janela.pack(side="left")
    #ttk.Label(janela, text="pao de queijo").grid(column=0, row=0)
    #ttk.Button(janela, text="botao", command=root.destroy).grid(column=0, row=1)
    
    ttk.Label(janela, text="pao de queijo").pack(side="top")
    ttk.Button(janela, text="botao", command=root.destroy).pack(side="bottom")
    
    #adiciona o canvas
    #canva = tk.Canvas(janela, width=500, height=400, bg="blue").pack(side="right", expand=True)


    canva = tk.Canvas(root,height=1200, width=1200, bg="blue")
    canva.place(relx=1.0, rely=.50, anchor="e")
    root.mainloop()

def main():
    window()
