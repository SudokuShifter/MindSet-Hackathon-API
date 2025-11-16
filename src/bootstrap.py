from src.application import Application
from src.common.container import create_container
from src.interfaces.router import BaseRouter


def bootstrap() -> Application:
    container = create_container()
    routers = container.get(list[BaseRouter])

    return Application(container=container, routers=routers)
