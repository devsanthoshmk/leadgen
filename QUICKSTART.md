# Quick Start Guide - LeadGen

Get up and running in 5 minutes.

## 🚀 Step 1: Install Python Module (1 min)

```bash
cd /path/to/leadgen

# Install dependencies
pip install -r requirements.txt
```

## 📝 Step 2: Test CLI (2 min)

```bash
# Simple test search
python cli.py search-keywords \
  --keywords "Sales Director" \
  --limit 10 \
  --output test_results.json

# Check results
cat test_results.json
```

## 🌐 Step 3: Run React Web App (1 min)

```bash
cd reactjs

# Install dependencies
npm install

# Start dev server
npm start

# Opens http://localhost:3000
```

**Note**: Web version shows mock data. Real data requires Android.

## 📱 Step 4: Build Android App (Optional)

See `ANDROID_SETUP.md` for complete guide.

Quick steps:
1. Open Android Studio
2. Create new project
3. Add Chaquopy dependency
4. Copy `leadgen_core/` folder
5. Build and run

---

## 🎯 Common Commands

### Search by Industry
```bash
python cli.py search-industry \
  --industry "Software Development" \
  --location "San Francisco" \
  --limit 50 \
  --output leads.json
```

### Search by Company
```bash
python cli.py search-company \
  --company "Google" \
  --limit 20 \
  --output google_leads.csv
```

### Search by Location
```bash
python cli.py search-location \
  --location "New York" \
  --keywords "Sales" \
  --output ny_leads.json
```

### Batch Search
```bash
# Create queries.txt:
# Industry 1
# Industry 2
# Industry 3

python cli.py batch \
  --file queries.txt \
  --limit 50 \
  --output all_leads.json
```

---

## 📊 Check Your Results

```bash
# View JSON results
cat results.json

# Pretty print JSON
python -m json.tool results.json

# Count leads
jq 'length' results.json

# Filter by score
jq '.[] | select(.lead_score > 70)' results.json
```

---

## 🔑 Configure API Keys

### LinkedIn Session
Create session interactively:
```python
from leadgen_core import LeadScraper
scraper = LeadScraper()
# Will prompt for LinkedIn login
```

### ScrapeGraphAI
```bash
# Get free API key from scrapegraphai.com
export SCRAPEGRAPH_API_KEY="your_key_here"

# Test in Python
python -c "
from leadgen_core import LeadScraper
scraper = LeadScraper(scrapegraph_api_key='your_key')
"
```

---

## 💡 Usage Tips

### Performance
- Start with `--limit 10` for testing
- Increase to 50 for real campaigns
- Use batch search for multiple queries
- Results are cached locally

### Data Quality
- Leads are automatically scored (0-100)
- High score (75+) = hot leads
- Email validation ensures deliverability
- Phone numbers are parsed/validated

### Export Options
```bash
# Export as JSON
python cli.py search-industry --industry "Tech" --output leads.json

# Export as CSV
python cli.py search-industry --industry "Tech" --output leads.csv

# Excel-friendly CSV
# Open .csv in Excel/Sheets directly
```

---

## 🆘 Troubleshooting

**"Module not found" error:**
```bash
pip install -r requirements.txt
```

**LinkedIn not working:**
```bash
# Delete old session and create new one
rm linkedin_session.json
python cli.py search-industry --industry "Tech"
# Will prompt for login
```

**API rate limit:**
```bash
# Slow down requests
# Script has built-in delays
# Or use fewer results per query
```

---

## 📚 Next Steps

1. **Customize Search**: Edit `search_by_*` functions in `leadgen_core/scraper.py`
2. **Improve Scoring**: Modify `Lead.calculate_lead_score()` in `models.py`
3. **Add Data Sources**: Create new scrapers in `leadgen_core/`
4. **Build Android**: Follow `ANDROID_SETUP.md`
5. **Deploy Web**: Host React build on Firebase/Vercel

---

## 📞 Need Help?

- Check `README.md` for full documentation
- See `ANDROID_SETUP.md` for mobile setup
- Review component code for customization
- Check Python logs for errors:

```bash
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

---

**Ready to generate leads! 🎯**
