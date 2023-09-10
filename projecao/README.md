# Laboratório de Projeção
## Utilização
Para usar o programa, a primeira linha da entrada é para definir o modo dentre dois possíveis, o modo "Projecao" e o modo "Vazio". Se o modo for o de "Projeção", a linha seguinte devera dar a direção, onde os valores do vetor serão separados por um espaço. A próxima linha devera conter o número de variáveis e o número de linhas do poliedro, separados por um espaço. Já as proxemas linhas devem conter a descrição do poliedro conforme descrito no enunciado.

## Exemplos entrada/saída
### Projecao:
Entrada:
```
Projecao
1 1
2 3
-1x1 <= -1
-1x1 + -1x2 <= -5
2x1 + 1x2 <= 8
```
Saída
```
-1.0x1 + 1.0x2 <= 5.0
1.0x1 + -1.0x2 <= 1.0

```

### Vazio:
Entrada:
```
Vazio
4 6
-1x1 <= -1
-1x2 <= -2
-1x3 <= -3
-1x4 <= -4
1x1 + 1x2 + 1x3 + 1x4 <= 5
-2x1 + -3x2 + -4x3 + -5x4 <= -20
```
Saída:
```
O poliedro eh vazio!
```
