// setup-android.mjs — 生成 Android 工程骨架 + 同步前端资源
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const appDir = __dirname;
const androidDir = path.join(appDir, 'android');

function mkdirs(...paths) {
  paths.forEach(p => fs.mkdirSync(p, { recursive: true }));
}

// 清理旧的 android 目录
if (fs.existsSync(androidDir)) fs.rmSync(androidDir, { recursive: true, force: true });

// 创建目录
mkdirs(
  androidDir,
  path.join(androidDir, 'app/src/main/java/com/kaoyan/recite'),
  path.join(androidDir, 'app/src/main/res/values'),
  path.join(androidDir, 'app/src/main/res/drawable'),
  path.join(androidDir, 'app/src/main/res/mipmap-anydpi-v26'),
  path.join(androidDir, 'app/src/main/assets'),
);

// ============= 根 build.gradle =============
fs.writeFileSync(path.join(androidDir, 'build.gradle'), `buildscript {
    repositories { google(); mavenCentral() }
    dependencies { classpath 'com.android.tools.build:gradle:8.2.2' }
}
allprojects { repositories { google(); mavenCentral() } }
`);

fs.writeFileSync(path.join(androidDir, 'settings.gradle'), `include ':app'
rootProject.name = 'KaoyanRecite'
`);

fs.writeFileSync(path.join(androidDir, 'gradle.properties'), `org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.nonTransitiveRClass=true
`);

// ============= app build.gradle =============
fs.writeFileSync(path.join(androidDir, 'app/build.gradle'), `plugins { id 'com.android.application' }
android {
    namespace 'com.kaoyan.recite'
    compileSdk 34
    defaultConfig {
        applicationId "com.kaoyan.recite"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0.0"
    }
    buildTypes {
        release {
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
        debug { applicationIdSuffix ".debug" }
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
}
`);

// ============= AndroidManifest.xml =============
fs.writeFileSync(path.join(androidDir, 'app/src/main/AndroidManifest.xml'), `<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"/>
    <application
        android:allowBackup="true"
        android:label="考研政治背诵"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:theme="@style/Theme.Recite"
        android:usesCleartextTraffic="true">
        <activity android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden"
            android:keepScreenOn="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
`);

// ============= MainActivity.java =============
fs.writeFileSync(path.join(androidDir, 'app/src/main/java/com/kaoyan/recite/MainActivity.java'), `package com.kaoyan.recite;
import android.os.Bundle;
import android.view.WindowManager;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        webView = new WebView(this);
        setContentView(webView);
        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setBuiltInZoomControls(false);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("file:///android_asset/index.html");
    }
    @Override public void onBackPressed() {
        if (webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }
    @Override protected void onDestroy() { if (webView != null) webView.destroy(); super.onDestroy(); }
}
`);

// ============= 资源 =============
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/values/themes.xml'), `<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.Recite" parent="android:Theme.Material.Light.NoActionBar">
        <item name="android:windowBackground">@color/bg</item>
        <item name="android:statusBarColor">#0f0f1a</item>
        <item name="android:navigationBarColor">#0f0f1a</item>
    </style>
</resources>
`);
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/values/colors.xml'), `<?xml version="1.0" encoding="utf-8"?>
<resources><color name="bg">#0f0f1a</color></resources>`);
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/values/strings.xml'), `<?xml version="1.0" encoding="utf-8"?>
<resources><string name="app_name">考研政治背诵</string></resources>`);

// 图标 (adaptive)
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/drawable/ic_launcher_fg.xml'), `<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#FFFFFF" android:pathData="M54,30 L82,54 L54,78 Z"/>
</vector>`);
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/drawable/ic_launcher_bg.xml'), `<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp" android:height="108dp"
    android:viewportWidth="108" android:viewportHeight="108">
    <path android:fillColor="#ff6b6b" android:pathData="M0,0h108v108h-108z"/>
