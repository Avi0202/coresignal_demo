import requests
import json

API_URL = "https://mcp.coresignal.com/mcp"
API_KEY = "LJf8CqR5d2K0C8Tv1ys0K3tbVKrvaWXp"

headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

# Example MCP request body — check docs for exact "method" names you can call
payload = {
    "jsonrpc": "2.0",
    "method": "job_multi_source.search",
    "params": {
        "query": {
            "bool": {
                "must": [
                    {"match": {"title": "software engineer"}},
                    {"match": {"company_hq_country": "United States"}}
                ],
                "filter": [
                    {"range": {"created_at": {"gte": "now-30d/d"}}}
                ]
            },
            "size": 10
        }
    },
    "id": 1
}

response = requests.post(API_URL, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    print(json.dumps(result, indent=2))
else:
    print(f"Error {response.status_code}: {response.text}")
