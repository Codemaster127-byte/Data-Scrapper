from multiprocessing import Pool, Manager
from config import get_tokens
from scraper import scrape_github

def run_scraper(process_id, total_processes, token_queue, token_blacklist, token_usage):
    scrape_github(token_queue, token_blacklist, token_usage, pages=100, process_id=process_id, total_processes=total_processes)

if __name__ == "__main__":
    tokens = get_tokens()
    num_processes = min(len(tokens), 5)

    with Manager() as manager:
        token_queue = manager.Queue()
        token_blacklist = manager.dict()
        token_usage = manager.dict()

        for token in tokens:
            token_queue.put(token)
            token_usage[token] = 0  # Initialize count

        with Pool(num_processes) as pool:
            pool.starmap(run_scraper, [(i, num_processes, token_queue, token_blacklist, token_usage) for i in range(num_processes)])

        # Convert multiprocessing dict to normal dict
        token_usage_dict = dict(token_usage)

    print("\n--- Token Usage Statistics ---")
    for token, count in token_usage_dict.items():
        print(f"Token {token[:10]}... used {count} times")
    print("GitHub scraping complete.")
