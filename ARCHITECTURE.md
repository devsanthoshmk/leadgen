# LeadGen Architecture

Comprehensive architecture guide for the B2B lead generation platform.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LEAD GENERATION PLATFORM                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   Android App    │    │   Web Browser    │                  │
│  │  (Chaquopy)      │    │  (React/Node)    │                  │
│  └────────┬─────────┘    └────────┬─────────┘                  │
│           │                       │                             │
│           │    WebMessageListener │ HTTP/WebSocket             │
│           │                       │                             │
│           └───────────┬───────────┘                             │
│                       │                                          │
│           ┌───────────▼────────────┐                            │
│           │   PYTHON BRIDGE LAYER  │                            │
│           │  (android_bridge.py)   │                            │
│           └───────────┬────────────┘                            │
│                       │                                          │
│           ┌───────────▼────────────────────┐                   │
│           │   CORE SCRAPER MODULE          │                   │
│           │  (LeadScraper Orchestrator)   │                   │
│           └───┬───┬───┬────────────────────┘                   │
│               │   │   │                                         │
│       ┌───────┘   │   └───────────────────┐                   │
│       │           │                       │                   │
│   ┌───▼───┐   ┌───▼───┐         ┌────────▼────┐              │
│   │LinkedIn│   │ GMaps │         │ ScrapeGraph │              │
│   │Scraper │   │Scraper│         │  Adapter    │              │
│   └───────┘   └───────┘         └─────────────┘              │
│       │           │                       │                   │
│       └───────────┼───────────────────────┘                   │
│                   │                                            │
│           ┌───────▼──────────┐                                │
│           │ LeadEnricher     │                                │
│           │ (Multi-source)   │                                │
│           └───────┬──────────┘                                │
│                   │                                            │
│           ┌───────▼──────────────┐                            │
│           │  Lead Data Model     │                            │
│           │ (Validation/Scoring) │                            │
│           └──────────────────────┘                            │
│                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Core Modules

### 1. **models.py** - Data Structures

Defines all data models:

```
Lead
├── company_name: str
├── contact_name: str
├── job_title: str
├── email: str
├── phone: str
├── linkedin_url: str
├── industry: str
├── location: str
├── company_size: str
├── revenue_estimate: str
├── lead_score: int (0-100)
├── status: LeadStatus
├── notes: str
├── source: ScrapeSource
└── tags: List[str]

LeadStatus (Enum)
├── NEW
├── CONTACTED
├── QUALIFIED
├── NEGOTIATION
├── CLOSED_WON
├── CLOSED_LOST
└── ARCHIVED

ScrapeSource (Enum)
├── LINKEDIN
├── GMAP
├── SCRAPEGRAPH
└── MANUAL
```

**Features:**
- Automatic lead scoring (0-100 scale)
- Data validation with error reporting
- JSON/CSV export support
- Immutable status tracking

### 2. **scraper.py** - Main Orchestrator

Entry point for all scraping operations:

```python
LeadScraper
├── search_by_industry()
├── search_by_company()
├── search_by_location()
├── search_by_keywords()
└── batch_search()

# Strategy:
# 1. Search LinkedIn (primary)
# 2. Fill gaps with Google Maps (secondary)
# 3. Enrich with ScrapeGraphAI (fallback)
```

**Features:**
- Multi-source data aggregation
- Automatic deduplication
- Progressive enrichment
- Batch processing support

### 3. **linkedin_scraper.py** - LinkedIn Integration

Wrapper for LinkedIn Web Scraper library:

```python
LinkedInScraper
├── search_company()        # Find company info
├── search_person()         # Find person/contact
├── extract_leads_from_company()
└── extract_leads_from_search()
```

**Data Points Captured:**
- Company name, size, industry
- Contact name, job title
- LinkedIn profile URL
- Location

### 4. **gmap_scraper.py** - Google Maps Integration

Local business discovery and enrichment:

```python
GMapScraper
├── search_business()       # Search by query + location
└── extract_leads_from_results()

# Extracts:
├── Business name
├── Address & location
├── Phone number
├── Website URL
├── Category
├── Ratings & reviews
└── Estimated company size
```

