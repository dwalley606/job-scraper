# Indeed Scraper
A Python-based web scraper to find developer jobs (full-stack, front-end, back-end) with specific tech stacks (JavaScript, TypeScript, Next.js, Supabase) on Indeed, designed to be extensible for other job boards.

## Setup
1. Clone the repo: `git clone https://github.com/your-username/indeed-scraper.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python scraper.py --position "full stack developer" --location "Remote"`

## Usage
- Customize `position` and `location` in `scraper.py` or via CLI.
- Output saved to `jobs.csv`.

## Future Plans
- Add scrapers for LinkedIn, ZipRecruiter, etc.
- Integrate with Supabase for job storage.
- Add filters for salary, experience level, etc.