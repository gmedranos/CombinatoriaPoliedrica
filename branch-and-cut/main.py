import sys
import gurobipy as gp
import networkx as nx
from gurobipy import GRB
import matplotlib.pyplot as plt
import copy
import math as mt
from networkx import NetworkXError
import cProfile
from networkx.algorithms import flow

contador = 0

teste1 = "C:\\Users\\gmedr\\Documents\\Estudos\\MC918\\branch-and-cut\\instancias\\C\\c08.stp"

# Le a entrada dada por um path
def read_input(path):

    f = open(path)
    linha = f.readline()
    # Chega na parte do grafo
    while(linha != "END\n"):
        linha = f.readline()
        pass

    f.readline()
    f.readline()

    # Le o numero de vertices e arestas
    linha = f.readline()
    nos = int(linha.split(" ")[1])
    linha = f.readline()
    arestas = int(linha.split(" ")[1]) 


    # Cria a lista de adjacencias
    adj = []
    for i in range(0, nos):
        adj.append([])
    
    weight = {}

    # Pega a informacao das arestas
    for i in range(0, arestas):
        linha = f.readline()
        linha_q = linha.split(" ")
        v1 = int (linha_q[1]) - 1
        v2 = int (linha_q[2]) - 1
        adj[v1].append(v2)
        adj[v2].append(v1)
        weight[(v1, v2)] = int (linha_q[3]) / 2
        weight[(v2, v1)] = int (linha_q[3]) / 2


    # Le as proximas linhas
    f.readline()
    f.readline()
    f.readline()


    # Pega a informacao dos terminais
    num_terminais = int(f.readline().split(" ")[1])

    terminais = []

    for i in range(0, num_terminais):
        terminais.append(int(f.readline().split(" ")[1]) - 1) 

    f.close()

    return nos, arestas, adj, terminais, weight

# Acha um corte minimo s,t dado uma arvore de Gomory-Hu
def acha_corte_minimo(s, t, arvore):
    # Cria os vetores de antecedencia e o visitado
    pi = []
    visitado = []
    for i in range(0, len(arvore)):
        pi.append(-1)
        visitado.append(False)
    
    Q = [s]

    # Roda o bfs ate acahr um caminho de s-t
    while Q != []:
        vertice = Q.pop(0)
        for i in arvore.neighbors(vertice):
            if not visitado[i]:
                visitado[i] = True
                pi[i] = vertice
                Q.append(i)
            if i == t:
                pi[i] = vertice
                Q = []
                break
    
    # Cria o caminho
    caminho = [t]
    i = t
    while pi[i] != s:
        caminho.append(pi[i])
        i = pi[i]

    caminho.append(s)
    caminho.reverse() # Inverte pra ficar certo


    # Acha o vertice minimo no caminho
    min = arvore[caminho[0]][caminho[1]]['weight']
    min_aresta = (caminho[0], caminho[1])
    for i in range(1, len(caminho)):
        if arvore[caminho[i - 1]][caminho[i]]['weight'] < min:
            min = arvore[caminho[i - 1]][caminho[i]]['weight']
            min_aresta = (caminho[i - 1], caminho[i])

    # Remove a aresta pra achar a particao
    arvore.remove_edge(min_aresta[0], min_aresta[1])

    for i in range(0, len(arvore)):
        visitado[i] = False

    Q = [s]
    corte = [s]
    visitado[s] = True

    # Acha o corte minimo, vendo quais vertices sao alcansaveis de s
    while Q != []:
        vertice = Q.pop(0)
        for i in arvore.neighbors(vertice):
            if not visitado[i]:
                visitado[i] = True
                Q.append(i)
                corte.append(i)

    # Adiciona a aresta de volta
    arvore.add_edge(min_aresta[0], min_aresta[1])
    arvore[min_aresta[0]][min_aresta[1]]['weight'] = min

    return corte, min

# Dado um corte, acha as arestas desse corte
def acha_valor_corte(corte, grafo):
    valor = 0
    arestas_corte = []
    # Percorre os vertices do corte e ve quais nao sao vizinhos
    # da mesma parte
    for i in corte:
        for j in grafo.neighbors(i):
            if j not in corte:
                arestas_corte.append((i, j))
    return arestas_corte

# Verifica se uma solucao inteira é valida
def verifica_solucao(grafo, terminais):
    s = terminais[0]
    visitado = [False for i in range(0, len(grafo))]
    Q = [s]

    visitado[s] = True
    # Roda o bfs a partir de um vertice terminal
    while Q != []:
        i = Q.pop(0)
        for j in grafo.neighbors(i):
            if grafo[i][j]['capacity'] == 1:
                if not visitado[j]:
                    visitado[j] = True
                    Q.append(j)

    # Se todo vertice for alcansavel, retorna true,
    # Se nao retorna false
    for i in terminais:
        if not visitado[i]:
            return False

    return True

