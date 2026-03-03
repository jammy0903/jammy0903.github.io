#!/usr/bin/env python3
"""
블로그 글 생성기 - 로컬 웹 GUI

사용법:
  python3 blog_gui.py
  # 브라우저에서 http://localhost:8080 접속
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from threading import Thread


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

# ollama_post.py에서 재사용할 함수들 import
from ollama_post import (
    get_next_post_number,
    make_slug,
    save_post,
    auto_commit,
    DEFAULT_MODEL,
    POSTS_DIR,
)

OLLAMA_API_GENERATE = "http://localhost:11434/api/generate"
OLLAMA_API_TAGS = "http://localhost:11434/api/tags"
HOST = "localhost"
PORT = 8080


# ---------------------------------------------------------------------------
# SSE 스트리밍용 Ollama 호출 (토큰 단위 yield)
# ---------------------------------------------------------------------------

def stream_ollama(prompt, model):
    """Ollama API를 호출하고 토큰 단위로 yield한다."""
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_API_GENERATE,
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(req, timeout=300) as resp:
        for line in resp:
            line = line.decode("utf-8").strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                token = obj.get("response", "")
                if token:
                    yield token
                if obj.get("done"):
                    break
            except json.JSONDecodeError:
                continue


def get_ollama_models():
    """Ollama에서 사용 가능한 모델 목록을 반환한다."""
    try:
        req = urllib.request.Request(OLLAMA_API_TAGS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        return [DEFAULT_MODEL]


# ---------------------------------------------------------------------------
# 프롬프트 (ollama_post.py와 동일)
# ---------------------------------------------------------------------------

def title_prompt(topic):
    return f"""아래 주제로 한국어 블로그 글 제목을 하나만 만들어 주세요.

주제: {topic}

규칙:
- 한국어로 작성
- 간결하고 흥미를 끄는 제목
- 따옴표 없이 제목만 출력

제목:"""


def content_prompt(topic):
    return f"""당신은 기술 블로그 작성자입니다. 아래 주제에 대해 한국어로 블로그 글을 작성하세요.

주제: {topic}

