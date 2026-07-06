"""Geração do relatório agregado de qualidade dos dados."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.switch_backend("Agg")

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_BRUTO = BASE_DIR / "data" / "raw" / "clientes.csv"

ARQUIVO_VALIDADO = BASE_DIR / "data" / "processed" / "clientes_validados.csv"

PASTA_FIGURAS = BASE_DIR / "reports" / "figures"

ARQUIVO_RELATORIO = BASE_DIR / "reports" / "relatorio_qualidade.md"

GRAFICO_PROBLEMAS = PASTA_FIGURAS / "problemas_qualidade.png"

GRAFICO_IDADES = PASTA_FIGURAS / "distribuicao_faixas_etarias.png"


def carregar_dados(
    caminho: Path,
    dtype: dict[str, str] | None = None,
) -> pd.DataFrame:
    """Carrega um arquivo CSV."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(
        caminho,
        dtype=dtype,
    )


def normalizar_booleano(
    serie: pd.Series,
) -> pd.Series:
    """Converte uma coluna textual ou booleana para boolean."""

    if pd.api.types.is_bool_dtype(serie):
        return serie.astype("boolean")

    return (
        serie.astype("string")
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
            }
        )
        .astype("boolean")
    )


def calcular_metricas(
    df_bruto: pd.DataFrame,
    df_validado: pd.DataFrame,
) -> dict[str, int | float]:
    """Calcula os principais indicadores de qualidade."""

    cpf_valido = normalizar_booleano(df_validado["cpf_valido"])

    idade_invalida = normalizar_booleano(df_validado["idade_invalida"])

    idade_compativel = normalizar_booleano(df_validado["idade_compativel"])

    estado_consistente = normalizar_booleano(df_validado["estado_consistente"])

    cadastro_incompleto = normalizar_booleano(df_validado["cadastro_incompleto"])

    motivos = (
        df_validado["motivos_inconsistencia"].astype("string").fillna("").str.strip()
    )

    registros_inconsistentes = int(motivos.ne("").sum())

    registros_consistentes = len(df_validado) - registros_inconsistentes

    taxa_consistencia = registros_consistentes / len(df_validado) * 100

    return {
        "registros_iniciais": len(df_bruto),
        "registros_finais": len(df_validado),
        "duplicidades_removidas": (len(df_bruto) - len(df_validado)),
        "valores_nulos_iniciais": int(df_bruto.isnull().sum().sum()),
        "linhas_com_nulos": int(df_bruto.isnull().any(axis=1).sum()),
        "cpfs_invalidos": int(cpf_valido.ne(True).fillna(True).sum()),
        "idades_invalidas": int(idade_invalida.eq(True).fillna(False).sum()),
        "idades_divergentes": int(idade_compativel.eq(False).fillna(False).sum()),
        "estados_divergentes": int(estado_consistente.eq(False).fillna(False).sum()),
        "cadastros_incompletos": int(cadastro_incompleto.eq(True).fillna(False).sum()),
        "registros_inconsistentes": (registros_inconsistentes),
        "registros_consistentes": (registros_consistentes),
        "taxa_consistencia": taxa_consistencia,
    }


def gerar_grafico_problemas(
    metricas: dict[str, int | float],
) -> None:
    """Gera gráfico com os problemas identificados."""

    categorias = [
        "CPF ausente\nou inválido",
        "Idade\ninválida",
        "Idade\ndivergente",
        "UF\ndivergente",
        "Cadastro\nincompleto",
    ]

    valores = [
        metricas["cpfs_invalidos"],
        metricas["idades_invalidas"],
        metricas["idades_divergentes"],
        metricas["estados_divergentes"],
        metricas["cadastros_incompletos"],
    ]

    figura, eixo = plt.subplots(figsize=(10, 6))

    barras = eixo.bar(
        categorias,
        valores,
    )

    eixo.set_title("Problemas de qualidade identificados")

    eixo.set_ylabel("Quantidade de registros")

    eixo.bar_label(
        barras,
        padding=3,
    )

    figura.tight_layout()

    figura.savefig(
        GRAFICO_PROBLEMAS,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figura)


