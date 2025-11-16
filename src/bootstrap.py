from src.application import Application


def bootstrap() -> Application:
    return Application(config=config)
