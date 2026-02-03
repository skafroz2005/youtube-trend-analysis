import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()

def run_command(command):
    """Helper to run subprocess commands safely on Windows"""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            encoding='utf-8', 
            errors='ignore' # Critical for handling progress bars
        )
        return result
    except Exception as e:
        print(f"Subprocess failed: {e}")
        return None

def trigger_scraping_channels(api_key, channel_urls, num_of_posts, start_date, end_date, order_by, country):
    dataset_id = "gd_lk56epmy2i5g7lzu0k"
    endpoint = f"https://api.brightdata.com/datasets/v3/trigger?dataset_id={dataset_id}&include_errors=true&type=discover_new&discover_by=url"

    # Filter empty URLs
    valid_urls = [url for url in channel_urls if url.strip()]
    if not valid_urls:
        return None

    payload = [
        {
            "url": url,
            "num_of_posts": num_of_posts,
            "start_date": start_date,
            "end_date": end_date,
            "order_by": order_by,
            "country": country
        }
        for url in valid_urls
    ]

    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload),
        endpoint
    ]

    result = run_command(command)
    if result and result.returncode == 0:
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            print("Failed to parse trigger response.")
            return None
    return None

def get_progress(api_key, snapshot_id):
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    ]

    result = run_command(command)
    if result and result.returncode == 0:
        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return None
    return None

def get_output(api_key, snapshot_id, format="json"):
    command = [
        "curl",
        "-H", f"Authorization: Bearer {api_key}",
        f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format={format}"
    ]

    result = run_command(command)

    if result and result.returncode == 0:
        if not result.stdout or not result.stdout.strip():
            print("Bright Data returned empty output.")
            return []

        try:
            # ✅ CORRECT: Parse as one block
            data = json.loads(result.stdout.strip())
            return data if isinstance(data, list) else [data]
        except json.JSONDecodeError:
            print("Warning: JSON block parse failed. Trying fallback...")
            try:
                lines = result.stdout.strip().split("\n")
                return [json.loads(line) for line in lines if line.strip()]
            except:
                print("CRITICAL: Could not parse output.")
                return []
    else:
        if result:
            print(f"Error: {result.stderr}")
        return []