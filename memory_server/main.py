"""Entry point for plyra-memory-server."""

import uvicorn
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import ServerConfig
from .router import build_app

console = Console()


def run():
    config = ServerConfig.default()
    app = build_app(config)

    console.print(
        Panel(
            Text.assemble(
                ("plyra-memory-server\n", "bold #818cf8"),
                ("version:  0.1.0\n", "dim"),
                (f"env:      {config.env}\n", "dim"),
                (f"store:    {config.store_url}\n", "dim"),
                (f"vectors:  {config.vectors_url}\n", "dim"),
                (f"keys db:  {config.key_store_url}\n", "dim"),
                (f"server:   http://{config.host}:{config.port}\n", "green"),
                ("\nAdmin key set: ",),
                (
                    "yes\n"
                    if config.admin_api_key != "plm_admin_changeme"
                    else "⚠ using default — change PLYRA_ADMIN_API_KEY\n",
                    "yellow",
                ),
            ),
            box=box.SIMPLE,
            border_style="#818cf8",
        )
    )

    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level="warning" if not config.debug else "info",
    )


if __name__ == "__main__":
    run()
