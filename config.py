import os


def get_tokens():
    tokens = os.getenv("GITHUB_TOKENS")
    if not tokens:
        print("No GitHub tokens found. Please set the GITHUB_TOKENS environment variable.")
        exit(1)
    print(len(tokens.split(",")))
    return tokens.split(",")


def get_headers(token):
    return {"Accept": "application/vnd.github.v3+json", "Authorization": f"Bearer {token}"}
