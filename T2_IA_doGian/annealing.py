"""
T2 - Algoritmos de Busca: Olimpiada (Simulated Annealing)

Distribui alunos de duas escolas em quartos duplos heterogeneos (1 de cada
escola) respeitando as preferencias registradas no arquivo de entrada.

Codificacao:
    A solucao e uma permutacao 'perm' de tamanho N. perm[i] = j significa que
    o aluno A_(i+1) divide o quarto com o aluno B_(j+1). Por ser uma permutacao,
    todo aluno de B e usado uma unica vez -> matching completo e heterogeneo.

Heuristica (custo a minimizar):
    Para cada dupla soma-se o rank que A da a B mais o rank que B da a A.
    Rank 1 = mais preferido, logo quanto MENOR o custo, melhor a solucao.

Uso:
    python annealing.py <arquivo>              # modo final (so o resultado)
    python annealing.py <arquivo> passo        # passo a passo autonomo
    python annealing.py <arquivo> passo 0.2    # idem, com 0.2s entre passos
"""

import sys
import os
import re
import random
import math
import time
import numpy as np

# Parametros do Simulated Annealing (justificados no relatorio).
T0 = 100.0           # temperatura inicial: alta -> aceita quase tudo no inicio
RESFRIAMENTO = 0.99  # fator geometrico de resfriamento (T = T * fator)
T_MIN = 0.01         # temperatura final: baixa -> praticamente so melhora
PAUSA_PADRAO = 0.1   # segundos entre passos no modo passo a passo


def resolver_caminho(caminho):
    """Acha o arquivo no diretorio atual ou ao lado do executavel/script.

    Necessario porque, ao dar duplo-clique no executavel, o diretorio de
    trabalho e a pasta home, e nao a pasta onde o binario esta.
    """
    if os.path.isfile(caminho):
        return caminho
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False)
                           else os.path.abspath(__file__))
    alternativo = os.path.join(base, caminho)
    return alternativo if os.path.isfile(alternativo) else caminho


def ler_arquivo(caminho):
    """Le o arquivo de preferencias de forma tolerante a cabecalhos/textos.

    Em vez de assumir um arquivo "limpo", extrai TODOS os numeros inteiros do
    texto e ignora qualquer rotulo ("Numero de duplas", "Escola A", etc.).

    Estrutura esperada apos a filtragem:
        - 1o numero  -> N (quantidade de duplas)
        - 2N linhas de dados (N para a escola A, N para a escola B)
        - cada linha com N valores (ranks) ou N+1 (id do aluno + N ranks)

    Retorna (n, prefA, prefB) onde:
        prefA[i][j] = rank que A_(i+1) atribui a B_(j+1)
        prefB[j][i] = rank que B_(j+1) atribui a A_(i+1)
    """
    with open(caminho) as f:
        numeros = [int(t) for t in re.findall(r"-?\d+", f.read())]

    if not numeros:
        raise ValueError("O arquivo nao contem nenhum numero (formato invalido).")

    n = numeros[0]
    dados = numeros[1:]
    n_linhas = 2 * n

    if n <= 0:
        raise ValueError(f"Numero de duplas invalido: {n}.")
    if n_linhas == 0 or len(dados) % n_linhas != 0:
        raise ValueError(
            f"Quantidade de valores ({len(dados)}) incompativel com {n} duplas "
            f"(esperado multiplo de {n_linhas}).")

    largura = len(dados) // n_linhas
    if largura not in (n, n + 1):
        raise ValueError(
            f"Largura de linha inesperada ({largura}); esperado {n} ou {n + 1}.")

    matriz = np.array(dados).reshape(n_linhas, largura)
    if largura == n + 1:          # primeira coluna = id do aluno -> descarta
        matriz = matriz[:, 1:]

    prefA, prefB = matriz[:n], matriz[n:]
    _validar_preferencias(prefA, prefB, n)
    return n, prefA, prefB


def _validar_preferencias(prefA, prefB, n):
    """Confere se cada linha e uma permutacao valida de ranks 1..N."""
    esperado = set(range(1, n + 1))
    for nome, matriz in (("A", prefA), ("B", prefB)):
        for i, linha in enumerate(matriz, start=1):
            if set(linha.tolist()) != esperado:
                print(f"[aviso] Linha {i} da escola {nome} nao e uma permutacao "
                      f"de 1..{n}: {linha.tolist()}. Verifique o arquivo de entrada.")


def custo(perm, prefA, prefB):
    """Soma dos ranks de todas as duplas da solucao (menor = melhor)."""
    idx = np.arange(len(perm))
    return int(prefA[idx, perm].sum() + prefB[perm, idx].sum())


def vizinho(perm):
    """Funcao sucessora: troca de posicao dois alunos sorteados ao acaso."""
    novo = perm.copy()
    i, j = random.sample(range(len(perm)), 2)
    novo[i], novo[j] = novo[j], novo[i]
    return novo


