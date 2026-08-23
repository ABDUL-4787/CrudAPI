# The Polite Scraper — Books to Scrape

A polite, Python-based web scraper that extracts book details from [Books to Scrape](https://books.toscrape.com/) across the first three pages, caches page contents locally, validates extracted data structures using Pydantic, and records execution metrics.

---

## Target Classification
- **Target Website**: [https://books.toscrape.com/](https://books.toscrape.com/)
- **Purpose**: A sandbox / training ground designed specifically for testing web scrapers. Since it is a practice environment, it has no commercial listings, personal data, or access limits.
- **Rules Agreement**: 
  "I will not reuse this code on another site without checking its rules and terms first."

---

## Robots.txt Result
The target site exposes a `robots.txt` configuration at `https://books.toscrape.com/robots.txt`. When requested, it returns empty rules (meaning it does not restrict user agents from accessing catalogue pages). 

---

## Politeness Rules
To ensure the target website is treated respectfully, this scraper enforces the following guidelines:
1. **User-Agent Identification**: Sends an identifying User-Agent containing the repository details:
   `FlyRankInternship-A9/1.0 (+https://github.com/ABDUL-4787/CrudAPI)`
2. **Request Delays**: Waits at least **500 milliseconds** (`time.sleep(0.5)`) between consecutive network requests. Caching reads occur instantly with no delay.
3. **Timeouts**: Incorporates a network request timeout limit of 10 seconds.
4. **Status Verification**: Verifies response code is `200 OK` before parsing HTML.

---

## Project Structure
```text
scraper/
├── src/
│   └── main.py          # The core scraping execution file
├── cache/               # Directory containing local HTML cached files (ignored by Git)
├── output/              # Extraction results and logs folder (ignored by Git)
├── README.md            # Scraper project details and instructions
├── requirements.txt     # Python package dependencies
└── .gitignore           # Excludes local cache/ and output/ directories from tracking
```

---

## How Caching Works
To minimize server load, pages are cached inside `scraper/cache/`:
- The MD5 hash of each page's URL determines its cached filename.
- If a cached file exists, the scraper reads the local HTML and logs `CACHE HIT: <url>` to the terminal (with no delay).
- If it does not exist, the scraper queries the website, stores the page contents locally on disk, logs `FETCH: <url>`, and enforces the politeness delay.

---

## How Broken Pages are Handled
- One deliberately broken URL is added to the URL list to check resilience.
- When a page request returns a non-200 status code (such as a 404), the error is logged into `scraper/output/errors.json`, and the program skips it, continuing to scrape the remaining valid books without crashing.

---

## Pydantic Record Validation Schema
Every extracted book detail is validated using Pydantic:

```python
class BookRecord(BaseModel):
    url: str
    title: str = Field(..., min_length=1)
    price: str
    price_gbp: float = Field(..., gt=0.0)
    availability: str
    rating: str
    upc: str = Field(..., min_length=1)
    product_type: str
    tax: str
    number_of_reviews: int = Field(..., ge=0)
    description: Optional[str] = None
```

---

## Required Packages
- `requests` (network queries)
- `beautifulsoup4` (HTML traversal and selection)
- `pydantic` (data validation)

---

## Installation & Setup

1. **Activate the virtual environment**:
   ```powershell
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   ```
2. **Install package dependencies**:
   ```bash
   pip install -r scraper/requirements.txt
   ```

---

## How to Run the Scraper
Run the scraper program from your root directory:
```bash
python scraper/src/main.py
```

---

## Generated Output Files
After a successful execution, the following files are populated in `scraper/output/`:
- **`books.json`**: An array containing exactly 60 unique book detail records.
- **`errors.json`**: Tracks any validation or network failures.
- **`run-report.json`**: A JSON file containing execution summary statistics.

---

## Verification Results
The following final checks have been performed and verified locally:
1. **Exactly 60 Books Collected**: The scraper processes catalogue pagination and saves exactly 60 unique book detail records to `output/books.json`.
2. **Numeric price_gbp**: The extracted currency string is parsed and stored as a native floating-point numeric value (`price_gbp`) inside the JSON records.
3. **Caching & Cache Hits**: Re-running the scraper uses local HTML cache files and outputs `CACHE HIT` messages to the terminal, completing the execution in seconds.
4. **Error & Broken Page Resilience**: Intentionally adding a broken URL returns an HTTP 404 response but does not crash the scraper. 
5. **Errors Logging**: All skipped or failed URLs (including `robots.txt` and the broken URL) are recorded with their reasons inside `output/errors.json`.
6. **Files Verification**: Verified that `output/books.json` and `output/run-report.json` are generated successfully with valid formats.
