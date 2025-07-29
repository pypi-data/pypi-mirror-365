from enum import IntEnum
from typing import Any, Dict
from uuid import UUID

from sqlalchemy import Enum as SQLEnum
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from one_public_api.common import constants
from one_public_api.core.i18n import translate as _
from one_public_api.models.mixins.id_mixin import IdMixin
from one_public_api.models.mixins.maintenance_mixin import MaintenanceMixin
from one_public_api.models.mixins.timestamp_mixin import TimestampMixin
from one_public_api.models.system.user_model import User


class ConfigurationType(IntEnum):
    """
    Enumeration for different configuration types.

    Attributes
    ----------
    OTHER : int
        Represents undefined or unclassified configuration.
    SYS : int
        Represents system-related configuration.
    API : int
        Represents API-related configuration.
    UI : int
        Represents UI-related configuration.
    """

    OTHER = 0
    SYS = 1
    API = 2
    UI = 3


class ConfigurationBase(SQLModel):
    name: str | None = Field(
        default=None,
        min_length=constants.MAX_LENGTH_6,
        max_length=constants.MAX_LENGTH_100,
        description=_("The name of the configuration."),
    )
    key: str | None = Field(
        default=None,
        min_length=constants.MAX_LENGTH_3,
        max_length=constants.MAX_LENGTH_100,
        description=_("The unique key representing this configuration."),
    )
    value: str | None = Field(
        default=None,
        max_length=constants.MAX_LENGTH_500,
        description=_("The value associated with the configuration."),
    )
    type: ConfigurationType = Field(
        default=ConfigurationType.OTHER,
        sa_column=Column(
            SQLEnum(ConfigurationType, name="configuration_type"),
        ),
        description=_("The type of configuration, represented as an enum."),
    )
    description: str | None = Field(
        default=None,
        max_length=constants.MAX_LENGTH_1000,
        description=_("Additional details or explanation about the configuration."),
    )


class Configuration(
    ConfigurationBase, TimestampMixin, MaintenanceMixin, IdMixin, table=True
):
    __tablename__ = constants.DB_PREFIX_SYS + "configurations"

    key: str = Field(
        min_length=constants.MAX_LENGTH_3,
        max_length=constants.MAX_LENGTH_100,
        description=_("The unique key representing this configuration."),
    )

    options: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description=_(
            "A JSON-encoded field to store additional configuration options as "
            "key-value pairs."
        ),
    )
    user_id: UUID | None = Field(
        default=None,
        foreign_key=constants.DB_PREFIX_SYS + "users.id",
        description=_("The owner of this configuration item."),
    )
    creator: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Configuration.created_by]",
            "primaryjoin": "Configuration.created_by==User.id",
        }
    )
    updater: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Configuration.updated_by]",
            "primaryjoin": "Configuration.updated_by==User.id",
        }
    )
    user: "User" = Relationship(
        sa_relationship_kwargs={
            "foreign_keys": "[Configuration.user_id]",
            "primaryjoin": "Configuration.user_id==User.id",
        }
    )
