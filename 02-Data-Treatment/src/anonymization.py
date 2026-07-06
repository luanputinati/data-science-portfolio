"""Geração de uma amostra pública e anonimizada dos dados."""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

ARQUIVO_ENTRADA = BASE_DIR / "data" / "processed" / "clientes_validados.csv"

ARQUIVO_SAIDA = BASE_DIR / "data" / "sample" / "clientes_demo.csv"

TAMANHO_AMOSTRA = 100

COLUNAS_SENSIVEIS = {
    "nome",
    "cpf",
    "data",
    "data_nascimento",
    "endereco",
    "idade",
    "idade_original",
    "idade_calculada",
}


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega a base validada."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(
        caminho,
        dtype={"cpf": "string"},
    )


def criar_faixa_etaria(
    idades: pd.Series,
) -> pd.Series:
    """Agrupa as idades em faixas para reduzir identificação."""

    idades_numericas = pd.to_numeric(
        idades,
        errors="coerce",
    )

    faixas = pd.cut(
        idades_numericas,
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

    return faixas.astype("string").fillna("Não informado")


def anonimizar_dados(
    df: pd.DataFrame,
    tamanho_amostra: int = TAMANHO_AMOSTRA,
) -> pd.DataFrame:
    """Remove informações pessoais e gera uma amostra pública."""

    df_publico = pd.DataFrame(index=df.index)

    df_publico["faixa_etaria"] = criar_faixa_etaria(df["idade_calculada"])

    df_publico["estado_uf"] = df["estado_uf"].astype("string").fillna("Não informado")

    df_publico["uf_endereco"] = (
        df["uf_endereco"].astype("string").fillna("Não informado")
    )

    df_publico["pais"] = df["pais"].astype("string").fillna("Não informado")

    colunas_qualidade = [
        "cpf_valido",
        "idade_invalida",
        "idade_compativel",
        "estado_consistente",
        "cadastro_incompleto",
    ]

    for coluna in colunas_qualidade:
        df_publico[coluna] = df[coluna]

    df_publico["motivos_inconsistencia"] = (
        df["motivos_inconsistencia"]
        .astype("string")
        .fillna("Nenhuma inconsistência")
        .replace("", "Nenhuma inconsistência")
    )

    quantidade = min(
        tamanho_amostra,
        len(df_publico),
    )

    amostra = df_publico.sample(
        n=quantidade,
        random_state=42,
    ).reset_index(drop=True)

    amostra.insert(
        0,
        "cliente_id",
        [
            f"CLI-{numero:04d}"
            for numero in range(
                1,
                len(amostra) + 1,
            )
        ],
    )

    return amostra


def validar_anonimizacao(
    df_publico: pd.DataFrame,
) -> None:
    """Impede a exportação de colunas sensíveis."""

    colunas_encontradas = COLUNAS_SENSIVEIS.intersection(df_publico.columns)

    if colunas_encontradas:
        raise ValueError(
            "A amostra ainda contém colunas sensíveis: "
            f"{sorted(colunas_encontradas)}"
        )

    if df_publico["cliente_id"].duplicated().any():
        raise ValueError("Foram encontrados identificadores duplicados.")


def salvar_amostra(
    df: pd.DataFrame,
    caminho: Path,
) -> None:
    """Salva a amostra anonimizada."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig",
    )


def main() -> None:
    """Executa a anonimização dos dados."""

    df = carregar_dados(ARQUIVO_ENTRADA)

    amostra_publica = anonimizar_dados(df)

    validar_anonimizacao(amostra_publica)

    salvar_amostra(
        amostra_publica,
        ARQUIVO_SAIDA,
    )

    print("\nCUSTOMER DATA ANONYMIZATION")
    print("-" * 40)
    print(f"Registros da base validada: {len(df)}")
    print("Registros da amostra pública: " f"{len(amostra_publica)}")
    print("Colunas sensíveis publicadas: 0")

    print("\nAmostra pública criada em:" f"\n{ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
