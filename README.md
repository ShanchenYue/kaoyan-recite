# 考研训练营（kaoyan-recite）

听、背、练一体化的考研全科训练工具。纯静态前端 + Android WebView 壳，离线可用。

制作人：**LZH**

---

## 功能一览

| 模块 | 说明 |
| --- | --- |
| 🎧 听 | 文字可独立阅读（不强制播放）、单条按需播放、MP3 分句播放、倍速（0.6–2.0x）、顺序/乱序/随机、段落停顿、自动下一段 |
| ⭐ 收藏夹 | 任意知识点一键收藏，可跨书籍集中播放与背诵 |
| ☀️ 主题 | 深色 / 日间模式一键切换，偏好本地保存 |
| ✏️ 挖空 | 肖秀荣《背诵手册》等资料挖空，支持文字填入 / 选项选择 |
| ✅ 选择 | 肖八套卷 1–8 + 2016–2025 政治真题选择题，答对自动进入下一题 |
| 🔤 单词 | 考研英语高频词库，支持清单浏览与搜索 |
| 📝 填空 | 政治 / 数学 / 信号与系统核心知识点填空 |
| ∑ 公式 | 数学公式默写（高数 / 线代 / 概率） |
| 📜 大题 | 2016–2025 政治真题材料分析题，附参考答案与自评 |
| ❌ 错题本 | 卡片式布局，完整题干 + 正确答案 + 解析，可一键只练错题 |
| 📊 评估 | 掌握度统计 + 学习记录导出/导入备份 |

- 学习记录：localStorage + Android SharedPreferences 双写，升级/清缓存不丢。
- 界面适配：手机、平板、横屏。

---

## 目录结构（脉络）

```
index.html        听书首页（播放器）
quiz.html         训练营（挖空 / 选择 / 单词 / 填空 / 公式 / 大题 / 错题 / 评估）
auth.js           激活校验 + 学习记录双写
sw.js             Service Worker（只缓存页面壳，音频一律直连）
manifest.json     PWA 配置
data.json         听力资料与音频索引
quiz_data.js      题库打包产物（由 quiz/*.json 生成）
quiz/             题库源数据
  ├─ choice.json     肖八选择题
  ├─ exam_choice.json 2016–2025 真题选择题
  ├─ essay.json      真题材料分析大题
  ├─ cloze.json      挖空题
  ├─ fill.json       填空题
  ├─ words.json      单词库
  └─ math.json       数学公式
audios/           MP3 语音（879 段）
math/             数学公式题图片
vendor/katex/     KaTeX 离线公式渲染
android/          Android WebView 壳工程（Gradle）
.github/          GitHub Actions：自动构建并签名 APK
sync_android.py   同步前端资源、内联 data.json 到 Android assets
build_*.py        从原始资料生成题库
quiz_bundle.py    打包 quiz/*.json → quiz_data.js
```

---

## 题库来源

| 模块 | 来源 |
| --- | --- |
| 挖空 | 肖秀荣《背诵手册》、肖190题客观题、1–10月时政热点、主观题背诵包、2027 重点时政（国内/国际） |
| 选择题 | 肖八套卷 1–8 套（单选/多选）+ 2016–2025 考研政治真题选择题 |
| 单词 | 考研英语高频词汇（按真题词频标注） |
| 填空 | 政治 / 数学 / 信号与系统 核心知识点 |
| 公式 | 考研数学公式（高数 / 线代 / 概率）+ 线代知识点总结（8 页图册） |
| 真题大题 | 2016–2025 考研政治真题材料分析题（马原 / 毛中特 / 史纲 / 思修 / 时政） |

---

## 本地运行

```bash
python start.py
# 浏览器打开 http://localhost:8000
```

## 构建 APK

推送到 `main` 会自动触发 GitHub Actions（`.github/workflows/build-apk.yml`）构建并签名 APK，产物在 Actions 页面的 Artifacts 中。

需要配置的仓库 Secrets（固定签名，保证覆盖安装不丢记录）：

- `KEYSTORE_B64`：keystore 的 base64
- `KEYSTORE_PASS`：keystore 密码
- `KEY_ALIAS`：key 别名
- `KEY_PASS`：key 密码

## 版本

当前版本：**v1.9.1**（versionCode 13）

## 过关规则

- 知识点挖空、填空、单词：连续答对 **3 次** 记为掌握。
- 政治选择题、数学公式套题、真题大题：**1 次** 答对即掌握；答错自动进入错题本。
