from pydantic import BaseModel
from typing import Optional

class Coordenadas(BaseModel):
    lat: float
    lng: float

class Species(BaseModel):
    id: int
    nombre: str
    imagen: str
    habitat: str
    alimentacion: str
    coordenadas: Coordenadas

class SpeciesSummary(BaseModel):
    id: int
    nombre: str
    habitat: str

class HabitatResponse(BaseModel):
    idEspecie: int
    habitat: str
