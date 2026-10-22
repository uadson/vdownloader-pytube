"""Ponto de entrada da aplicação vdownloader."""

import sys
import uvicorn


def main() -> None:
    """Executa a aplicação web FastAPI ou CLI legada conforme argumentos."""
    if "--cli" in sys.argv:
        from vdownloader.cli import main as cli_main

        cli_main()
    else:
        uvicorn.run("vdownloader.api.app:app", host="0.0.0.0", port=8088, reload=False)


if __name__ == "__main__":
    main()
