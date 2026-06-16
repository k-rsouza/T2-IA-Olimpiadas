"""
T2 - Algoritmos de Busca: Olimpiada (PUCRS - Inteligencia Artificial)
Distribuicao de alunos de duas escolas em quartos duplos (1 de cada escola)
respeitando as preferencias, resolvida com SIMULATED ANNEALING.

Codificacao : a solucao e uma permutacao -> sol[i-1] = id do aluno B na dupla do aluno A "i".
Heuristica  : custo = soma, para cada dupla, do (rank que A da ao B) + (rank que B da ao A).
              Quanto menor o custo, melhor a distribuicao. Minimo teorico = 2*N.

Uso:
    python main.py <arquivo_de_preferencias.txt> [--passo | --final]
    (sem o modo, o programa pergunta interativamente)
"""

import sys
import math
import random


# --------------------------------------------------------------------------- #
# 1. Leitura do arquivo de entrada
# --------------------------------------------------------------------------- #
def ler_arquivo(caminho):
    """Le o arquivo e devolve (n, pref_a, pref_b).

    pref_a[id_A] = lista de ids de B em ordem de preferencia do aluno A.
    pref_b[id_B] = lista de ids de A em ordem de preferencia do aluno B.
    A leitura e feita por tokens, entao funciona com os dados em varias linhas
    ou todos em uma unica linha.
    """
    numeros = [int(x) for x in open(caminho, encoding="utf-8").read().split()]
    n = numeros[0]
    pos = 1

    def ler_grupo():
        nonlocal pos
        prefs = {}
        for _ in range(n):
            ident = numeros[pos]
            prefs[ident] = numeros[pos + 1:pos + 1 + n]
            pos += 1 + n
        return prefs

    pref_a = ler_grupo()   # alunos da escola A
    pref_b = ler_grupo()   # alunos da escola B
    return n, pref_a, pref_b


def matriz_rank(prefs, n):
    """Converte listas de preferencia em matriz de ranks (1 = favorito).

    rank[origem][alvo] = posicao do "alvo" na lista de preferencia de "origem".
    Acesso O(1) na funcao heuristica. Indexada de 1..n.
    """
    rank = [[0] * (n + 1) for _ in range(n + 1)]
    for origem, lista in prefs.items():
        for posicao, alvo in enumerate(lista, start=1):
            rank[origem][alvo] = posicao
    return rank


# --------------------------------------------------------------------------- #
# 2. Funcao heuristica (de aptidao / custo)
# --------------------------------------------------------------------------- #
def custo(sol, rank_a, rank_b):
    """Soma o descontentamento de todas as duplas. Independe do numero de duplas."""
    total = 0
    for i, b in enumerate(sol, start=1):      # i = id do aluno A, b = id do aluno B
        total += rank_a[i][b] + rank_b[b][i]
    return total


# --------------------------------------------------------------------------- #
# 3. Ciclo do Simulated Annealing
# --------------------------------------------------------------------------- #
# Parametros por modo (o modo passo usa um resfriamento mais curto para ser
# possivel acompanhar cada iteracao manualmente).
PARAMS_FINAL = dict(t0=100.0, alfa=0.95, t_min=0.01, iter_temp=30)
PARAMS_PASSO = dict(t0=20.0,  alfa=0.90, t_min=0.10, iter_temp=1)


