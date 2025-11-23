# davis.food

Chronicling food reviews posted by Davis, a middle schooler who has gained fame on TikTok for critiquing his school lunches. 

🌐 **Live dashboard**: [davis.food](https://davis.food) (coming soon)

## About this project

This project extracts structured data from @davis_big_dawg's school lunch review videos and presents them in a modern, interactive dashboard.

**Features**:
- D3.js charts showing engagement and rating trends
- Real-time stats cards with key metrics
- Top posts by engagement
- Searchable, sortable table of all reviews
- Automated daily updates via GitHub Actions
- Modern, responsive design

The scripts use OpenAI's API to extract:
- Day number of the review
- Food items with names, categories, scores and comments
- Flags for posts needing manual review

## Files

### Data pipeline
- `fetch_archive.py` - Complete workflow to fetch posts, transcripts and reviews
- `extract_reviews.py` - Extract structured review data using OpenAI
- `calculate_stats.py` - Calculate statistics from extracted reviews
- `generate_dashboard_data.py` - Generate pre-computed stats for dashboard
- `upload_to_s3.py` - Upload data files to S3 for public access

### Dashboard
- `src/` - Eleventy static site source files
- `_site/` - Generated dashboard (deployed to GitHub Pages)

## Quick start

### 1. Install tiktools

```bash
pip install tiktools openai
```

### 2. Set up API keys

```bash
# Required: TikAPI key
export TIKAPI_KEY="your_tikapi_key_here"

# Optional: OpenAI key (for review extraction)
export OPENAI_API_KEY="your_openai_key_here"
```

Get your keys:
- TikAPI: https://tikapi.io
- OpenAI: https://platform.openai.com/api-keys

### 3. Fetch the complete archive

```bash
cd examples/food_reviews

# Fetch posts and transcripts
python fetch_archive.py

# Or fetch everything including AI-extracted reviews
python fetch_archive.py --extract-reviews
```

This will create:
```
data/
└── davis_big_dawg/
    ├── davis_big_dawg_posts.json       # Post metadata
    ├── davis_big_dawg_reviews.json     # Extracted reviews (if using --extract-reviews)
    └── transcripts/
        ├── 7575304937580547342.txt     # Individual transcripts
        └── davis_big_dawg_transcripts.json  # All transcripts
```

## Step-by-step workflow

### Option A: All-in-one script (recommended)

```bash
# Full workflow: posts + transcripts + reviews
python fetch_archive.py --extract-reviews

# Update mode (only fetch new content)
python fetch_archive.py --update --extract-reviews
```

### Option B: Manual steps

```bash
# Step 1: Fetch posts using tiktools
python -c "
from tiktools import fetch_user_posts
from pathlib import Path

fetch_user_posts(
    username='davis_big_dawg',
    output_file=Path('data/davis_big_dawg/davis_big_dawg_posts.json')
)
"

# Step 2: Extract transcripts
python -c "
from tiktools import extract_transcripts
from pathlib import Path

extract_transcripts(
    posts_file=Path('data/davis_big_dawg/davis_big_dawg_posts.json'),
    output_format='both',
    language='eng'
)
"

# Step 3: Extract reviews (requires OPENAI_API_KEY)
python extract_reviews.py data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json

# Step 4: Calculate statistics
python calculate_stats.py data/davis_big_dawg/davis_big_dawg_reviews.json
```

## Updating your archive

To fetch only new content since last run:

```bash
python fetch_archive.py --update --extract-reviews
```

This saves API costs by skipping content you already have.

## Example output

### Extracted review

```json
{
  "post_id": "7575304937580547342",
  "day_number": 30,
  "needs_review": false,
  "foods": [
    {
      "name": "burger on a biscuit",
      "category": "main_dish",
      "score": 6,
      "comments": "Kind of dry but still pretty good..."
    },
    {
      "name": "Tropical Lime Baha Blast",
      "category": "drink",
      "score": 8,
      "comments": "One of my favorite sodas..."
    }
  ]
}
```

### Statistics

```
Overall:
  Average score: 6.44/10
  Total items: 131
  
Average scores by category:
  drink    7.58/10 (13 items)
  dessert  7.40/10 (5 items)
  side     5.91/10 (47 items)
  
Trend: ↑ Improving (+0.42 points)
```

## Public data access

All data files are available for public access via S3. These files are updated daily via GitHub Actions:

**Dashboard stats** (pre-computed metrics):
```
https://stilesdata.com/davis.food/data/dashboard_stats.json
```

**Raw reviews** (structured review data):
```
https://stilesdata.com/davis.food/data/davis_big_dawg/davis_big_dawg_reviews.json
```

**Post metadata** (engagement stats, dates, URLs):
```
https://stilesdata.com/davis.food/data/davis_big_dawg/davis_big_dawg_posts.json
```

**Transcripts** (video transcriptions):
```
https://stilesdata.com/davis.food/data/davis_big_dawg/transcripts/davis_big_dawg_transcripts.json
```

### Uploading data to S3

To manually upload data files:

```bash
# Set AWS credentials
export MY_AWS_ACCESS_KEY_ID="your_key"
export MY_AWS_SECRET_ACCESS_KEY="your_secret"
export MY_DEFAULT_REGION="us-east-1"

# Upload all data files
python scripts/upload_to_s3.py
```

The script uploads with:
- Public read access
- Content-Type: application/json
- Cache-Control: max-age=3600

## Adapting this example

You can use this as a template for other types of content analysis:

1. Modify the OpenAI prompt in `extract_reviews.py` to extract different information
2. Adjust the categories and scoring system to match your content
3. Update `calculate_stats.py` to compute relevant statistics
4. Change the username in `fetch_archive.py` to analyze other creators

Example for different use cases:

```python
# Analyze a different creator
python fetch_archive.py --username "other_creator" --extract-reviews

# Just fetch and transcribe (no OpenAI)
python fetch_archive.py --username "creator_name"
```

## Command-line options

```bash
python fetch_archive.py --help

Options:
  --username USERNAME       TikTok username (default: davis_big_dawg)
  --output-dir DIR         Base directory for output (default: ./data)
  --update                 Only fetch new content
  --extract-reviews        Extract reviews using OpenAI
  --skip-transcripts       Only fetch posts, skip transcripts
```

## Requirements

- Python 3.8+
- tiktools package: `pip install tiktools`
- TikAPI key from https://tikapi.io
- Optional: OpenAI API key for review extraction

## Cost considerations

- **TikAPI**: Costs vary by plan, update mode reduces costs
- **OpenAI**: Using gpt-4o-mini is recommended for cost-effective extraction
- **Update mode**: Only processes new content to minimize API usage

## Notes

**Review numbering**: The dashboard uses an accurate chronological review count (1, 2, 3...) rather than Davis's stated day numbers, which sometimes contain errors or repeats. For example, Davis said "day 26" twice in a row (Nov 7 and Nov 10, 2025). The original day numbers from his videos are preserved in the data for reference.

**Transcript limitations**: TikTok's ASR may misinterpret words (e.g., "Baha Blast" → "Brawha Blast"). For journalistic or public-facing analysis, manually verify transcripts for proper nouns and brand names.

**Non-original audio**: Videos using TikTok sounds may contain song lyrics instead of speech. The scripts flag these videos automatically.

