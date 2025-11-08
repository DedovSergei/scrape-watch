import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

class ScrapedItem(BaseModel):
    title: str
    price: str
    url: str

class IngestPayload(BaseModel):
    job_id: int
    items: List[ScrapedItem]

influx_url = "http://influxdb:8086"
influx_token = os.environ.get("INFLUXDB_ADMIN_TOKEN")
influx_org = os.environ.get("INFLUXDB_ORG")
influx_bucket = os.environ.get("INFLUXDB_BUCKET")

try:
    influx_client = InfluxDBClient(url=influx_url, token=influx_token, org=influx_org)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)
    print("Successfully connected to InfluxDB.")
except Exception as e:
    print(f"Error connecting to InfluxDB: {e}")
    influx_client = None

app = FastAPI()

def parse_price(price_str: str) -> float | None:
    """Helper function to clean and convert price strings to numbers."""
    if not price_str or price_str.lower() in ["n_a", "dohodou"]:
        return None
    
    cleaned_str = "".join(filter(str.isdigit, price_str))
    
    try:
        return float(cleaned_str)
    except (ValueError, TypeError):
        return None

@app.get("/")
def read_root():
    """Root endpoint for health checks."""
    return {"status": "Ingestion API is running"}

@app.post("/ingest")
async def ingest_data(payload: IngestPayload):
    """
    Receives scraped data from the worker AND writes it to InfluxDB.
    """
    if not influx_client:
        raise HTTPException(status_code=500, detail="InfluxDB client not initialized.")

    print(f"--- Received Data for Job ID: {payload.job_id} ---")

    points = []
    for item in payload.items:
        price_float = parse_price(item.price)

        if price_float is not None:
            point = (
                Point("item_prices")
                .tag("job_id", str(payload.job_id))
                .tag("item_title", item.title[:255])
                .tag("item_url", item.url)
                .field("price", price_float)
                .time(datetime.utcnow(), WritePrecision.NS)
            )
            points.append(point)

    if not points:
        print("No items with valid prices found. Nothing to write.")
        return {
            "status": "success",
            "job_id": payload.job_id,
            "items_received": len(payload.items),
            "items_written": 0
        }

    try:
        write_api.write(bucket=influx_bucket, org=influx_org, record=points)
        print(f"Successfully wrote {len(points)} data points to InfluxDB.")
    except Exception as e:
        print(f"Error writing to InfluxDB: {e}")
        raise HTTPException(status_code=500, detail=f"Error writing to InfluxDB: {e}")

    return {
        "status": "success",
        "job_id": payload.job_id,
        "items_received": len(payload.items),
        "items_written": len(points)
    }