</vector>`);
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/mipmap-anydpi-v26/ic_launcher.xml'),
`<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
<background android:drawable="@drawable/ic_launcher_bg"/>
<foreground android:drawable="@drawable/ic_launcher_fg"/>
</adaptive-icon>`);
fs.writeFileSync(path.join(androidDir, 'app/src/main/res/mipmap-anydpi-v26/ic_launcher_round.xml'),
`<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
<background android:drawable="@drawable/ic_launcher_bg"/>
<foreground android:drawable="@drawable/ic_launcher_fg"/>
</adaptive-icon>`);
fs.writeFileSync(path.join(androidDir, 'app/proguard-rules.pro'), '');

console.log('✅ Android 工程骨架完成');

// ============= 同步前端资源到 assets =============
const assetsDir = path.join(androidDir, 'app/src/main/assets');
const toCopy = ['index.html', 'data.json', 'manifest.json', 'sw.js', 'icon.svg'];
toCopy.forEach(f => {
  const src = path.join(appDir, f);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(assetsDir, f));
    console.log(`  📄 ${f}`);
  }
});
// audios
const audiosSrc = path.join(appDir, 'audios');
const audiosDst = path.join(assetsDir, 'audios');
if (fs.existsSync(audiosSrc)) {
  if (fs.existsSync(audiosDst)) fs.rmSync(audiosDst, { recursive: true, force: true });
  fs.cpSync(audiosSrc, audiosDst, { recursive: true });
  const mp3s = [];
  function walk(d) { for (const e of fs.readdirSync(d)) { const p = path.join(d, e); if (fs.statSync(p).isDirectory()) walk(p); else if (e.endsWith('.mp3')) mp3s.push(p); } }
  walk(audiosDst);
  console.log(`  🎧 audios/  ${mp3s.length} 个mp3  (${(mp3s.reduce((s,p)=>s+fs.statSync(p).size,0)/1024/1024).toFixed(1)} MB)`);
} else {
  mkdirs(audiosDst);
  console.log('  🎧 audios/  (空 - TTS后台还在跑)');
}

// ============= GitHub Actions workflow =============
const ghDir = path.join(appDir, '.github/workflows');
mkdirs(ghDir);
fs.writeFileSync(path.join(ghDir, 'build-apk.yml'), `name: Build APK

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        java-version: '17'
        distribution: 'temurin'

    - name: Setup Gradle
      uses: gradle/actions/setup-gradle@v3

    - name: Copy web assets
      run: |
        mkdir -p android/app/src/main/assets/audios
        cp index.html data.json manifest.json sw.js icon.svg android/app/src/main/assets/ 2>/dev/null || true
        if [ -d audios ]; then cp -r audios/* android/app/src/main/assets/audios/; fi

    - name: Build Debug APK
      run: cd android && ./gradlew assembleDebug

    - name: Build Release APK
      run: cd android && ./gradlew assembleRelease

    - name: Upload Debug APK
      uses: actions/upload-artifact@v4
      with:
        name: kaoyan-debug
        path: android/app/build/outputs/apk/debug/*.apk

    - name: Upload Release APK
      uses: actions/upload-artifact@v4
      with:
        name: kaoyan-release
        path: android/app/build/outputs/apk/release/*.apk
`);
console.log('\n✅ .github/workflows/build-apk.yml 已生成');

// ============= README for APK =============
const pkgCmd = (process.platform === 'win32') ?
`# Windows (用 Git Bash)
cd d:/Desktop/背诵/app
rm -rf .git
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/你的用户名/kaoyan-recite.git
git push -u origin main` :
`cd 你的项目目录
git init && git add . && git commit -m "init"
git branch -M main
git remote add origin https://github.com/你的用户名/kaoyan-recite.git
git push -u origin main`;

console.log(`\n🚀 现在你可以推到 GitHub 云打包了!

步骤:
1. 在 GitHub 创建一个新仓库 (比如叫 kaoyan-recite), 不要勾选 README
2. 在 ${appDir} 目录下执行:
   ${pkgCmd.replace(/# /g, '')}
3. 打开仓库页面 → Actions 标签 → 等它跑完 (约 5-8 分钟)
4. 跑完后点 Artifacts 下载 kaoyan-debug.zip
5. 解压得到 app-debug.apk → 传到小米手机安装即可!

💡 以后更新 data.json 或加新PDF后:
   python build_data.py && python scan_audio.py && git add . && git commit -m "update" && git push
   → Actions 自动重新构建 APK
`);
