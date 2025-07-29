from gettext import GNUTranslations
from typing import Annotated, List

from fastapi.params import Depends
from sqlmodel import Session

from one_public_api.core import get_session
from one_public_api.core.exceptions import DataError
from one_public_api.core.i18n import get_translator
from one_public_api.models import User
from one_public_api.services.base_service import BaseService


class UserService(BaseService[User]):
    search_columns: List[str] = ["name", "firstname", "lastname", "nickname", "email"]
    model = User

    def __init__(
        self,
        session: Annotated[Session, Depends(get_session)],
        translator: Annotated[GNUTranslations, Depends(get_translator)],
    ):
        super().__init__(session, translator)

    def add_one(self, data: User) -> User:
        try:
            return super().add_one(data)
        except DataError:
            del data.password
            raise DataError(
                self._("Data already exists."), data.model_dump_json(), "E40900003"
            )
