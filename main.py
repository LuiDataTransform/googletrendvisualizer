from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import time
from pytrends.request import TrendReq
import json

app = FastAPI(title="Google Trends API")

# Configure CORS so GitHub Pages can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you can restrict this to your GitHub Pages URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fetch_google_trends(keywords: list[str]):
    # Initialize pytrends with a timeout to handle rate limits
    try:
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing Pytrends: {str(e)}")
        
    try:
        pytrends.build_payload(keywords, cat=0, timeframe='today 5-y', geo='', gprop='')
        
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
                    time.sleep(wait_time)
                else:
                    raise e
        
        if df.empty:
            raise HTTPException(status_code=404, detail="Google Trends returned no data for the specified keywords.")
        
        if 'isPartial' in df.columns:
            df = df.drop(columns=['isPartial'])
            
        df.index = df.index.strftime('%Y-%m-%d')
        
        # Convert to a dictionary orientation that the frontend expects
        return json.loads(df.to_json(orient='index'))
        
    except HTTPException as h:
        raise h
    except Exception as e:
        if "429" in str(e):
            raise HTTPException(status_code=429, detail="Too Many Requests: Google is rate-limiting the server. Try again later.")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/trends")
def get_trends(keywords: str = Query(..., description="Comma-separated list of keywords")):
    keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
    
    if not keyword_list:
        raise HTTPException(status_code=400, detail="No valid keywords provided.")
        
    if len(keyword_list) > 5:
        raise HTTPException(status_code=400, detail="Google Trends only supports up to 5 keywords per request.")
        
    data = fetch_google_trends(keyword_list)
    return data

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Google Trends API is running. Use /api/trends?keywords=A,B"}
