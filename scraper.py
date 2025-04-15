from bs4 import BeautifulSoup
import pandas as pd
from abc import ABC, abstractmethod
import argparse
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import pickle
import os

class JobScraper(ABC):
    @abstractmethod
    def scrape(self, position, location):
        pass

class IndeedScraper(JobScraper):
    def scrape(self, position, location):
        position = position.replace(" ", "+")
        location = location.replace(" ", "+")
        url = f"https://www.indeed.com/jobs?q={position}&l={location}"
        cookie_file = "indeed_cookies.pkl"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        service = Service(ChromeDriverManager().install())
        driver = None
        jobs = []
        try:
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            if os.path.exists(cookie_file):
                print("Loading saved cookies for Indeed...")
                driver.get("https://www.indeed.com")
                cookies = pickle.load(open(cookie_file, "rb"))
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        continue
                driver.refresh()
            
            driver.get(url)
            print("Check Indeed in the browser and click any CAPTCHA...")
            time.sleep(15)  # Longer wait for CAPTCHA
            
            pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))  # Extra time for JS
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
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
                    
        except Exception as e:
            print(f"Indeed failed: {e}")
            if driver:
                with open("indeed_error.html", "w") as f:
                    f.write(driver.page_source)
                print("Saved page source to indeed_error.html")
        finally:
            if driver:
                driver.quit()
        
        return jobs

class ZipRecruiterScraper(JobScraper):
    def scrape(self, position, location):
        position = position.replace(" ", "-")
        location = location.replace(" ", "-")
        url = f"https://www.ziprecruiter.com/jobs-search?search={position}&location={location}"
        cookie_file = "ziprecruiter_cookies.pkl"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        driver = None
        jobs = []
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            if os.path.exists(cookie_file):
                print("Loading saved cookies for ZipRecruiter...")
                driver.get("https://www.ziprecruiter.com")
                cookies = pickle.load(open(cookie_file, "rb"))
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        continue
                driver.refresh()
            
            driver.get(url)
            print("Check ZipRecruiter in the browser and click any CAPTCHA...")
            time.sleep(15)
            
            pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.find_all("article", class_="job_result")
            
            for card in job_cards:
                try:
                    title_elem = card.find("h2", class_="job_title")
                    title = title_elem.text.strip() if title_elem else "Not listed"
                    company_elem = card.find("span", class_="company_name")
                    company = company_elem.text.strip() if company_elem else "Not listed"
                    location_elem = card.find("span", class_="job_location")
                    job_location = location_elem.text.strip() if location_elem else "Not listed"
                    salary_elem = card.find("span", class_="job_salary")
                    salary = salary_elem.text.strip() if salary_elem else "Not listed"
                    link_elem = card.find("a", class_="job_link")
                    link = link_elem["href"] if link_elem else "Not listed"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": salary,
                        "link": link,
                        "source": "ZipRecruiter"
                    })
                except (AttributeError, TypeError):
                    continue
        
        except Exception as e:
            print(f"ZipRecruiter failed: {e}")
            if driver:
                with open("ziprecruiter_error.html", "w") as f:
                    f.write(driver.page_source)
                print("Saved page source to ziprecruiter_error.html")
        finally:
            if driver:
                driver.quit()
        
        return jobs

class SimplyHiredScraper(JobScraper):
    def scrape(self, position, location):
        position = position.replace(" ", "+")
        location = location.replace(" ", "+")
        url = f"https://www.simplyhired.com/search?q={position}&l={location}"
        cookie_file = "simplyhired_cookies.pkl"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        driver = None
        jobs = []
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            if os.path.exists(cookie_file):
                print("Loading saved cookies for SimplyHired...")
                driver.get("https://www.simplyhired.com")
                cookies = pickle.load(open(cookie_file, "rb"))
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        continue
                driver.refresh()
            
            driver.get(url)
            print("Check SimplyHired in the browser and click any CAPTCHA...")
            time.sleep(15)
            
            pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.find_all("li", class_="job-listing")
            
            for card in job_cards:
                try:
                    title_elem = card.find("a", class_="card-link")
                    title = title_elem.text.strip() if title_elem else "Not listed"
                    company_elem = card.find("span", class_="jobposting-company")
                    company = company_elem.text.strip() if company_elem else "Not listed"
                    location_elem = card.find("span", class_="jobposting-location")
                    job_location = location_elem.text.strip() if location_elem else "Not listed"
                    salary_elem = card.find("span", class_="jobposting-salary")
                    salary = salary_elem.text.strip() if salary_elem else "Not listed"
                    link = title_elem["href"] if title_elem else "Not listed"
                    if link != "Not listed":
                        link = "https://www.simplyhired.com" + link
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": salary,
                        "link": link,
                        "source": "SimplyHired"
                    })
                except (AttributeError, TypeError):
                    continue
        
        except Exception as e:
            print(f"SimplyHired failed: {e}")
            if driver:
                with open("simplyhired_error.html", "w") as f:
                    f.write(driver.page_source)
                print("Saved page source to simplyhired_error.html")
        finally:
            if driver:
                driver.quit()
        
        return jobs

