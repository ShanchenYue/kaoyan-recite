package com.kaoyan.recite;

import android.app.Activity;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Log;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.util.HashMap;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final String TAG = "KaoyanRecite";
    private WebView webView;
    private TextToSpeech tts;
    private boolean ttsReady = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);

        // ─── 原生 TextToSpeech 初始化 ───
        tts = new TextToSpeech(this, new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if (status == TextToSpeech.SUCCESS) {
                    int langRes = tts.setLanguage(Locale.CHINESE);
                    if (langRes == TextToSpeech.LANG_MISSING_DATA || langRes == TextToSpeech.LANG_NOT_SUPPORTED) {
                        // 有些机型中文叫 zh_CN
                        tts.setLanguage(Locale.CHINA);
                    }
                    tts.setSpeechRate(1.0f);
                    tts.setPitch(1.0f);
                    ttsReady = true;
                    Log.d(TAG, "✅ TTS 原生引擎就绪");
                    // 通知前端
                    if (webView != null) {
                        webView.evaluateJavascript("if(window.onNativeTTSReady) window.onNativeTTSReady();", null);
                    }
                } else {
                    Log.e(TAG, "❌ TTS 初始化失败: " + status);
                }
            }
        });

        // 语音进度/完成回调 → JS
        tts.setOnUtteranceProgressListener(new UtteranceProgressListener() {
            @Override public void onStart(String utteranceId) {
                Log.d(TAG, "TTS onStart: " + utteranceId);
            }
            @Override public void onDone(String utteranceId) {
                Log.d(TAG, "TTS onDone: " + utteranceId);
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript(
                            "if(window.onNativeTTSDone) window.onNativeTTSDone('" + utteranceId + "');",
                            null
                        );
                    }
                });
            }
            @Override public void onError(String utteranceId) {
                Log.d(TAG, "TTS onError: " + utteranceId);
                runOnUiThread(() -> {
                    if (webView != null) {
                        webView.evaluateJavascript(
                            "if(window.onNativeTTSError) window.onNativeTTSError('" + utteranceId + "');",
                            null
                        );
                    }
                });
            }
        });

        // ─── WebView ───
        webView = new WebView(this);
        setContentView(webView);

        WebSettings s = webView.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowFileAccessFromFileURLs(true);
        s.setAllowUniversalAccessFromFileURLs(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setBuiltInZoomControls(false);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setSupportZoom(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);

        // ─── 注册原生 TTS Bridge ───
        webView.addJavascriptInterface(new TTSBridge(), "AndroidTTS");

        webView.setWebViewClient(new WebViewClient());
        webView.loadUrl("file:///android_asset/index.html");
    }

    /**
     * JS 可调用的原生 TTS 接口
     */
    public class TTSBridge {
        @JavascriptInterface
        public boolean isAvailable() {
            return ttsReady && tts != null;
        }

        @JavascriptInterface
        public void speak(String text, float rate, String utteranceId) {
            if (tts == null || !ttsReady) return;
            try {
                tts.setSpeechRate(rate);
                HashMap<String, String> params = new HashMap<>();
                params.put(TextToSpeech.Engine.KEY_PARAM_UTTERANCE_ID, utteranceId);
                tts.speak(text, TextToSpeech.QUEUE_FLUSH, params);
            } catch (Exception e) {
                Log.e(TAG, "TTS speak 异常: " + e.getMessage());
            }
        }

        @JavascriptInterface
        public void stop() {
            if (tts != null) {
                tts.stop();
            }
        }

        @JavascriptInterface
        public void pause() {
            if (tts != null) {
                tts.stop();  // TextToSpeech 没有真正的 pause, 用 stop 代替
            }
        }
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) webView.onResume();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) webView.onPause();
    }

    @Override
    protected void onDestroy() {
        if (tts != null) {
            tts.stop();
            tts.shutdown();
            tts = null;
        }
        if (webView != null) {
            webView.stopLoading();
            webView.removeAllViews();
            webView.destroy();
            webView = null;
        }
        super.onDestroy();
    }
}
