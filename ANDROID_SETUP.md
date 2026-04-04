# Android App Setup with Chaquopy + WebView

Complete guide to set up the Lead Generation Android app with Chaquopy and React WebView integration.

## Prerequisites

- Android Studio 4.1+
- Python 3.8+
- Node.js 14+
- Gradle 7.0+

## Project Structure

```
android-app/
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── AndroidManifest.xml
│   │   │   ├── java/com/mergex/leadgen/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── PythonBridge.kt
│   │   │   │   └── WebViewSetup.kt
│   │   │   └── assets/
│   │   │       └── html/
│   │   │           ├── index.html
│   │   │           └── (React build files)
│   │   └── res/
│   │       ├── layout/
│   │       ├── values/
│   │       └── drawable/
│   ├── build.gradle
│   └── proguard-rules.pro
├── build.gradle
├── settings.gradle
├── python/
│   └── requirements.txt
└── README.md
```

## Step 1: Create Android Project

```bash
# Create new Android project with Kotlin support
# In Android Studio:
# File > New > New Project
# Select "Empty Activity" template
# Name: LeadGen
# Package: com.mergex.leadgen
# Language: Kotlin
# Minimum API: 24
```

## Step 2: Add Chaquopy Dependency

Update `build.gradle` (Project level):

```gradle
buildscript {
    repositories {
        google()
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:7.4.0'
        classpath 'org.chaquo.python:gradle:14.0.0'  // Add this
    }
}
```

Update `build.gradle` (App level):

```gradle
plugins {
    id 'com.android.application'
    id 'kotlin-android'
    id 'com.chaquo.python'  // Add this
}

android {
    compileSdk 33

    defaultConfig {
        applicationId "com.mergex.leadgen"
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName "1.0"

        // Chaquopy configuration
        python {
            version "3.10"
            staticMethod "com.mergex.leadgen.MainActivity.start_chaquopy"

            // Python requirements
            pip {
                install "-r", "${rootDir}/python/requirements.txt"
            }

            // Include Python modules
            extractPackages "leadgen_core"
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_11
        targetCompatibility JavaVersion.VERSION_11
    }
}

dependencies {
    implementation 'org.chaquo.python:python:14.0.0'
    implementation 'androidx.appcompat:appcompat:1.5.1'
    implementation 'com.google.android.material:material:1.7.0'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'androidx.webkit:webkit:1.5.0'
}
```

## Step 3: Create Python Requirements

`python/requirements.txt`:

```
selenium>=4.0.0
beautifulsoup4>=4.11.0
requests>=2.28.0
lxml>=4.9.0
libphonenumber-js>=8.12.0
```

## Step 4: Copy Python Module

```bash
# Copy leadgen_core to your Android project
cp -r leadgen_core/ android-app/app/src/main/python/

# Or configure Gradle to include it
```

## Step 5: Create MainActivity

`app/src/main/java/com/mergex/leadgen/MainActivity.kt`:

```kotlin
package com.mergex.leadgen

import android.os.Bundle
import android.webkit.WebView
import android.webkit.WebViewClient
import android.webkit.WebChromeClient
import androidx.appcompat.app.AppCompatActivity
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize Chaquopy
        if (!Python.isStarted()) {
            Python.start(AndroidPlatform(this))
        }

        setContentView(R.layout.activity_main)
        setupWebView()
    }

    private fun setupWebView() {
        webView = findViewById(R.id.webView)

        // Configure WebView settings
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            useWideViewPort = true
            loadWithOverviewMode = true
        }

        // Add Python JavaScript interface
        webView.addJavascriptInterface(
            PythonBridge(this),
            "Android"
        )

        // Set WebViewClient
        webView.webViewClient = WebViewClient()
        webView.webChromeClient = WebChromeClient()

        // Load React app from assets
        webView.loadUrl("file:///android_asset/html/index.html")
    }

    companion object {
        @JvmStatic
        fun start_chaquopy(context: Any) {
            // Called when Chaquopy initializes
        }
    }
}
```

## Step 6: Create Python Bridge

`app/src/main/java/com/mergex/leadgen/PythonBridge.kt`:

```kotlin
package com.mergex.leadgen

import android.content.Context
import android.webkit.JavascriptInterface
import android.util.Log
import com.chaquo.python.Python
import org.json.JSONObject

class PythonBridge(private val context: Context) {
    private val tag = "PythonBridge"

    @JavascriptInterface
    fun bridge(messageJson: String): String {
        return try {
            Log.d(tag, "Received: $messageJson")

            // Get Python bridge
            val py = Python.getInstance()
            val pyModule = py.getModule("leadgen_core.android_bridge")

            // Call Python handler
            val response = pyModule.callAttr(
                "bridge_handler",
                messageJson
            ).toString()

            Log.d(tag, "Response: $response")
            response

        } catch (e: Exception) {
            Log.e(tag, "Error: ${e.message}", e)
            JSONObject().apply {
                put("success", false)
                put("error", e.message)
            }.toString()
        }
    }
}
```

## Step 7: Create Layout

`app/src/main/res/layout/activity_main.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
```

## Step 8: Update Manifest

`app/src/main/AndroidManifest.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        android:allowBackup="true"
        android:debuggable="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.LeadGen">

        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

## Step 9: Build React App

```bash
cd reactjs/

# Install dependencies
npm install

# Build for production
npm run build

# Copy to Android assets
cp -r build/* ../android-app/app/src/main/assets/html/
```

## Step 10: Build and Run

```bash
# In Android Studio or command line
./gradlew build
./gradlew installDebug

# Or use Android Studio's Run button
```

## Troubleshooting

### Chaquopy not initializing
- Ensure Python version is compatible
- Check `build.gradle` configuration
- Verify Python modules are in correct path

### WebView not loading
- Check Logcat for errors
- Ensure HTML/React files are in `assets/html/`
- Verify JavaScript is enabled in WebView settings

### Python imports failing
- Update `requirements.txt` with all dependencies
- Use `pip install` in Gradle configuration
- Check module paths

### Bridge not communicating
- Verify `@JavascriptInterface` annotations
- Check JSON message format
- Monitor Logcat for errors

## Performance Tips

1. **Lazy load Python**: Only initialize heavy modules when needed
2. **Cache results**: Store search results locally
3. **Background processing**: Use coroutines for long operations
4. **Memory management**: Clear unused data regularly
5. **WebView optimization**: Enable hardware acceleration

```kotlin
webView.settings.apply {
    mixedContentMode = WebSettings.MIXED_CONTENT_ALLOW_ALL
    setAppCacheEnabled(true)
    cacheMode = WebSettings.LOAD_CACHE_ELSE_NETWORK
}

// Hardware acceleration
webView.setLayerType(View.LAYER_TYPE_HARDWARE, null)
```

## Testing

```bash
# Run Python tests locally first
python -m pytest leadgen_core/tests/

# Then test on Android emulator/device
```

## Distribution

When ready to publish:

1. Sign APK with keystore
2. Optimize with ProGuard rules
3. Test on multiple devices
4. Version accordingly
5. Upload to Play Store or distribute via APK

See `android-app/app/proguard-rules.pro` for optimization rules.
