# Relatório de preparação dos dados

## 1. Visão geral

Este relatório apresenta as etapas executadas no pipeline de
preparação da base de clientes.

| Métrica | Resultado |
|---|---:|
| Registros iniciais | 10000 |
| Colunas iniciais | 13 |
| Registros finais | 9972 |
| Colunas finais | 63 |
| Linhas completamente duplicadas | 0 |
| CPFs duplicados distintos | 14 |

## 2. Diagnóstico inicial

Foram identificados
28
registros envolvidos em duplicidade de CPF.

### Valores ausentes após a remoção dos CPFs conflitantes

| Coluna | Quantidade |
|---|---:|
| estado | 584 |
| salario | 571 |
| nivel_educacao | 451 |
| estado_civil | 451 |
| area_atuacao | 451 |

## 3. Validações de consistência

| Validação | Ocorrências |
|---|---:|
| Datas inválidas | 0 |
| Idades fora do intervalo | 0 |
| Salários não positivos | 0 |
| Número de filhos inválido | 0 |
| Experiência negativa | 0 |
| Experiência maior que a idade | 0 |
| Início da carreira antes dos 14 anos | 0 |
| CPFs com identidades conflitantes | 14 |

Colunas constantes identificadas: `pais`.

## 4. Desidentificação

Foram removidos
28
registros associados a CPFs conflitantes.

As seguintes colunas identificadoras foram removidas:

- `nome`
- `cpf`
- `data`
- `endereco`
- `pais`

Foi criada a coluna artificial `cliente_id`.

## 5. Tratamento de valores ausentes

A coluna `salario` foi preenchida com sua mediana:
**R$ 6.061,63**.

As variáveis categóricas foram preenchidas com
`Não informado`.

Total de valores ausentes após o tratamento:
**0**.

## 6. Engenharia de features

Foram criadas
5
novas variáveis:

- `faixa_etaria`
- `faixa_experiencia`
- `salario_anual`
- `tem_filhos`
- `idade_inicio_carreira`

## 7. Padronização e normalização

### StandardScaler

- `salario_std`
- `anos_experiencia_std`

### MinMaxScaler

- `idade_minmax`
- `numero_filhos_minmax`
- `idade_inicio_carreira_minmax`

## 8. Codificação das variáveis categóricas

### OrdinalEncoder

- `nivel_educacao_ord`
- `faixa_etaria_ord`
- `faixa_experiencia_ord`

### OneHotEncoder

Foram criadas
39
colunas binárias.

## 9. Resultado final

| Informação | Resultado |
|---|---:|
| Registros exportados | 9972 |
| Colunas exportadas | 63 |
| Tamanho do arquivo | 2.755,32 KB |

Arquivo gerado: `data/processed/clientes_preparados.csv`.

A base final não contém identificadores pessoais diretos,
valores ausentes ou registros associados a CPFs conflitantes.
