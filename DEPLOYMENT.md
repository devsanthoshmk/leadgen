# Deployment Checklist - LeadGen

Complete guide for deploying LeadGen to production.

---

## ✅ Pre-Deployment Checklist

### Code Quality
- [ ] Run linter on Python code
- [ ] Run formatter on React code
- [ ] Fix all warnings/errors
- [ ] Test all search types
- [ ] Verify lead scoring
- [ ] Test data export (JSON/CSV)

### Security
- [ ] Remove debug logging
- [ ] Check for hardcoded credentials
- [ ] Verify API key handling
- [ ] Set environment variables
- [ ] Enable HTTPS (web)
- [ ] Review permissions (Android)

### Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Mobile responsiveness verified
- [ ] Android app tested on device
- [ ] Edge cases handled

### Documentation
- [ ] README.md updated
- [ ] API documentation complete
- [ ] Setup guide reviewed
- [ ] Troubleshooting section filled
- [ ] Architecture documented
- [ ] Comments added to complex code

---

## 🚀 CLI Deployment

### Package as Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile cli.py \
  --hidden-import=selenium \
  --hidden-import=bs4 \
  --hidden-import=lxml

# Test executable
dist/cli --help

# Distribute dist/cli binary
# OR dist/cli.exe on Windows
```

### Create Windows MSI Installer

```bash
# Install requirements
pip install cx_Freeze

# Create setup script (setup.py)
# Run: python setup.py bdist_msi

# Distribute .msi file
```

### Docker Containerization

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY leadgen_core/ ./leadgen_core/
COPY cli.py .

ENTRYPOINT ["python", "cli.py"]
```

```bash
# Build and run
docker build -t leadgen-cli .
docker run leadgen-cli search-keywords --keywords "Tech"
```

---

## 🌐 Web Deployment

### Build React App

```bash
cd reactjs/

# Install dependencies
npm install

# Create production build
npm run build

# Output in build/ directory
```

### Firebase Hosting

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Initialize project
firebase init hosting

# Deploy
firebase deploy
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Or connect GitHub for auto-deploy
```

### Docker Web Container

```dockerfile
FROM node:18 AS build
WORKDIR /app
COPY reactjs/ .
RUN npm install && npm run build

FROM node:18
WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/build ./build
EXPOSE 3000
CMD ["serve", "-s", "build"]
```

```bash
docker build -t leadgen-web .
docker run -p 3000:3000 leadgen-web
```

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name leadgen.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name leadgen.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/leadgen.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/leadgen.yourdomain.com/privkey.pem;

    # React build files
    root /var/www/leadgen/build;

    # Serve index.html for all routes (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (if needed)
    location /api/ {
        proxy_pass http://localhost:3001;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

---

## 📱 Android Deployment

### Build Release APK

```bash
# In Android Studio or command line
./gradlew assembleRelease

# Output: app/build/outputs/apk/release/app-release-unsigned.apk
```

### Sign APK

```bash
# Create keystore (one-time)
keytool -genkey -v -keystore leadgen.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias leadgen

# Sign APK
jarsigner -verbose -sigalg SHA256withRSA \
  -digestalg SHA-256 \
  -keystore leadgen.jks \
  app/build/outputs/apk/release/app-release-unsigned.apk \
  leadgen

# Align APK (optimize)
zipalign -v 4 \
  app/build/outputs/apk/release/app-release-unsigned.apk \
  leadgen.apk
```

### Play Store Submission

1. **Prepare Store Listing**
   - App title, description
   - Screenshots (4-5)
   - Feature graphic (1024x500)
   - Icon (512x512)
   - Privacy policy URL

2. **Configure Release**
   - Version number: 1.0
   - Version code: 1
   - Supported devices
   - Permissions needed

3. **Create Release**
   - Upload signed APK
   - Add release notes
   - Set rollout percentage (5% → 100%)

4. **Review & Publish**
   - Google Play reviews (24-48 hours)
   - Monitor crash reports
   - Respond to reviews

### GitHub Releases

```bash
# Create release tag
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Upload APK to GitHub releases
# Automated via GitHub Actions (optional)
```

### Direct APK Distribution

```bash
# Host on your server
scp leadgen.apk user@server:/var/www/downloads/

