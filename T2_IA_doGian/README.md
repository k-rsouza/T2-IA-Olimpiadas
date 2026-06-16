## Bibliotecas

Todas nativas do Python, exceto numpy.


| Biblioteca | Tipo    | Uso                                          |
| ---------- | ------- | -------------------------------------------- |
| `random`   | nativa  | função sucessora e roleta de aceitação       |
| `math`     | nativa  | probabilidade `e^(-ΔE/T)`                    |
| `numpy`    | externa | carga do arquivo e cálculo do custo          |
| `sys`      | nativa  | leitura dos argumentos da linha de comando   |
| `re`       | nativa  | leitura robusta (ignora cabeçalhos de texto) |
| `time`     | nativa  | pausa entre passos no modo passo a passo     |


Instalar a dependência externa:

```bash
pip install numpy
```

## Como executar

Via Python:

```bash
python annealing.py <arquivo> [passo|final] [pausa_seg]
```

Via executável (não precisa de Python):

```bash
./dist/annealing <arquivo> [passo|final] [pausa_seg]
```

## Parâmetros

- `<arquivo>` (obrigatório): arquivo de preferências. Ex: `exemplo.txt`
- `[passo|final]` (opcional): modo de execução. Padrão: `final`
  - `final` — roda e mostra só o resultado
  - `passo` — mostra cada iteração pausadamente
- `[pausa_seg]` (opcional): segundos entre passos no modo `passo`. Padrão: `0.1`

## Exemplos

```bash
python annealing.py exemplo.txt              # modo final
python annealing.py exemplo.txt passo        # passo a passo (0.1s)
python annealing.py exemplo.txt passo 0.3    # passo a passo (0.3s)
```

## Saída

- Evolução da heurística ao longo das iterações.
- Solução codificada (permutação) e decodificada (quartos).
- Arquivo `evolucao.csv` com a curva de temperatura e custo por iteração.

