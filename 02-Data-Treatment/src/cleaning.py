"""Pipeline de limpeza da base cadastral de clientes."""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = BASE_DIR / "data" / "raw" / "clientes.csv"
ARQUIVO_SAIDA = BASE_DIR / "data" / "processed" / "clientes_tratados.csv"


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega a base bruta de clientes."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(caminho, dtype={"cpf": "string"})


def normalizar_texto(serie: pd.Series) -> pd.Series:
    """Remove espaços extras de uma coluna textual."""

    return (
        serie.astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .replace("", pd.NA)
    )


def limpar_dados(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, int]:
    """Aplica as regras iniciais de limpeza."""

    df_limpo = df.copy()

    quantidade_original = len(df_limpo)

    # Remove linhas completamente duplicadas.
    df_limpo = df_limpo.drop_duplicates().reset_index(drop=True)

    duplicadas_removidas = quantidade_original - len(df_limpo)

    # Padroniza o nome.
    df_limpo["nome"] = normalizar_texto(df_limpo["nome"]).str.title()

    # Mantém o CPF como texto e remove pontuação.
    df_limpo["cpf"] = (
        df_limpo["cpf"]
        .astype("string")
        .str.replace(r"\D", "", regex=True)
        .replace("", pd.NA)
    )

    # Preserva a idade recebida na base original.
    df_limpo["idade_original"] = pd.to_numeric(
        df_limpo["idade"], errors="coerce"
    ).astype("Int64")

    # Considera válida uma idade entre 0 e 120 anos.
    idade_valida = df_limpo["idade_original"].between(0, 120).fillna(False)

    df_limpo["idade_invalida"] = ~idade_valida

    # Valores inválidos tornam-se ausentes na coluna tratada.
    df_limpo["idade"] = df_limpo["idade_original"].where(idade_valida).astype("Int64")

    # Converte a data para o tipo datetime.
    df_limpo["data_nascimento"] = pd.to_datetime(
        df_limpo["data"], format="%d/%m/%Y", errors="coerce"
    )

    # Padroniza os endereços em uma única linha.
    df_limpo["endereco"] = normalizar_texto(df_limpo["endereco"])

    # Padroniza estado e país.
    df_limpo["estado"] = normalizar_texto(df_limpo["estado"]).str.upper()

    df_limpo["pais"] = normalizar_texto(df_limpo["pais"]).str.title()

    # Nome, CPF e data de nascimento são considerados
    # campos críticos para este projeto.
    df_limpo["cadastro_incompleto"] = (
        df_limpo[["nome", "cpf", "data_nascimento"]].isnull().any(axis=1)
    )

    return df_limpo, duplicadas_removidas


def salvar_dados(df: pd.DataFrame, caminho: Path) -> None:
    """Salva a base tratada em formato CSV."""

    caminho.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(caminho, index=False, encoding="utf-8-sig")


def main() -> None:
    """Executa o pipeline de limpeza."""

    df = carregar_dados(ARQUIVO_ENTRADA)

    df_limpo, duplicadas_removidas = limpar_dados(df)

    salvar_dados(df_limpo, ARQUIVO_SAIDA)

    idades_invalidas = int(df_limpo["idade_invalida"].sum())

    cadastros_incompletos = int(df_limpo["cadastro_incompleto"].sum())

    print("\nCUSTOMER DATA QUALITY PIPELINE")
    print("-" * 40)

    print(f"Registros recebidos: {len(df)}")
    print("Duplicidades removidas: " f"{duplicadas_removidas}")
    print("Registros após a limpeza: " f"{len(df_limpo)}")
    print("Idades inválidas identificadas: " f"{idades_invalidas}")
    print("Cadastros incompletos: " f"{cadastros_incompletos}")

    print("\nArquivo tratado criado em:" f"\n{ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
