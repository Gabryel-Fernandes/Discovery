from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import casos, analises, usuarios, analise_manual

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Discovery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(casos.router)
app.include_router(analises.router)
app.include_router(usuarios.router)
app.include_router(analise_manual.router)

@app.get("/")
def root():
    return {"status": "Discovery API rodando!"}