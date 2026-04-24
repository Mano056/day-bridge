import requests
from dotenv import load_dotenv
import os

load_dotenv()

def create_notion_page(title, content):
    notion_url = "https://api.notion.com/v1/pages"
    notion_page_id = os.getenv("NOTION_PAGE_ID")
    notion_access_token = os.getenv("NOTION_ACCESS_TOKEN")

    if not notion_page_id or not notion_access_token:
        raise ValueError("Missing NOTION_PAGE_ID or NOTION_ACCESS_TOKEN")
    
    payload = {
        "parent": {"page_id": notion_page_id},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": content}
                        }
                    ]
                }
            }
        ]
    }

    headers = {
        "Notion-Version": "2026-03-11",
        "Authorization": f"Bearer {notion_access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(notion_url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    return {
        "success": True,
        "id": data.get("id"),
        "url": data.get("url")
    }

def search_notion(query):
    url = "https://api.notion.com/v1/search"
    notion_access_token = os.getenv("NOTION_ACCESS_TOKEN")

    if not notion_access_token:
        raise ValueError("Missing NOTION_ACCESS_TOKEN")
    
    payload = {"query": query}
    headers = {
        "Authorization": "Bearer " + notion_access_token,
        "Notion-Version": "2026-03-11",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def parse_notion_results(response):
    results = response.get("results", [])
    search_results = []

    for result in results:
        if result.get("object") != "page":
            continue
        
        title = "Untitled"
        properties = result.get("properties", {})

        for prop in properties.values():
            if prop.get("type") == "title":
                title_items = prop.get("title", [])
                if title_items:
                    title = "".join(
                        item.get("plain_text", "")
                        for item in title_items
                    ).strip() or "Untitled"
                break

        search_results.append({
            "title": title,
            "url": result.get("url", "")
        })

    return search_results