# Users download and install:
# adb install leadgen.apk
# OR open browser and download
```

---

## 🔑 Environment Variables

### Development

```bash
# .env.development
REACT_APP_API_URL=http://localhost:3000
REACT_APP_DEBUG=true
```

### Production

```bash
# .env.production
REACT_APP_API_URL=https://api.leadgen.com
REACT_APP_DEBUG=false

# Python
export SCRAPEGRAPH_API_KEY="your_api_key"
export LINKEDIN_SESSION_FILE="/path/to/session.json"
```

### Android

```
# In build.gradle or gradle.properties
api_key=SCRAPEGRAPH_API_KEY
debug=false
```

---

## 📊 Monitoring & Analytics

### Python Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('leadgen.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
```

### React Error Tracking

```javascript
// Setup error boundary
class ErrorBoundary extends React.Component {
  componentDidCatch(error, info) {
    // Send to error tracking service
    console.error('Error caught:', error, info);
  }
}
```

### Android Crash Reporting

```kotlin
// Firebase Crashlytics
FirebaseCrashlytics.getInstance().recordException(e)
```

### Key Metrics to Track

- [ ] Total leads generated
- [ ] Average lead score
- [ ] Search success rate
- [ ] API response time
- [ ] Error rate
- [ ] User retention
- [ ] Feature usage

---

## 🔄 Updates & Maintenance

### Python Module Updates

```bash
# Publish to PyPI (optional)
pip install twine
python setup.py sdist bdist_wheel
twine upload dist/*

# Or: pip install --upgrade leadgen-core
```

### React App Updates

```bash
# Build and redeploy
npm run build
firebase deploy

# Or auto-deploy via GitHub Actions
```

### Android App Updates

```bash
# Increment version code
# Build release
# Sign APK
# Upload new version to Play Store

# Play Store auto-updates users
```

---

## 🆘 Rollback Procedures

### If Something Breaks

**Web App:**
```bash
# Revert to previous build
git revert HEAD
npm run build
firebase deploy
```

**Android:**
```bash
# In Play Store:
# 1. View version history
# 2. Select previous stable version
# 3. Click "Rollout to 100%"
```

**Python CLI:**
```bash
# Keep backup of previous version
cp cli-v1.0 cli-v1.0-backup
# Distribute previous version
```

---

## 📋 Post-Deployment

### Verification
- [ ] All features work in production
- [ ] No errors in logs
- [ ] API integrations functioning
- [ ] Mobile app responsive
- [ ] Search results accurate

### User Communication
- [ ] Announce new version
- [ ] Document changes
- [ ] Gather feedback
- [ ] Monitor support tickets

### Performance Monitoring
- [ ] Check load times
- [ ] Monitor API usage
- [ ] Track error rates
- [ ] Review user feedback

### Iterate
- [ ] Collect usage data
- [ ] Identify improvements
- [ ] Plan next release
- [ ] Update roadmap

---

## 🎯 Release Schedule

### Version Strategy

```
Version Format: MAJOR.MINOR.PATCH

1.0.0 - Initial Release
  - Core features
  - CLI tool
  - Web app
  - Android app

1.1.0 - Feature Release
  - New data sources
  - Improved scoring
  - UI enhancements

1.0.1 - Patch Release
  - Bug fixes
  - Performance improvements
  - Security updates
```

### Release Cadence

- **Major**: Quarterly (3 months)
- **Minor**: Monthly
- **Patch**: As needed (critical bugs)

---

## 📞 Support Strategy

### User Support Channels
- [ ] Email: support@leadgen.com
- [ ] GitHub Issues: project/issues
- [ ] Discord: community.leadgen.com
- [ ] Documentation: docs.leadgen.com

### SLA (Service Level Agreement)
- Critical bugs: 24 hours
- Feature requests: 2 weeks
- Documentation: 1 week

---

## ✨ Success Criteria

Deployment is successful when:

- ✅ All tests pass
- ✅ No critical bugs reported
- ✅ Performance meets targets
- ✅ Users can complete workflows
- ✅ Analytics show adoption
- ✅ Support tickets minimal

---

**Ready for production! 🚀**
