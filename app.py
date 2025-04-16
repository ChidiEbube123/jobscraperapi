from flask import Flask, jsonify
import json
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import (
    RelevanceFilters, TimeFilters, TypeFilters,
    ExperienceLevelFilters, OnSiteOrRemoteFilters, SalaryBaseFilters
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


@app.route('/scrape', methods=['GET'])
def scrape_jobs():
    jobs = []

    def on_data(data: EventData):
        jobs.append({
            'title': data.title,
            'company': data.company,
            'company_link': data.company_link,
            'date': data.date,
            'date_text': data.date_text,
            'link': data.link,
            'insights': data.insights,
            'description_length': len(data.description)
        })

    def on_error(error):
        logging.error(f"[ON_ERROR] {error}")

    def on_end():
        logging.info("[ON_END]")

    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_binary_location=None,
        chrome_options=None,
        headless=True,
        max_workers=1,
        slow_mo=0.5,
        page_load_timeout=40
    )

    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    queries = [
        Query(
            options=QueryOptions(limit=2)
        ),
        Query(
            query='Engineer',
            options=QueryOptions(
                locations=['United States', 'Europe'],
                apply_link=True,
                skip_promoted_jobs=True,
                page_offset=2,
                limit=5,
                filters=QueryFilters(
                    company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.MONTH,
                    type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                    on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE],
                    experience=[ExperienceLevelFilters.MID_SENIOR],
                    base_salary=SalaryBaseFilters.SALARY_100K
                )
            )
        ),
    ]

    scraper.run(queries)

    return jsonify(jobs)
@app.route('/', methods=['GET'])
def home():
    return "herro"
if __name__ == '__main__':
    app.run(debug=True)
