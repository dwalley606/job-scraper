import requests
from bs4 import BeautifulSoup
import pandas as pd
from abc import ABC, abstractmethod
import argparse
import time

class JobScraper(ABC):
    @abstractmethod
    def scrape(self, position, location):
        pass

class IndeedScraper(JobScraper):
    def scrape(self, position, location):
        # Format URL
        position = position.replace(" ", "+")
        location = location.replace(" ", "+")
        url = f"https://www.indeed.com/jobs?q={position}&l={location}"
        
        # Enhanced headers to mimic a real browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        # Use a session to persist cookies
        session = requests.Session()
        try:
            # Add a small delay to avoid rate-limiting
            time.sleep(1)
            response = session.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to load page: {e}")
            return []
        
        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        
        # Find job cards
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        
        for card in job_cards:
            try:
                title = card.find("h2", class_="jobTitle").text.strip()
                company = card.find("span", attrs={"data-testid": "company-name"}).text.strip()
                location_elem = card.find("div", attrs={"data-testid": "text-location"})
                job_location = location_elem.text.strip() if location_elem else "Not listed"
                
                salary_elem = card.find("div", class_="metadata salary-snippet-container")
                salary = salary_elem.text.strip() if salary_elem else "Not listed"
                
                link = "https://www.indeed.com" + card.find("a", href=True)["href"]
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": job_location,
                    "salary": salary,
                    "link": link,
                    "source": "Indeed"
                })
            except (AttributeError, TypeError):
                continue
        
        return jobs

def save_to_csv(jobs, filename="jobs.csv"):
    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv(filename, index=False)
        print(f"Saved {len(jobs)} jobs to {filename}")
    else:
        print("No jobs found to save")

def main():
    parser = argparse.ArgumentParser(description="Job Scraper for developer roles")
    parser.add_argument("--position", default="full stack developer", help="Job title to search")
    parser.add_argument("--location", default="Remote", help="Job location")
    args = parser.parse_args()

    scraper = IndeedScraper()
    jobs = scraper.scrape(args.position, args.location)
    save_to_csv(jobs)

if __name__ == "__main__":
    main()