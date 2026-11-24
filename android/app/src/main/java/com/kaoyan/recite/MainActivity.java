package com.kaoyan.recite;

import android.app.Activity;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.speech.tts.UtteranceProgressListener;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import java.util.HashMap;
import java.util.Locale;

public class MainActivity extends Activity {
    private static final String TAG = "KaoyanRecite";
    private WebView webView;
    private TextToSpeech tts;
    private boolean ttsReady = false;
    private boolean focusActive = false;

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
        webView.addJavascriptInterface(new FocusBridge(), "AndroidFocus");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                // 页面刷新/跳转时解除专注，避免停留在固定屏幕却没有退出按钮
                if (focusActive) {
                    focusActive = false;
                    try { stopLockTask(); } catch (Exception e) { Log.w(TAG, "stopLockTask 失败: " + e.getMessage()); }
                    setImmersiveMode(false);
                }
            }
        });
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

    /**
     * JS 可调用的专注模式接口：沉浸全屏 + 屏幕固定
     */
    public class FocusBridge {
        @JavascriptInterface
        public void startFocus() {
            runOnUiThread(() -> {
                focusActive = true;
                setImmersiveMode(true);
                try {
                    startLockTask();
                } catch (Exception e) {
                    Log.w(TAG, "startLockTask 失败: " + e.getMessage());
                }
            });
        }

        @JavascriptInterface
        public void stopFocus() {
            runOnUiThread(() -> {
                focusActive = false;
                try {
                    stopLockTask();
                } catch (Exception e) {
                    Log.w(TAG, "stopLockTask 失败: " + e.getMessage());
                }
                setImmersiveMode(false);
            });
        }
    }

    @SuppressWarnings("deprecation")
    private void setImmersiveMode(boolean on) {
        View decor = getWindow().getDecorView();
        if (on) {
            decor.setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
        } else {
            decor.setSystemUiVisibility(View.SYSTEM_UI_FLAG_VISIBLE);
        }
    }

    @Override
    public void onBackPressed() {
        if (focusActive) {
            Toast.makeText(this, "专注中，请长按顶部「结束」按钮", Toast.LENGTH_SHORT).show();
            return;
        }
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
        if (focusActive) {
            try { stopLockTask(); } catch (Exception e) { Log.w(TAG, "stopLockTask 失败: " + e.getMessage()); }
            focusActive = false;
        }
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
