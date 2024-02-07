from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from datetime import timezone
from typing import Set
from typing import List


class Base(DeclarativeBase):
    pass


def lazy_utc_now():
    return datetime.now(timezone.utc)


random_uuid_generator = text("gen_random_uuid()")


class Empresa(Base):
    __tablename__ = "empresas"

    rnc: Mapped[str] = mapped_column(primary_key=True)
    nombre: Mapped[str]
    tipo_de_persona: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now, onupdate=datetime.now
    )

    relacionados: Mapped[Set["Cliente"]] = relationship(
        secondary="clientes_empresas", back_populates="empresas"
    )
    cuenta: Mapped["Cuenta"] = relationship(viewonly=True)


class Cliente(Base):
    __tablename__ = "clientes"

    cliente_id = mapped_column(
        UUID, primary_key=True, server_default=random_uuid_generator
    )
    nombre: Mapped[str]
    email: Mapped[str]
    telefono: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=lazy_utc_now, onupdate=lazy_utc_now
    )

    empresas: Mapped[Set["Empresa"]] = relationship(
        secondary="clientes_empresas", back_populates="relacionados"
    )


class ClienteEmpresa(Base):
    __tablename__ = "clientes_empresas"

    cliente_id = mapped_column(
        UUID,
        ForeignKey("clientes.cliente_id"),
        primary_key=True,
    )
    rnc: Mapped[str] = mapped_column(ForeignKey("empresas.rnc"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)


class Servicio(Base):
    __tablename__ = "servicios"

    servicio_id = mapped_column(
        UUID, primary_key=True, server_default=random_uuid_generator
    )
    nombre: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=lazy_utc_now, onupdate=lazy_utc_now
    )
    tags: Mapped[List["Tag"]] = relationship(secondary="tags_servicios", viewonly=True)
    tag_servicios: Mapped[List["TagServicio"]] = relationship()


class Tag(Base):
    __tablename__ = "tags"

    tag_id = mapped_column(UUID, primary_key=True, server_default=random_uuid_generator)
    nombre: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=lazy_utc_now, onupdate=lazy_utc_now
    )
    servicios: Mapped[List["Servicio"]] = relationship(
        secondary="tags_servicios", viewonly=True, lazy="selectin"
    )


class TagServicio(Base):
    __tablename__ = "tags_servicios"

    tag_id = mapped_column(ForeignKey("tags.tag_id"), primary_key=True)
    servicio_id = mapped_column(
        ForeignKey("servicios.servicio_id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)


class Cuenta(Base):
    __tablename__ = "cuentas"

    cuenta_id = mapped_column(
        UUID, primary_key=True, server_default=random_uuid_generator
    )
    rnc = mapped_column(ForeignKey("empresas.rnc"), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        default=lazy_utc_now, onupdate=lazy_utc_now
    )
    cuenta_servicios: Mapped[List["CuentaServicio"]] = relationship()
    servicios: Mapped[List[Servicio]] = relationship(
        secondary="cuentas_servicios", viewonly=True
    )
    empresa: Mapped["Empresa"] = relationship(viewonly=True, single_parent=True)


class CuentaServicio(Base):
    __tablename__ = "cuentas_servicios"
    cuenta_id = mapped_column(
        ForeignKey("cuentas.cuenta_id", ondelete="CASCADE"), primary_key=True
    )
    servicio_id = mapped_column(ForeignKey("servicios.servicio_id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)


class User(Base):
    __tablename__ = "usuarios"

    usuario_id = mapped_column(
        UUID, primary_key=True, server_default=random_uuid_generator
    )
    nombre: Mapped[str]
    email: Mapped[str] = mapped_column(index=True)
    password: Mapped[str]
    status: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    rol: Mapped[str]
    org: Mapped["Organizacion"] = relationship(secondary="organizaciones_usuarios")


class Organizacion(Base):
    __tablename__ = "organizaciones"

    organizacion_id = mapped_column(
        UUID, primary_key=True, server_default=random_uuid_generator
    )
    nombre: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
    # organizacion_usuarios: Mapped[List["OrganizacionUsuario"]] = relationship()


class OrganizacionUsuario(Base):
    __tablename__ = "organizaciones_usuarios"
    organizacion_id = mapped_column(
        ForeignKey("organizaciones.organizacion_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = mapped_column(ForeignKey("usuarios.usuario_id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lazy_utc_now)
