import os
import sys
import time
import json
import hashlib
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, List, Dict

# Scraper project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Create folders dynamically if they do not exist
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Target configuration
ROBOTS_URL = "https://books.toscrape.com/robots.txt"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"
USER_AGENT = "FlyRankInternship-A9/1.0 (+https://github.com/ABDUL-4787/CrudAPI)"
HEADERS = {"User-Agent": USER_AGENT}
DELAY_MS = 500  # 500ms delay between live requests

def safe_print(text: str):
    """Print text safely by replacing unencodable characters (useful for Windows CP1252 consoles)."""
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            encoding = sys.stdout.encoding or "ascii"
            print(text.encode(encoding, errors="replace").decode(encoding))
        except Exception:
            print(text.encode("ascii", errors="replace").decode("ascii"))

# Pydantic Schema for Book Records
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

class Scraper:
    def __init__(self):
        self.cache_hits = 0
        self.real_fetches = 0
        self.books: List[Dict] = []
        self.errors: List[Dict] = []
        self.discovered_urls: List[str] = []

    def get_cache_filepath(self, url: str) -> str:
        """Generate a safe, hashed file path for cached HTML."""
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, f"{url_hash}.html")

    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch the HTML of a page, reading from local cache if it exists, or fetching over network politely."""
        cache_path = self.get_cache_filepath(url)
        
        # Check cache
        if os.path.exists(cache_path):
            self.cache_hits += 1
            safe_print(f"CACHE HIT: {url}")
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
                
        # Cache miss, fetch over network
        self.real_fetches += 1
        safe_print(f"FETCH: {url}")
        
        # Enforce politeness delay
        time.sleep(DELAY_MS / 1000.0)
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                safe_print(f"Error: Received HTTP status code {response.status_code} for {url}")
                self.errors.append({
                    "url": url,
                    "reason": f"HTTP status code {response.status_code}"
                })
                return None
                
            html_content = response.text
            # Write to cache
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            return html_content
        except Exception as e:
            safe_print(f"Network error fetching {url}: {e}")
            self.errors.append({
                "url": url,
                "reason": f"Network exception: {str(e)}"
            })
            return None

    def check_robots_txt(self):
        """Programmatically fetch and read robots.txt once."""
        safe_print("Checking robots.txt...")
        content = self.fetch_page(ROBOTS_URL)
        if content:
            safe_print("--- robots.txt content start ---")
            safe_print(content.strip())
            safe_print("--- robots.txt content end ---")
        else:
            safe_print("robots.txt not found or could not be read.")

    def discover_books(self) -> List[str]:
        """Iterate through page 1 to 3 and collect unique book URLs."""
        current_url = START_URL
        book_urls = []
        
        for page_num in range(1, 4):
            safe_print(f"\n[Processing Page {page_num}] Scanning catalogue URL: {current_url}")
            html = self.fetch_page(current_url)
            if not html:
                safe_print(f"Failed to fetch catalogue page {page_num}.")
                break
                
            soup = BeautifulSoup(html, "html.parser")
            
            # Find all book article link URLs on the page
            page_discoveries = 0
            articles = soup.find_all("article", class_="product_pod")
            for article in articles:
                link = article.find("h3").find("a")
                if link and "href" in link.attrs:
                    rel_url = link.attrs["href"]
                    # Convert to absolute URL
                    abs_url = urllib.parse.urljoin(current_url, rel_url)
                    if abs_url not in book_urls:
                        book_urls.append(abs_url)
                        self.discovered_urls.append(abs_url)
                    page_discoveries += 1
            
            safe_print(f"Page {page_num} processing complete. Discovered {page_discoveries} book URLs on this page.")
            
            # Find the 'next' button
            next_li = soup.find("li", class_="next")
            if next_li:
                next_a = next_li.find("a")
                if next_a and "href" in next_a.attrs:
                    current_url = urllib.parse.urljoin(current_url, next_a.attrs["href"])
                else:
                    break
            else:
                break
                
        # Dedup list
        unique_urls = list(set(book_urls))
        safe_print(f"\nDiscovery complete. Discovered {len(unique_urls)} unique book URLs across the 3 catalogue pages.")
        return unique_urls

    def parse_book_details(self, url: str, html: str) -> Optional[BookRecord]:
        """Parse raw HTML structure of a book details page and return a Pydantic verified record."""
        soup = BeautifulSoup(html, "html.parser")
        
        # 1. Title
        title_tag = soup.find("h1")
        title = title_tag.get_text().strip() if title_tag else ""
        
        # 2. Price
        price_tag = soup.find("p", class_="price_color")
        price = price_tag.get_text().strip() if price_tag else ""
        
        # Extract numeric float for price_gbp
        price_gbp = 0.0
        if price:
            try:
                # Remove symbols and parse as float
                price_numeric_str = "".join(c for c in price if c.isdigit() or c == ".")
                price_gbp = float(price_numeric_str)
            except Exception:
                price_gbp = 0.0
                
        # 3. Stock & Availability
        availability_tag = soup.find("p", class_="instock availability")
        availability = availability_tag.get_text().strip() if availability_tag else ""
        
        # 4. Rating
        rating = "One"
        rating_tag = soup.find("p", class_=["star-rating"])
        if rating_tag:
            classes = rating_tag.attrs.get("class", [])
            for c in classes:
                if c != "star-rating":
                    rating = c
                    break

        # 5. Description
        desc_h2 = soup.find("div", id="product_description")
        description = ""
        if desc_h2:
            desc_p = desc_h2.find_next_sibling("p")
            if desc_p:
                description = desc_p.get_text().strip()
                
        # 6. Product Information Table
        info_table = soup.find("table", class_="table-striped")
        upc = ""
        product_type = ""
        tax = ""
        number_of_reviews = 0
        
        if info_table:
            rows = info_table.find_all("tr")
            for row in rows:
                th = row.find("th")
                td = row.find("td")
                if th and td:
                    header = th.get_text().strip().lower()
                    val = td.get_text().strip()
                    if "upc" in header:
                        upc = val
                    elif "product type" in header:
                        product_type = val
                    elif "tax" in header:
                        tax = val
                    elif "number of reviews" in header:
                        try:
                            number_of_reviews = int(val)
                        except Exception:
                            number_of_reviews = 0

        # Build dict and validate with Pydantic
        record_data = {
            "url": url,
            "title": title,
            "price": price,
            "price_gbp": price_gbp,
            "availability": availability,
            "rating": rating,
            "upc": upc,
            "product_type": product_type,
            "tax": tax,
            "number_of_reviews": number_of_reviews,
            "description": description if description else None
        }
        
        try:
            return BookRecord(**record_data)
        except ValidationError as val_err:
            error_lines = []
            for err in val_err.errors():
                loc_str = " -> ".join(str(loc) for loc in err.get("loc", []))
                msg = err.get("msg", "Validation error")
                error_lines.append(f"  - Field '{loc_str}': {msg}")
            
            error_summary = "\n".join(error_lines)
            safe_print(f"\n[VALIDATION FAILED] Book: '{title}' at URL: {url}\n{error_summary}\n")
            
            self.errors.append({
                "url": url,
                "reason": "Pydantic validation error",
                "validation_details": val_err.errors(),
                "raw_data": record_data
            })
            return None

    def run(self):
        start_time = datetime.now()
        
        # 1. Fetch robots.txt
        self.check_robots_txt()
        
        # 2. Page iteration and url discovery
        book_urls = self.discover_books()
        
        # 3. Add one deliberately broken URL for resilience testing
        broken_url = "https://books.toscrape.com/catalogue/broken-book-id-999_abc/index.html"
        book_urls.append(broken_url)
        
        safe_print(f"\nProcessing details pages (60 books + 1 broken URL)...")
        
        # Keep track of unique books to prevent duplication
        unique_books_inserted = set()
        
        for idx, url in enumerate(book_urls):
            # Limit to exactly 60 books successfully scraped
            if len(self.books) >= 60 and url != broken_url:
                continue
                
            html = self.fetch_page(url)
            if not html:
                # HTTP errors or connection exceptions are tracked during fetch_page
                continue
                
            record = self.parse_book_details(url, html)
            if record:
                # De-duplicate record logic
                if record.upc not in unique_books_inserted:
                    unique_books_inserted.add(record.upc)
                    self.books.append(record.model_dump())
                    safe_print(f"[{len(self.books)}/60] Scraped: {record.title}")
                    
        # Sort output books by index ID/url order for stable structure
        self.books = self.books[:60]
        
        # Save output records
        books_path = os.path.join(OUTPUT_DIR, "books.json")
        with open(books_path, "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=2, ensure_ascii=False)
        safe_print(f"\nSaved exactly {len(self.books)} books to {books_path}")
        
        # Save validation errors
        errors_path = os.path.join(OUTPUT_DIR, "errors.json")
        with open(errors_path, "w", encoding="utf-8") as f:
            json.dump(self.errors, f, indent=2, ensure_ascii=False)
        safe_print(f"Saved {len(self.errors)} errors to {errors_path}")
        
        # Create execution summary report
        duration = (datetime.now() - start_time).total_seconds()
        report = {
            "total_discovered_urls": len(self.discovered_urls),
            "successfully_processed_records": len(self.books),
            "failed_records": len(self.errors),
            "cache_hits": self.cache_hits,
            "real_fetches": self.real_fetches,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        report_path = os.path.join(OUTPUT_DIR, "run-report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        safe_print(f"Saved execution report to {report_path}\n")

if __name__ == "__main__":
    scraper = Scraper()
    scraper.run()
