from fastapi import APIRouter, HTTPException
import json
from models.species import Species, SpeciesSummary, HabitatResponse

router = APIRouter(prefix="/especies", tags=["Fauna Data Inc"])

def load_data():
    with open("data/species_db.json", "r", encoding="utf-8") as f:
        return json.load(f)

# MENSAJE DE NEGOCIO: SolicitarListadoEspecies
@router.get("/listar", response_model=list[SpeciesSummary])
def solicitar_listado_especies():
    data = load_data()
    return [
        {"id": s["id"], "nombre": s["nombre"], "habitat": s["habitat"]}
        for s in data
    ]

# MENSAJE DE NEGOCIO: SolicitarEspeciePorID
@router.get("/{idEspecie}", response_model=Species)
def solicitar_especie_por_id(idEspecie: int):
    data = load_data()
    especie = next((s for s in data if s["id"] == idEspecie), None)

    if not especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")

    return especie

# MENSAJE DE NEGOCIO: SolicitarEspeciesPorHabitat
@router.get("/habitat/{habitat}", response_model=list[Species])
def solicitar_especies_por_habitat(habitat: str):
    data = load_data()
    result = [s for s in data if s["habitat"].lower() == habitat.lower()]

    if not result:
        raise HTTPException(status_code=404, detail="No existen especies para este hábitat")

    return result

# MENSAJE DE NEGOCIO: SolicitarEspeciesConCoordenadas
@router.get("/coordenadas/area", response_model=list[Species])
def solicitar_especies_con_coordenadas():
    data = load_data()
    return data  # todas tienen coordenadas para este ejemplo

# MENSAJE DE NEGOCIO: SolicitarHabitatDeEspecie
@router.get("/habitat/id/{idEspecie}", response_model=HabitatResponse)
def solicitar_habitat_de_especie(idEspecie: int):
    data = load_data()
    especie = next((s for s in data if s["id"] == idEspecie), None)

    if not especie:
        raise HTTPException(status_code=404, detail="Especie no encontrada")

    return {"idEspecie": especie["id"], "habitat": especie["habitat"]}
