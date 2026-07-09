from pathlib import Path

import pandas as pd
from src.data_preparation import (
    carregar_dados,
    criar_features,
    desidentificar_dados,
    exibir_diagnostico,
    exibir_resumo_desidentificacao,
    exibir_resumo_features,
    exibir_resumo_finalizacao,
    exibir_resumo_transformacoes,
    exibir_resumo_valores_ausentes,
    exibir_validacoes_consistencia,
    exportar_dados,
    gerar_diagnostico_inicial,
    gerar_relatorio_preparacao,
    gerar_validacoes_consistencia,
    organizar_colunas,
    transformar_variaveis,
    tratar_valores_ausentes,
)


def validar_condicao(
    condicao: bool,
    mensagem: str,
) -> None:
    """
    Interrompe o pipeline quando uma validação não é atendida.
    """
    if not condicao:
        raise ValueError(f"Falha de validação: {mensagem}")


def validar_desidentificacao(
    df: pd.DataFrame,
) -> None:
    """
    Verifica a remoção dos identificadores pessoais.
    """
    colunas_pessoais = {
        "nome",
        "cpf",
        "data",
        "endereco",
        "pais",
    }

    validar_condicao(
        colunas_pessoais.isdisjoint(df.columns),
        "a base ainda contém colunas pessoais ou identificadoras.",
    )

    validar_condicao(
        "cliente_id" in df.columns,
        "a coluna cliente_id não foi criada.",
    )

    validar_condicao(
        bool(df["cliente_id"].is_unique),
        "a coluna cliente_id possui valores duplicados.",
    )

    validar_condicao(
        bool(df["cliente_id"].notna().all()),
        "a coluna cliente_id possui valores ausentes.",
    )


def validar_base_sem_nulos(
    df: pd.DataFrame,
    etapa: str,
) -> None:
    """
    Verifica se o DataFrame contém valores ausentes.
    """
    quantidade_nulos = int(df.isna().sum().sum())

    validar_condicao(
        quantidade_nulos == 0,
        (f"a etapa '{etapa}' terminou com " f"{quantidade_nulos} valores ausentes."),
    )


def validar_engenharia_features(
    df: pd.DataFrame,
) -> None:
    """
    Valida as variáveis criadas pela engenharia de features.
    """
    features_esperadas = {
        "faixa_etaria",
        "faixa_experiencia",
        "salario_anual",
        "tem_filhos",
        "idade_inicio_carreira",
    }

    features_ausentes = features_esperadas - set(df.columns)

    validar_condicao(
        not features_ausentes,
        (
            "as seguintes features não foram criadas: "
            + ", ".join(sorted(features_ausentes))
        ),
    )

    validar_base_sem_nulos(
        df,
        "engenharia de features",
    )

    validar_condicao(
        bool(df["tem_filhos"].isin([0, 1]).all()),
        "a coluna tem_filhos contém valores diferentes de 0 e 1.",
    )

    salario_anual_esperado = (df["salario"] * 12).round(2)

    validar_condicao(
        bool(df["salario_anual"].eq(salario_anual_esperado).all()),
        "a coluna salario_anual não corresponde a salario multiplicado por 12.",
    )


def validar_transformacoes(
    df: pd.DataFrame,
    quantidade_registros_esperada: int,
) -> None:
    """
    Valida normalização, codificação e preservação dos registros.
    """
    colunas_minmax = [
        "idade_minmax",
        "numero_filhos_minmax",
        "idade_inicio_carreira_minmax",
    ]

    for coluna in colunas_minmax:
        validar_condicao(
            coluna in df.columns,
            f"a coluna normalizada {coluna} não foi criada.",
        )

        validar_condicao(
            bool(df[coluna].min() >= -1e-9),
            f"a coluna {coluna} possui valor inferior a zero.",
        )

        validar_condicao(
            bool(df[coluna].max() <= 1 + 1e-9),
            f"a coluna {coluna} possui valor superior a um.",
        )

    colunas_ordinais = [
        "nivel_educacao_ord",
        "faixa_etaria_ord",
        "faixa_experiencia_ord",
    ]

    for coluna in colunas_ordinais:
        validar_condicao(
            coluna in df.columns,
            f"a coluna ordinal {coluna} não foi criada.",
        )

        validar_condicao(
            bool(df[coluna].ge(0).all()),
            f"a coluna {coluna} possui códigos negativos.",
        )

    validar_base_sem_nulos(
        df,
        "transformação das variáveis",
    )

    validar_condicao(
        "salario_anual_std" not in df.columns,
        "a coluna redundante salario_anual_std foi criada.",
    )

    validar_condicao(
        len(df) == quantidade_registros_esperada,
        "a transformação alterou a quantidade de registros.",
    )


