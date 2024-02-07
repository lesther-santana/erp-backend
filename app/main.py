from fastapi import FastAPI
from fastapi.openapi.models import Info, Contact, License

from .endpoints.routers import (
    clientes,
    organizaciones,
    token,
    usuarios,
    empresas,
    servicios,
    tags,
    cuentas,
)


tag_descriptions = {
    "Organizaciones": "Operations related to organizations.",
    "Clientes": "Operations related to clients.",
    "Empresas": "Operations related to companies.",
    "Servicios": "Operations related to services.",
    "Tags": "Operations related to tags.",
    "Cuentas": "Operations related to accounts.",
    "Authorization": "Operations related to authorization tokens.",
    "Usuarios": "Operations related to users.",
}

tags_metadata = [{"name": n, "description": d} for n, d in tag_descriptions.items()]
security = [{"bearerAuth": []}]

info = Info(
    title="Carsant ERP",
    version="1.0.0",
    summary="Backend API for the ERP",
    description="Your API description",
    terms_of_service="http://example.com/terms/",
    contact=Contact(name="Your Name", email="your.email@example.com"),
    license=License(name="Your License", url="http://example.com/license/"),
)

app = FastAPI(
    title=info.title,
    summary=info.summary,
    description=info.description,
    version=info.version,
    contact=info.contact,
    license=info.license,
    openapi_tags=tags_metadata,
    security=security,
)

app.include_router(token.router, prefix="/token", tags=["Authorization"])
app.include_router(
    organizaciones.router, prefix="/organizaciones", tags=["Organizaciones"]
)
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
app.include_router(empresas.router, prefix="/empresas", tags=["Empresas"])
app.include_router(servicios.router, prefix="/servicios", tags=["Servicios"])
app.include_router(tags.router, prefix="/tags", tags=["Tags"])
app.include_router(cuentas.router, prefix="/cuentas", tags=["Cuentas"])