class MonsterScraper(JobScraper):
    def scrape(self, position, location):
        position = position.replace(" ", "-")
        location = location.replace(" ", "-")
        url = f"https://www.monster.com/jobs/search?q={position}&where={location}"
        cookie_file = "monster_cookies.pkl"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-maximized")
        
        service = Service(ChromeDriverManager().install())
        driver = None
        jobs = []
        
        try:
            driver = webdriver.Chrome(service=service, options=options)
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True)
            
            if os.path.exists(cookie_file):
                print("Loading saved cookies for Monster...")
                driver.get("https://www.monster.com")
                cookies = pickle.load(open(cookie_file, "rb"))
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except:
                        continue
                driver.refresh()
            
            driver.get(url)
            print("Check Monster in the browser and click any CAPTCHA...")
            time.sleep(15)
            
            pickle.dump(driver.get_cookies(), open(cookie_file, "wb"))
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 3))
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.find_all("div", class_="job-card")
            
            for card in job_cards:
                try:
                    title_elem = card.find("h2", class_="job-title")
                    title = title_elem.text.strip() if title_elem else "Not listed"
                    company_elem = card.find("span", class_="company-name")
                    company = company_elem.text.strip() if company_elem else "Not listed"
                    location_elem = card.find("span", class_="location")
                    job_location = location_elem.text.strip() if location_elem else "Not listed"
                    salary_elem = card.find("span", class_="salary")
                    salary = salary_elem.text.strip() if salary_elem else "Not listed"
                    link_elem = card.find("a", class_="job-link")
                    link = link_elem["href"] if link_elem else "Not listed"
                    
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": job_location,
                        "salary": salary,
                        "link": link,
                        "source": "Monster"
                    })
                except (AttributeError, TypeError):
                    continue
        
        except Exception as e:
            print(f"Monster failed: {e}")
            if driver:
                with open("monster_error.html", "w") as f:
                    f.write(driver.page_source)
                print("Saved page source to monster_error.html")
        finally:
            if driver:
                driver.quit()
        
        return jobs

def save_to_csv(jobs, filename="jobs.csv"):
    if jobs:
        df = pd.DataFrame(jobs)
        df.to_csv(filename, index=False)
        print(f"Saved {len(jobs)} jobs to {filename}")
    else:
        print("No jobs found to save")

def main():
    parser = argparse.ArgumentParser(description="Job Scraper for data analyst roles")
    parser.add_argument("--position", default="data analyst", help="Job title to search")
    parser.add_argument("--location", default="New York", help="Job location")
    args = parser.parse_args()

    jobs = []
    
    print("Trying ZipRecruiter first...")
    zip_scraper = ZipRecruiterScraper()
    jobs.extend(zip_scraper.scrape(args.position, args.location))
    
    if not jobs:
        print("ZipRecruiter’s stonewalling, going for SimplyHired...")
        simply_scraper = SimplyHiredScraper()
        jobs.extend(simply_scraper.scrape(args.position, args.location))
    
    if not jobs:
        print("SimplyHired’s not cooperating, hitting Monster...")
        monster_scraper = MonsterScraper()
        jobs.extend(monster_scraper.scrape(args.position, args.location))
    
    if not jobs:
        print("Monster flopped, last shot with Indeed...")
        indeed_scraper = IndeedScraper()
        jobs.extend(indeed_scraper.scrape(args.position, args.location))
    
    save_to_csv(jobs)

if __name__ == "__main__":
    main()