def validar_exportacao(
    resumo_exportacao: dict,
    df_final: pd.DataFrame,
    caminho_relatorio: Path,
) -> None:
    """
    Valida os arquivos e as dimensões do resultado final.
    """
    validar_condicao(
        resumo_exportacao["quantidade_linhas"] == len(df_final),
        "a quantidade de linhas exportadas está incorreta.",
    )

    validar_condicao(
        resumo_exportacao["quantidade_colunas"] == df_final.shape[1],
        "a quantidade de colunas exportadas está incorreta.",
    )

    validar_condicao(
        resumo_exportacao["caminho"].exists(),
        "o arquivo CSV preparado não foi criado.",
    )

    validar_condicao(
        caminho_relatorio.exists(),
        "o relatório de preparação não foi criado.",
    )


def executar_pipeline() -> None:
    """
    Executa todas as etapas de preparação dos dados.
    """
    # 1. Carregamento e diagnóstico
    df = carregar_dados()

    diagnostico = gerar_diagnostico_inicial(df)
    exibir_diagnostico(diagnostico)

    # 2. Validações de consistência
    validacoes = gerar_validacoes_consistencia(df)
    exibir_validacoes_consistencia(validacoes)

    # 3. Desidentificação
    df_desidentificado, resumo_desidentificacao = desidentificar_dados(df)

    exibir_resumo_desidentificacao(resumo_desidentificacao)

    validar_desidentificacao(df_desidentificado)

    # 4. Tratamento de valores ausentes
    df_tratado, resumo_valores_ausentes = tratar_valores_ausentes(df_desidentificado)

    exibir_resumo_valores_ausentes(resumo_valores_ausentes)

    validar_base_sem_nulos(
        df_tratado,
        "tratamento de valores ausentes",
    )

    # 5. Engenharia de features
    df_features, resumo_features = criar_features(df_tratado)

    exibir_resumo_features(resumo_features)
    validar_engenharia_features(df_features)

    # 6. Transformação das variáveis
    df_transformado, resumo_transformacoes = transformar_variaveis(df_features)

    exibir_resumo_transformacoes(resumo_transformacoes)

    validar_transformacoes(
        df_transformado,
        quantidade_registros_esperada=len(df_features),
    )

    # 7. Organização e exportação
    df_final = organizar_colunas(df_transformado)
    resumo_exportacao = exportar_dados(df_final)

    # 8. Relatório final
    caminho_relatorio = gerar_relatorio_preparacao(
        diagnostico=diagnostico,
        validacoes=validacoes,
        resumo_desidentificacao=resumo_desidentificacao,
        resumo_valores_ausentes=resumo_valores_ausentes,
        resumo_features=resumo_features,
        resumo_transformacoes=resumo_transformacoes,
        resumo_exportacao=resumo_exportacao,
    )

    validar_exportacao(
        resumo_exportacao,
        df_final,
        caminho_relatorio,
    )

    exibir_resumo_finalizacao(
        resumo_exportacao,
        caminho_relatorio,
    )


def main() -> int:
    """
    Controla a execução do pipeline e o tratamento de erros.
    """
    try:
        executar_pipeline()
        return 0

    except (ValueError, OSError) as erro:
        print(f"\nErro ao executar o pipeline: {erro}")
        return 1

    except Exception as erro:
        print(f"\nErro inesperado " f"({type(erro).__name__}): {erro}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
