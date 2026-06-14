# 🚀 Deploy Sentinel Zero Backend → Hugging Face Spaces

## Step 1 — Create HF Space

1. Go to https://huggingface.co/new-space
2. Set **Space name:** `sentinel-zero`
3. Set **SDK:** Docker
4. Set **Visibility:** Public
5. Click "Create Space"

## Step 2 — Clone the HF Space repo

```bash
git clone https://huggingface.co/spaces/YOUR_HF_USERNAME/sentinel-zero
cd sentinel-zero
```

## Step 3 — Copy files into the HF Space repo

From the root of this project, copy:

```
hf_space/Dockerfile       → Dockerfile
hf_space/README.md        → README.md
app.py                    → app.py
requirements.txt          → requirements.txt
core/                     → core/
sift_mcp_server/          → sift_mcp_server/
demo_data/                → demo_data/
```

Quick copy command (run from project root):
```bash
cp hf_space/Dockerfile   ../sentinel-zero/Dockerfile
cp hf_space/README.md    ../sentinel-zero/README.md
cp app.py                ../sentinel-zero/app.py
cp requirements.txt      ../sentinel-zero/requirements.txt
cp -r core               ../sentinel-zero/core
cp -r sift_mcp_server    ../sentinel-zero/sift_mcp_server
cp -r demo_data          ../sentinel-zero/demo_data
```

## Step 4 — Add GEMINI_API_KEY as Space Secret

1. Go to your Space → **Settings** tab
2. Scroll to **Variables and secrets**
3. Click **New secret**
4. Name: `GEMINI_API_KEY`
5. Value: your Gemini API key
6. Save

> ⚠️ NEVER put the API key in code or Dockerfile

## Step 5 — Push to HF

```bash
cd ../sentinel-zero
git add .
git commit -m "Deploy Sentinel Zero backend"
git push
```

HF Space will build the Docker image automatically (~2-3 minutes).

## Step 6 — Get your Space URL

Your backend URL will be:
```
https://YOUR_HF_USERNAME-sentinel-zero.hf.space
```

## Step 7 — Update Frontend

In `frontend/app.js`, find this line and update with your HF URL:
```javascript
: 'https://REPLACE_WITH_YOUR_HF_SPACE_URL';
```

Replace with:
```javascript
: 'https://YOUR_HF_USERNAME-sentinel-zero.hf.space';
```

Then commit and push to GitHub (Vercel auto-deploys frontend).