# Cria corte de steiner a partir de uma solucao
def cria_cortes_steiner(grafo_novo, terminais, model, vars, modo):
    # Acha a arvore de gomory-hu  
    arvore = nx.gomory_hu_tree(grafo_novo)
    # Calcula os cortes minimos para ver se é possivel adicionar um corte de steiner
    cortes = 0
    flag = False
    a = [terminais[0]]
    # Percorre pares de terminais e ve se o corte minimo é menor que 1 (0,9 porque tive problemas com ponto flutuante)
    for i in terminais:
        for j in terminais:
            if i != j:
                corte, valor_corte = acha_corte_minimo(i, j, arvore)
                arestas_corte = acha_valor_corte(corte, grafo_novo)
                if valor_corte < 0.9:
                    if modo == 1:
                        model.cbLazy(sum(vars[(a,b)] for (a,b) in arestas_corte) >= 1.0)
                        cortes += 1
                        break
                    elif modo == 0 and 1 - valor_corte > 0:
                        model.cbLazy(sum(vars[(a,b)] for (a,b) in arestas_corte) >= 1.0)
                        cortes += 1
                        break
            if modo == 0 and cortes >= 2:
                flag = True
                break
            elif modo == 1 and cortes >= 2:
                flag = True
                break
        if flag:
            break

# Acha os cortes que a solucao precisa
def corte_gomory_hu(model, where, grafo, terminais, vars, weight):
    global contador
    # Verifica se a solucao é fracionaria
    if where == GRB.Callback.MIPNODE:
        status = model.cbGet(GRB.Callback.MIPNODE_STATUS)
        if status == GRB.OPTIMAL:
            vals = model.cbGetNodeRel(model._vars)
            grafo_novo = grafo.copy()
            for i in range(len(grafo_novo)):
                for j in grafo_novo.neighbors(i):
                    grafo_novo[i][j]['capacity'] = vals[(i, j)]
            #Se adicionamos muitos cortes, pula essa parte
            if contador < 500:
                heuristica_primal(grafo_novo, vals, vars, terminais, model, weight)
                cria_cortes_steiner(grafo_novo, terminais, model, vars, 0)        
            # Acha o corte da particao de steiner pela heuristica
            acha_corte_heuristica(grafo_novo, terminais, model, vars, vals)
            contador += 1

    # Verifica se a solucao é inteira
    if where == GRB.Callback.MIPSOL:
        vals = model.cbGetSolution(model._vars)
        grafo_novo = grafo.copy()
        
        for i in range(len(grafo_novo)):
            for j in grafo_novo.neighbors(i):
                grafo_novo[i][j]['capacity'] = vals[(i, j)]

        # Verifica se a solucao é valida, se for nao faz nada
        # Se nao for acha um corte
        if verifica_solucao(grafo, terminais):
            return
        cria_cortes_steiner(grafo_novo, terminais, model, vars, 1)
    return

# Calcula a particao e seu valor de um grafo
def calcula_particao(particao, grafo):
    valor = 0
    arestas = []
    for i in range(0, len(particao)):
        for j in particao[i]:
            for k in grafo.neighbors(j):
                if k not in particao[i]:
                    if (k, j) not in arestas:
                        valor += grafo[j][k]['capacity']
                        arestas.append((j, k))

    return valor, arestas

# Dado um v e a particao, acha o V_i que maximiza o peso das
# Arestas q saem de v e entram em V_i
def acha_max_heuristica(v, particao, vals, grafo):
    max = -1
    indice = -1
    # Pega a adjacencia de v e compara com os valores de
    # x com realcao a cada parte da particao
    for i in range(1, len(particao)):
        valor_atual = 0
        for j in grafo.neighbors(v):
            if j in particao[i]:
                valor_atual += vals[(v, j)]
        if valor_atual > max:
            max = valor_atual
            indice = i

    return indice

