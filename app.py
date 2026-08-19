# GERENCIADOR DE ESTOQUE

import sqlite3
import customtkinter as ctk
from tkinter import messagebox

conexao = sqlite3.connect('Estoque.db')
c = conexao.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade INTEGER NOT NULL
)'''
)
conexao.commit()

def inserir_produto(nome, preco, quantidade):
    c.execute("INSERT INTO produtos (nome, preco, quantidade) VALUES (?, ?, ?)", (nome, preco, quantidade))
    conexao.commit()

def obter_produtos():
    c.execute("SELECT * FROM produtos")
    produtos = c.fetchall()
    return produtos

def editar_produto(id_produto, nome, preco, quantidade):
    c.execute("UPDATE produtos SET nome = ?, preco = ?, quantidade = ? WHERE id = ?", (nome, preco, quantidade, id_produto))


def excluir_produto(id_produto):
    c.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conexao.commit()

id_editar = None

# 2. FUNÇÕES DA INTERFACE

def salvar_produto():
    global id_editar 
    
    nome = entry_nome.get().strip()
    preco_str = entry_preco.get().strip().replace(",", ".")
    qtd_str = entry_qtd.get().strip()

    if not nome or not preco_str or not qtd_str:
        messagebox.showerror("Erro", "Preencha todos os campos!")
        return

    try:
        preco = float(preco_str)
        quantidade = int(qtd_str)
    except ValueError:
        messagebox.showerror("Erro", "O preço deve ser numérico e a quantidade inteira!")
        return

    # Se há um ID guardado, faz o UPDATE; senão, faz o INSERT
    if id_editar is not None:
        editar_produto(id_editar, nome, preco, quantidade)
        messagebox.showinfo("Sucesso", "Produto atualizado com sucesso!")
        
        id_editar = None
        btn_salvar.configure(text="Cadastrar Produto", fg_color="green", hover_color="darkgreen")
    else:
        inserir_produto(nome, preco, quantidade)
        messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso!")

    limpar_campos()
    atualizar_lista()

def editar(id_prod, nome, preco, qtd):
    global id_editar
    id_editar = id_prod

    entry_nome.delete(0, "end")
    entry_nome.insert(0, nome)
    
    entry_preco.delete(0, "end")
    entry_preco.insert(0, str(preco))
    
    entry_qtd.delete(0, "end")
    entry_qtd.insert(0, str(qtd))

    btn_salvar.configure(text="Salvar Alteração", fg_color="orange", hover_color="darkorange")

def limpar_campos():
    entry_nome.delete(0, "end")
    entry_preco.delete(0, "end")
    entry_qtd.delete(0, "end")

def deletar_produto(id_produto):
    if messagebox.askyesno("Confirmação", "Deseja realmente excluir este produto?"):
        excluir_produto(id_produto)
        atualizar_lista()

def atualizar_lista():
    for widget in scroll_frame.winfo_children():
        widget.destroy()

    produtos = obter_produtos()

    if not produtos:
        lbl_vazio = ctk.CTkLabel(scroll_frame, text="Nenhum produto cadastrado.", text_color="gray")
        lbl_vazio.pack(pady=20)
        return

    for p in produtos:
        id_prod, nome, preco, qtd = p

        item_frame = ctk.CTkFrame(scroll_frame, fg_color=("gray85", "gray20"))
        item_frame.pack(fill="x", pady=5, padx=5)

        texto_item = f"ID: {id_prod} | {nome} | Preço: R$ {preco:.2f} | Qtd: {qtd} "
        
        cor_texto = None
        if qtd < 3:
            texto_item += "\nESTOQUE BAIXO!"
            cor_texto = "#FF5555"

        lbl_item = ctk.CTkLabel(item_frame, text=texto_item, justify="left", text_color=cor_texto)
        lbl_item.pack(side="left", padx=10, pady=5)

        btn_excluir = ctk.CTkButton(
            item_frame, 
            text="Excluir", 
            width=70, 
            fg_color="red", 
            hover_color="darkred", 
            command=lambda id=id_prod: deletar_produto(id)
        )
        btn_excluir.pack(side="right", padx=10)

        btn_editar = ctk.CTkButton(
            item_frame, 
            text="Editar", 
            width=60, 
            fg_color="#D4AC0D", 
            hover_color="#B7950B", 
            command=lambda id=id_prod, n=nome, pr=preco, q=qtd: editar(id, n, pr, q)
        )
        btn_editar.pack(side="right", padx=5)

# 3. CONFIGURAÇÃO DA JANELA PRINCIPAL

app = ctk.CTk()
app.title("Sistema de Estoque")
app.geometry("750x550")
app.iconbitmap("icone.ico")

# --- FRAME ESQUERDO: FORMULÁRIO DE CADASTRO ---
frame_form = ctk.CTkFrame(app, width=250, corner_radius=0)
frame_form.pack(side="left", fill="y", padx=10, pady=10)

label_titulo = ctk.CTkLabel(frame_form, text="Novo Produto", font=("Arial", 18, "bold"))
label_titulo.pack(pady=20)

entry_nome = ctk.CTkEntry(frame_form, placeholder_text="Nome do Produto")
entry_nome.pack(pady=10, padx=15, fill="x")

entry_preco = ctk.CTkEntry(frame_form, placeholder_text="Preço (Ex: 19.99)")
entry_preco.pack(pady=10, padx=15, fill="x")

entry_qtd = ctk.CTkEntry(frame_form, placeholder_text="Quantidade")
entry_qtd.pack(pady=10, padx=15, fill="x")

btn_salvar = ctk.CTkButton(
    frame_form, 
    text="Cadastrar Produto", 
    fg_color="green", 
    hover_color="darkgreen", 
    command=salvar_produto
)
btn_salvar.pack(pady=20, padx=15, fill="x")

# --- FRAME DIREITO: LISTAGEM DE PRODUTOS ---
frame_lista = ctk.CTkFrame(app)
frame_lista.pack(side="right", fill="both", expand=True, padx=10, pady=10)

label_lista_titulo = ctk.CTkLabel(frame_lista, text="Produtos em Estoque", font=("Arial", 16, "bold"))
label_lista_titulo.pack(pady=10)

scroll_frame = ctk.CTkScrollableFrame(frame_lista, width=430, height=280)
scroll_frame.pack(pady=5, padx=10, fill="both", expand=True)

atualizar_lista()

app.mainloop()
