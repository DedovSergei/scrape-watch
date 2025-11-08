import os
import time
import psycopg2
import requests
from bs4 import BeautifulSoup

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            dbname=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD'),
            host='db'
        )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def fetch_active_jobs(conn):
    """Fetches all active scrape jobs from the database."""
    jobs = []
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, target_url, css_selector_listing, "
                "css_selector_title, css_selector_price, css_selector_url "
                "FROM jobs_scrapejob WHERE is_active = TRUE"
            )
            for row in cur.fetchall():
                jobs.append({
                    "id": row[0],
                    "url": row[1],
                    "listing_selector": row[2],
                    "title_selector": row[3],
                    "price_selector": row[4],
                    "url_selector": row[5],
                })
        return jobs
    except psycopg2.Error as e:
        print(f"Error fetching jobs: {e}")
        return []

def scrape_job(job):
    """Performs a single scrape job and sends the results to the API."""
    print(f"\n--- Scraping Job: {job['id']} ({job['url']}) ---")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(job['url'], headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        listings = soup.select(job['listing_selector'])
        print(f"Found {len(listings)} listings.")

        scraped_data = []
        for item in listings:
            title = item.select_one(job['title_selector'])
            price = item.select_one(job['price_selector'])
            url = item.select_one(job['url_selector'])

            data = {
                "title": title.text.strip() if title else "N_A",
                "price": price.text.strip() if price else "N_A",
                "url": url['href'] if url and 'href' in url.attrs else "N_A"
            }
            scraped_data.append(data)

        if scraped_data:
            api_url = "http://ingestion_api:8001/ingest"
            
            payload = {
                "job_id": job['id'],
                "items": scraped_data
            }
            
            try:
                response = requests.post(api_url, json=payload, timeout=10)
                response.raise_for_status()
                
                print(f"Successfully sent {len(scraped_data)} items to API.")
                
            except requests.RequestException as e:
                print(f"Error sending data to API: {e}")

    except requests.RequestException as e:
        print(f"Error during request: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Worker starting...")
    conn = get_db_connection()

    if not conn:
        print("Could not connect to DB. Exiting.")
        return

    active_jobs = fetch_active_jobs(conn)
    print(f"Found {len(active_jobs)} active job(s).")

    for job in active_jobs:
        scrape_job(job)

    print("\nWorker run finished.")
    conn.close()

if __name__ == "__main__":
    main()