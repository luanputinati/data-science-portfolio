"""Validação da qualidade da base cadastral de clientes."""

import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_REFERENCIA = pd.Timestamp("2024-04-04")

ARQUIVO_ENTRADA = BASE_DIR / "data" / "processed" / "clientes_tratados.csv"

ARQUIVO_VALIDADO = BASE_DIR / "data" / "processed" / "clientes_validados.csv"

ARQUIVO_INCONSISTENCIAS = (
    BASE_DIR / "data" / "processed" / "registros_inconsistentes.csv"
)

UF_POR_ESTADO = {
    "ACRE": "AC",
    "ALAGOAS": "AL",
    "AMAPÁ": "AP",
    "AMAZONAS": "AM",
    "BAHIA": "BA",
    "CEARÁ": "CE",
    "DISTRITO FEDERAL": "DF",
    "ESPÍRITO SANTO": "ES",
    "GOIÁS": "GO",
    "MARANHÃO": "MA",
    "MATO GROSSO": "MT",
    "MATO GROSSO DO SUL": "MS",
    "MINAS GERAIS": "MG",
    "PARÁ": "PA",
    "PARAÍBA": "PB",
    "PARANÁ": "PR",
    "PERNAMBUCO": "PE",
    "PIAUÍ": "PI",
    "RIO DE JANEIRO": "RJ",
    "RIO GRANDE DO NORTE": "RN",
    "RIO GRANDE DO SUL": "RS",
    "RONDÔNIA": "RO",
    "RORAIMA": "RR",
    "SANTA CATARINA": "SC",
    "SÃO PAULO": "SP",
    "SERGIPE": "SE",
    "TOCANTINS": "TO",
}


def carregar_dados(caminho: Path) -> pd.DataFrame:
    """Carrega a base tratada preservando o CPF como texto."""

    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    return pd.read_csv(
        caminho,
        dtype={
            "cpf": "string",
            "estado": "string",
            "endereco": "string",
        },
    )


def validar_cpf(valor: object) -> bool:
    """Valida os dígitos verificadores de um CPF."""

    if pd.isna(valor):
        return False

    cpf = re.sub(r"\D", "", str(valor))

    if len(cpf) != 11:
        return False

    # CPFs formados por um único algarismo são inválidos.
    if cpf == cpf[0] * 11:
        return False

    numeros = [int(digito) for digito in cpf]

    soma_primeiro = sum(numeros[indice] * (10 - indice) for indice in range(9))

    primeiro_digito = (soma_primeiro * 10) % 11

    if primeiro_digito == 10:
        primeiro_digito = 0

    soma_segundo = sum(numeros[indice] * (11 - indice) for indice in range(10))

    segundo_digito = (soma_segundo * 10) % 11

    if segundo_digito == 10:
        segundo_digito = 0

    return numeros[9] == primeiro_digito and numeros[10] == segundo_digito


def calcular_idade(
    datas_nascimento: pd.Series,
) -> pd.Series:
    """Calcula a idade com base na data atual."""

    hoje = DATA_REFERENCIA

    idades = pd.Series(
        pd.NA,
        index=datas_nascimento.index,
        dtype="Int64",
    )

    datas_validas = datas_nascimento.notna()
    nascimentos = datas_nascimento.loc[datas_validas]

    ainda_nao_fez_aniversario = (
        (nascimentos.dt.month > hoje.month)
        | ((nascimentos.dt.month == hoje.month) & (nascimentos.dt.day > hoje.day))
    ).astype(int)

    idades.loc[datas_validas] = (
        hoje.year - nascimentos.dt.year - ainda_nao_fez_aniversario
    ).astype("Int64")

    return idades


def extrair_uf_endereco(
    enderecos: pd.Series,
) -> pd.Series:
    """Extrai a UF localizada no final do endereço."""

    return (
        enderecos.astype("string")
        .str.extract(
            r"/\s*([A-Za-z]{2})\s*$",
            expand=False,
        )
        .str.upper()
    )


