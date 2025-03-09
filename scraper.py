import aiohttp
import asyncio
import json
import random
from github_api import fetch
from utils import save_progress, load_progress

def scrape_github(token_queue, token_blacklist, token_usage, pages=100, filename="github_training_data.jsonl", process_id=0, total_processes=1):
    vulnerabilities = []
    completed_pages = load_progress(filename)
    queries = ["security+vulnerability", "python+security", "insecure+code", "python+exploit"]

    async def async_scrape():
        async with aiohttp.ClientSession() as session:
            for i in range(process_id, pages, total_processes):
                if i + 1 in completed_pages:
                    print(f"Skipping already processed page {i + 1}")
                    continue

                query = random.choice(queries)
                url = f"https://api.github.com/search/code?q={query}+language:python&page={i + 1}&per_page=100"
                response_text = await fetch(session, url, token_queue, token_blacklist, token_usage)

                if not response_text:
                    continue

                data = json.loads(response_text)
                code_tasks = []
                for item in data.get("items", []):
                    file_url = item.get("html_url", "")
                    raw_url = file_url.replace("github.com", "raw.githubusercontent.com").replace("blob/", "")
                    code_tasks.append(fetch(session, raw_url, token_queue, token_blacklist, token_usage))
                    await asyncio.sleep(random.uniform(0.5, 2))

                codes = await asyncio.gather(*code_tasks)

                for j, item in enumerate(data.get("items", [])):
                    if codes[j]:
                        vulnerabilities.append({"description": item.get("name", ""), "link": item.get("html_url", ""), "code": codes[j]})

                save_progress(filename, i + 1, vulnerabilities)
                await asyncio.sleep(random.uniform(1, 3))

    asyncio.run(async_scrape())
    return vulnerabilities
