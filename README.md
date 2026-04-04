# LeadGen - B2B Lead Generation Platform
## Chaquopy + React + Python for Android + Web

A comprehensive lead generation platform for sales teams, combining LinkedIn scraping, Google Maps business discovery, and ScrapeGraphAI enrichment. Works both as a web app and native Android app using Chaquopy.

---

## 📋 Features

### Search Capabilities
- **Industry Search**: Find leads by industry and location
- **Company Search**: Get contacts from specific companies
- **Location Search**: Discover leads in geographic areas
- **Advanced Keywords**: Search by job titles, skills, or keywords

### Data Sources
1. **LinkedIn** (Primary) - Professional contacts and company info
2. **Google Maps** (Secondary) - Local businesses and reviews
3. **ScrapeGraphAI** (Enrichment) - Website data extraction (fallback)

### Lead Management
- **Lead Database**: Store and manage all discovered leads
- **Scoring System**: Automatic lead score calculation (0-100)
- **Contact Tracking**: Email, phone, LinkedIn profiles
- **Sales Status**: Track lead status through sales funnel
- **Notes**: Salesperson notes for each lead

### Sales Analytics
- **Lead Scoring**: Hot/Warm/Cold classification
- **Status Distribution**: View leads by sales stage
- **Industry Analytics**: Leads grouped by industry
- **Sales Funnel**: Conversion metrics and funnel analysis
- **Export**: Download leads as JSON or CSV

### UI/UX
- **Modern Dashboard**: Clean, professional interface
- **Mobile Responsive**: Works on desktop and tablets
- **Real-time Updates**: Live analytics and search results
- **Search Filters**: Sort and filter leads instantly

---

## 🏗️ Project Structure

```
leadgen/
├── leadgen_core/                    # Python core module
│   ├── __init__.py
│   ├── models.py                   # Lead, ScrapeSource, LeadStatus
│   ├── scraper.py                  # Main scraper orchestrator
│   ├── linkedin_scraper.py         # LinkedIn integration
│   ├── gmap_scraper.py             # Google Maps integration
│   ├── scrapegraph_adapter.py      # ScrapeGraphAI integration
│   ├── enricher.py                 # Multi-source enrichment
│   └── android_bridge.py           # Android/Chaquopy bridge
├── cli.py                          # CLI tool for desktop testing
├── reactjs/                         # React web UI
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── components/
│   │   │   ├── SearchPanel.jsx
│   │   │   ├── LeadsTable.jsx
│   │   │   ├── LeadDetail.jsx
│   │   │   ├── Analytics.jsx
│   │   │   └── Navigation.jsx
│   │   └── styles/
│   ├── package.json
│   └── public/
├── ANDROID_SETUP.md                # Android setup guide
└── README.md                       # This file
```

---

## 🚀 Quick Start

### 1. Install Python Core Module

```bash
cd leadgen/

# Install dependencies
pip install -r requirements.txt

# Or install individual packages
pip install selenium beautifulsoup4 requests lxml
```

### 2. CLI Usage (Desktop Testing)

```bash
# Search by industry
python cli.py search-industry \
  --industry "Software Development" \
  --location "San Francisco" \
  --limit 50 \
  --output results.json

# Search by company
python cli.py search-company \
  --company "Google" \
  --limit 20 \
  --output google_leads.csv

# Search by location
python cli.py search-location \
  --location "New York" \
  --keywords "Sales Manager" \
  --output ny_sales.json

# Batch search from file
python cli.py batch \
  --file queries.txt \
  --type industry \
  --limit 50 \
  --output batch_results.json
```

**Query file format** (`queries.txt`):
```
Software Development
Marketing
Sales Management
Product Management
```

### 3. React Web App

```bash
cd reactjs/

# Install dependencies
npm install

# Development
npm start          # Runs on http://localhost:3000

# Production build
npm run build      # Creates optimized build
```

**Note**: Web version uses mock Python responses. For real data, use the Android app with Chaquopy.

### 4. Android App with Chaquopy

See `ANDROID_SETUP.md` for complete Android setup guide.

Quick overview:
1. Create Android Studio project
2. Add Chaquopy dependency
3. Copy `leadgen_core/` to Python path
4. Set up WebView with React UI
5. Use `PythonBridge` for Android/Python communication
6. Build and run on Android device

---

## 🔧 Configuration

