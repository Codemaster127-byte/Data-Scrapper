import aiohttp
import asyncio
import time
import json
import random

def get_headers(token):
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}"
    }

async def fetch(session, url, token_queue, token_blacklist, token_usage, retry_count=3):
    for attempt in range(retry_count):
        if token_queue.empty():
            print("❌ No available tokens, waiting...")
            await asyncio.sleep(60)
            continue

        token = token_queue.get()

        if token in token_blacklist and time.time() < token_blacklist[token]:
            print(f"⚠️ Token {token[:10]} is blacklisted. Skipping...")
            token_queue.put(token)
            await asyncio.sleep(1)
            continue

        headers = get_headers(token)

        print(f"🔍 Attempting request to: {url}")
        async with session.get(url, headers=headers) as response:
            print(f"📡 Response Status: {response.status} | Token: {token[:10]}...")

            if response.status == 200:
                token_queue.put(token)
                token_usage[token] = token_usage.get(token, 0) + 1
                return await response.text()

            elif response.status == 401:
                print(f"❌ Unauthorized request. Blacklisting token {token[:10]}...")
                token_blacklist[token] = time.time() + 600  # Blacklist for 10 mins

            elif response.status in [403, 429]:  # Rate limit hit
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait_time = max(reset_time - time.time(), 1)
                print(f"⚠️ Rate limit exceeded. Token {token[:10]} blacklisted for {wait_time:.2f} seconds...")
                token_blacklist[token] = time.time() + wait_time

            elif response.status == 422:
                print(f"⚠️ Skipping {url} due to status 422 (Unprocessable Entity)")

            else:
                print(f"❓ Unexpected status {response.status} for {url}")

            token_queue.put(token)
            await asyncio.sleep(random.uniform(1, 3))

    print(f"❌ Failed to fetch {url} after {retry_count} attempts.")
    return None
