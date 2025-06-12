import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text
from chatlse.postgres_engine import create_postgres_engine_from_env_sync
from chatlse.crawler import parse_doc, generate_json_entry, generate_list_ingested_data
from datetime import datetime

load_dotenv(override=True)

# Open the Postgres connection
engine = create_postgres_engine_from_env_sync()
conn = engine.connect()

BASE_DIR = Path(__file__).parents[1]

# Local directory holding copies of PDF documents to ingest
OFFLINE_PDFS_DIR = 'offline_pdfs'


def process_pdf(pdf_file_path):
    # attributes and metadata about the item
    url = pdf_file_path
    title = pdf_file_path.split('/')[-1]
    date_scraped = datetime.now()
    # using the code implemented within the crawler
    content, doc_id, type = parse_doc(pdf_file_path)

    # Check if the url already exists in the database
    result = conn.execute(text('SELECT url, doc_id FROM lse_doc WHERE url = :url'), {
                          'url': url}).fetchone()

    # If url exists, check if it has changed since last scrape
    if result:
        _, previous_hash = result
        # Skipping insertion and return if document has not changed
        if previous_hash == doc_id:
            print(f"Skipping insertion. File not modified since last ingested:", url)
            return
        # Delete old insertions if document has changed
        else:
            print(f"File modified since last ingested. Deleting previous data for:", url)
            conn.execute(
                text('DELETE FROM lse_doc WHERE url = :url'), {'url': url})

    # Insert document into the database (if document not exist or if it has changed)
    output_list = generate_json_entry(
        content, type, url, title, date_scraped, doc_id)
    for idx, doc_id, chunk_id, type, url, title, content, date_scraped in output_list:
        conn.execute(text('''
                                INSERT INTO lse_doc (id, doc_id, chunk_id, type, url, title, content, date_scraped)
                                VALUES (:id, :doc_id, :chunk_id, :type, :url, :title, :content, :date_scraped)
                            '''), {
            "id": idx,
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "type": type,
            "url": url,
            "title": title,
            "content": content,
            "date_scraped": date_scraped
            # "embedding": embedding
        })

    generate_list_ingested_data(
        "data/ingested_data.json", idx, type, url, title, date_scraped)

    # Commit the database transaction
    conn.commit()


# Full directory path for location of PDFs
DIR = os.path.join(BASE_DIR, OFFLINE_PDFS_DIR)

# List of all the PDFs to ingest
pdf_files = list(Path(DIR).rglob('*.pdf'))
print(f"Found {len(pdf_files)} PDF files to process")

for pdf_file in pdf_files:
    # Need to convert to a string for existing code to work
    pdf_file = str(pdf_file)

    process_pdf(pdf_file)

# Close the Postgres connection
engine.dispose()
