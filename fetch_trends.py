import argparse
import sys
import pandas as pd
import time
from pytrends.request import TrendReq
from requests.exceptions import Timeout

def fetch_google_trends(keywords, output_file="trends_data.json"):
    """
    Fetches Google Trends interest-over-time data for the given keywords
    and saves the result as a JSON file.
    """
    print(f"Initializing Google Trends request for keywords: {keywords}...")
    
    # Initialize pytrends with a timeout to handle rate limits
    # Note: We don't use the built-in retries parameter because it relies on deprecated urllib3 'method_whitelist'
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
    except Exception as e:
        print(f"Error initializing Pytrends: {e}")
        return False
        
    try:
        # Build the payload for the specified keywords (last 5 years by default)
        pytrends.build_payload(keywords, cat=0, timeframe='today 5-y', geo='', gprop='')
        
        print("Fetching interest over time data...")
        
        # Manual retry mechanism for rate limits (HTTP 429)
        max_retries = 3
        df = pd.DataFrame()
        
        for attempt in range(max_retries):
            try:
                df = pytrends.interest_over_time()
                break
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limited (429). Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    raise e
        
        # Check if the DataFrame is empty (no data returned)
        if df.empty:
            print("Warning: Google Trends returned no data for the specified keywords.")
            return False
        
        # Pytrends adds an 'isPartial' column, we can drop it as it's not needed for visualization
        if 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
            
        # Ensure the index (date) is explicitly converted to string for JSON serialization
        df.index = df.index.strftime('%Y-%m-%d')
        
        # Export to JSON using orient='index' to maintain the date mapping properly
        df.to_json(output_file, orient='index')
        
        print("\n[SUCCESS]")
        print(f"Successfully fetched data for {len(df)} time periods.")
        print(f"Data saved to {output_file}")
        
        # Print a small preview of the data
        print("\nData Summary (Last 5 rows):")
        print(df.tail(5).to_string())
        
        return True
        
    except Timeout:
        print("Error: The request timed out. Google Trends might be rate-limiting you. Try again later.")
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        if "429" in str(e):
            print("\nNote: HTTP 429 means 'Too Many Requests'. Google is rate-limiting your IP.")
            print("Consider taking a break before trying again.")
    return False

def main():
    parser = argparse.ArgumentParser(description="Fetch Google Trends data for a list of keywords.")
    parser.add_argument(
        "--keywords", 
        type=str, 
        default="Python,JavaScript", 
        help="Comma-separated list of keywords to fetch (max 5). Example: 'Python,JavaScript'"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="trends_data.json",
        help="Output JSON file name (default: trends_data.json)"
    )
    
    args = parser.parse_args()
    
    # Parse keywords into a list
    keyword_list = [k.strip() for k in args.keywords.split(",") if k.strip()]
    
    # Pytrends only allows a maximum of 5 keywords per request
    if len(keyword_list) > 5:
        print("Error: Google Trends only supports up to 5 keywords per request.")
        print(f"You provided {len(keyword_list)} keywords. Please reduce the list.")
        sys.exit(1)
        
    if not keyword_list:
        print("Error: No keywords provided.")
        sys.exit(1)
        
    fetch_google_trends(keyword_list, args.output)

if __name__ == "__main__":
    main()
