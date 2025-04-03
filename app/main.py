"""
Main FastAPI application.
"""

from api.metadata import tags_metadata
from api.v1.endpoints import profitability, ticker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Pyicatu Financial API",
    description="Retorna dados brutos e calculados definidos no projeto",
    openapi_url="/api/v1/openapi.json",
    openapi_tags=tags_metadata,
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(ticker.router, prefix="/api/v1/tickers")

app.include_router(profitability.router, prefix="/api/v1/tickers")


@app.get("/")
def root():
    return {"message": "FastAPI rodando via Astro"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