**Features:**
- Phone number extraction and validation
- Estimated company size from review count
- Website contact extraction (when available)

### 5. **scrapegraph_adapter.py** - ScrapeGraphAI

Advanced web scraping with AI:

```python
ScrapeGraphAdapter
├── scrape_website()        # Extract data from URL
├── enrich_lead()          # Enrich single lead
└── bulk_enrich_leads()    # Batch enrichment with rate limiting

# Fallback for:
├── Missing emails
├── Missing phone numbers
├── Industry classification
├── Company size estimation
└── Revenue estimates
```

**Rate Limiting:**
- Free tier: 5 requests/minute
- Built-in delays and throttling
- Progress tracking for batch operations

### 6. **enricher.py** - Multi-Source Enrichment

Intelligent lead enrichment pipeline:

```python
LeadEnricher
├── enrich_lead()           # Single lead from multiple sources
├── enrich_leads()          # Batch with progress tracking
└── _merge_leads()          # Non-destructive data merging

# Strategy:
# 1. Try LinkedIn first (primary for B2B)
# 2. Fill gaps with Google Maps
# 3. Use ScrapeGraphAI for missing critical fields
# 4. Never overwrite existing quality data
```

**Features:**
- Non-destructive merging (preserves existing data)
- Source attribution
- Configurable enrichment pipeline
- Progress reporting

### 7. **android_bridge.py** - Chaquopy Integration

Python/Android bridge for WebView communication:

```python
AndroidBridge
├── Search operations
│   ├── search_industry()
│   ├── search_company()
│   ├── search_location()
│   └── search_keywords()
├── Lead management
│   ├── add_lead()
│   ├── get_leads()
│   ├── update_lead()
│   ├── delete_lead()
│   └── search_leads()
├── Analytics
│   ├── get_stats()
│   └── export_leads()
└── Message handling
    └── handle_message()    # Main WebMessageListener handler
```

**JSON Protocol:**

Request:
```json
{
  "action": "search_industry",
  "params": {
    "industry": "Software Development",
    "location": "San Francisco",
    "limit": 50
  }
}
```

Response:
```json
{
  "success": true,
  "message": "Found 42 leads",
  "data": [
    { "Lead object 1" },
    { "Lead object 2" }
  ]
}
```

---

## 🎨 React Component Architecture

### Navigation
- Tab-based interface
- Active state tracking
- Brand display

### SearchPanel
- Multiple search types (industry, company, location, keywords)
- Form validation
- Progress feedback
- Search tips

### LeadsTable
- Sortable/filterable list
- Inline actions (view, add, delete)
- Score visualization
- Status badges
- Email/phone links

### LeadDetail
- Full lead information
- Edit mode toggle
- Status management
- Note taking
- Metadata display

### Analytics
- Metrics cards (total, avg score, high priority, conversion rate)
- Status distribution
- Industry breakdown
- Sales funnel
- Score distribution
- Performance table

### Android Bridge (PythonBridge)
```javascript
const PythonBridge = {
  isAndroid: window.Android !== undefined,
  send: async (action, params) => {
    // Sends JSON message
    // Gets response from Python
    // Parses and returns
  }
}
```

---

## 🔄 Data Flow

### Search Operation Flow

```
1. User Initiates Search
   ↓
2. SearchPanel collects input
   ↓
3. React sends message to PythonBridge
   ↓
4. PythonBridge.send() → JSON message
   ↓
5. Android WebMessageListener (Chaquopy)
   ↓
6. android_bridge.handle_message()
   ↓
7. LeadScraper.search_by_*()
   ↓
8. LinkedIn search (primary)
   ↓
9. Merge with GMaps search (secondary)
   ↓
10. LeadEnricher enriches results
    ↓
11. Calculate lead scores
    ↓
12. Return JSON response
    ↓
13. React updates state
    ↓
14. UI renders results
```

### Lead Addition Flow