# Acha o corte da heuristica gulosa
def acha_corte_heuristica(grafo_novo, terminais, model, vars, vals):
    particoes = [set({})]
    # Cria as particoes com um terminal e o resto
    for i in range(0, len(grafo_novo)):
        if i in terminais:
            particoes.append({i})
        else:
            particoes[0].add(i)
    valor, arestas = calcula_particao(particoes, grafo_novo)
    k = len(terminais)
    # Enquanto o valor do corte for maior que tal valor
    # Junta os conjuntos
    while valor >= len(particoes) - 2 and arestas != []:
        max = vals[(arestas[0])]
        aresta_max = arestas[0]
        # Acha aresta de custo maximo
        for i in range(1, len(arestas)):
            if vals[(arestas[i])] > max:
                max = vals[arestas[i]]
                aresta_max = arestas[i]
        conjunto_i = -1
        conjunto_j = -1
        # Acha qual parte da particao pertence cada vertice
        for i in range(0, len(particoes)):
            if aresta_max[0] in particoes[i]:
                conjunto_i = i
            elif aresta_max[1] in particoes[i]:
                conjunto_j = i
        
        if conjunto_i > conjunto_j:
            temp = conjunto_j
            conjunto_j = conjunto_i
            conjunto_i = temp
            aresta_max = (aresta_max[1], aresta_max[0])

        # Se nenhum dos dois for o 0, junta os dois
        if conjunto_i >= 1:
            conj_j = particoes.pop(conjunto_j)
            conj_i = particoes.pop(conjunto_i)
            particoes.append(conj_i.union(conj_j))
        # Se um deles for 0, adiciona o u nesse conjunto
        else:
            particoes[0].remove(aresta_max[0])
            particoes[conjunto_j].add(aresta_max[0])
        # Recalcula os valores e as arestas
        valor, arestas = calcula_particao(particoes, grafo_novo)
    
    # Adiciona o que sobrou do V_0 no resto
    for i in particoes[0]:
        j = acha_max_heuristica(i, particoes, vals, grafo_novo)
        particoes[j].add(i)

    particoes.pop(0)

    valor , arestas = calcula_particao(particoes, grafo_novo)

    # Cria o corte se precisar
    k = len(particoes) - 1
    if arestas != [] and valor < k:
        model.cbCut(sum(vars[(i, j)] for (i, j) in arestas) >= k)
    return

# Acha uma solucao valida a partir da solucao fracionaria
def heuristica_primal(grafo, vals, vars, terminais, model, weight):
    arvore = nx.maximum_spanning_tree(grafo, weight='capacity')
    # A partir da arvore geradora maxima, vai removendo as folhas nao terminais
    flag = True
    while flag:
        contador = 0
        for i in arvore:
            if arvore.degree(i) == 1:
                if i in terminais:
                    pass
                else:
                    arvore.remove_node(i)
                    break
            contador += 1
        if contador == len(arvore):    
            flag = False
    
    valor = 0

    solution = model.cbGetNodeRel(model._vars)

    # Cria os valores da solucao nova
    contador = 0
    for i in vals:
        if arvore.has_edge(i[0], i[1]):
            solution[i] = 1
            valor += weight[i]
        else:
            solution[i] = 0
    
    # Usa a solucao no modelo
    model.cbSetSolution(model._vars, solution)

    return

# Cria o modelo de PLI
def steiner_tree(nos, arestas, adj, terminais, weight):
    m = gp.Model()

    # Adiciona as variaveis
    vars = m.addVars(weight.keys(), obj=weight, vtype=GRB.BINARY, name='e')


    # Adiciona as restrições que |M| = 1
    for i in terminais: 
        m.addConstr(sum(vars[i, j] for j in adj[i]) >= 1)
    for i in range(0, nos):
        for j in adj[i]:
            m.addConstr(vars[i, j] == vars[j, i])

    for j in range(0, nos):
        arestas_corte = []
        for k in terminais:
            for l in adj[k]:
                if l != j:
                    arestas_corte.append((k, l))
            for l in adj[j]:
                if l != k:
                    arestas_corte.append((j, l))
        m.addConstr(sum(vars[i, j] for (i, j) in arestas_corte) >= 1)
    
    G = nx.Graph()
    G.add_nodes_from(range(0, nos))

    # Cria o grafo do networkx
    for i in range(0, nos):
        for j in adj[i]:
            G.add_edge(i, j)
            try:
                G[i][j]["capacity"] = weight[(i, j)] * 2
            except KeyError:
                G[i][j]["capacity"] = weight[(j, i)] * 2


    # Funcao de call back so chama outra funcao
    def callback_gomory(model, where):
        corte_gomory_hu(model, where, G, terminais, vars, weight)

    # Parametros do modelo
    m._vars = vars
    m.Params.LazyConstraints = 1
    m.Params.PreCrush = 1
    m.Params.MIPFocus = 3
    m.Params.LogFile = "./resultados/log.log"
    m.Params.TimeLimit = 600
    m.optimize(callback_gomory)
    m.write("./resultados/out.sol")

    return

def main():
    path = sys.argv[1]
    nos, arestas, adj, terminais, weight = read_input(path)
    
    steiner_tree(nos, arestas, adj, terminais, weight)
    return 0

main()
