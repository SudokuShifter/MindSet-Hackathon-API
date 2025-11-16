from src.common.database.postgres import Postgres


class ExampleRepository:
    def __init__(self, conn: Postgres):
        self._session = conn
