"""
Y Combinator Company Scraper
Scrapes company data from YC's company directory
"""

import requests
import time
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class YCombinatorScraper:
    """Scraper for Y Combinator company directory"""
    
    BASE_URL = "https://www.ycombinator.com"
    COMPANIES_URL = f"{BASE_URL}/companies"
    
    # Headers to mimic browser request
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize scraper
        
        Args:
            delay: Delay between requests in seconds (be respectful!)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)
        self.companies = []
    
    def scrape_companies(self, batch: str = None, industry: str = None, 
                        limit: Optional[int] = None) -> List[Dict]:
        """
        Scrape YC companies
        
        Args:
            batch: Filter by batch (e.g., 'W24', 'S23')
            industry: Filter by industry
            limit: Maximum number of companies to scrape
        
        Returns:
            List of company dictionaries
        """
        logger.info("Starting YC company scraper...")
        
        # Build URL with filters
        url = self.COMPANIES_URL
        params = []
        if batch:
            params.append(f"batch={batch}")
        if industry:
            params.append(f"industry={industry}")
        
        if params:
            url += "?" + "&".join(params)
        
        logger.info(f"Scraping from: {url}")
        
        try:
            # YC uses a JSON API endpoint for company data
            # Try the API first
            companies = self._scrape_from_api(batch, industry, limit)
            
            if not companies:
                # Fallback to HTML scraping if API doesn't work
                logger.info("API scraping failed, falling back to HTML parsing...")
                companies = self._scrape_from_html(url, limit)
            
            self.companies = companies
            logger.info(f"✓ Successfully scraped {len(companies)} companies")
            
            return companies
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return []
    
    def _scrape_from_api(self, batch: Optional[str], industry: Optional[str], 
                         limit: Optional[int]) -> List[Dict]:
        """
        Scrape using YC's API endpoint
        
        YC has a public API at: https://api.ycombinator.com/v0.1/companies
        """
        api_url = "https://api.ycombinator.com/v0.1/companies"
        
        try:
            logger.info("Attempting API scraping...")
            response = self.session.get(api_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            companies = []
            
            for company_data in data:
                # Filter by batch if specified
                if batch and company_data.get('batch') != batch:
                    continue
                
                # Filter by industry if specified
                if industry and industry.lower() not in str(company_data.get('tags', [])).lower():
                    continue
                
                company = self._parse_company_api(company_data)
                companies.append(company)
                
                if limit and len(companies) >= limit:
                    break
                
                # Be respectful with delays
                time.sleep(self.delay)
            
            return companies
            
        except Exception as e:
            logger.warning(f"API scraping failed: {e}")
            return []
    
    def _scrape_from_html(self, url: str, limit: Optional[int]) -> List[Dict]:
        """Scrape companies from HTML pages"""
        companies = []
        page = 1
        
        while True:
            logger.info(f"Scraping page {page}...")
            
            try:
                # Add pagination if needed
                page_url = f"{url}&page={page}" if '?' in url else f"{url}?page={page}"
                
                response = self.session.get(page_url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find company cards/entries
                # YC's HTML structure may vary, adjust selectors as needed
                company_elements = soup.find_all(['div', 'article'], class_=lambda x: x and 'company' in x.lower())
                
                if not company_elements:
                    # Try alternative selectors
                    company_elements = soup.select('a[href*="/companies/"]')
                
                if not company_elements:
                    logger.info("No more companies found")
                    break
                
                for element in company_elements:
                    try:
                        company = self._parse_company_html(element)
                        if company:
                            companies.append(company)
                            logger.info(f"  Scraped: {company['name']}")
                        
                        if limit and len(companies) >= limit:
                            return companies
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse company: {e}")
                        continue
                
                # Check if there's a next page
                next_button = soup.find('a', text=lambda x: x and 'next' in x.lower())
                if not next_button:
                    break
                
                page += 1
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error scraping page {page}: {e}")
                break
        
        return companies
    
    def _parse_company_api(self, data: Dict) -> Dict:
        """Parse company data from API response"""
        return {
            'name': data.get('name', ''),
            'batch': data.get('batch', ''),
            'status': data.get('status', 'Active'),
            'description': data.get('one_liner', ''),
            'long_description': data.get('long_description', ''),
            'website': data.get('website', ''),
            'location': data.get('location', ''),
            'industry': ', '.join(data.get('tags', [])),
            'team_size': data.get('team_size'),
            'founded_year': data.get('founded_year'),
            'logo_url': data.get('logo_url', ''),
            'yc_url': f"{self.BASE_URL}/companies/{data.get('slug', '')}",
            'scraped_at': datetime.now().isoformat(),
        }
    
    def _parse_company_html(self, element) -> Optional[Dict]:
        """Parse company data from HTML element"""
        try:
            # Extract company name
            name_elem = element.find(['h2', 'h3', 'a'])
            name = name_elem.get_text(strip=True) if name_elem else ''
            
            # Extract company URL
            link = element.find('a', href=True)
            company_url = urljoin(self.BASE_URL, link['href']) if link else ''
            
            # Extract description
            desc_elem = element.find('p') or element.find('div', class_=lambda x: x and 'description' in x.lower())
            description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Extract batch info
            batch_elem = element.find(text=lambda x: x and any(b in str(x) for b in ['W', 'S']) and any(c.isdigit() for c in str(x)))
            batch = batch_elem.strip() if batch_elem else ''
            
            if not name:
                return None
            
            return {
                'name': name,
                'batch': batch,
                'status': 'Active',
                'description': description,
                'long_description': '',
                'website': '',
                'location': '',
                'industry': '',
                'team_size': None,
                'founded_year': None,
                'logo_url': '',
                'yc_url': company_url,
                'scraped_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.warning(f"Error parsing HTML element: {e}")
            return None
    
    def save_to_json(self, filename: str = 'yc_companies.json'):
        """Save scraped data to JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.companies, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Saved {len(self.companies)} companies to {filename}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")
    
    def save_to_csv(self, filename: str = 'yc_companies.csv'):
        """Save scraped data to CSV file"""
        try:
            if not self.companies:
                logger.warning("No companies to save")
                return
            
            keys = self.companies[0].keys()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(self.companies)
            
            logger.info(f"✓ Saved {len(self.companies)} companies to {filename}")
        except Exception as e:
            logger.error(f"Failed to save CSV: {e}")
    
    def get_company_details(self, company_slug: str) -> Optional[Dict]:
        """
        Scrape detailed information for a specific company
        
        Args:
            company_slug: Company slug/identifier (e.g., 'airbnb')
        
        Returns:
            Detailed company information
        """
        url = f"{self.BASE_URL}/companies/{company_slug}"
        
        try:
            logger.info(f"Scraping details for: {company_slug}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract detailed information
            # This structure may vary, adjust as needed
            details = {
                'slug': company_slug,
                'url': url,
                'scraped_at': datetime.now().isoformat(),
            }
            
            # Add more detailed parsing as needed
            
            time.sleep(self.delay)
            return details
            
        except Exception as e:
            logger.error(f"Failed to get company details: {e}")
            return None


def main():
    """Example usage"""
    # Initialize scraper with 1 second delay between requests
    scraper = YCombinatorScraper(delay=1.0)
    
    # Example 1: Scrape all companies from Winter 2024 batch
    companies = scraper.scrape_companies(batch='W24', limit=50)
    
    # Example 2: Scrape companies by industry
    # companies = scraper.scrape_companies(industry='B2B', limit=100)
    
    # Example 3: Scrape all companies (no limit - use carefully!)
    # companies = scraper.scrape_companies()
    
    # Save results
    if companies:
        scraper.save_to_json('yc_companies.json')
        scraper.save_to_csv('yc_companies.csv')
        
        # Print sample
        print(f"\n✓ Scraped {len(companies)} companies")
        print("\nSample companies:")
        for company in companies[:5]:
            print(f"  - {company['name']} ({company['batch']})")
            print(f"    {company['description']}")
            print()


if __name__ == "__main__":
    main()
