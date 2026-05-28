# Google Trends Visualizer

A complete, self-contained project that fetches real-time Google Trends interest data using Python and visualizes it in a beautiful, modern standalone HTML page.

## Project Structure

- `main.py`: A FastAPI backend that handles the `pytrends` requests and returns JSON to the browser.
- `index.html`: A 100% self-contained frontend visualization built with Vanilla JS, CSS variables, and Chart.js.
- `requirements.txt`: Python dependencies required for the backend.

## Setup Instructions

### 1. Prerequisites
You need Python 3.7+ installed on your system.

### 2. Install Dependencies
It's recommended to create a virtual environment first.

```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\activate
# OR (Mac/Linux)
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

## How to Run Locally

### Step 1: Start the Backend Server
Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```
The API will now be running at `http://localhost:8000`.

### Step 2: View the Visualization
You can now open `index.html` directly in your browser or run a simple local web server to view it:
```bash
python -m http.server 3000
```
Then navigate to `http://localhost:3000`. The chart will automatically query your local FastAPI backend!

## Deployment

### 1. Deploy the Backend (FastAPI)
1. Push your code to GitHub.
2. Sign up for a free account on [Render](https://render.com/) or [Vercel](https://vercel.com/).
3. Create a new Web Service and link your GitHub repository.
4. Set the Start Command to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Once deployed, copy the public URL (e.g., `https://my-trends-api.onrender.com`).
6. Update the `API_BASE_URL` variable in `index.html` to point to your new live backend URL.

### 2. Deploy the Frontend (GitHub Pages)
Since the frontend is entirely static (HTML/CSS/JS), it's perfectly suited for GitHub Pages!
1. Commit the updated `index.html` with your production API URL to GitHub.
2. Go to your repository **Settings** > **Pages**.
3. Select the `main` branch as the source and click Save.
4. Your dynamic visualization is now live!

## Known Limitations of Pytrends

- **Rate Limiting**: Google Trends aggressively rate-limits IPs. If you make too many requests in a short period, you will receive an HTTP 429 Error. The script includes delays and retries to mitigate this, but if you hit the limit, you may need to wait an hour or change your IP.
- **Max 5 Keywords**: The Google Trends API only allows comparing up to 5 keywords per request.
- **Data Granularity**: For the default 5-year timeframe (`today 5-y`), data points are aggregated weekly. Daily data is only available for shorter timeframes (e.g., 90 days).
