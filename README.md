# T2 – Algoritmos de Busca: Olimpíada

**PUCRS – Inteligência Artificial** · Profa. Silvia Moraes

Distribuição de alunos de duas escolas em **quartos duplos** (um aluno de cada
escola por quarto), respeitando as preferências de todos, resolvida com o
algoritmo de busca com informação **Simulated Annealing (Têmpera Simulada)**.

---

## 1. O que o enunciado pede

Uma olimpíada reuniu alunos de **duas escolas** (A e B), do mesmo tamanho. O hotel
só tem quartos **duplos**, e cada dupla precisa ser **heterogênea**: um aluno da
escola A + um aluno da escola B. Ninguém pode ficar sem quarto.

Cada aluno respondeu a um questionário e, a partir dele, **ordenou os alunos da
outra escola por preferência**. A tarefa é encontrar a **melhor distribuição em
duplas** segundo essas preferências, usando um algoritmo de busca com informação
(o enunciado permite Algoritmo Genético **ou** Simulated Annealing).

### Por que Simulated Annealing?

Uma distribuição válida é sempre uma **permutação** (cada aluno de A casado com
exatamente um de B, sem repetir). O SA combina perfeitamente com isso:

- a vizinhança (trocar dois alunos de quarto) **nunca gera solução inválida**;
- mantém **um único estado** por vez (sem população, seleção ou cruzamento);
- o cruzamento de permutações no Algoritmo Genético exigiria operadores
  especiais (PMX/OX) — a principal fonte de bugs. O SA evita isso por completo.

---

## 2. Formato do arquivo de entrada

```
N                         <- número de alunos por escola
id  p1 p2 ... pN          <- aluno A 1: preferências sobre os alunos de B
...                          (N linhas de alunos da escola A)
id  p1 p2 ... pN          <- aluno B 1: preferências sobre os alunos de A
...                          (N linhas de alunos da escola B)
```

A leitura é feita por **tokens** (não por linha), então o mesmo código funciona
com os dados em várias linhas ou todos em uma só.

Em cada linha, o **primeiro número é o id do aluno** e os demais são os ids da
outra escola **em ordem de preferência** (o 1º é o favorito).

Exemplo (`arquivoDeTeste1.txt`, escola A):

```
1 1 2 3 4 5 6 7 8 9 10    -> Aluno A1 prefere B1, depois B2, depois B3, ...
```

---

## 3. Como o algoritmo funciona (e como ele "raciocina")

### 3.1 Codificação da solução

A solução é um **vetor de tamanho N** (uma permutação):

```
sol[i-1] = id do aluno B que está na dupla do aluno A "i"
```

Exemplo: `sol = [2, 3, 4, ...]` → A1 com B2, A2 com B3, A3 com B4...

### 3.2 Função heurística (o "quão boa é a solução")

Para cada dupla somamos **dois ranks**:

```
custo da dupla (A_i , B_j) = rank que A_i dá a B_j  +  rank que B_j dá a A_i
custo total                = soma do custo de todas as duplas
```

`rank = 1` significa "primeira opção". Logo, **quanto menor o custo, melhor** a
distribuição. O mínimo teórico é `2 × N` (todos casados com a 1ª opção mútua —
nem sempre alcançável).

### 3.3 Como ele busca a solução (o raciocínio do SA)

O SA imita o resfriamento de um metal: começa "quente" (aceita mudanças ruins
para explorar) e vai "esfriando" (fica cada vez mais exigente, refinando a
solução). O ciclo é:

1. **Começa** com uma distribuição aleatória válida.
2. **Gera um vizinho**: sorteia dois alunos de A e **troca seus parceiros de B**
   (*swap*). Continua sendo uma permutação válida.
3. **Decide se aceita** o vizinho:
   - se o custo **melhora** (Δ ≤ 0) → aceita sempre;
   - se **piora** (Δ > 0) → aceita mesmo assim com probabilidade `exp(-Δ / T)`.
     Isso é o que permite **escapar de mínimos locais**: com temperatura `T`
     alta, pioras são aceitas com facilidade; com `T` baixa, quase nunca.
