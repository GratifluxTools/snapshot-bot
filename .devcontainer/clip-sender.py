#!/usr/bin/env python3
import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>Clipboard Sender</title></head>
<body style="font-family:sans-serif">
<h3>リモートブラウザのクリップボードに送信</h3>
<textarea id="t" rows="10" cols="60" placeholder="ここに日本語を貼り付け"></textarea><br>
<button id="b">送信 (リモートのクリップボードへ)</button>
<span id="s"></span>
<script>
document.getElementById("b").onclick = async () => {
  const r = await fetch("/set", {method: "POST", body: document.getElementById("t").value});
  document.getElementById("s").textContent = r.ok ? " 送信完了。リモートで Ctrl+V" : " 失敗";
};
</script>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        text = self.rfile.read(length).decode("utf-8")
        env = {**os.environ, "DISPLAY": ":1"}
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode("utf-8"),
            env=env,
            check=True,
        )
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass

if __name__ == "__main__":
    # 127.0.0.1 に限定。PORTSタブのポート転送経由でのみアクセス可能
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