def simulated_annealing(n, rank_a, rank_b, modo_passo):
    p = PARAMS_PASSO if modo_passo else PARAMS_FINAL

    sol = list(range(1, n + 1))
    random.shuffle(sol)                       # solucao inicial aleatoria (permutacao valida)
    custo_atual = custo(sol, rank_a, rank_b)
    melhor_sol, melhor_custo = sol[:], custo_atual
    historico = [custo_atual]

    temperatura = p["t0"]
    iteracao = 0
    while temperatura > p["t_min"]:
        for _ in range(p["iter_temp"]):
            iteracao += 1

            # Funcao sucessor: troca dois alunos B de quarto (continua permutacao valida).
            i, j = random.sample(range(n), 2)
            sol[i], sol[j] = sol[j], sol[i]
            novo_custo = custo(sol, rank_a, rank_b)
            delta = novo_custo - custo_atual

            # Aceita se melhora; senao, aceita uma solucao ruim com prob. exp(-delta/T).
            if delta <= 0 or random.random() < math.exp(-delta / temperatura):
                custo_atual = novo_custo
                if custo_atual < melhor_custo:
                    melhor_sol, melhor_custo = sol[:], custo_atual
            else:
                sol[i], sol[j] = sol[j], sol[i]   # rejeita: desfaz a troca

            historico.append(custo_atual)

            if modo_passo:
                print(f"  iter {iteracao:4d} | T={temperatura:7.3f} | "
                      f"custo atual={custo_atual:4d} | melhor={melhor_custo:4d}")
                input("  [Enter para o proximo passo] ")

        temperatura *= p["alfa"]               # resfriamento

    return melhor_sol, melhor_custo, historico


# --------------------------------------------------------------------------- #
# 4. Saidas (evolucao da heuristica + solucao codificada/decodificada)
# --------------------------------------------------------------------------- #
def mostrar_evolucao(historico, alturas=12, largura=60):
    """Grafico ASCII da evolucao do custo ao longo das iteracoes."""
    amostras = historico
    if len(historico) > largura:
        passo = len(historico) / largura
        amostras = [historico[int(k * passo)] for k in range(largura)]

    c_min, c_max = min(amostras), max(amostras)
    print("\nEvolucao da funcao heuristica (custo) ao longo das iteracoes:")
    if c_max == c_min:
        print(f"  custo constante = {c_min}")
        return
    for nivel in range(alturas, 0, -1):
        limiar = c_min + (c_max - c_min) * (nivel - 0.5) / alturas
        linha = "".join("*" if v >= limiar else " " for v in amostras)
        print(f"  {limiar:6.0f} |{linha}")
    print("         +" + "-" * len(amostras))
    print(f"  inicial = {historico[0]}   ->   melhor encontrado = {min(historico)}")


def mostrar_solucao(sol, rank_a, rank_b, n):
    print("\nSolucao CODIFICADA (indice = aluno A, valor = aluno B):")
    print("  ", sol)

    print("\nSolucao DECODIFICADA (duplas heterogeneas A-B):")
    print(f"  {'Dupla':<12}{'rank A':>8}{'rank B':>8}{'soma':>7}")
    total = 0
    for i, b in enumerate(sol, start=1):
        ra, rb = rank_a[i][b], rank_b[b][i]
        total += ra + rb
        print(f"  A{i:<3}- B{b:<5}{ra:>8}{rb:>8}{ra + rb:>7}")
    print(f"\n  Custo total (funcao heuristica) = {total}")
    print(f"  Minimo teorico (todos 1a opcao mutua) = {2 * n}")


# --------------------------------------------------------------------------- #
# 5. Programa principal (recebe o arquivo via args e escolhe o modo)
# --------------------------------------------------------------------------- #
def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <arquivo_de_preferencias.txt> [--passo | --final]")
        return

    caminho = sys.argv[1]
    if "--passo" in sys.argv:
        modo = "passo"
    elif "--final" in sys.argv:
        modo = "final"
    else:
        print("Modos de execucao:")
        print("  1 - Passo a passo (pausa a cada iteracao)")
        print("  2 - Final (executa tudo e mostra o resultado)")
        modo = "passo" if input("Escolha o modo [1/2]: ").strip() == "1" else "final"

    n, pref_a, pref_b = ler_arquivo(caminho)
    rank_a = matriz_rank(pref_a, n)
    rank_b = matriz_rank(pref_b, n)

    print(f"\nArquivo: {caminho}  |  N = {n} alunos por escola  |  Modo: {modo}\n")
    melhor_sol, melhor_custo, historico = simulated_annealing(n, rank_a, rank_b, modo == "passo")

    mostrar_evolucao(historico)
    mostrar_solucao(melhor_sol, rank_a, rank_b, n)


if __name__ == "__main__":
    main()
