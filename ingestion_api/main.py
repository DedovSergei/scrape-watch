from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from typing import List


class ScrapedItem(BaseModel):
    """Defines the data for a single scraped item."""
    title: str
    price: str
    url: str

class IngestPayload(BaseModel):
    """Defines the payload our worker will send."""
    job_id: int
    items: List[ScrapedItem]

app = FastAPI()

@app.get("/")
def read_root():
    """Root endpoint for health checks."""
    return {"status": "Ingestion API is running"}

@app.post("/ingest")
async def ingest_data(payload: IngestPayload):
    """
    Receives scraped data from the worker.
    This is the core of the ingestion API.
    """
    
    
    print(f"--- Received Data for Job ID: {payload.job_id} ---")
    print(f"Total items received: {len(payload.items)}")
    
    for item in payload.items[:3]:
        print(f"  - Title: {item.title}")
        print(f"  - Price: {item.price}")

    
    return {
        "status": "success",
        "job_id": payload.job_id,
        "items_received": len(payload.items)
    }