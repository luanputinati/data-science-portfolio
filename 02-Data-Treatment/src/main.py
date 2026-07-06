"""Ponto de entrada do Customer Data Quality Pipeline."""

from collections.abc import Callable
from time import perf_counter
from typing import Final

from anonymization import main as executar_anonimizacao
from cleaning import main as executar_limpeza
from diagnostico_inicial import main as executar_diagnostico
from reporting import main as executar_relatorio
from validation import main as executar_validacao

Etapa = tuple[str, Callable[[], None]]

ETAPAS: Final[tuple[Etapa, ...]] = (
    ("Diagnóstico inicial", executar_diagnostico),
    ("Limpeza e padronização", executar_limpeza),
    ("Validação dos dados", executar_validacao),
    ("Anonimização", executar_anonimizacao),
    ("Relatório de qualidade", executar_relatorio),
)


def executar_etapa(
    numero: int,
    total: int,
    nome: str,
    funcao: Callable[[], None],
) -> None:
    """Executa uma etapa e informa seu tempo de processamento."""

    print("\n" + "=" * 60)
    print(f"ETAPA {numero}/{total}: {nome.upper()}")
    print("=" * 60)

    inicio = perf_counter()

    funcao()

    duracao = perf_counter() - inicio

    print(f"\nEtapa concluída em {duracao:.2f} segundo(s).")


def main() -> None:
    """Executa todas as etapas do pipeline."""

    inicio_pipeline = perf_counter()
    total_etapas = len(ETAPAS)

    print("\nCUSTOMER DATA QUALITY PIPELINE")
    print("=" * 60)
    print("Diagnóstico, limpeza, validação, anonimização " "e geração de relatórios.")

    try:
        for numero, (nome, funcao) in enumerate(
            ETAPAS,
            start=1,
        ):
            executar_etapa(
                numero=numero,
                total=total_etapas,
                nome=nome,
                funcao=funcao,
            )

    except (
        FileNotFoundError,
        KeyError,
        TypeError,
        ValueError,
    ) as erro:
        print("\n" + "!" * 60)
        print("O PIPELINE FOI INTERROMPIDO")
        print("!" * 60)
        print(f"Motivo: {erro}")

        raise SystemExit(1) from erro

    duracao_total = perf_counter() - inicio_pipeline

    print("\n" + "=" * 60)
    print("PIPELINE CONCLUÍDO COM SUCESSO")
    print("=" * 60)
    print(f"Etapas executadas: {total_etapas}")
    print("Tempo total: " f"{duracao_total:.2f} segundo(s)")

    print(
        "\nPrincipais resultados:"
        "\n- reports/diagnostico_inicial.md"
        "\n- reports/relatorio_qualidade.md"
        "\n- reports/figures/"
        "\n- data/sample/clientes_demo.csv"
    )


if __name__ == "__main__":
    main()
