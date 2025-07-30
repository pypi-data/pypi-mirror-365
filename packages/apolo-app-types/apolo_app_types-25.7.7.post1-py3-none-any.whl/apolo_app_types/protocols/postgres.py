from __future__ import annotations

import enum
import typing as t

from pydantic import ConfigDict, Field

from apolo_app_types import AppInputs
from apolo_app_types.protocols.common import (
    AbstractAppFieldType,
    AppOutputs,
    AppOutputsDeployer,
    Preset,
    SchemaExtraMetadata,
    SchemaMetaType,
)


class PostgresURI(AbstractAppFieldType):
    """Configuration for the Postgres connection URI."""

    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Postgres URI",
            description="Full Postgres connection URI configuration.",
        ).as_json_schema_extra(),
    )
    uri: str = Field(
        ...,
        json_schema_extra=SchemaExtraMetadata(
            title="URI",
            description=(
                "Specify full Postgres connection URI. E.g. 'postgresql://user:pass@host:5432/db'"
            ),
        ).as_json_schema_extra(),
    )


class PGBouncer(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="PG Bouncer",
            description="Configuration for PG Bouncer.",
        ).as_json_schema_extra(),
    )
    preset: Preset = Field(
        ...,
        description="Preset to use for the PGBouncer instance.",
        title="Preset",
    )
    replicas: int = Field(
        default=2,
        description="Number of replicas for the PGBouncer instance.",
        title="PGBouncer replicas",
    )


class PostgresSupportedVersions(enum.StrEnum):
    v12 = "12"
    v13 = "13"
    v14 = "14"
    v15 = "15"
    v16 = "16"


class PostgresDBUser(AbstractAppFieldType):
    name: str = Field(
        ...,
        description="Name of the database user.",
        title="Database user name",
    )
    db_names: list[str] = Field(
        default_factory=list,
        description="Name of the database.",
        title="Database name",
    )


class PostgresConfig(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Postgres",
            description="Configuration for Postgres.",
        ).as_json_schema_extra(),
    )
    postgres_version: PostgresSupportedVersions = Field(
        default=PostgresSupportedVersions.v16,
        description="Set version of the Postgres server to use.",
        title="Postgres version",
    )
    instance_replicas: int = Field(
        default=3,
        description="Set number of replicas for the Postgres instance.",
        title="Postgres instance replicas",
    )
    instance_size: int = Field(
        default=1,
        description="Set size of the Postgres instance disk (in GB).",
        title="Postgres instance disk size",
    )
    db_users: list[PostgresDBUser] = Field(
        default_factory=list,
        description=(
            "Configure list of users and databases they have access to. "
            "Multiple users could have access to the same database."
        ),
        title="Database users",
    )


class PGBackupConfig(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Backup configuration",
            description="Set up backup configuration for your Postgres cluster.",
        ).as_json_schema_extra(),
    )
    enable: bool = Field(
        default=True,
        title="Enable backups",
        description=(
            "Enable backups for the Postgres cluster. "
            "We automatically create and configure the corresponding backup "
            "bucket for you. "
            "Note: this bucket will not be automatically removed when you remove "
            "the app."
        ),
    )
    # backup_bucket: Bucket


class PostgresInputs(AppInputs):
    preset: Preset
    postgres_config: PostgresConfig
    pg_bouncer: PGBouncer
    backup: PGBackupConfig


class CrunchyPostgresUserCredentials(AbstractAppFieldType):
    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra=SchemaExtraMetadata(
            title="Postgres User Credentials",
            description="Configuration for Crunchy Postgres user credentials.",
            meta_type=SchemaMetaType.INTEGRATION,
        ).as_json_schema_extra(),
    )
    user: str
    password: str
    host: str
    port: int
    pgbouncer_host: str
    pgbouncer_port: int
    dbname: str | None = None
    jdbc_uri: str | None = None
    pgbouncer_jdbc_uri: str | None = None
    pgbouncer_uri: str | None = None
    uri: str | None = None
    postgres_uri: PostgresURI | None = None

    def with_database(self, database: str) -> CrunchyPostgresUserCredentials:
        updates: dict[str, t.Any] = {
            "dbname": database,
        }
        if self.jdbc_uri:
            updates["jdbc_uri"] = self.jdbc_uri.replace(
                f"/{self.dbname}", f"/{database}"
            )
        if self.pgbouncer_jdbc_uri:
            updates["pgbouncer_jdbc_uri"] = self.pgbouncer_jdbc_uri.replace(
                f"/{self.dbname}", f"/{database}"
            )
        if self.pgbouncer_uri:
            updates["pgbouncer_uri"] = self.pgbouncer_uri.replace(
                f"/{self.dbname}", f"/{database}"
            )
        if self.uri:
            updates["uri"] = self.uri.replace(f"/{self.dbname}", f"/{database}")
        if self.postgres_uri:
            uri = self.postgres_uri.uri or ""
            uri = uri.replace(f"/{self.dbname}", f"/{database}")
            updates["postgres_uri"] = PostgresURI(uri=uri)
        return self.model_copy(update=updates)


class CrunchyPostgresOutputs(AppOutputsDeployer):
    users: list[CrunchyPostgresUserCredentials]


class PostgresUsers(AbstractAppFieldType):
    users: list[CrunchyPostgresUserCredentials]


class PostgresOutputs(AppOutputs):
    postgres_users: PostgresUsers | None = None
