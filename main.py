import tkinter as tk
from tkinter import messagebox, scrolledtext
import math
import time
import os

class Page:
    def __init__(self, page_id):
        self.page_id = page_id
        self.records = [] 

class Bucket:
    def __init__(self, fr):
        self.fr = fr
        self.entries = [] 
        self.overflow_bucket = None 

    def insert(self, key, page_id):
        if len(self.entries) < self.fr:
            self.entries.append((key, page_id))
            return 0
        else:
            if not self.overflow_bucket:
                self.overflow_bucket = Bucket(self.fr)

            self.overflow_bucket.insert(key, page_id)
            return 1


class HashIndexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Índice Hash Estático")
        self.root.geometry("900x700") 
        self.root.configure(padx=10, pady=10)
        
        self.words = []
        self.pages = []
        self.buckets = []
        self.fr = 20 
        self.last_index_time = 0 
        
        frame_config = tk.LabelFrame(self.root, text="1. Configuração do Banco de Dados", padx=10, pady=10)
        frame_config.pack(fill="x", pady=5)
        
        tk.Label(frame_config, text="Tamanho da Página (Qtd Palavras):").pack(side="left")
        
        self.entry_page_size = tk.Entry(frame_config, width=10)
        self.entry_page_size.pack(side="left", padx=5)
        self.entry_page_size.insert(0, "1000") 

        tk.Label(frame_config, text="Tamanho do Bucket (FR):").pack(side="left", padx=(10, 0))
        
        self.entry_bucket_size = tk.Entry(frame_config, width=10)
        self.entry_bucket_size.pack(side="left", padx=5)
        self.entry_bucket_size.insert(0, "20")
        
        self.btn_load = tk.Button(frame_config, text="Carregar Dados e Construir Índice", 
                                  command=self.build_database, bg="#4CAF50", fg="black")
        self.btn_load.pack(side="left", padx=15)

        frame_busca = tk.LabelFrame(self.root, text="2. Pesquisa de Registros", padx=10, pady=10)
        frame_busca.pack(fill="x", pady=5)
        
        tk.Label(frame_busca, text="Chave de Busca (Palavra):").pack(side="left")
        
        self.entry_search = tk.Entry(frame_busca, width=20)
        self.entry_search.pack(side="left", padx=10)
        self.entry_search.bind("<KeyRelease>", self.check_search_input)
        
        self.btn_search_hash = tk.Button(frame_busca, text="Busca via Índice Hash", 
                                         command=self.search_index, bg="#2196F3", fg="black", state=tk.DISABLED)
        self.btn_search_hash.pack(side="left", padx=5)
        
        self.btn_table_scan = tk.Button(frame_busca, text="Table Scan", 
                                        command=self.table_scan, bg="#FF9800", fg="black", state=tk.DISABLED)
        self.btn_table_scan.pack(side="left", padx=5)

        frame_stats = tk.Frame(self.root)
        frame_stats.pack(fill="x", pady=5)
        
        self.lbl_collisions = tk.Label(frame_stats, text="Taxa de Colisões: -- %", font=("Arial", 10, "bold"), fg="red")
        self.lbl_collisions.pack(side="left", padx=20)
        
        self.lbl_overflows = tk.Label(frame_stats, text="Taxa de Overflows: -- %", font=("Arial", 10, "bold"), fg="red")
        self.lbl_overflows.pack(side="left", padx=20)

        tk.Label(self.root, text="Visualização de Páginas e Resultados:").pack(anchor="w", pady=(10, 0))
        self.display_area = scrolledtext.ScrolledText(self.root, width=100, height=25, font=("Consolas", 10))
        self.display_area.pack(fill="both", expand=True)


    def check_search_input(self, event=None):
        if len(self.pages) > 0 and len(self.entry_search.get().strip()) > 0:
            self.btn_search_hash.config(state=tk.NORMAL)
            self.btn_table_scan.config(state=tk.NORMAL)
        else:
            self.btn_search_hash.config(state=tk.DISABLED)
            self.btn_table_scan.config(state=tk.DISABLED)

    def djb2_hash(self, string, nb):
        """Função Hash clássica para espalhar bem as strings e evitar colisões."""
        hash_value = 5381
        for char in string:
            hash_value = ((hash_value << 5) + hash_value) + ord(char)
        return hash_value % nb

    def load_words(self):
        """Lê o ficheiro txt, formata para minúsculas e remove espaços ocultos."""
        caminho_arquivo = 'words.txt' 
        palavras_formatadas = []
        
        if not os.path.exists(caminho_arquivo):
            messagebox.showerror(
                "Erro de Arquivo", 
                f"O arquivo '{caminho_arquivo}' não foi encontrado na pasta atual.\nPor favor, baixe-o e coloque-o na mesma pasta do script."
            )
            return []

        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            for linha in arquivo:
                palavra = linha.strip().lower()
                if palavra:
                    palavras_formatadas.append(palavra)
        
        return palavras_formatadas

    def build_database(self):
        try:
            page_size = int(self.entry_page_size.get())
            self.fr = int(self.entry_bucket_size.get())
            if page_size <= 0 or self.fr <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Insira números inteiros maiores que zero para os tamanhos.")
            return

        self.display_area.delete(1.0, tk.END)
        self.display_area.insert(tk.END, "Carregando dados e construindo índice... Aguarde.\n")
        self.root.update()

        self.words = self.load_words()
        nr = len(self.words)
        if nr == 0: return

        self.pages = []
        for i in range(0, nr, page_size):
            page = Page(page_id=len(self.pages))
            page.records = self.words[i:i+page_size]
            self.pages.append(page)
            
        nb = math.ceil((nr / self.fr) * 1.2) 
        self.buckets = [Bucket(self.fr) for _ in range(nb)]
        
        collisions = 0
        overflow_records = 0
        used_buckets = set()
        
        for page in self.pages:
            for word in page.records:
                h = self.djb2_hash(word, nb)
                
                if h in used_buckets:
                    collisions += 1
                else:
                    used_buckets.add(h)
                
                is_overflow = self.buckets[h].insert(word, page.page_id)
                if is_overflow > 0:
                    overflow_records += 1

        taxa_colisao = (collisions / nr) * 100
        taxa_overflow = (overflow_records / nr) * 100
        
        self.lbl_collisions.config(text=f"Taxa de Colisões: {taxa_colisao:.2f} %")
        self.lbl_overflows.config(text=f"Taxa de Overflows: {taxa_overflow:.2f} %")
        
        self.display_area.insert(tk.END, "-"*60 + "\n")
        self.display_area.insert(tk.END, "ÍNDICE CONSTRUÍDO COM SUCESSO!\n")
        self.display_area.insert(tk.END, f"Total de Tuplas (NR): {nr}\n")
        self.display_area.insert(tk.END, f"Tamanho da Página: {page_size} tuplas\n")
        self.display_area.insert(tk.END, f"Quantidade de Páginas: {len(self.pages)}\n")
        self.display_area.insert(tk.END, f"Tuplas por Bucket (FR): {self.fr}\n")
        self.display_area.insert(tk.END, f"Número de Buckets (NB): {nb}\n")
        self.display_area.insert(tk.END, "-"*60 + "\n\n")
        
        primeira = self.pages[0]
        ultima = self.pages[-1]
        
        self.display_area.insert(tk.END, f"[PRIMEIRA PÁGINA Carregada] ID: {primeira.page_id}\n")
        self.display_area.insert(tk.END, f"Registros iniciais: {primeira.records[:5]} ...\n\n")
        
        self.display_area.insert(tk.END, f"[ÚLTIMA PÁGINA Carregada] ID: {ultima.page_id}\n")
        self.display_area.insert(tk.END, f"Registros iniciais: {ultima.records[:5]} ...\n\n")
        
        self.display_area.see(tk.END)
        self.check_search_input()

    def search_index(self):
        chave = self.entry_search.get().strip().lower()
        if not chave: return

        self.display_area.insert(tk.END, f"\n{'='*40}\n")
        self.display_area.insert(tk.END, f"--- PESQUISA VIA ÍNDICE HASH ---\n")
        self.display_area.insert(tk.END, f"A procurar por: '{chave}'\n")

        start_time = time.perf_counter()
        nb = len(self.buckets)
        h = self.djb2_hash(chave, nb)

        bucket_atual = self.buckets[h]
        page_id_encontrada = -1
        
        while bucket_atual:
            for entrada in bucket_atual.entries:
                if entrada[0] == chave:
                    page_id_encontrada = entrada[1]
                    break
            if page_id_encontrada != -1: break
            bucket_atual = bucket_atual.overflow_bucket 

        custo_paginas = 0
        if page_id_encontrada != -1:
            pagina_lida = self.pages[page_id_encontrada]
            custo_paginas = 1 

        end_time = time.perf_counter()
        self.last_index_time = end_time - start_time 

        if page_id_encontrada != -1:
            self.display_area.insert(tk.END, f"[SUCESSO] A chave '{chave}' foi encontrada!\n")
            self.display_area.insert(tk.END, f"-> Localização: Página {page_id_encontrada}\n")
            self.display_area.insert(tk.END, f"-> Estimativa de Custo: {custo_paginas} acesso a disco (leitura de 1 página).\n")
            self.display_area.insert(tk.END, f"-> Tempo de execução: {self.last_index_time:.6f} segundos.\n")
        else:
            self.display_area.insert(tk.END, f"[FALHA] A chave '{chave}' não existe na base de dados.\n")
        
        self.display_area.see(tk.END)


    def table_scan(self):
        chave = self.entry_search.get().strip().lower()
        if not chave: return

        self.display_area.insert(tk.END, f"\n{'='*40}\n")
        self.display_area.insert(tk.END, f"--- PESQUISA VIA TABLE SCAN ---\n")
        self.display_area.insert(tk.END, f"A procurar por: '{chave}'\n")

        start_time = time.perf_counter()
        page_id_encontrada = -1
        custo_paginas = 0

        for pagina in self.pages:
            custo_paginas += 1 
            if chave in pagina.records:
                page_id_encontrada = pagina.page_id
                break 

        end_time = time.perf_counter()
        scan_time = end_time - start_time

        if page_id_encontrada != -1:
            self.display_area.insert(tk.END, f"[SUCESSO] A chave '{chave}' foi encontrada no Scan!\n")
            self.display_area.insert(tk.END, f"-> Localização: Página {page_id_encontrada}\n")
            self.display_area.insert(tk.END, f"-> Estimativa de Custo: {custo_paginas} acessos a disco (páginas lidas).\n")
            self.display_area.insert(tk.END, f"-> Tempo de execução: {scan_time:.6f} segundos.\n")
            
            if self.last_index_time > 0:
                diferenca = scan_time - self.last_index_time
                multiplicador = scan_time / self.last_index_time if self.last_index_time > 0 else 0
                
                self.display_area.insert(tk.END, f"\n[COMPARATIVO DE DESEMPENHO]\n")
                if diferenca > 0:
                    self.display_area.insert(tk.END, f"O Índice Hash poupou {custo_paginas - 1} acessos a disco!\n")
                    self.display_area.insert(tk.END, f"Em tempo, o Índice foi {diferenca:.6f} segundos mais rápido.\n")
                    self.display_area.insert(tk.END, f"Isto é cerca de {multiplicador:.0f} vezes mais rápido do que o Table Scan!\n")
        else:
            self.display_area.insert(tk.END, f"[FALHA] A chave '{chave}' não foi encontrada após ler todas as {custo_paginas} páginas do banco.\n")

        self.display_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = HashIndexApp(root)
    root.mainloop()