from fastapi import FastAPI
from routers import species

app = FastAPI(
    title="Fauna Data Inc API",
    description="Servicio de Información de Especies Endémicas del Ecuador",
)

app.include_router(species.router)
