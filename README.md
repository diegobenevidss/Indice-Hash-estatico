# Simulador de Índice Hash Estático 🗂️

Este projeto é uma ferramenta educacional desenvolvida em **Python** para visualizar e comparar a eficiência de diferentes métodos de busca em um Banco de Dados simulado. A aplicação demonstra a diferença prática entre um **Table Scan** (busca sequencial) e uma **Busca via Índice Hash**.

---

## 🚀 Sobre o Projeto

O simulador organiza um conjunto de dados (palavras) em **Páginas** e constrói um **Índice Hash Estático** para acelerar a recuperação dessas informações. Ele permite configurar parâmetros fundamentais de armazenamento e observar como eles afetam o desempenho e a integridade da estrutura de dados.



### 🛠️ Funcionalidades Principais

* **Configuração de Armazenamento:** Ajuste o tamanho das páginas e o fator de preenchimento (FR) dos buckets.
* **Algoritmo de Hashing (DJB2):** Utiliza uma função hash robusta para garantir uma distribuição uniforme das chaves.
* **Tratamento de Transbordo (Overflow):** Simulação real de buckets de overflow quando a capacidade principal é excedida.
* **Comparativo de Performance:** Exibição detalhada de:
    * Tempo de execução em milissegundos.
    * Quantidade de "acessos a disco" (páginas lidas).
    * Taxas de colisão e overflow.

---

## 📦 Pré-requisitos

* **Python 3.x** instalado.
* Arquivo `words.txt` no mesmo diretório do script (o programa busca por este arquivo para popular a base de dados).

---

## 🔧 Como Usar

1.  **Clone o repositório** ou baixe o código fonte.
2.  **Prepare os dados:** Certifique-se de ter um arquivo chamado `words.txt` na mesma pasta.
3.  **Execute o simulador:**
    ```bash
    python seu_arquivo.py
    ```
4.  **Configure os parâmetros:**
    * *Tamanho da Página:* Quantas palavras cabem em cada bloco de dados.
    * *Tamanho do Bucket (FR):* Quantas entradas o índice suporta por endereço antes de gerar um overflow.
5.  **Indexar:** Clique em "Carregar Dados e Construir Índice".
6.  **Pesquisar:** Digite uma palavra e compare os botões de **Busca via Índice** e **Table Scan**.

---

## 📊 Conceitos de Banco de Dados Aplicados

| Conceito | Descrição no Simulador |
| :--- | :--- |
| **NR (Número de Registros)** | Total de palavras lidas do arquivo. |
| **Páginas (Pages)** | Simulação do armazenamento físico onde os dados residem. |
| **Bucket** | Entrada no arquivo de índice que aponta para o local físico do dado. |
| **Colisão** | Quando o cálculo $h(K)$ resulta em um endereço já ocupado. |
| **Table Scan** | O "pior caso" de busca, onde todas as páginas são lidas ($O(N)$). |

---

## 🧬 Estrutura do Código

* `Page`: Classe que representa a unidade de armazenamento de dados.
* `Bucket`: Estrutura do índice que mapeia chaves para IDs de páginas.
* `djb2_hash`: Implementação da função hash para strings.
* `HashIndexApp`: Interface gráfica e lógica de controle construída com **Tkinter**.

---

Este projeto foi desenvolvido para fins didáticos, ilustrando por que índices são essenciais para a escalabilidade de sistemas de bancos de dados modernos.