작성 규칙:
- 한국어로 작성하되, 말투는 "음슴체"를 사용 (예: ~임, ~함, ~됨, ~있음, ~인 듯)
- 마크다운 문법을 적극적으로 활용:
  - ## / ### 헤더로 섹션 구분
  - `---` 수평선으로 섹션 사이를 시각적으로 구분
  - **굵게**, *기울임*, `인라인 코드` 적극 활용
  - > 인용 블록(콜아웃)으로 핵심 포인트나 주의사항 강조
  - 표(| 헤더 | 헤더 |)가 유용한 경우 표로 정리
  - 순서 있는 목록(1. 2. 3.)과 순서 없는 목록(- ) 혼합 사용
  - 코드 예시가 필요하면 코드블럭(```)에 언어 지정 포함
- 핵심 개념을 일상생활에 비유해서 쉽게 설명
- 제목(# 또는 title)은 포함하지 말 것 (frontmatter에서 처리)
- 글 분량은 적당히 (너무 짧지도, 너무 길지도 않게)

바로 본문 내용만 작성하세요:"""


def tags_prompt(topic, content_text):
    return f"""아래 블로그 글의 주제와 내용을 보고 적절한 태그를 1~5개 추출하세요.

주제: {topic}
내용 일부: {content_text[:500]}

규칙:
- 태그는 영어 소문자, 하이픈(-) 사용
- 쉼표(,)로 구분
- 태그만 출력 (설명 없이)

예시 출력: linux, file-permission, security

태그:"""


def parse_tags(raw):
    """태그 문자열을 파싱한다."""
    tags = []
    for t in raw.replace("\n", ",").split(","):
        t = t.strip().strip("'\"").strip()
        t = re.sub(r"[^a-zA-Z0-9가-힣\-]", "", t)
        if t:
            tags.append(t)
    tags = tags[:5]
    if not tags:
        tags = ["blog"]
    return tags


# ---------------------------------------------------------------------------
# HTTP 요청 핸들러
# ---------------------------------------------------------------------------

class BlogHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        """요청 로깅."""
        print(f"[{self.log_date_time_string()}] {format % args}")

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    # ----- 라우팅 -----

    def do_GET(self):
        if self.path == "/":
            self._serve_html()
        elif self.path == "/api/models":
            self._handle_models()
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/generate":
            self._handle_generate()
        elif self.path == "/api/save":
            self._handle_save()
        elif self.path == "/api/commit":
            self._handle_commit()
        else:
            self.send_error(404)

    # ----- 핸들러 구현 -----

    def _serve_html(self):
        body = HTML_PAGE.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_models(self):
        models = get_ollama_models()
        self._send_json({"models": models, "default": DEFAULT_MODEL})

    def _handle_generate(self):
        """SSE로 글 생성 과정을 스트리밍한다."""
        body = self._read_body()
        topic = body.get("topic", "").strip()
        model = body.get("model", DEFAULT_MODEL).strip()

        if not topic:
            self._send_json({"error": "토픽을 입력하세요."}, 400)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        def send_event(event, data):
            payload = json.dumps(data, ensure_ascii=False)
            msg = f"event: {event}\ndata: {payload}\n\n"
            try:
                self.wfile.write(msg.encode("utf-8"))
                self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                raise

        try:
            # 1단계: 제목 생성
            send_event("phase", {"phase": "title", "message": "제목 생성 중..."})
            title_parts = []
            for token in stream_ollama(title_prompt(topic), model):
                title_parts.append(token)
                send_event("token", {"phase": "title", "token": token})
            raw_title = "".join(title_parts).strip().strip('"').strip("'").strip()
            raw_title = raw_title.split("\n")[0].strip()
            if not raw_title:
                raw_title = topic
            send_event("phase_done", {"phase": "title", "result": raw_title})

            # 2단계: 본문 생성
            send_event("phase", {"phase": "content", "message": "본문 생성 중..."})
            content_parts = []
            for token in stream_ollama(content_prompt(topic), model):
                content_parts.append(token)
                send_event("token", {"phase": "content", "token": token})
            full_content = "".join(content_parts).strip()
            send_event("phase_done", {"phase": "content", "result": ""})

            # 3단계: 태그 생성
            send_event("phase", {"phase": "tags", "message": "태그 생성 중..."})
            tag_parts = []
            for token in stream_ollama(tags_prompt(topic, full_content), model):
                tag_parts.append(token)
                send_event("token", {"phase": "tags", "token": token})
            tags = parse_tags("".join(tag_parts))
            send_event("phase_done", {"phase": "tags", "result": tags})

            # 완료
            post_number = get_next_post_number()
            send_event("done", {
                "title": raw_title,
                "content": full_content,
                "tags": tags,
                "post_number": post_number,
            })

        except (BrokenPipeError, ConnectionResetError):
            pass
        except urllib.error.URLError as e:
            send_event("error", {"message": f"Ollama 연결 실패: {e}"})
        except Exception as e:
            try:
                send_event("error", {"message": str(e)})
            except Exception:
                pass

    def _handle_save(self):
        body = self._read_body()
        title = body.get("title", "")
        content = body.get("content", "")
        tags = body.get("tags", ["blog"])
        post_number = body.get("post_number", get_next_post_number())

        if not title or not content:
            self._send_json({"error": "제목과 내용이 필요합니다."}, 400)
            return

        filepath, filename = save_post(title, content, tags, post_number)
        self._send_json({
            "filepath": filepath,
            "filename": filename,
            "post_number": post_number,
        })

    def _handle_commit(self):
        body = self._read_body()
        title = body.get("title", "")
        content = body.get("content", "")
        tags = body.get("tags", ["blog"])
        post_number = body.get("post_number", get_next_post_number())

        if not title or not content:
            self._send_json({"error": "제목과 내용이 필요합니다."}, 400)
            return

        filepath, filename = save_post(title, content, tags, post_number)
        auto_commit(filepath, post_number, title)
        self._send_json({
            "filepath": filepath,
            "filename": filename,
            "post_number": post_number,
            "committed": True,
        })


# ---------------------------------------------------------------------------
# 임베드 HTML
# ---------------------------------------------------------------------------

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>블로그 글 생성기</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d1117;--surface:#161b22;--border:#30363d;
  --text:#c9d1d9;--text-dim:#8b949e;--accent:#58a6ff;
  --green:#3fb950;--red:#f85149;--yellow:#d29922;
  --radius:8px;
}
body{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  background:var(--bg);color:var(--text);line-height:1.6;
  min-height:100vh;display:flex;flex-direction:column;align-items:center;
  padding:2rem 1rem;
}
h1{font-size:1.6rem;margin-bottom:1.5rem;color:#fff}
.container{width:100%;max-width:820px}
/* 입력 영역 */
.input-group{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1.2rem;margin-bottom:1rem;
}
.input-group label{display:block;font-size:.85rem;color:var(--text-dim);margin-bottom:.4rem}
.input-group input[type=text],
.input-group select{
  width:100%;padding:.55rem .7rem;
  background:var(--bg);color:var(--text);
  border:1px solid var(--border);border-radius:var(--radius);
  font-size:.95rem;outline:none;
}
.input-group input:focus,
.input-group select:focus{border-color:var(--accent)}
.row{display:flex;gap:1rem;margin-top:.8rem}
.row>*{flex:1}
/* 버튼 */
.btn{
  display:inline-flex;align-items:center;justify-content:center;gap:.4rem;
  padding:.55rem 1.2rem;border:none;border-radius:var(--radius);
  font-size:.9rem;font-weight:600;cursor:pointer;transition:opacity .15s;
}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn:hover:not(:disabled){opacity:.85}
.btn-primary{background:var(--accent);color:#fff}
.btn-green{background:var(--green);color:#fff}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--text)}
.actions{display:flex;gap:.6rem;margin-top:.8rem;flex-wrap:wrap}
/* 진행 상태 */
.progress{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:1rem;
  display:none;
}
.progress.active{display:block}
.phase{
  display:flex;align-items:center;gap:.5rem;
  padding:.3rem 0;font-size:.88rem;color:var(--text-dim);
}
.phase .icon{width:18px;text-align:center}
.phase.running{color:var(--yellow)}
.phase.done{color:var(--green)}
.phase.error{color:var(--red)}
.spinner{display:inline-block;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
/* 스트리밍 출력 */
.stream-box{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:1rem;
  display:none;max-height:420px;overflow-y:auto;
  font-size:.88rem;white-space:pre-wrap;word-break:break-word;
}
.stream-box.active{display:block}
.stream-label{
  font-size:.78rem;color:var(--text-dim);margin-bottom:.5rem;
  text-transform:uppercase;letter-spacing:.05em;
}
/* 결과 영역 */
.result{
  background:var(--surface);border:1px solid var(--border);
  border-radius:var(--radius);padding:1.2rem;margin-bottom:1rem;
  display:none;
}
.result.active{display:block}
.result .field-label{font-size:.78rem;color:var(--text-dim);margin-bottom:.3rem;text-transform:uppercase;letter-spacing:.05em}
.result .title-input{
  width:100%;padding:.5rem .7rem;margin-bottom:.6rem;
  background:var(--bg);color:#fff;font-size:1.05rem;font-weight:600;
  border:1px solid var(--border);border-radius:var(--radius);outline:none;
}
.result .title-input:focus{border-color:var(--accent)}
.result .meta{font-size:.82rem;color:var(--text-dim);margin-bottom:.8rem}
.result .meta span{margin-right:.8rem}
.preview{
  background:var(--bg);border:1px solid var(--border);
  border-radius:var(--radius);padding:1rem;
  min-height:200px;max-height:500px;overflow-y:auto;
  font-size:.88rem;font-family:inherit;line-height:1.6;
  color:var(--text);width:100%;resize:vertical;
}
/* 상태 메시지 */
.toast{
  position:fixed;bottom:2rem;left:50%;transform:translateX(-50%);
  padding:.6rem 1.2rem;border-radius:var(--radius);
  font-size:.88rem;font-weight:500;
  opacity:0;transition:opacity .3s;pointer-events:none;z-index:100;
}
.toast.show{opacity:1}
.toast.success{background:var(--green);color:#fff}
.toast.error{background:var(--red);color:#fff}
</style>
</head>
<body>
<div class="container">
  <h1>&#9997;&#65039; 블로그 글 생성기</h1>

  <!-- 입력 -->
  <div class="input-group">
    <label for="topic">주제 (Topic)</label>
    <input type="text" id="topic" placeholder="예: Docker 네트워크 이해하기" autofocus>
    <div class="row">
      <div>
        <label for="model">모델</label>
        <select id="model"><option>불러오는 중...</option></select>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-primary" id="btnGenerate" onclick="startGenerate()">글 생성</button>
      <button class="btn btn-outline" id="btnStop" onclick="stopGenerate()" disabled>중지</button>
    </div>
  </div>

  <!-- 진행 상태 -->
  <div class="progress" id="progress">
    <div class="phase" id="phaseTitle"><span class="icon">&#9711;</span> 제목 생성</div>
    <div class="phase" id="phaseContent"><span class="icon">&#9711;</span> 본문 생성</div>
    <div class="phase" id="phaseTags"><span class="icon">&#9711;</span> 태그 생성</div>
  </div>

  <!-- 스트리밍 출력 -->
  <div class="stream-box" id="streamBox">
    <div class="stream-label" id="streamLabel">생성 중...</div>
    <div id="streamText"></div>
  </div>

  <!-- 결과 -->
  <div class="result" id="result">
    <div class="field-label">제목 (편집 가능)</div>
    <input type="text" class="title-input" id="resultTitle">
    <div class="meta">
      <span id="resultNumber"></span>
      <span id="resultTags"></span>
    </div>
    <div class="field-label">본문 (편집 가능)</div>
    <textarea class="preview" id="resultPreview" rows="16"></textarea>
    <div class="actions" style="margin-top:1rem">
      <button class="btn btn-green" onclick="doSave()">저장</button>
      <button class="btn btn-primary" onclick="doCommit()">저장 + 커밋</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let generated = null;
let abortCtrl = null;

// ---------- 모델 목록 로드 ----------
async function loadModels() {
  try {
    const res = await fetch('/api/models');
    const data = await res.json();
    const sel = document.getElementById('model');
    sel.innerHTML = '';
    data.models.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m; opt.textContent = m;
      if (m === data.default) opt.selected = true;
      sel.appendChild(opt);
    });
  } catch(e) {
    console.error('모델 로드 실패:', e);
  }
}
loadModels();

// ---------- 글 생성 ----------
async function startGenerate() {
  const topic = document.getElementById('topic').value.trim();
  if (!topic) { showToast('주제를 입력하세요.', 'error'); return; }
  const model = document.getElementById('model').value;

  // UI 초기화
  generated = null;
  setUI('generating');
  resetPhases();
  document.getElementById('streamText').textContent = '';
  document.getElementById('streamLabel').textContent = '생성 중...';

  abortCtrl = new AbortController();

  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({topic, model}),
      signal: abortCtrl.signal,
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let currentPhase = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});

      const lines = buffer.split('\n');
      buffer = lines.pop(); // 마지막 불완전한 줄 보존

      let eventType = '';
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          eventType = line.slice(7).trim();
        } else if (line.startsWith('data: ')) {
          const data = JSON.parse(line.slice(6));
          handleSSE(eventType, data);
        }
      }
    }
  } catch(e) {
    if (e.name !== 'AbortError') {
      showToast('생성 실패: ' + e.message, 'error');
      setUI('idle');
    }
  }
}

function stopGenerate() {
  if (abortCtrl) { abortCtrl.abort(); abortCtrl = null; }
  setUI('idle');
  showToast('중지됨', 'error');
}

function handleSSE(event, data) {
  const streamText = document.getElementById('streamText');
  const streamLabel = document.getElementById('streamLabel');

  if (event === 'phase') {
    const el = phaseEl(data.phase);
    if (el) { el.className = 'phase running'; el.querySelector('.icon').innerHTML = '<span class="spinner">&#9696;</span>'; }
    streamLabel.textContent = data.message;
    streamText.textContent = '';
  }
  else if (event === 'token') {
    streamText.textContent += data.token;
    // 자동 스크롤
    const box = document.getElementById('streamBox');
    box.scrollTop = box.scrollHeight;
  }
  else if (event === 'phase_done') {
    const el = phaseEl(data.phase);
    if (el) { el.className = 'phase done'; el.querySelector('.icon').textContent = '\u2713'; }
  }
  else if (event === 'done') {
    generated = data;
    showResult(data);
    setUI('done');
  }
  else if (event === 'error') {
    showToast(data.message, 'error');
    setUI('idle');
  }
}

function phaseEl(name) {
  const map = {title:'phaseTitle', content:'phaseContent', tags:'phaseTags'};
  return document.getElementById(map[name]);
}

function resetPhases() {
  ['phaseTitle','phaseContent','phaseTags'].forEach(id => {
    const el = document.getElementById(id);
    el.className = 'phase';
    el.querySelector('.icon').textContent = '\u25CB';
  });
}

function showResult(data) {
  document.getElementById('resultTitle').value = data.title;
  document.getElementById('resultNumber').textContent = '#' + data.post_number;
  document.getElementById('resultTags').textContent = data.tags.map(t => '#'+t).join(' ');
  document.getElementById('resultPreview').value = data.content;
}

function getEditedData() {
  return {
    ...generated,
    title: document.getElementById('resultTitle').value.trim() || generated.title,
    content: document.getElementById('resultPreview').value.trim() || generated.content,
  };
}

// ---------- 저장 / 커밋 ----------
async function doSave() {
  if (!generated) { showToast('먼저 글을 생성하세요.', 'error'); return; }
  try {
    const res = await fetch('/api/save', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(getEditedData()),
    });
    const data = await res.json();
    if (data.error) { showToast(data.error, 'error'); return; }
    showToast('저장 완료: ' + data.filename, 'success');
  } catch(e) {
    showToast('저장 실패: ' + e.message, 'error');
  }
}

async function doCommit() {
  if (!generated) { showToast('먼저 글을 생성하세요.', 'error'); return; }
  try {
    const res = await fetch('/api/commit', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(getEditedData()),
    });
    const data = await res.json();
    if (data.error) { showToast(data.error, 'error'); return; }
    showToast('저장 + 커밋 완료: ' + data.filename, 'success');
  } catch(e) {
    showToast('커밋 실패: ' + e.message, 'error');
  }
}

// ---------- UI 상태 ----------
function setUI(state) {
  const btnGen = document.getElementById('btnGenerate');
  const btnStop = document.getElementById('btnStop');
  const progress = document.getElementById('progress');
  const streamBox = document.getElementById('streamBox');
  const result = document.getElementById('result');

  if (state === 'generating') {
    btnGen.disabled = true; btnStop.disabled = false;
    progress.classList.add('active');
    streamBox.classList.add('active');
    result.classList.remove('active');
  } else if (state === 'done') {
    btnGen.disabled = false; btnStop.disabled = true;
    result.classList.add('active');
  } else {
    btnGen.disabled = false; btnStop.disabled = true;
  }
}

// ---------- 토스트 ----------
function showToast(msg, type) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = 'toast show ' + type;
  setTimeout(() => el.className = 'toast', 3000);
}

// Enter 키로 생성
document.getElementById('topic').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !document.getElementById('btnGenerate').disabled) startGenerate();
});
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 서버 실행
# ---------------------------------------------------------------------------

def main():
    server = ThreadingHTTPServer((HOST, PORT), BlogHandler)
    print(f"블로그 글 생성기 GUI 실행 중: http://{HOST}:{PORT}")
    print("종료하려면 Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n서버 종료.")
        server.server_close()


if __name__ == "__main__":
    main()
