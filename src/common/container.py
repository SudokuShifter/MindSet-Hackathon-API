from dishka import Scope, Container, Provider, provide, make_container

from src.common.database.postgres import Postgres
from src.repositories.user_repository import UserRepository
from src.services.auth_service import AuthService
