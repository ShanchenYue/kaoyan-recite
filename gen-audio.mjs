// gen-audio.mjs — 批量生成拟人语音MP3 (直接调用 node-edge-tts API)
// 用法: node gen-audio.mjs [--book 0|1|2] [--limit 10] [--skip-existing]
import { EdgeTTS } from 'node-edge-tts';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = __dirname;
const AUDIO_DIR = path.join(ROOT, 'audios');

// 每本书不同音色 (edge-tts 神经语音)
const BOOK_VOICES = [
  'zh-CN-XiaoyiNeural',    // 0: 时政热点 - 晓伊女声
  'zh-CN-YunxiNeural',     // 1: 肖190题 - 云希男声
  'zh-CN-XiaohanNeural',   // 2: 周年事件 - 晓涵女声
  'zh-CN-XiaoxiaoNeural',  // 3: 背诵包 - 晓晓女声
];

const args = process.argv.slice(2);
const targetBook = parseInt(args[args.indexOf('--book') + 1]) || -1;
const limitArg = parseInt(args[args.indexOf('--limit') + 1]) || 0;
const skipExisting = args.includes('--skip-existing');

const data = JSON.parse(fs.readFileSync(path.join(ROOT, 'data.json'), 'utf-8'));
fs.mkdirSync(AUDIO_DIR, { recursive: true });

const tasks = [];
data.books.forEach((book, bi) => {
  if (book.is_scanned) return;
  if (targetBook >= 0 && bi !== targetBook) return;
  const voice = BOOK_VOICES[bi % BOOK_VOICES.length];
  const bookDir = path.join(AUDIO_DIR, String(bi).padStart(2, '0'));
  fs.mkdirSync(bookDir, { recursive: true });
  book.segments.forEach((seg, si) => {
    const outPath = path.join(bookDir, `${String(si).padStart(4, '0')}.mp3`);
    if (skipExisting && fs.existsSync(outPath) && fs.statSync(outPath).size > 500) return;
    tasks.push({ bi, si, text: seg.text, voice, outPath });
  });
});
if (limitArg > 0) tasks.splice(limitArg);

console.log(`共 ${tasks.length} 个音频待生成`);
if (tasks.length === 0) { console.log('全部已存在或无任务，退出'); process.exit(0); }

// 估算
const est = tasks.reduce((s, t) => s + Math.min(t.text.length, 4800), 0);
console.log(`预计总字符: ${est}  (~${(est/15).toFixed(0)}s 语音, ~${(est*0.02).toFixed(0)} MB mp3)`);
console.log();

let done = 0, fail = 0, rateLimitWait = 0;
const start = Date.now();

for (const task of tasks) {
  const text = task.text.length > 4800 ? task.text.slice(0, 4800) : task.text;
  let ok = false;

  for (let retry = 0; retry < 3; retry++) {
    try {
      const tts = new EdgeTTS({
        voice: task.voice,
        lang: 'zh-CN',
        outputFormat: 'audio-24khz-48kbitrate-mono-mp3',
        timeout: 20000,
      });
      await tts.ttsPromise(text, task.outPath);
      if (fs.existsSync(task.outPath) && fs.statSync(task.outPath).size > 500) {
        ok = true;
        break;
      }
    } catch (e) {
      const msg = String(e);
      if (msg.includes('429') || msg.includes('rate limit') || msg.includes('40007')) {
        // 微软限流 —— 等久一点
        rateLimitWait++;
        const wait = 5000 * (retry + 1);
        process.stdout.write(`\n  [限流] 等${wait/1000}s后第${retry+1}次重试... `);
        await new Promise(r => setTimeout(r, wait));
      } else {
        await new Promise(r => setTimeout(r, 300 * (retry + 1)));
      }
    }
  }

  if (ok) {
    done++;
  } else {
    fail++;
    if (fail <= 5) {
      console.log(`\n  失败 book${task.bi}#${task.si}: ${task.text.slice(0,30)}...`);
    }
  }

  const elapsed = (Date.now() - start) / 1000;
  const rate = done / Math.max(elapsed, 1);
  const remain = (tasks.length - done - fail) / Math.max(rate, 0.01);
  process.stdout.write(
    `\r${done+fail}/${tasks.length}  ✓${done} ✗${fail}  ${elapsed.toFixed(0)}s  ~剩${remain.toFixed(0)}s  ${(rate*60).toFixed(0)}/min  `
  );

  // 每条间隔 400ms 降低限流概率
  await new Promise(r => setTimeout(r, 400));
}

console.log(`\n\n=== 完成 ===`);
console.log(`成功: ${done} / 失败: ${fail}`);
console.log(`限流次数: ${rateLimitWait}`);
console.log(`总耗时: ${((Date.now()-start)/1000/60).toFixed(1)} 分钟`);
console.log(`输出: ${AUDIO_DIR}`);

// 统计总大小
let totalBytes = 0;
for (const task of tasks) {
  if (fs.existsSync(task.outPath)) {
    totalBytes += fs.statSync(task.outPath).size;
  }
}
console.log(`音频总大小: ${(totalBytes/1024/1024).toFixed(1)} MB`);