### LinkedIn Setup

To use the LinkedIn scraper, you need a session file:

```bash
# Create LinkedIn session (one-time setup)
# Use your credentials to create linkedin_session.json
# Then reference it:

python -c "
from leadgen_core import LeadScraper
scraper = LeadScraper(linkedin_session_file='linkedin_session.json')
"
```

### ScrapeGraphAI Setup

Get free API key and set environment variable:

```bash
export SCRAPEGRAPH_API_KEY="your_api_key_here"

# Or pass directly:
from leadgen_core import LeadScraper
scraper = LeadScraper(scrapegraph_api_key="your_key")
```

---

## 📊 Lead Data Model

Each lead includes:

```python
Lead(
    # Core Info
    company_name: str,
    contact_name: str,
    job_title: str,
    email: str,
    phone: str,
    linkedin_url: str,

    # Company Details
    industry: str,
    location: str,
    company_size: str,
    revenue_estimate: str,

    # Sales Tracking
    lead_score: int,          # 0-100
    status: LeadStatus,       # new, contacted, qualified, etc.
    notes: str,               # Salesperson notes

    # Metadata
    source: ScrapeSource,     # LinkedIn, GMaps, ScrapeGraph
    created_at: str,
    last_updated: str
)
```

### Lead Scoring

Automatic scoring (0-100) based on:
- ✓ Valid email (+20)
- ✓ Phone number (+15)
- ✓ LinkedIn profile (+15)
- ✓ Complete contact info (+10)
- ✓ Company details (+15)
- ✓ Revenue estimate (+10)

---

## 🔗 Python Bridge (Android)

### WebView Integration

In React, send messages to Python:

```javascript
// React Component
const PythonBridge = {
  send: async (action, params) => {
    const message = JSON.stringify({ action, params });
    const response = await window.Android.bridge(message);
    return JSON.parse(response);
  }
};

// Search for leads
const result = await PythonBridge.send('search_industry', {
  industry: 'Software Development',
  location: 'San Francisco',
  limit: 50
});
```

### Available Actions

**Search Operations:**
- `search_industry`: Search by industry
- `search_company`: Search by company name
- `search_location`: Search by location
- `search_keywords`: Advanced keyword search

**Lead Management:**
- `add_lead`: Add lead to database
- `get_leads`: Retrieve all leads
- `update_lead`: Update lead information
- `delete_lead`: Remove a lead
- `search_leads`: Search leads in database

**Analytics:**
- `get_stats`: Get database statistics
- `export_leads`: Export to JSON/CSV

---

## 📱 Android Architecture

### Chaquopy Integration

```kotlin
// MainActivity.kt
class MainActivity : AppCompatActivity() {
    private fun setupWebView() {
        webView.addJavascriptInterface(
            PythonBridge(this),
            "Android"
        )
    }
}

// PythonBridge.kt
class PythonBridge {
    @JavascriptInterface
    fun bridge(messageJson: String): String {
        val py = Python.getInstance()
        val response = py.getModule("leadgen_core.android_bridge")
            .callAttr("bridge_handler", messageJson)
        return response.toString()
    }
}
```

### WebMessageListener Communication

```kotlin
// One-way communication from WebView to Python
webView.addJavascriptInterface(bridge, "Android")

// JavaScript in React:
window.Android.bridge(JSON.stringify({
    action: 'search_industry',
    params: { industry: 'Tech' }
}))
```

---

## 📈 Usage Examples

### Example 1: CLI Search

```bash
python cli.py search-industry \
  --industry "Software Development" \
  --location "San Francisco" \
  --limit 50 \
  --output leads.json
```

Output:
```json
[
  {
    "company_name": "Tech Corp",
    "contact_name": "John Doe",
    "job_title": "VP Engineering",
    "email": "john@techcorp.com",
    "phone": "+1-555-0100",
    "linkedin_url": "https://linkedin.com/in/johndoe",
    "industry": "Software Development",
    "location": "San Francisco, CA",
    "lead_score": 85,
    "status": "new"
  }
]
```

### Example 2: Python API

```python
from leadgen_core import LeadScraper

# Initialize scraper
scraper = LeadScraper(
    linkedin_session_file='linkedin_session.json',
    scrapegraph_api_key='your_key'
)

# Search for leads
leads = scraper.search_by_industry(
    industry='Marketing',
    location='New York',
    limit=50,
    enrich=True
)

# Export results
for lead in leads:
    print(f"{lead.company_name}: {lead.contact_name} ({lead.lead_score}/100)")
```

