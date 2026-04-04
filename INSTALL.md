# Installation & Setup Guide

Complete step-by-step installation for all platforms.

---

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 14 or higher
- **RAM**: 4GB minimum
- **Disk**: 2GB for dependencies

### Software Requirements
- Git
- Python package manager (pip)
- Node package manager (npm)

---

## 🖥️ Windows Installation

### Step 1: Install Python

```bash
# Download from python.org or use Chocolatey
choco install python

# Verify installation
python --version
pip --version
```

### Step 2: Clone/Download Project

```bash
# Navigate to leadgen folder
cd "C:\path\to\leadgen"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test CLI

```bash
python cli.py search-keywords --keywords "Sales" --limit 5
```

### Step 5: Setup React App

```bash
cd reactjs
npm install
npm start
```

Browser opens at `http://localhost:3000`

---

## 🍎 macOS Installation

### Step 1: Install Python

```bash
# Using Homebrew
brew install python@3.10

# Verify
python3 --version
```

### Step 2: Navigate & Setup

```bash
cd /path/to/leadgen

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test CLI

```bash
python cli.py search-keywords --keywords "Marketing" --limit 5
```

### Step 5: React App

```bash
cd reactjs
npm install
npm start
```

---

## 🐧 Linux Installation

### Step 1: Install Python

```bash
# Ubuntu/Debian
sudo apt-get install python3 python3-pip python3-venv

# Fedora
sudo dnf install python3 python3-pip

# Verify
python3 --version
```

### Step 2: Setup Project

```bash
cd /path/to/leadgen

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Test CLI

```bash
python cli.py search-keywords --keywords "Technology" --limit 5
```

### Step 5: React App

```bash
cd reactjs
npm install
npm start
```

---

## 🔧 Configuration

### Step 1: LinkedIn Setup (Optional)

For LinkedIn scraping, you need a session file. This is created automatically on first use:

```bash
# First search will prompt for LinkedIn login
python cli.py search-company --company "Google"

# Saves session to linkedin_session.json
```

### Step 2: ScrapeGraphAI API Key

```bash
# Get free API key from scrapegraphai.com
# Set environment variable:

# Windows
set SCRAPEGRAPH_API_KEY=your_key_here

# macOS/Linux
export SCRAPEGRAPH_API_KEY=your_key_here

# Verify
echo $SCRAPEGRAPH_API_KEY
```

### Step 3: Verify All Systems

```bash
# Test Python module
python -c "from leadgen_core import LeadScraper; print('✓ Python OK')"

# Test Node.js
node --version

# Test npm
npm --version
```

---

## 🚀 Quick Test

### Test 1: CLI Search

```bash
python cli.py search-keywords \
  --keywords "Sales Director" \
  --limit 10 \
  --output test_results.json

# Check results
cat test_results.json
```

### Test 2: Web App

```bash
cd reactjs
npm start

# Opens http://localhost:3000
# Try searching for something
```

### Test 3: Batch Search

Create `queries.txt`:
```
Software Development
Marketing Management
Sales Leadership
Product Management
```

Run batch:
```bash
python cli.py batch \
  --file queries.txt \
  --limit 20 \
  --output batch_results.json
```

---

## 📱 Android Setup

See **ANDROID_SETUP.md** for complete Android installation guide.

Quick overview:
1. Install Android Studio
2. Add Chaquopy dependency
3. Copy `leadgen_core/` folder
4. Build and run on device

---

## 🐛 Troubleshooting Installation

### Issue: "Python not found"
```bash
# Windows: Add Python to PATH
# Settings > Environment Variables > Add Python installation folder

# macOS/Linux: Check installation
which python3
python3 --version
```

### Issue: "pip: command not found"
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Or use python3
python3 -m pip install -r requirements.txt
```

### Issue: "Module not found"
```bash
# Make sure you're in virtual environment
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

### Issue: "npm install fails"
```bash
# Clear cache
npm cache clean --force

# Delete node_modules
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: "Port 3000 already in use"
```bash
# Use different port
npm start -- --port 3001

# Or kill process using port 3000
# Windows: netstat -ano | findstr :3000
# macOS/Linux: lsof -ti:3000 | xargs kill -9
```

### Issue: "React app not starting"
```bash
# Check Node version (14+ required)
node --version

# Update Node if needed
# Download from nodejs.org

# Clear React cache
npm start -- --reset-cache
```

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Python installed and in PATH
- [ ] Virtual environment created and activated
- [ ] Python dependencies installed (`pip list`)
- [ ] Node.js 14+ installed (`node --version`)
- [ ] npm installed (`npm --version`)
- [ ] Can import leadgen_core (`python -c "from leadgen_core import LeadScraper"`)
- [ ] CLI works (`python cli.py --help`)
- [ ] React app runs (`npm start` in reactjs/)
- [ ] Can perform a search and get results

---

## 📚 Next Steps

1. **Read Documentation**
   - Start with README.md
   - Check QUICKSTART.md for 5-minute guide
   - Review ARCHITECTURE.md for design details

2. **Test Features**
   - Try different search types
   - Test export to JSON/CSV
   - View analytics dashboard

3. **Customize**
   - Adjust lead scoring logic
   - Change UI colors/branding
   - Modify search strategy

4. **Deploy**
   - Setup Android app (ANDROID_SETUP.md)
   - Deploy web app (DEPLOYMENT.md)
   - Configure production settings

---

## 🎯 Common Commands

```bash
# Activate virtual environment
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Run CLI
python cli.py search-industry --industry "Tech"

# Export results
python cli.py search-company --company "Google" --output leads.csv

# Run web app
cd reactjs && npm start

# Build for production
cd reactjs && npm run build

# Run tests
pytest leadgen_core/tests/
```

---

## 💡 Tips

1. **Use Virtual Environment**
   - Keeps dependencies isolated
   - Easy to clean up
   - Prevents conflicts

2. **Start with Small Limits**
   - Test with `--limit 5` first
   - Increase as you get comfortable
   - Monitor API usage

3. **Check Documentation**
   - README.md has comprehensive guide
   - QUICKSTART.md for quick overview
   - Check component code for details

4. **Enable Debug Mode**
   ```bash
   # For more verbose logging
   export DEBUG=1
   python cli.py search-keywords --keywords "test"
   ```

5. **Save Results Locally**
   ```bash
   # Always use --output flag
   python cli.py search-industry \
     --industry "Tech" \
     --output my_leads.json
   ```

---

## 🆘 Need Help?

1. **Check Troubleshooting Section** above
2. **Review Documentation**
   - README.md
   - ARCHITECTURE.md
   - QUICKSTART.md

3. **Check Python/React Errors**
   ```bash
   # Python debug mode
   python -u cli.py search-keywords --keywords "test"

   # React errors in browser console
   # F12 > Console tab
   ```

4. **Verify Installation**
   ```bash
   python -m pip list
   npm list
   ```

---

## 📞 Support Resources

- **Python Docs**: https://docs.python.org/3/
- **React Docs**: https://react.dev
- **Selenium**: https://selenium.dev
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/

---

**Installation Complete! 🎉**

You're ready to start generating leads!
