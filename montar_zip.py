"""
montar_zip.py - Monta o Arquivo 2 da entrega (.zip com DER, script SQL e código).

Como usar (na pasta raiz do projeto):
    python montar_zip.py

O arquivo é criado em dist/grupo3-iaad_entrega.zip. Ele leva só o que a
professora precisa para rodar o sistema: o arquivo .env (com a senha), a
pasta .venv e os arquivos __pycache__ ficam de fora.
"""

import sys
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DESTINO = RAIZ / "dist" / "grupo3-iaad_entrega.zip"
PASTA_NO_ZIP = "grupo3-iaad"  # ao extrair, tudo fica dentro desta pasta

# Pastas e arquivos que entram no .zip
PASTAS = ["banco", "app", "nosql", ".streamlit"]
ARQUIVOS = ["README.md", "requirements.txt", ".env.example", "montar_zip.py"]

# Nunca entram (senha, ambiente virtual, arquivos gerados)
IGNORAR_PASTAS = {"__pycache__", ".venv", "venv", ".git"}
IGNORAR_ARQUIVOS = {".env"}
IGNORAR_EXTENSOES = {".pyc", ".pyo", ".bak", ".mwb.bak"}


def deve_entrar(caminho):
    partes = set(caminho.relative_to(RAIZ).parts)
    if partes & IGNORAR_PASTAS:
        return False
    if caminho.name in IGNORAR_ARQUIVOS:
        return False
    return not any(caminho.name.endswith(ext) for ext in IGNORAR_EXTENSOES)


def listar_arquivos():
    arquivos = []
    for pasta in PASTAS:
        arquivos += [p for p in sorted((RAIZ / pasta).rglob("*"))
                     if p.is_file() and deve_entrar(p)]
    for nome in ARQUIVOS:
        caminho = RAIZ / nome
        if caminho.is_file():
            arquivos.append(caminho)
        else:
            print(f"AVISO: {nome} não encontrado.")
    return arquivos


def main():
    arquivos = listar_arquivos()

    # O DER do Workbench é obrigatório na entrega: avisamos se ainda faltar
    tem_der = any(p.suffix == ".mwb" for p in arquivos)
    tem_sql = any(p.suffix == ".sql" for p in arquivos)
    if not tem_sql:
        print("ERRO: nenhum script .sql em banco/. O .zip não foi criado.")
        sys.exit(1)

    DESTINO.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(DESTINO, "w", zipfile.ZIP_DEFLATED) as zipado:
        for caminho in arquivos:
            nome = Path(PASTA_NO_ZIP) / caminho.relative_to(RAIZ)
            zipado.write(caminho, nome.as_posix())

    print(f"Criado: {DESTINO.relative_to(RAIZ)} ({len(arquivos)} arquivos)")
    for caminho in arquivos:
        print("  -", caminho.relative_to(RAIZ).as_posix())
    if not tem_der:
        print("\nATENÇÃO: falta o DER do Workbench (.mwb) na pasta banco/. "
              "Salve o arquivo lá e rode este script de novo antes de entregar.")


if __name__ == "__main__":
    main()
