from pathlib import Path

import pandas as pd
from sklearn.preprocessing import (
    MinMaxScaler,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_DIR / "data" / "raw" / "clientes-v2.csv"
PROCESSED_DATA_PATH = PROJECT_DIR / "data" / "processed" / "clientes_preparados.csv"

REPORT_PATH = PROJECT_DIR / "reports" / "relatorio_preparacao.md"


def formatar_numero_br(
    valor: float,
    casas_decimais: int = 2,
) -> str:
    """
    Formata números com ponto para milhares e vírgula
    para casas decimais.
    """
    numero_formatado = f"{valor:,.{casas_decimais}f}"

    return numero_formatado.replace(",", "_").replace(".", ",").replace("_", ".")


def carregar_dados(caminho: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Carrega o conjunto de dados bruto.

    Args:
        caminho: caminho do arquivo CSV.

    Returns:
        DataFrame contendo os dados carregados.

    Raises:
        FileNotFoundError: caso o arquivo não seja encontrado.
        ValueError: caso o arquivo esteja vazio.
    """
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {caminho}")

    df = pd.read_csv(caminho)

    if df.empty:
        raise ValueError("O arquivo de dados está vazio.")

    return df


def gerar_diagnostico_inicial(df: pd.DataFrame) -> dict:
    """
    Gera um diagnóstico inicial de qualidade dos dados.

    O diagnóstico contém:
    - dimensões da base;
    - tipos das colunas;
    - valores nulos;
    - percentual de valores nulos;
    - valores únicos;
    - duplicidades exatas;
    - duplicidades de CPF;
    - estatísticas das variáveis numéricas.
    """
    resumo_colunas = pd.DataFrame(
        {
            "tipo": df.dtypes.astype(str),
            "nulos": df.isna().sum(),
            "percentual_nulos": (df.isna().mean() * 100).round(2),
            "valores_unicos": df.nunique(dropna=False),
        }
    )

    linhas_duplicadas = int(df.duplicated().sum())

    registros_com_cpf_duplicado = 0
    cpfs_duplicados_distintos = 0

    if "cpf" in df.columns:
        mascara_cpf_duplicado = df["cpf"].duplicated(keep=False)

        registros_com_cpf_duplicado = int(mascara_cpf_duplicado.sum())

        cpfs_duplicados_distintos = int(df.loc[mascara_cpf_duplicado, "cpf"].nunique())

    estatisticas_numericas = df.describe().transpose().round(2)

    return {
        "quantidade_linhas": df.shape[0],
        "quantidade_colunas": df.shape[1],
        "resumo_colunas": resumo_colunas,
        "linhas_duplicadas": linhas_duplicadas,
        "registros_com_cpf_duplicado": (registros_com_cpf_duplicado),
        "cpfs_duplicados_distintos": (cpfs_duplicados_distintos),
        "estatisticas_numericas": estatisticas_numericas,
    }


def exibir_diagnostico(diagnostico: dict) -> None:
    """
    Exibe o diagnóstico inicial no terminal.
    """
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO INICIAL DA BASE")
    print("=" * 60)

    print(f"\nQuantidade de linhas: " f"{diagnostico['quantidade_linhas']}")

    print(f"Quantidade de colunas: " f"{diagnostico['quantidade_colunas']}")

    print("\nRESUMO DAS COLUNAS")
    print("-" * 60)
    print(diagnostico["resumo_colunas"].to_string())

    print("\nDUPLICIDADES")
    print("-" * 60)

    print(f"Linhas completamente duplicadas: " f"{diagnostico['linhas_duplicadas']}")

    print(
        f"Registros envolvidos em CPF duplicado: "
        f"{diagnostico['registros_com_cpf_duplicado']}"
    )

    print(f"CPFs duplicados distintos: " f"{diagnostico['cpfs_duplicados_distintos']}")

    print("\nESTATÍSTICAS DAS VARIÁVEIS NUMÉRICAS")
    print("-" * 60)
    print(diagnostico["estatisticas_numericas"].to_string())

    print("\n" + "=" * 60)
    print("DIAGNÓSTICO CONCLUÍDO")
    print("=" * 60)


def gerar_validacoes_consistencia(df: pd.DataFrame) -> dict:
    """
    Verifica regras básicas de consistência da base.

    As validações não modificam o DataFrame.
    """
    colunas_esperadas = {
        "nome",
        "cpf",
        "idade",
        "data",
        "endereco",
        "estado",
        "pais",
        "salario",
        "nivel_educacao",
        "numero_filhos",
        "estado_civil",
        "anos_experiencia",
        "area_atuacao",
    }

    colunas_ausentes = sorted(colunas_esperadas - set(df.columns))

    if colunas_ausentes:
        raise ValueError(
            "Colunas obrigatórias ausentes: " + ", ".join(colunas_ausentes)
        )

    datas_convertidas = pd.to_datetime(
        df["data"],
        format="%d/%m/%Y",
        errors="coerce",
    )

    mascara_cpf_duplicado = df["cpf"].duplicated(keep=False)

    resumo_cpfs_duplicados = (
        df.loc[mascara_cpf_duplicado]
        .groupby("cpf")[["nome", "data", "endereco"]]
        .nunique(dropna=False)
    )

    cpfs_com_identidades_conflitantes = int(
        (resumo_cpfs_duplicados > 1).any(axis=1).sum()
    )

    colunas_constantes = [
        coluna for coluna in df.columns if df[coluna].nunique(dropna=False) == 1
    ]

    idade_inicio_carreira = df["idade"] - df["anos_experiencia"]

    return {
        "datas_invalidas": int(datas_convertidas.isna().sum()),
        "idades_fora_intervalo": int((~df["idade"].between(18, 100)).sum()),
        "salarios_nao_positivos": int(df["salario"].le(0).sum()),
        "numero_filhos_invalido": int((~df["numero_filhos"].between(0, 5)).sum()),
        "experiencia_negativa": int(df["anos_experiencia"].lt(0).sum()),
        "experiencia_maior_que_idade": int(
            (df["anos_experiencia"] > df["idade"]).sum()
        ),
        "inicio_carreira_antes_14": int(idade_inicio_carreira.lt(14).sum()),
        "cpfs_com_identidades_conflitantes": (cpfs_com_identidades_conflitantes),
        "colunas_constantes": colunas_constantes,
    }


def exibir_validacoes_consistencia(
    validacoes: dict,
) -> None:
    """
    Exibe no terminal os resultados das validações.
    """
    print("\n" + "=" * 60)
    print("VALIDAÇÕES DE CONSISTÊNCIA")
    print("=" * 60)

    print(f"\nDatas inválidas: " f"{validacoes['datas_invalidas']}")

    print(
        f"Idades fora do intervalo de 18 a 100 anos: "
        f"{validacoes['idades_fora_intervalo']}"
    )

    print(f"Salários não positivos: " f"{validacoes['salarios_nao_positivos']}")

    print(
        f"Quantidade de filhos fora do intervalo de 0 a 5: "
        f"{validacoes['numero_filhos_invalido']}"
    )

    print(
        f"Experiências profissionais negativas: "
        f"{validacoes['experiencia_negativa']}"
    )

    print(
        f"Experiência maior que a idade: "
        f"{validacoes['experiencia_maior_que_idade']}"
    )

    print(
        f"Início de carreira calculado antes dos 14 anos: "
        f"{validacoes['inicio_carreira_antes_14']}"
    )

    print(
        f"CPFs associados a identidades conflitantes: "
        f"{validacoes['cpfs_com_identidades_conflitantes']}"
    )

    print("Colunas constantes: " + ", ".join(validacoes["colunas_constantes"]))

    print("\n" + "=" * 60)
    print("VALIDAÇÕES CONCLUÍDAS")
    print("=" * 60)


def desidentificar_dados(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Remove identificadores pessoais e registros com CPF conflitante.

    A função:
    - remove todos os registros envolvidos em duplicidade de CPF;
    - cria um identificador artificial;
    - extrai o ano de nascimento;
    - remove identificadores diretos;
    - remove a coluna constante 'pais'.

    Returns:
        DataFrame desidentificado e resumo da operação.
    """
    df_desidentificado = df.copy()

    quantidade_inicial = len(df_desidentificado)

    mascara_cpf_duplicado = df_desidentificado["cpf"].duplicated(keep=False)

    registros_cpf_conflitante = int(mascara_cpf_duplicado.sum())

    df_desidentificado = df_desidentificado.loc[~mascara_cpf_duplicado].copy()

    datas_convertidas = pd.to_datetime(
        df_desidentificado["data"],
        format="%d/%m/%Y",
        errors="raise",
    )

    df_desidentificado["ano_nascimento"] = datas_convertidas.dt.year

    df_desidentificado.reset_index(
        drop=True,
        inplace=True,
    )

    identificadores = [
        f"CLI{numero:06d}"
        for numero in range(
            1,
            len(df_desidentificado) + 1,
        )
    ]

    df_desidentificado.insert(
        0,
        "cliente_id",
        identificadores,
    )

    colunas_removidas = [
        "nome",
        "cpf",
        "data",
        "endereco",
        "pais",
    ]

    df_desidentificado.drop(
        columns=colunas_removidas,
        inplace=True,
    )

    resumo = {
        "quantidade_inicial": quantidade_inicial,
        "registros_cpf_conflitante": (registros_cpf_conflitante),
        "quantidade_final": len(df_desidentificado),
        "colunas_removidas": colunas_removidas,
    }

    return df_desidentificado, resumo


def exibir_resumo_desidentificacao(
    resumo: dict,
) -> None:
    """
    Exibe os resultados da desidentificação no terminal.
    """
    print("\n" + "=" * 60)
    print("DESIDENTIFICAÇÃO DOS DADOS")
    print("=" * 60)

    print(f"\nRegistros iniciais: " f"{resumo['quantidade_inicial']}")

    print(
        f"Registros removidos por CPF conflitante: "
        f"{resumo['registros_cpf_conflitante']}"
    )

    print(f"Registros restantes: " f"{resumo['quantidade_final']}")

    print("Colunas removidas: " + ", ".join(resumo["colunas_removidas"]))

    print("\n" + "=" * 60)
    print("DESIDENTIFICAÇÃO CONCLUÍDA")
    print("=" * 60)


def tratar_valores_ausentes(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Trata os valores ausentes da base desidentificada.

    Estratégia:
    - salário: preenchimento pela mediana;
    - variáveis categóricas: preenchimento com
      'Não informado';
    - criação de indicador para salário originalmente ausente.
    """
    df_tratado = df.copy()

    nulos_antes = {
        coluna: int(quantidade)
        for coluna, quantidade in df_tratado.isna().sum().items()
        if quantidade > 0
    }

    df_tratado["salario_ausente"] = df_tratado["salario"].isna().astype("int8")

    mediana_salario = float(df_tratado["salario"].median())

    df_tratado["salario"] = df_tratado["salario"].fillna(mediana_salario)

    colunas_categoricas = [
        "estado",
        "nivel_educacao",
        "estado_civil",
        "area_atuacao",
    ]

    df_tratado[colunas_categoricas] = df_tratado[colunas_categoricas].fillna(
        "Não informado"
    )

    nulos_depois = int(df_tratado.isna().sum().sum())

    resumo = {
        "nulos_antes": nulos_antes,
        "mediana_salario": round(mediana_salario, 2),
        "nulos_depois": nulos_depois,
        "categorias_preenchidas": colunas_categoricas,
    }

    return df_tratado, resumo


def exibir_resumo_valores_ausentes(
    resumo: dict,
) -> None:
    """
    Exibe o resumo do tratamento de valores ausentes.
    """
    print("\n" + "=" * 60)
    print("TRATAMENTO DE VALORES AUSENTES")
    print("=" * 60)

    print("\nValores ausentes antes do tratamento:")

    for coluna, quantidade in resumo["nulos_antes"].items():
        print(f"- {coluna}: {quantidade}")

    print(f"\nMediana utilizada para salário: " f"{resumo['mediana_salario']:.2f}")

    print(
        "Colunas categóricas preenchidas: "
        + ", ".join(resumo["categorias_preenchidas"])
    )

    print(f"Total de valores ausentes após o tratamento: " f"{resumo['nulos_depois']}")

    print("\n" + "=" * 60)
    print("TRATAMENTO CONCLUÍDO")
    print("=" * 60)


def criar_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Cria novas variáveis derivadas dos dados existentes.

    Features criadas:
    - faixa_etaria;
    - faixa_experiencia;
    - salario_anual;
    - tem_filhos;
    - idade_inicio_carreira.
    """
    df_features = df.copy()

    df_features["faixa_etaria"] = pd.cut(
        df_features["idade"],
        bins=[17, 29, 39, 49, 59, float("inf")],
        labels=[
            "18 a 29 anos",
            "30 a 39 anos",
            "40 a 49 anos",
            "50 a 59 anos",
            "60 anos ou mais",
        ],
        include_lowest=True,
    )

    df_features["faixa_experiencia"] = pd.cut(
        df_features["anos_experiencia"],
        bins=[-1, 2, 5, 10, 20, float("inf")],
        labels=[
            "Até 2 anos",
            "3 a 5 anos",
            "6 a 10 anos",
            "11 a 20 anos",
            "Mais de 20 anos",
        ],
    )

    df_features["salario_anual"] = (df_features["salario"] * 12).round(2)

    df_features["tem_filhos"] = df_features["numero_filhos"].gt(0).astype("int8")

    df_features["idade_inicio_carreira"] = (
        df_features["idade"] - df_features["anos_experiencia"]
    )

    features_criadas = [
        "faixa_etaria",
        "faixa_experiencia",
        "salario_anual",
        "tem_filhos",
        "idade_inicio_carreira",
    ]

    resumo = {
        "features_criadas": features_criadas,
        "quantidade_features": len(features_criadas),
        "registros_com_filhos": int(df_features["tem_filhos"].sum()),
        "idade_inicio_carreira_minima": int(df_features["idade_inicio_carreira"].min()),
        "idade_inicio_carreira_maxima": int(df_features["idade_inicio_carreira"].max()),
        "salario_anual_medio": round(
            float(df_features["salario_anual"].mean()),
            2,
        ),
    }

    return df_features, resumo


def exibir_resumo_features(
    resumo: dict,
) -> None:
    """
    Exibe o resumo da engenharia de features.
    """
    print("\n" + "=" * 60)
    print("ENGENHARIA DE FEATURES")
    print("=" * 60)

    print(f"\nQuantidade de features criadas: " f"{resumo['quantidade_features']}")

    print("\nNovas features:")

    for feature in resumo["features_criadas"]:
        print(f"- {feature}")

    print(f"\nRegistros de clientes com filhos: " f"{resumo['registros_com_filhos']}")

    print(
        f"Menor idade estimada de início da carreira: "
        f"{resumo['idade_inicio_carreira_minima']} anos"
    )

    print(
        f"Maior idade estimada de início da carreira: "
        f"{resumo['idade_inicio_carreira_maxima']} anos"
    )

    print(f"Salário anual médio: " f"R$ {resumo['salario_anual_medio']:.2f}")

    print("\n" + "=" * 60)
    print("ENGENHARIA DE FEATURES CONCLUÍDA")
    print("=" * 60)


def transformar_variaveis(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict]:
    """
    Aplica escalonamento e codificação às variáveis.

    Estratégias:
    - StandardScaler para variáveis numéricas contínuas;
    - MinMaxScaler para variáveis numéricas limitadas;
    - OrdinalEncoder para categorias ordenadas;
    - OneHotEncoder para categorias nominais.
    """
    df_transformado = df.copy()

    quantidade_colunas_inicial = df_transformado.shape[1]

    # Padronização: média próxima de 0 e desvio-padrão próximo de 1
    colunas_padronizadas = [
        "salario",
        "anos_experiencia",
    ]

    padronizador = StandardScaler()

    valores_padronizados = padronizador.fit_transform(
        df_transformado[colunas_padronizadas]
    )

    nomes_padronizados = []

    for indice, coluna in enumerate(colunas_padronizadas):
        nova_coluna = f"{coluna}_std"
        df_transformado[nova_coluna] = valores_padronizados[:, indice]
        nomes_padronizados.append(nova_coluna)

    # Normalização: valores entre 0 e 1
    colunas_normalizadas = [
        "idade",
        "numero_filhos",
        "idade_inicio_carreira",
    ]

    normalizador = MinMaxScaler()

    valores_normalizados = normalizador.fit_transform(
        df_transformado[colunas_normalizadas]
    )

    nomes_normalizados = []

    for indice, coluna in enumerate(colunas_normalizadas):
        nova_coluna = f"{coluna}_minmax"
        df_transformado[nova_coluna] = valores_normalizados[:, indice]
        nomes_normalizados.append(nova_coluna)

    # Codificação de categorias com ordem natural
    colunas_ordinais = [
        "nivel_educacao",
        "faixa_etaria",
        "faixa_experiencia",
    ]

    categorias_ordinais = [
        [
            "Não informado",
            "Ensino Fundamental",
            "Ensino Médio",
            "Ensino Superior",
            "Pós-graduação",
        ],
        [
            "18 a 29 anos",
            "30 a 39 anos",
            "40 a 49 anos",
            "50 a 59 anos",
            "60 anos ou mais",
        ],
        [
            "Até 2 anos",
            "3 a 5 anos",
            "6 a 10 anos",
            "11 a 20 anos",
            "Mais de 20 anos",
        ],
    ]

    codificador_ordinal = OrdinalEncoder(
        categories=categorias_ordinais,
        handle_unknown="use_encoded_value",
        unknown_value=-1,
        dtype=int,
    )

    valores_ordinais = codificador_ordinal.fit_transform(
        df_transformado[colunas_ordinais]
    )

    nomes_ordinais = [
        "nivel_educacao_ord",
        "faixa_etaria_ord",
        "faixa_experiencia_ord",
    ]

    for indice, coluna in enumerate(nomes_ordinais):
        df_transformado[coluna] = valores_ordinais[:, indice]

    # Codificação de categorias sem ordem natural
    colunas_nominais = [
        "estado",
        "estado_civil",
        "area_atuacao",
    ]

    codificador_one_hot = OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False,
        dtype=int,
    )

    valores_one_hot = codificador_one_hot.fit_transform(
        df_transformado[colunas_nominais]
    )

    nomes_one_hot = codificador_one_hot.get_feature_names_out(colunas_nominais).tolist()

    df_one_hot = pd.DataFrame(
        valores_one_hot,
        columns=nomes_one_hot,
        index=df_transformado.index,
    )

    df_transformado = pd.concat(
        [df_transformado, df_one_hot],
        axis=1,
    )

    resumo = {
        "colunas_padronizadas": nomes_padronizados,
        "colunas_normalizadas": nomes_normalizados,
        "colunas_ordinais": nomes_ordinais,
        "quantidade_one_hot": len(nomes_one_hot),
        "quantidade_colunas_inicial": quantidade_colunas_inicial,
        "quantidade_colunas_final": df_transformado.shape[1],
    }

    return df_transformado, resumo


def exibir_resumo_transformacoes(
    resumo: dict,
) -> None:
    """
    Exibe o resumo das transformações realizadas.
    """
    print("\n" + "=" * 60)
    print("TRANSFORMAÇÃO DAS VARIÁVEIS")
    print("=" * 60)

    print("\nColunas padronizadas com StandardScaler:")

    for coluna in resumo["colunas_padronizadas"]:
        print(f"- {coluna}")

    print("\nColunas normalizadas com MinMaxScaler:")

    for coluna in resumo["colunas_normalizadas"]:
        print(f"- {coluna}")

    print("\nColunas codificadas com OrdinalEncoder:")

    for coluna in resumo["colunas_ordinais"]:
        print(f"- {coluna}")

    print("\nColunas criadas com OneHotEncoder: " f"{resumo['quantidade_one_hot']}")

    print(f"Quantidade inicial de colunas: " f"{resumo['quantidade_colunas_inicial']}")

    print(f"Quantidade final de colunas: " f"{resumo['quantidade_colunas_final']}")

    print("\n" + "=" * 60)
    print("TRANSFORMAÇÕES CONCLUÍDAS")
    print("=" * 60)


def organizar_colunas(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Organiza as colunas da base final.

    As variáveis originais e as features interpretáveis
    aparecem primeiro. As colunas transformadas ficam
    organizadas posteriormente em ordem alfabética.
    """
    colunas_prioritarias = [
        "cliente_id",
        "idade",
        "faixa_etaria",
        "ano_nascimento",
        "estado",
        "salario",
        "salario_anual",
        "salario_ausente",
        "nivel_educacao",
        "numero_filhos",
        "tem_filhos",
        "estado_civil",
        "anos_experiencia",
        "faixa_experiencia",
        "idade_inicio_carreira",
        "area_atuacao",
    ]

    colunas_prioritarias_existentes = [
        coluna for coluna in colunas_prioritarias if coluna in df.columns
    ]

    colunas_restantes = sorted(
        coluna for coluna in df.columns if coluna not in colunas_prioritarias_existentes
    )

    ordem_final = colunas_prioritarias_existentes + colunas_restantes

    return df.loc[:, ordem_final].copy()


def exportar_dados(
    df: pd.DataFrame,
    caminho: Path = PROCESSED_DATA_PATH,
) -> dict:
    """
    Exporta a base preparada para um arquivo CSV.
    """
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8",
    )

    if not caminho.exists():
        raise OSError(f"O arquivo de saída não foi criado: {caminho}")

    resumo = {
        "caminho": caminho,
        "quantidade_linhas": df.shape[0],
        "quantidade_colunas": df.shape[1],
        "tamanho_kb": round(
            caminho.stat().st_size / 1024,
            2,
        ),
    }

    return resumo


def gerar_relatorio_preparacao(
    diagnostico: dict,
    validacoes: dict,
    resumo_desidentificacao: dict,
    resumo_valores_ausentes: dict,
    resumo_features: dict,
    resumo_transformacoes: dict,
    resumo_exportacao: dict,
    caminho: Path = REPORT_PATH,
) -> Path:
    """
    Gera um relatório em Markdown com as etapas do pipeline.
    """
    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas_nulos = "\n".join(
        f"| {coluna} | {quantidade} |"
        for coluna, quantidade in resumo_valores_ausentes["nulos_antes"].items()
    )

    features = "\n".join(
        f"- `{feature}`" for feature in resumo_features["features_criadas"]
    )

    colunas_padronizadas = "\n".join(
        f"- `{coluna}`" for coluna in resumo_transformacoes["colunas_padronizadas"]
    )

    colunas_normalizadas = "\n".join(
        f"- `{coluna}`" for coluna in resumo_transformacoes["colunas_normalizadas"]
    )

    colunas_ordinais = "\n".join(
        f"- `{coluna}`" for coluna in resumo_transformacoes["colunas_ordinais"]
    )

    colunas_constantes = ", ".join(validacoes["colunas_constantes"]) or "Nenhuma"
    mediana_salario_formatada = formatar_numero_br(
        resumo_valores_ausentes["mediana_salario"]
    )
    tamanho_arquivo_formatado = formatar_numero_br(resumo_exportacao["tamanho_kb"])

    conteudo = f"""# Relatório de preparação dos dados

## 1. Visão geral

Este relatório apresenta as etapas executadas no pipeline de
preparação da base de clientes.

| Métrica | Resultado |
|---|---:|
| Registros iniciais | {diagnostico['quantidade_linhas']} |
| Colunas iniciais | {diagnostico['quantidade_colunas']} |
| Registros finais | {resumo_exportacao['quantidade_linhas']} |
| Colunas finais | {resumo_exportacao['quantidade_colunas']} |
| Linhas completamente duplicadas | {diagnostico['linhas_duplicadas']} |
| CPFs duplicados distintos | {diagnostico['cpfs_duplicados_distintos']} |

## 2. Diagnóstico inicial

Foram identificados
{diagnostico['registros_com_cpf_duplicado']}
registros envolvidos em duplicidade de CPF.

### Valores ausentes após a remoção dos CPFs conflitantes

| Coluna | Quantidade |
|---|---:|
{linhas_nulos}

## 3. Validações de consistência

| Validação | Ocorrências |
|---|---:|
| Datas inválidas | {validacoes['datas_invalidas']} |
| Idades fora do intervalo | {validacoes['idades_fora_intervalo']} |
| Salários não positivos | {validacoes['salarios_nao_positivos']} |
| Número de filhos inválido | {validacoes['numero_filhos_invalido']} |
| Experiência negativa | {validacoes['experiencia_negativa']} |
| Experiência maior que a idade | {validacoes['experiencia_maior_que_idade']} |
| Início da carreira antes dos 14 anos | {validacoes['inicio_carreira_antes_14']} |
| CPFs com identidades conflitantes | {validacoes['cpfs_com_identidades_conflitantes']} |

Colunas constantes identificadas: `{colunas_constantes}`.

## 4. Desidentificação

Foram removidos
{resumo_desidentificacao['registros_cpf_conflitante']}
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
**R$ {mediana_salario_formatada}**.

As variáveis categóricas foram preenchidas com
`Não informado`.

Total de valores ausentes após o tratamento:
**{resumo_valores_ausentes['nulos_depois']}**.

## 6. Engenharia de features

Foram criadas
{resumo_features['quantidade_features']}
novas variáveis:

{features}

## 7. Padronização e normalização

### StandardScaler

{colunas_padronizadas}

### MinMaxScaler

{colunas_normalizadas}

## 8. Codificação das variáveis categóricas

### OrdinalEncoder

{colunas_ordinais}

### OneHotEncoder

Foram criadas
{resumo_transformacoes['quantidade_one_hot']}
colunas binárias.

## 9. Resultado final

| Informação | Resultado |
|---|---:|
| Registros exportados | {resumo_exportacao['quantidade_linhas']} |
| Colunas exportadas | {resumo_exportacao['quantidade_colunas']} |
| Tamanho do arquivo | {tamanho_arquivo_formatado} KB |

Arquivo gerado: `data/processed/clientes_preparados.csv`.

A base final não contém identificadores pessoais diretos,
valores ausentes ou registros associados a CPFs conflitantes.
"""

    caminho.write_text(
        conteudo.strip() + "\n",
        encoding="utf-8",
    )

    return caminho


def exibir_resumo_finalizacao(
    resumo_exportacao: dict,
    caminho_relatorio: Path,
) -> None:
    """
    Exibe no terminal o resumo da exportação e os caminhos
    dos arquivos produzidos pelo pipeline.
    """
    print("\n" + "=" * 60)
    print("FINALIZAÇÃO DO PIPELINE")
    print("=" * 60)

    print(f"\nRegistros exportados: " f"{resumo_exportacao['quantidade_linhas']}")

    print(f"Colunas exportadas: " f"{resumo_exportacao['quantidade_colunas']}")

    print(f"Tamanho do CSV: " f"{resumo_exportacao['tamanho_kb']:.2f} KB")

    print(f"\nBase preparada:\n" f"{resumo_exportacao['caminho']}")

    print(f"\nRelatório gerado:\n" f"{caminho_relatorio}")

    print("\n" + "=" * 60)
    print("PIPELINE CONCLUÍDO COM SUCESSO")
    print("=" * 60)
