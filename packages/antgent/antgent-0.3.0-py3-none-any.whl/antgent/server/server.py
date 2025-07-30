from typing import ClassVar

from ant31box.server.server import Server, serve_from_config
from fastapi import FastAPI

from antgent.config import config


class AntgentServer(Server):
    _routers: ClassVar[set[str]] = {
        "antgent.server.api.job_info:router",
    }
    _middlewares: ClassVar[set[str]] = {"tokenAuth"}


# override this method to use a different server class/config
def serve() -> FastAPI:
    return serve_from_config(config(), AntgentServer)
