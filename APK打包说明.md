# 考研政治背诵播放器 - APK 打包指南

## 方法一：PWA 快速方案 (推荐, 5分钟搞定)

小米澎湃OS / 安卓手机都支持：

1. 电脑上启动 `python start.py` (在 app 目录下)
2. 手机连同一WiFi，浏览器打开 `http://电脑IP:8000`
3. 浏览器菜单 → "添加到主屏幕" / "安装应用"
4. 桌面上就会有一个独立图标，点开全屏运行，体验和原生App一样
5. 以后即使离线也能用(Service Worker已缓存)

## 方法二：Capacitor 打包真正的 APK

需要在 Windows 上装 Node.js 和 Android Studio（或命令行工具）。

### 1. 环境准备

```powershell
# 装 Node.js (如果没有)
winget install OpenJS.NodeJS.LTS
# 重新打开 PowerShell
node --version  # 应该 >= 18
npm --version
```

### 2. 初始化 Capacitor 项目

```powershell
cd d:\Desktop\背诵\app
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android

npx cap init "考研政治背诵" "com.kaoyan.recite" --web-dir=.
```

### 3. 添加 Android 平台

```powershell
npx cap add android
npx cap sync
```

### 4. 用 Android Studio 打开打包

```powershell
npx cap open android
```

Android Studio 打开后：
- 菜单 Build → Build Bundle(s) / APK(s) → Build APK(s)
- 等构建完成，右下角会有提示，点击 "locate" 找到 APK
- 或者路径: `android\app\build\outputs\apk\debug\app-debug.apk`

### 5. 安装到手机

- 手机 USB 连电脑，开"USB调试"，直接 adb install
- 或把 APK 传到手机，文件管理器里点开安装
- 小米澎湃OS 需要在 设置 → 隐私保护 → 特殊权限 → 安装未知应用 里允许文件管理器安装

### 更新数据后重新打包

每次更新 data.json 后：

```powershell
cd d:\Desktop\背诵\app
npx cap sync
# 然后在 Android Studio 里重新 Build APK
```

## 以后扩充新 PDF

1. 把新 PDF 放到 `d:\Desktop\背诵\资源\` 目录
2. 运行 `python build_data.py` 重新生成 data.json
3. 如果是服务器模式，浏览器刷新即可
4. 如果是 APK，重新 `npx cap sync` + Build APK

## 文件结构

```
d:\Desktop\背诵\
├── 资源\                    # 原始PDF资料
│   ├── 1-10月的时政热点精选.pdf
│   ├── 27 肖《背诵手册》190 题背诵版(1).pdf
│   ├── 27考研政治周年事件讲义.pdf   (扫描版, 需OCR)
│   └── 客观题和主观题背诵包.pdf
└── app\                     # 播放器程序
    ├── build_data.py        # PDF → JSON 转换脚本
    ├── data.json            # 生成的结构化知识点
    ├── index.html           # 播放器主界面
    ├── manifest.json        # PWA 配置
    ├── sw.js                # Service Worker (离线缓存)
    ├── start.py             # 一键启动服务器
    └── server.py            # HTTP服务器(备用)
```
