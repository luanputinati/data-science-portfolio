"""Diagnóstico inicial da base cadastral de clientes."""

from pathlib import Path

import pandas as pd

# Localiza automaticamente a pasta 02-Data-Treatment.
BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = BASE_DIR / "data" / "raw" / "clientes.csv"
ARQUIVO_RELATORIO = BASE_DIR / "reports" / "diagnostico_inicial.md"


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega o arquivo CSV e retorna um DataFrame."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(caminho)


def gerar_relatorio(df: pd.DataFrame) -> str:
    """Gera um relatório de qualidade em formato Markdown."""

    quantidade_linhas, quantidade_colunas = df.shape

    nulos_por_coluna = df.isnull().sum()
    total_nulos = int(nulos_por_coluna.sum())

    linhas_com_nulos = int(df.isnull().any(axis=1).sum())

    duplicadas = int(df.duplicated().sum())

    tabela_nulos = "\n".join(
        f"| {coluna} | {int(quantidade)} |"
        for coluna, quantidade in nulos_por_coluna.items()
    )

    tabela_tipos = "\n".join(
        f"| {coluna} | {tipo} |" for coluna, tipo in df.dtypes.items()
    )

    estatisticas_idade = df["idade"].describe()

    relatorio = f"""# Diagnóstico inicial da base de clientes

## Visão geral

| Indicador | Resultado |
|---|---:|
| Registros | {quantidade_linhas} |
| Colunas | {quantidade_colunas} |
| Valores nulos | {total_nulos} |
| Linhas com algum valor nulo | {linhas_com_nulos} |
| Linhas completamente duplicadas | {duplicadas} |

## Tipos de dados

| Coluna | Tipo |
|---|---|
{tabela_tipos}

## Valores nulos por coluna

| Coluna | Valores nulos |
|---|---:|
{tabela_nulos}

## Estatísticas da coluna idade

| Estatística | Valor |
|---|---:|
| Quantidade | {estatisticas_idade["count"]:.0f} |
| Média | {estatisticas_idade["mean"]:.2f} |
| Desvio padrão | {estatisticas_idade["std"]:.2f} |
| Mínimo | {estatisticas_idade["min"]:.0f} |
| Primeiro quartil | {estatisticas_idade["25%"]:.0f} |
| Mediana | {estatisticas_idade["50%"]:.0f} |
| Terceiro quartil | {estatisticas_idade["75%"]:.0f} |
| Máximo | {estatisticas_idade["max"]:.0f} |

## Observação de privacidade

O arquivo original contém dados cadastrais e não deve ser publicado.
Os arquivos disponibilizados publicamente serão previamente anonimizados.
"""

    return relatorio


def main() -> None:
    """Executa o diagnóstico inicial."""

    df = carregar_dados(ARQUIVO_ENTRADA)

    print("\nCUSTOMER DATA QUALITY PIPELINE")
    print("-" * 40)

    print("\nPrimeiras cinco linhas:")
    print(df.head())

    print("\nÚltimas cinco linhas:")
    print(df.tail())

    print("\nInformações estruturais:")
    df.info()

    total_nulos = int(df.isnull().sum().sum())
    linhas_com_nulos = int(df.isnull().any(axis=1).sum())
    duplicadas = int(df.duplicated().sum())

    print("\nResumo do diagnóstico:")
    print(f"Registros: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")
    print(f"Valores nulos: {total_nulos}")
    print(f"Linhas com valores nulos: {linhas_com_nulos}")
    print(f"Linhas duplicadas: {duplicadas}")

    relatorio = gerar_relatorio(df)

    ARQUIVO_RELATORIO.parent.mkdir(parents=True, exist_ok=True)

    ARQUIVO_RELATORIO.write_text(relatorio, encoding="utf-8")

    print("\nRelatório criado em:" f"\n{ARQUIVO_RELATORIO}")


if __name__ == "__main__":
    main()