def gerar_motivos_inconsistencia(
    linha: pd.Series,
) -> str:
    """Descreve os problemas encontrados em um registro."""

    motivos: list[str] = []

    if not bool(linha["cpf_valido"]):
        motivos.append("CPF ausente ou inválido")

    if pd.isna(linha["data_nascimento"]):
        motivos.append("Data de nascimento ausente ou inválida")

    if bool(linha["idade_invalida"]):
        motivos.append("Idade fora do intervalo permitido")

    if pd.notna(linha["idade_compativel"]) and not bool(linha["idade_compativel"]):
        motivos.append("Idade informada diverge da data de nascimento")

    if pd.notna(linha["estado_consistente"]) and not bool(linha["estado_consistente"]):
        motivos.append("Estado informado diverge da UF do endereço")

    if bool(linha["cadastro_incompleto"]):
        motivos.append("Cadastro incompleto")

    return " | ".join(motivos)


def validar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica as regras de validação cadastral."""

    df_validado = df.copy()

    df_validado["cpf_valido"] = df_validado["cpf"].apply(validar_cpf).astype("boolean")

    df_validado["data_nascimento"] = pd.to_datetime(
        df_validado["data_nascimento"],
        errors="coerce",
    )

    df_validado["idade_calculada"] = calcular_idade(df_validado["data_nascimento"])

    df_validado["idade_original"] = pd.to_numeric(
        df_validado["idade_original"],
        errors="coerce",
    ).astype("Int64")

    df_validado["idade_compativel"] = pd.Series(
        pd.NA,
        index=df_validado.index,
        dtype="boolean",
    )

    possui_idades_comparaveis = (
        df_validado["idade_original"].notna() & df_validado["idade_calculada"].notna()
    )

    diferenca_idades = (
        df_validado["idade_original"] - df_validado["idade_calculada"]
    ).abs()

    # Aceita diferença de até um ano por causa da data
    # em que a informação original foi produzida.
    df_validado.loc[
        possui_idades_comparaveis,
        "idade_compativel",
    ] = (
        diferenca_idades.loc[possui_idades_comparaveis] <= 1
    )

    df_validado["uf_endereco"] = extrair_uf_endereco(df_validado["endereco"])
    df_validado["estado_uf"] = (
        df_validado["estado"]
        .astype("string")
        .str.strip()
        .str.upper()
        .map(UF_POR_ESTADO)
    )

    df_validado["estado_consistente"] = pd.Series(
        pd.NA,
        index=df_validado.index,
        dtype="boolean",
    )

    possui_estado_e_uf = (
        df_validado["estado_uf"].notna() & df_validado["uf_endereco"].notna()
    )

    df_validado.loc[
        possui_estado_e_uf,
        "estado_consistente",
    ] = (
        df_validado.loc[
            possui_estado_e_uf,
            "estado_uf",
        ]
        == df_validado.loc[
            possui_estado_e_uf,
            "uf_endereco",
        ]
    )

    df_validado["motivos_inconsistencia"] = df_validado.apply(
        gerar_motivos_inconsistencia,
        axis=1,
    )

    return df_validado


def salvar_dados(
    df: pd.DataFrame,
    caminho: Path,
) -> None:
    """Salva um DataFrame em CSV."""

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
    """Executa a validação dos dados."""

    df = carregar_dados(ARQUIVO_ENTRADA)

    df_validado = validar_dados(df)

    registros_inconsistentes = df_validado[
        df_validado["motivos_inconsistencia"] != ""
    ].copy()

    salvar_dados(
        df_validado,
        ARQUIVO_VALIDADO,
    )

    salvar_dados(
        registros_inconsistentes,
        ARQUIVO_INCONSISTENCIAS,
    )

    cpfs_invalidos = int((~df_validado["cpf_valido"]).sum())

    idades_divergentes = int((df_validado["idade_compativel"] == False).sum())

    estados_divergentes = int((df_validado["estado_consistente"] == False).sum())

    print("\nCUSTOMER DATA VALIDATION")
    print("-" * 40)
    print(f"Registros analisados: {len(df_validado)}")
    print(f"CPFs ausentes ou inválidos: {cpfs_invalidos}")
    print("Idades incompatíveis com a data: " f"{idades_divergentes}")
    print("Divergências entre estado e endereço: " f"{estados_divergentes}")
    print("Registros com alguma inconsistência: " f"{len(registros_inconsistentes)}")

    print("\nBase validada criada em:" f"\n{ARQUIVO_VALIDADO}")

    print("\nRelatório de inconsistências criado em:" f"\n{ARQUIVO_INCONSISTENCIAS}")


if __name__ == "__main__":
    main()
