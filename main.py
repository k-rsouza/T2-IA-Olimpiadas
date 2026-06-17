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

    Levanta ValueError se o numero de tokens nao bate com N, ou se qualquer
    lista de preferencias nao for uma permutacao valida de 1..N.
    """
    with open(caminho, encoding="utf-8") as f:
        numeros = [int(x) for x in f.read().split()]

    if not numeros:
        raise ValueError("Arquivo vazio ou sem dados numericos.")

    n = numeros[0]
    if n < 2:
        raise ValueError(f"N deve ser >= 2 (encontrado: {n}).")

    # Cada grupo tem N linhas de (1 id + N preferencias) = N*(N+1) tokens.
    # Total esperado: 1 (o N) + 2 * N * (N+1).
    tokens_esperados = 1 + 2 * n * (n + 1)
    if len(numeros) < tokens_esperados:
        raise ValueError(
            f"Arquivo incompleto: {len(numeros)} tokens encontrados, "
            f"esperado pelo menos {tokens_esperados} para N={n}."
        )

    pos = 1
    ids_validos = set(range(1, n + 1))

    def ler_grupo(escola):
        nonlocal pos
        prefs = {}
        for _ in range(n):
            ident = numeros[pos]
            lista = numeros[pos + 1:pos + 1 + n]
            if set(lista) != ids_validos:
                raise ValueError(
                    f"Preferencias do aluno {escola}{ident} invalidas "
                    f"(esperado permutacao de 1..{n}, encontrado: {lista})."
                )
            prefs[ident] = lista
            pos += 1 + n
        return prefs

    pref_a = ler_grupo("A")
    pref_b = ler_grupo("B")
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
    """Soma dos ranks de todas as duplas (rank A + rank B por par). Menor = melhor."""
    total = 0
    for i, b in enumerate(sol, start=1):      # i = id do aluno A, b = id do aluno B
        total += rank_a[i][b] + rank_b[b][i]
    return total


# --------------------------------------------------------------------------- #
# 3. Ciclo do Simulated Annealing
# --------------------------------------------------------------------------- #
# Parametros do SA — modo FINAL (~5370 iteracoes totais):
#   T0=100 : para N<=20 o maior delta possivel e 2*(N-1)<=38; exp(-38/100)=0.68,
#            logo ~68% das pioras maximas sao aceitas no inicio -> boa exploracao.
#   alfa=0.95: resfriamento lento, favorece qualidade (179 niveis de temperatura).
#   iter_temp=30: cadeia de Markov de 30 vizinhos antes de resfriar (convencao SA).
PARAMS_FINAL = dict(t0=100.0, alfa=0.95, t_min=0.01, iter_temp=30)

# Parametros do SA — modo PASSO (~65 iteracoes totais, 1 por temperatura):
#   Resfriamento rapido (alfa=0.90) para limitar o numero de Enter na demo.
#   Resultado e subotimo para N grande — o proposito e mostrar a dinamica do SA,
#   nao encontrar o otimo. O modo final usa os parametros completos.
PARAMS_PASSO = dict(t0=100.0, alfa=0.90, t_min=0.10, iter_temp=1)

# Criterio de parada por estagnacao (modo final apenas):
#   Se PACIENCIA iteracoes consecutivas nao melhorarem o melhor custo, encerra
#   antes de atingir T_min. Para o modo final (~5370 iter max), PACIENCIA=300
#   representa ~5.6% do total — conservador o suficiente para nao parar durante
#   a fase de exploracao (T alto), mas evita iteracoes vazias apos convergencia.
PACIENCIA = 300


def simulated_annealing(n, rank_a, rank_b, modo_passo):
    p = PARAMS_PASSO if modo_passo else PARAMS_FINAL
    paciencia = 0 if modo_passo else PACIENCIA   # estagnacao desativada no modo passo

    sol = list(range(1, n + 1))
    random.shuffle(sol)                       # solucao inicial aleatoria (permutacao valida)
    custo_atual = custo(sol, rank_a, rank_b)
    melhor_sol, melhor_custo = sol[:], custo_atual
    historico = [(custo_atual, custo_atual)]   # (custo_atual, melhor_custo)

    temperatura = p["t0"]
    iteracao = 0
    sem_melhora = 0

    while temperatura > p["t_min"] and (paciencia == 0 or sem_melhora < paciencia):
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
                    sem_melhora = 0          # melhora encontrada: zera a contagem
                else:
                    sem_melhora += 1
            else:
                sol[i], sol[j] = sol[j], sol[i]   # rejeita: desfaz a troca
                sem_melhora += 1

            historico.append((custo_atual, melhor_custo))

            if modo_passo:
                print(f"  iter {iteracao:4d} | T={temperatura:7.3f} | "
                      f"custo atual={custo_atual:4d} | melhor={melhor_custo:4d}")
                input("  [Enter para o proximo passo] ")

        temperatura *= p["alfa"]               # resfriamento

    if paciencia > 0 and sem_melhora >= paciencia:
        print(f"  [encerrado por estagnacao: {paciencia} iteracoes sem melhora "
              f"| iteracao {iteracao} de ~5370 max]")

    return melhor_sol, melhor_custo, historico


# --------------------------------------------------------------------------- #
# 4. Saidas (evolucao da heuristica + solucao codificada/decodificada)
# --------------------------------------------------------------------------- #
def mostrar_evolucao(historico, alturas=12, largura=60):
    """Grafico ASCII da convergencia: plota o melhor custo ja encontrado por iteracao.

    historico: lista de tuplas (custo_atual, melhor_custo).
    Usar o melhor custo (monotonicamente nao-crescente) deixa o grafico limpo e
    mostra claramente que o algoritmo converge para um minimo.
    """
    amostras_h = historico
    if len(historico) > largura:
        passo = len(historico) / largura
        amostras_h = [historico[int(k * passo)] for k in range(largura)]

    melhor_vals = [h[1] for h in amostras_h]
    c_min, c_max = min(melhor_vals), max(melhor_vals)
    print("\nEvolucao do melhor custo encontrado (convergencia do SA):")
    if c_max == c_min:
        print(f"  custo constante = {c_min}")
        return
    for nivel in range(alturas, 0, -1):
        limiar = c_min + (c_max - c_min) * (nivel - 0.5) / alturas
        linha = "".join("*" if v >= limiar else " " for v in melhor_vals)
        print(f"  {limiar:6.0f} |{linha}")
    print("         +" + "-" * len(melhor_vals))
    custo_inicial = historico[0][0]
    melhor_final = historico[-1][1]
    print(f"  custo inicial = {custo_inicial}   ->   melhor encontrado = {melhor_final}")


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
    custo_medio = total / n
    minimo_teorico = 2 * n
    maximo_teorico = 2 * n * n             # pior caso: todos emparelhados com o menos preferido (rank N cada lado)
    qualidade = (maximo_teorico - total) / (maximo_teorico - minimo_teorico) * 100

    print(f"\n  Custo total (funcao heuristica) = {total}")
    print(f"  Custo medio por dupla          = {custo_medio:.2f}  "
          f"(independe de N; minimo teorico = 2.00)")
    print(f"  Qualidade da solucao           = {qualidade:.1f}%  "
          f"(0% = pior possivel, 100% = todos na 1a opcao mutua)")


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

    try:
        n, pref_a, pref_b = ler_arquivo(caminho)
    except FileNotFoundError:
        print(f"Erro: arquivo '{caminho}' nao encontrado.")
        return
    except (IndexError, ValueError) as e:
        print(f"Erro ao ler '{caminho}': {e}")
        return

    rank_a = matriz_rank(pref_a, n)
    rank_b = matriz_rank(pref_b, n)

    print(f"\nArquivo: {caminho}  |  N = {n} alunos por escola  |  Modo: {modo}")
    if modo == "passo":
        p = PARAMS_PASSO
        n_passos = round(math.log(p["t_min"] / p["t0"]) / math.log(p["alfa"])) * p["iter_temp"]
        print(f"  [~{n_passos} iteracoes no total | pressione Enter para avancar]\n")
    else:
        print()

    melhor_sol, _, historico = simulated_annealing(n, rank_a, rank_b, modo == "passo")

    mostrar_evolucao(historico)   # sempre exibe o grafico de convergencia ao final
    mostrar_solucao(melhor_sol, rank_a, rank_b, n)


if __name__ == "__main__":
    main()
