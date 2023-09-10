# Funcao que subtrai um vetor de outro
def sub_vet(a, b):
    n = len(a)
    resp = []
    for i in range(0, n):
        resp.append(a[i] - b[i])
    return resp

# Funcao que calcula o produto interno de dois vetores
def prod_int(a, b):
    n = len(a)
    resp = 0
    for i in range(0, n):
        resp = resp + a[i]*b[i]
    return resp

# Funcao que calcula o produto de um vetor por um escalar
def prod_esc(vet, esc):
    vet_c = vet.copy()
    n = len(vet)
    for i in range(0, n):
        vet_c[i] = vet_c[i]*esc
    return vet_c

# Funcao que retorna um dos vetores da base canonica de certa dimensao. A posicao do 1 será determinada pela variavel pos 
def vet_unit(dim, pos):
    vet = []
    for i in range(0, dim):
        vet.append(0)
    vet[pos - 1] = 1
    return vet

# Funcao que calcula o D, d, tendo em base um poliedro na forma Ax <= b, em uma direcao c
def proj(A, b, c):
    m = len(A)
    N, Z, P = [], [], []
    # Particiona as linhas em conjuntos N, Z, P que indica o sinal do produto interno de linhas nesse conjunto
    # pelo vetor direcao
    for i in range(0, m):
        prod_interno = prod_int(A[i], c)
        if prod_interno > 0:
            P.append(i)
        elif prod_interno == 0:
            Z.append(i)
        else:
            N.append(i)


    r = len(Z) + len(P)*len(N) # Calcula a cardinalidade de Z U (N x P)

    bijecao = []
    
    # Cria uma bijecao de {1, 2, ... , r} -> Z U (N x P) atraves de uma lista. Nessa lista,
    # cada elemento ou é uma linha com produto interno com c igual a zero, ou uma tupla de 
    # linhas. 
    for i in range(0, len(Z)):
        bijecao.append(Z[i])
    for i in range(0, len(P)):
        for j in range(0, len(N)):
            bijecao.append((N[j], P[i]))
    
    D = []
    d = []

    for i in range(0, r):
        if(type(bijecao[i]) == type(1)): # Se bijecao[i] for inteiro, entao trata de uma linha que veio de Z, portanto so a adicionamos na resposta
            D.append(A[bijecao[i]])
            d.append(b[bijecao[i]])
        else: # Caso contrario, adicionamos uma combinação conica das linhas em N e P.
            s, t = bijecao[i]
            Atc = prod_int(A[t], c)
            Asc = prod_int(A[s], c)
            As_esc = prod_esc(A[s], Atc)
            At_esc = prod_esc(A[t], Asc)
            
            D.append(sub_vet(As_esc, At_esc))
            d.append(Atc * b[s] - Asc * b[t])
            
    return D,d

# Determina se um poliedro é ou nao vazio
# Se ele for, retorna True, se nao, retorna False
def is_empty(A, b):
    dim = len(A[0])
    D, d = proj(A, b, vet_unit(dim, 1)) # Calcula os primeiro D, d, fazendo a projecao na direção de um dos vetores da base canonica
    # Faz sucessivas projecoes nas direções dos vetores da base canonica
    for i in range(1, dim):
        D, d = proj(D, d, vet_unit(dim, i + 1))

    # Verifica se algum dos elementos do vetor d resultante é zero
    # Se algum for, retorna que o poliedro é vazio
    for i in range(0, len(d)):
        if d[i] < 0:
            return True
    return False

# Funcao que imprime o poliedro com base na formataçã da entrada
def print_poliedro(A, b):
    # O algoritimo pode produzir A, b sem nada. Nesse caso, o poliedro é o espaço todo, que pode ser representado por 
    # 0 * x1 <= 0
    if len(A) == 0: 
        print("0x1 <= 0")
    # Percorre o poliedro
    for i in range(0, len(A)):
        primeiro = True
        for j in range(0, len(A[0])):
            # Se for a primeira variavel a ser impressa, nao precisa do "+" no comeco
            if A[i][j] != 0 and primeiro:
                primeiro = False
                print(str(A[i][j]) + "x" + str(j + 1), end="")
            # Como nao é mais a primeira variavel a ser impressa, imprime no comeco um " + "
            elif A[i][j] != 0:
                print(" + " + str(A[i][j]) + "x" + str(j + 1), end="")
        if not primeiro:
            print(" <= " + str(b[i]))
    return

# Pega as informacoes do proble
# Retorna uma matriz e um vetor b que representam o poliedro Ax <= b.
# Tambem retornam o modo escolhido e a direcao que faremos a projecao se esse for o modo
def get_info():
    modo = input("")
    c = []
    if modo == "Projecao": # Se o modo for projecao, precisa pegar a direcao
        direcao = input("").split(" ")
        for i in range(0, len(direcao)): 
            c.append(float(direcao[i]))    
    tamanhos = input("").split(" ")
    A, b = [], []
    n, m = int(tamanhos[0]), int(tamanhos[1])

    # Cria uma lista de lista com o numero de linhas certo
    for i in range(0, m):
        A.append([])
        for j in range(0, n):
            A[i].append(0)
        b.append(0)
    
    for i in range(0, m):
        linha = input("").split(" ")
        # Percorre cada linha, lendo os valores para colocar na matriz
        for j in range(0, len(linha) - 1):
            if j % 2 == 0:
                op = linha[j].split("x")
                var = int(op[1])
                value = float(op[0])
                A[i][var - 1] = value
        b[i] = float(linha[-1])

    return A, b, modo, c

# Pega as informacoes
A, b, modo, c = get_info()

# Se for projecao, realiza a projecao e imprime o poliedro
if modo == "Projecao":
    D, d = proj(A, b, c)
    print_poliedro(D, d)
# Caso contrario, imprime se o poliedro é ou nao vazio
elif modo == "Vazio":
    if (is_empty(A, b)):
        print("O poliedro eh vazio!")
    else:
        print("O poliedro nao eh vazio")
