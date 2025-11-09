# scrape-watch

A personal web-scraper dashboard to monitor prices, track listings, and log time-series data. Built with Python, Django, FastAPI, PostgreSQL, and InfluxDB.

## Core Concept

This tool is designed to track items on e-commerce or classifieds sites (like `bazos.cz`). You define *what* you want to track (a URL and CSS selectors), and a background worker scrapes the data on a schedule. The data is stored in a time-series database (InfluxDB) for price history visualization.

## Tech Stack & Architecture

This project uses a service-oriented architecture to separate concerns:

* **Control Panel: Django + PostgreSQL**
    * Handles user accounts and the configuration of `ScrapeJob`s (URLs, selectors, etc.).
    * **Access:** `http://localhost:8000/admin`

* **Ingestion API: FastAPI**
    * A lightweight, high-speed endpoint that receives JSON data from the scraper.
    * **Docs:** `http://localhost:8001/docs`

* **Time-Series Storage: InfluxDB**
    * Stores all historical price data with timestamps for visualization.
    * **Access:** `http://localhost:8086`

* **Scraper Worker: Python (Requests + BeautifulSoup)**
    * A separate, scheduled process that fetches jobs from Postgres, scrapes the data, and sends it to the FastAPI endpoint.

* **Orchestration: Docker Compose**
    * A single `docker-compose.yml` file is used to build, launch, and connect all services.

## How to Run

### 1. Clone the Repository
```bash
git clone [https://github.com/DedovSergei/scrape-watch.git](https://github.com/DedovSergei/scrape-watch.git)
```

```bash
cd scrape-watch
```

### 2. Create Environment File
Copy the example environment file to create your own local .env file. This file holds all passwords and secrets and is ignored by Git.

Windows (CMD/PowerShell):

```bash
copy .env.example .env
```

(The default credentials in .env.example will work for local development.)

### 3. Build and Start All Services

```bash
docker-compose up -d --build
```

### 4. Create Your Admin Account
Once the containers are running, you must create an administrator account for the Django control panel.

```bash
docker-compose exec control_panel python manage.py createsuperuser
```

### 5. Log In and Create a Scrape Job
- Go to the Django Admin at http://localhost:8000/admin

- Log in with the user you just created.

- On the dashboard, find JOBS and click "Add" next to "Scrape jobs".

- Fill out the form with the example job data below.

### 6. Run the Worker Manually
To test the full pipeline, run the worker manually. This command will start the worker, execute the scrape, send the data, and then stop, automatically cleaning up the container.

```bash
docker-compose run --rm worker
```

### 7. View Your Data
- Go to the InfluxDB UI at http://localhost:8086

- Log in (the defaults from your .env file are admin / adminadmin).

- On the left menu, navigate to the Data Explorer (graph icon).

- In the query builder:

  - From scrape_data (your bucket)

  - Select item_prices (your measurement)

  - Select price (your field)

- Click Submit to see your data.

### Example Scrape Job
Use this configuration to test the bazos.cz scraper.

- Name: Bazos - BMW E30

- User: (Your admin user)

- Is active: ✅

- Target url: https://auto.bazos.cz/inzeraty/bmw-e30/

- Css selector listing: div.inzeraty.inzeratyflex

- Css selector title: div.inzeratynadpis > h2

- Css selector price: div.inzeratycena > b

- Css selector url: div.inzeratynadpis > a

### Quick Access
- Django Admin: http://localhost:8000/admin

- FastAPI Docs: http://localhost:8001/docs

- InfluxDB UI: http://localhost:8086