```
1. User clicks "Add to Database"
   ↓
2. LeadDetail.handleAddLead()
   ↓
3. PythonBridge.send('add_lead', {lead_data})
   ↓
4. android_bridge.add_lead()
   ↓
5. Lead validation
   ↓
6. Stored in current_leads_db (in-memory)
   ↓
7. Auto-save to device storage (optional)
   ↓
8. Return lead with ID
   ↓
9. React updates leads state
   ↓
10. UI re-renders leads table
```

---

## 🔐 Security Considerations

### Data Protection
- ✓ No plaintext credentials in code
- ✓ Environment variable configuration
- ✓ HTTPS for external API calls
- ✓ Local device storage only on Android

### Input Validation
- ✓ All user inputs validated
- ✓ Lead data validated before storage
- ✓ Email format checking
- ✓ Phone number validation

### Rate Limiting
- ✓ Built-in delays in batch operations
- ✓ Respect LinkedIn ToS (limits)
- ✓ ScrapeGraphAI free tier rate limiting
- ✓ Configurable throttling

### Privacy
- ✓ No data sent to external servers (except APIs)
- ✓ GDPR compliant (no tracking)
- ✓ User controls all data
- ✓ Local-first architecture

---

## 📊 Database Schema (Optional)

For production, implement with:

```sql
-- Leads table
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    company_name VARCHAR(255),
    contact_name VARCHAR(255),
    job_title VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),
    linkedin_url TEXT,
    industry VARCHAR(100),
    location VARCHAR(255),
    company_size VARCHAR(50),
    revenue_estimate VARCHAR(100),
    lead_score INT,
    status VARCHAR(50),
    notes TEXT,
    source VARCHAR(50),
    created_at TIMESTAMP,
    last_updated TIMESTAMP,
    created_by VARCHAR(255)
);

-- Search history (optional)
CREATE TABLE search_history (
    id UUID PRIMARY KEY,
    search_type VARCHAR(50),
    search_query TEXT,
    results_count INT,
    timestamp TIMESTAMP
);

-- Lead activities (optional)
CREATE TABLE lead_activities (
    id UUID PRIMARY KEY,
    lead_id UUID REFERENCES leads(id),
    activity_type VARCHAR(50),
    description TEXT,
    timestamp TIMESTAMP
);
```

---

## 🚀 Deployment

### CLI (Python Only)
```bash
# Package as executable
pip install pyinstaller
pyinstaller --onefile cli.py
# Distribute cli.exe or cli binary
```

### Web App
```bash
# Deploy React build
npm run build
# Upload to Firebase, Vercel, or your server
```

### Android App
```
# Build APK
./gradlew assembleRelease

# Sign APK
jarsigner -verbose -sigalg SHA1withRSA ...

# Upload to Play Store or distribute directly
```

---

## 📈 Performance Optimization

### Python Side
- Lazy loading of modules
- Caching of search results
- Batch processing with progress
- Connection pooling

### React Side
- Code splitting by component
- Lazy component loading
- Memoization of expensive computations
- Virtual scrolling for large lists

### Android Side
- Hardware acceleration for WebView
- Memory management
- Background processing
- Local caching

---

## 🔧 Extending the Platform

### Add New Data Source

1. Create new scraper: `leadgen_core/new_source_scraper.py`
2. Implement required methods
3. Register in `enricher.py`
4. Add to search pipeline

### Add New Lead Fields

1. Update `models.py` Lead dataclass
2. Update database schema (if applicable)
3. Update React components (SearchPanel, LeadDetail, LeadsTable)
4. Update scoring logic if relevant

### Custom Scoring

1. Override `Lead.calculate_lead_score()` in models.py
2. Add industry-specific multipliers
3. Consider engagement history
4. Implement custom rules

---

## 📚 Testing

```bash
# Python unit tests
pytest leadgen_core/tests/

# React component tests
npm test

# Android instrumentation tests
./gradlew connectedAndroidTest

# CLI integration tests
python cli.py search-keywords --keywords "test" --limit 5
```

---

**Architecture designed for scalability, maintainability, and extensibility.**
