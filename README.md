# scrape-watch

A personal web-scraper dashboard to monitor prices, track listings, and log data over time. Built with Python, FastAPI, Django, and InfluxDB.

> **Note:** This project is in the early stages of development.

## Core Concept

This tool is designed to track items on e-commerce or classifieds sites (like `bazos.cz`). You define *what* you want to track (a URL and CSS selectors), and a background worker scrapes the data on a schedule. The data is stored in a time-series database (InfluxDB) so you can visualize price history.

A key feature is the ability to monitor for *new* listings and send real-time alerts.

## Tech Stack & Architecture

This project uses a service-oriented architecture to separate concerns:

* **Control Panel:** **Django + PostgreSQL**
    * Handles user accounts and the configuration of `ScrapeJob`s (URLs, selectors, etc.).
* **Ingestion API:** **FastAPI**
    * A lightweight, high-speed endpoint that receives data from the scraper.
* **Time-Series Storage:** **InfluxDB**
    * Stores all historical data (e.g., prices, item counts) with timestamps.
* **Scraper Worker:** **Python (Requests + BeautifulSoup)**
    * A separate, scheduled process that fetches jobs from Postgres, scrapes the data, and sends it to the FastAPI endpoint.
* **Orchestration:** **Docker Compose**
    * A single `docker-compose.yml` file is used to build, launch, and connect all services.

## How to Run (Work in Progress)

*(Detailed instructions will be added as the project is built).*

1.  Clone the repository.
2.  Create a `.env` file for the database passwords and other secrets.
3.  Run `docker-compose up --build`.