def simulated_annealing(prefA, prefB, t0=T0, resfriamento=RESFRIAMENTO,
                        t_min=T_MIN, passo=False, pausa=PAUSA_PADRAO):
    n = len(prefA)
    atual = np.random.permutation(n)
    custo_atual = custo(atual, prefA, prefB)
    melhor, custo_melhor = atual.copy(), custo_atual

    # historico = lista de (iteracao, temperatura, custo_atual, melhor_custo)
    historico = [(0, t0, custo_atual, custo_melhor)]

    temp = t0
    iteracao = 0
    while temp > t_min:
        candidato = vizinho(atual)
        custo_cand = custo(candidato, prefA, prefB)
        delta = custo_cand - custo_atual

        # aceita se melhora; senao, aceita com probabilidade e^(-delta/T)
        if delta < 0 or random.random() < math.exp(-delta / temp):
            atual, custo_atual = candidato, custo_cand
            if custo_atual < custo_melhor:
                melhor, custo_melhor = atual.copy(), custo_atual

        iteracao += 1
        historico.append((iteracao, temp, custo_atual, custo_melhor))

        if passo:
            print(f"Iter {iteracao:4d} | T={temp:8.3f} | custo atual={custo_atual:3d}"
                  f" | melhor={custo_melhor:3d} | {atual.tolist()}")
            time.sleep(pausa)

        temp *= resfriamento

    return melhor, custo_melhor, historico


def salvar_metricas(historico, caminho="evolucao.csv"):
    """Exporta a curva de decaimento para alimentar os graficos do relatorio."""
    with open(caminho, "w") as f:
        f.write("iteracao,temperatura,custo_atual,melhor_custo\n")
        for it, temp, c_atual, c_melhor in historico:
            f.write(f"{it},{temp:.4f},{c_atual},{c_melhor}\n")
    return caminho


def mostrar_evolucao(historico, amostras=20):
    print("\nEvolucao da heuristica:")
    passo = max(1, len(historico) // amostras)
    for it, temp, c_atual, c_melhor in historico[::passo]:
        print(f"   iter {it:4d} | T={temp:8.3f} | custo={c_atual:3d} | melhor={c_melhor:3d}")
    it, temp, c_atual, c_melhor = historico[-1]
    print(f"   iter {it:4d} | T={temp:8.3f} | custo={c_atual:3d} | melhor={c_melhor:3d} (final)")


def mostrar_solucao(perm, custo_total, prefA, prefB):
    print("\n" + "=" * 52)
    print("Solucao codificada :", perm.tolist())
    print("Custo (heuristica) :", custo_total)
    print("Solucao decodificada (quartos):")
    for i, j in enumerate(perm):
        c = prefA[i][j] + prefB[j][i]
        print(f"   Quarto {i + 1}: A{i + 1} + B{j + 1}   (ranks somados = {c})")
    print("=" * 52)


def main():
    args = sys.argv[1:]
    if args:
        # uso normal via linha de comando: arquivo [modo] [pausa]
        caminho = args[0]
        modo = args[1].lower() if len(args) > 1 else "final"
        try:
            pausa = float(args[2]) if len(args) > 2 else PAUSA_PADRAO
        except ValueError:
            pausa = PAUSA_PADRAO
    else:
        # sem argumentos (ex: duplo-clique): pergunta interativamente
        print("Uso: annealing <arquivo> [passo|final] [pausa_seg]\n")
        caminho = input("Arquivo de preferencias: ").strip().strip('"')
        if not caminho:
            print("Nenhum arquivo informado.")
            return
        modo = input("Modo [final/passo] (Enter = final): ").strip().lower() or "final"
        pausa = PAUSA_PADRAO

    caminho = resolver_caminho(caminho)
    try:
        n, prefA, prefB = ler_arquivo(caminho)
    except FileNotFoundError:
        print(f"Arquivo nao encontrado: {caminho}")
        return
    except ValueError as e:
        print(f"Erro ao ler '{caminho}': {e}")
        return

    print(f"Arquivo: {caminho}  |  {n} duplas  |  modo: {modo}")
    print(f"Parametros SA: T0={T0}  resfriamento={RESFRIAMENTO}  T_min={T_MIN}")

    melhor, custo_melhor, historico = simulated_annealing(
        prefA, prefB, passo=(modo == "passo"), pausa=pausa)

    if modo != "passo":
        mostrar_evolucao(historico)

    arquivo_csv = salvar_metricas(historico)
    print(f"\nMetricas salvas em: {arquivo_csv}  ({len(historico)} iteracoes)")
    print(f"Custo inicial: {historico[0][2]}  ->  custo final (melhor): {custo_melhor}")

    mostrar_solucao(melhor, custo_melhor, prefA, prefB)


if __name__ == "__main__":
    main()