def gerar_grafico_idades(
    df_validado: pd.DataFrame,
) -> None:
    """Gera a distribuição agregada das faixas etárias."""

    idades = pd.to_numeric(
        df_validado["idade_calculada"],
        errors="coerce",
    )

    faixas = pd.cut(
        idades,
        bins=[
            -1,
            17,
            29,
            39,
            49,
            59,
            69,
            79,
            120,
        ],
        labels=[
            "0-17",
            "18-29",
            "30-39",
            "40-49",
            "50-59",
            "60-69",
            "70-79",
            "80+",
        ],
    )

    distribuicao = faixas.value_counts(sort=False)

    figura, eixo = plt.subplots(figsize=(10, 6))

    barras = eixo.bar(
        distribuicao.index.astype(str),
        distribuicao.values,
    )

    eixo.set_title("Distribuição dos clientes por faixa etária")

    eixo.set_xlabel("Faixa etária")

    eixo.set_ylabel("Quantidade de registros")

    eixo.bar_label(
        barras,
        padding=3,
    )

    figura.tight_layout()

    figura.savefig(
        GRAFICO_IDADES,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(figura)


def gerar_relatorio(
    metricas: dict[str, int | float],
) -> str:
    """Produz o relatório final em Markdown."""

    return f"""# Relatório de Qualidade dos Dados

## Visão geral

Este relatório apresenta os resultados agregados do pipeline de
diagnóstico, limpeza, validação e anonimização da base cadastral de
clientes.

Nenhum nome, CPF, endereço ou data de nascimento é apresentado neste
relatório.

## Resultados do pipeline

| Indicador | Resultado |
|---|---:|
| Registros recebidos | {metricas["registros_iniciais"]} |
| Registros após a limpeza | {metricas["registros_finais"]} |
| Duplicidades removidas | {metricas["duplicidades_removidas"]} |
| Valores nulos na base original | {metricas["valores_nulos_iniciais"]} |
| Linhas originalmente incompletas | {metricas["linhas_com_nulos"]} |
| CPFs ausentes ou inválidos | {metricas["cpfs_invalidos"]} |
| Idades fora do intervalo permitido | {metricas["idades_invalidas"]} |
| Idades divergentes da data de nascimento | {metricas["idades_divergentes"]} |
| Divergências entre estado e UF do endereço | {metricas["estados_divergentes"]} |
| Cadastros incompletos | {metricas["cadastros_incompletos"]} |
| Registros com alguma inconsistência | {metricas["registros_inconsistentes"]} |
| Registros sem inconsistências identificadas | {metricas["registros_consistentes"]} |
| Taxa de consistência | {metricas["taxa_consistencia"]:.2f}% |

## Problemas identificados

![Problemas de qualidade](figures/problemas_qualidade.png)

## Distribuição por faixa etária

![Distribuição por faixa etária](figures/distribuicao_faixas_etarias.png)

## Principais conclusões

- Foram removidos registros completamente duplicados.
- Valores de idade fora do intervalo de 0 a 120 anos foram sinalizados.
- Os CPFs foram preservados como texto e tiveram os dígitos verificadores validados.
- A idade foi recalculada usando 4 de abril de 2024 como data de referência da base.
- Divergências entre o estado informado e a UF do endereço foram registradas para auditoria.
- Nenhuma divergência geográfica foi corrigida automaticamente, pois não é possível determinar qual fonte é a correta sem validação externa.
- Foi criada uma amostra anonimizada para demonstração pública.

## Privacidade

Os arquivos originais e processados permanecem fora do controle de
versão. Somente informações agregadas e uma amostra sem dados pessoais
são disponibilizadas publicamente.

[Acessar a amostra anonimizada](../data/sample/clientes_demo.csv)
"""


def main() -> None:
    """Executa a geração do relatório e dos gráficos."""

    df_bruto = carregar_dados(
        ARQUIVO_BRUTO,
        dtype={"cpf": "string"},
    )

    df_validado = carregar_dados(
        ARQUIVO_VALIDADO,
        dtype={"cpf": "string"},
    )

    PASTA_FIGURAS.mkdir(
        parents=True,
        exist_ok=True,
    )

    metricas = calcular_metricas(
        df_bruto,
        df_validado,
    )

    gerar_grafico_problemas(metricas)

    gerar_grafico_idades(df_validado)

    relatorio = gerar_relatorio(metricas)

    ARQUIVO_RELATORIO.write_text(
        relatorio,
        encoding="utf-8",
    )

    print("\nCUSTOMER DATA QUALITY REPORT")
    print("-" * 40)

    print("Registros iniciais: " f"{metricas['registros_iniciais']}")

    print("Registros após a limpeza: " f"{metricas['registros_finais']}")

    print("Registros inconsistentes: " f"{metricas['registros_inconsistentes']}")

    print("Registros consistentes: " f"{metricas['registros_consistentes']}")

    print("Taxa de consistência: " f"{metricas['taxa_consistencia']:.2f}%")

    print("\nRelatório criado em:" f"\n{ARQUIVO_RELATORIO}")

    print("\nGráficos criados em:" f"\n{PASTA_FIGURAS}")


if __name__ == "__main__":
    main()