4. **Esfria**: `T = T × α` (α < 1) e repete até `T` ficar mínima.
5. Guarda a **melhor solução já vista** durante todo o processo.

Ao longo das iterações o custo tende a **cair** — é exatamente isso que o gráfico
de evolução mostra.

---

## 4. Como ler o resultado (exemplo resolvido)

A saída tem duas partes:

**Solução CODIFICADA** — o vetor cru, como o algoritmo guarda:

```
[2, 3, 4, 5, 6, 7, 8, 9, 10, 1]
```

**Solução DECODIFICADA** — as duplas legíveis, com o custo de cada uma:

```
  Dupla         rank A  rank B   soma
  A1  - B2           2       1      3
  ...
  Custo total (função heurística) = 30
```

### Por que a dupla A1–B2 tem custo 3?

- Lista de A1: `1 2 3 4 5 6 7 8 9 10` → B2 é a **2ª** opção de A1 → **rank A = 2**.
- Lista de B2: `1 10 9 8 7 6 5 4 3 2` → A1 é a **1ª** opção de B2 → **rank B = 1**.
- **soma = 2 + 1 = 3**.

Repare que, neste arquivo de teste, nenhuma dupla consegue custo 2 (1ª opção dos
dois ao mesmo tempo), porque a 1ª preferência de cada A nunca coincide com a 1ª
preferência do B correspondente. Por isso o melhor possível é **3 por dupla**, e
o algoritmo encontrou exatamente isso: `10 duplas × 3 = 30`. Esse é o **ótimo**
desta instância — o resultado não é confuso, é o equilíbrio que deixa todo mundo
o mais perto possível do topo da sua lista.

---

## 5. Estrutura do código ([main.py](main.py))

| Bloco | Função | Requisito do enunciado |
|---|---|---|
| `ler_arquivo` / `matriz_rank` | Lê o `.txt` por *tokens* (robusto a quebras de linha) e monta as matrizes de rank | Leitura da entrada (0,5) |
| `custo` | Soma `rank_A + rank_B` de cada dupla — independe do nº de duplas | Função heurística (2,0) |
| `simulated_annealing` | Ciclo do SA: sucessor por *swap*, aceita piora com `exp(-Δ/T)`, resfriamento `T × α` | Ciclo do SA (1,5) |
| `mostrar_evolucao` / `mostrar_solucao` | Curva ASCII da heurística + solução codificada e decodificada | Execução / modos (2,0) |
| `main` | Recebe o arquivo via `args` e escolhe o modo de execução | `args` + modos |

---

## 6. Como executar

Requer apenas **Python 3** (sem bibliotecas externas).

```powershell
# Modo FINAL: executa tudo e mostra o resultado de uma vez
python main.py "C:\Users\kaua_\Downloads\arquivoDeTeste1.txt" --final

# Modo PASSO A PASSO: pausa a cada iteração (Enter avança)
python main.py "C:\Users\kaua_\Downloads\arquivoDeTeste1.txt" --passo

# Sem o modo: o programa pergunta qual usar
python main.py "C:\Users\kaua_\Downloads\arquivoDeTeste1.txt"
```

O nome do arquivo é passado como **argumento** (`args`), conforme exigido.

### Os dois modos

- **Final** — resfriamento longo (~5000 iterações); busca a melhor solução possível.
- **Passo a passo** — resfriamento curto (~50 iterações) para ser possível
  acompanhar **cada iteração** manualmente; serve para visualizar o mecanismo do
  algoritmo (pode parar num custo um pouco pior por ter menos iterações).

Os parâmetros de cada modo ficam em `PARAMS_FINAL` e `PARAMS_PASSO`, no topo da
função do Simulated Annealing, fáceis de ajustar.