### Example 3: Android Usage

```javascript
// React component on Android
const [leads, setLeads] = useState([]);

const handleSearch = async () => {
  const results = await PythonBridge.send('search_industry', {
    industry: 'Sales',
    limit: 50
  });

  setLeads(results.data);
};
```

---

## 🔐 Best Practices

### Data Privacy
- ✓ Store credentials securely (environment variables)
- ✓ Validate email addresses before storing
- ✓ GDPR compliant (no automatic tracking)

### Performance
- ✓ Use rate limiting for large batch searches
- ✓ Cache search results locally
- ✓ Lazy load Python modules on Android
- ✓ Index database for faster searches

### Quality
- ✓ Validate lead data before storing
- ✓ Deduplicate leads automatically
- ✓ Calculate scores for ranking
- ✓ Track data sources

---

## 🐛 Troubleshooting

### CLI Issues

**LinkedIn session not working:**
```bash
# Recreate session
rm linkedin_session.json
# Run any search operation - will prompt for auth
python cli.py search-industry --industry "Tech"
```

**Import errors:**
```bash
pip install --upgrade -r requirements.txt
```

### React App Issues

**Port 3000 already in use:**
```bash
npm start -- --port 3001
```

**Build fails:**
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Android App Issues

**Chaquopy not initializing:**
- Check gradle configuration
- Verify Python version compatibility (3.8+)
- Clean and rebuild project

**WebView bridge not working:**
- Ensure `@JavascriptInterface` annotations
- Check Android API level (min 24)
- Enable JavaScript in WebView settings

---

## 📚 API Reference

### LeadScraper Class

```python
class LeadScraper:
    def search_by_industry(
        industry: str,
        location: Optional[str] = None,
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]

    def search_by_company(
        company_name: str,
        limit: int = 20,
        enrich: bool = True
    ) -> List[Lead]

    def search_by_location(
        location: str,
        keywords: Optional[str] = None,
        limit: int = 50,
        use_gmap: bool = True,
        enrich: bool = True
    ) -> List[Lead]

    def search_by_keywords(
        keywords: str,
        location: Optional[str] = None,
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]

    def batch_search(
        queries: List[str],
        search_type: str = 'keywords',
        limit: int = 50,
        enrich: bool = True
    ) -> List[Lead]
```

### Lead Model

```python
@dataclass
class Lead:
    company_name: str
    contact_name: str
    job_title: str
    email: str
    phone: str
    linkedin_url: str
    industry: str
    location: str
    company_size: str
    revenue_estimate: str = ""
    lead_score: int = 0
    status: LeadStatus = LeadStatus.NEW
    notes: str = ""
    source: ScrapeSource = ScrapeSource.LINKEDIN

    def to_dict() -> Dict
    def to_json() -> str
    def calculate_lead_score() -> int
    def validate() -> Tuple[bool, List[str]]
```

---

## 📦 Dependencies

### Python
- `selenium>=4.0.0` - Browser automation
- `beautifulsoup4>=4.11.0` - HTML parsing
- `requests>=2.28.0` - HTTP client
- `lxml>=4.9.0` - XML/HTML processing
- `libphonenumber-js>=8.12.0` - Phone validation

### React
- `react>=18.0.0`
- `react-dom>=18.0.0`

### Android
- `com.chaquo.python:python:14.0.0`
- `androidx.webkit:webkit:1.5.0`

---

## 📄 License

MIT License - Free for commercial use

---

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows Python PEP 8
- React components are functional with hooks
- All features tested locally
- Documentation updated

---

## 📞 Support

For issues or questions:
1. Check ANDROID_SETUP.md for Android-specific help
2. Review troubleshooting section above
3. Check Python/React component documentation
4. Open an issue with detailed steps to reproduce

---

## 🎯 Roadmap

Future features:
- [ ] Salesforce CRM integration
- [ ] Multi-language support
- [ ] Advanced lead scoring ML model
- [ ] Email validation service
- [ ] Phone number verification
- [ ] Company logo fetching
- [ ] Website screenshot capture
- [ ] Competitor tracking
- [ ] Lead auto-assignment
- [ ] Email sequence automation

---

**Built with ❤️ for sales teams**
