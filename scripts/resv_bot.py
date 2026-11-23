"""
予約クリックボット（Playwright）

指定URLにアクセスし、<i title="L -013"> を選択して #resv-purchase をクリックする。
以降、 INTERVAL_SECONDS（既定600秒=10分）ごとに再アクセスして同じ操作を繰り返す。
MAX_DURATION_SECONDS（既定21000秒=5時間50分）に達したら終了し、
ワークフロー側の「次回起動ステップ」が次の Actions を引き継いで起動する。
"""

import datetime
import os
import time

from playwright.sync_api import sync_playwright

TARGET_URL = os.environ["TARGET_URL"]
INTERVAL_SECONDS = int(os.environ.get("INTERVAL_SECONDS", "600"))       # クリック間隔（10分）
MAX_DURATION_SECONDS = int(os.environ.get("MAX_DURATION_SECONDS", "21000"))  # 5時間50分
CLICK_RETRIES = int(os.environ.get("CLICK_RETRIES", "3"))               # 1ラウンドあたりの再試行回数
RETRY_WAIT_SECONDS = int(os.environ.get("RETRY_WAIT_SECONDS", "15"))

# セレクタ（title属性の "L -013" は空白を含むためそのまま指定）
SELECTOR_ITEM = 'i[title="L -013"]'
SELECTOR_NEXT = "#resv-purchase"

os.makedirs("screenshots", exist_ok=True)


def log(msg: str) -> None:
    print(
        f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}",
        flush=True,
    )


def ts() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def attempt_once(page) -> bool:
    """1回分の操作: アクセス → L -013 を選択 → 次へ をクリック"""
    log(f"アクセス中: {TARGET_URL}")
    page.goto(TARGET_URL, wait_until="networkidle", timeout=120_000)

    page.wait_for_selector(SELECTOR_ITEM, timeout=60_000)
    page.click(SELECTOR_ITEM)
    log('項目 "L -013" を選択しました')

    page.wait_for_selector(SELECTOR_NEXT, timeout=60_000)
    page.click(SELECTOR_NEXT)
    log('"次へ" (#resv-purchase) をクリックしました')

    page.screenshot(path=f"screenshots/click-{ts()}.png")
    return True


def main() -> None:
    log(f"開始: 間隔={INTERVAL_SECONDS}秒, 上限={MAX_DURATION_SECONDS}秒")
    start = time.monotonic()
    round_no = 0

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        while True:
            elapsed = time.monotonic() - start
            if elapsed >= MAX_DURATION_SECONDS:
                log(
                    f"上限時間 {MAX_DURATION_SECONDS} 秒に到達 "
                    f"(経過 {int(elapsed)} 秒)。ループを終了し、次回を実行します。"
                )
                break

            round_no += 1
            log(f"--- ラウンド {round_no} (経過 {int(elapsed)} 秒) ---")

            ok = False
            for attempt in range(1, CLICK_RETRIES + 1):
                try:
                    attempt_once(page)
                    ok = True
                    break
                except Exception as e:  # noqa: BLE001
                    log(f"エラー (試行 {attempt}/{CLICK_RETRIES}): {e}")
                    try:
                        page.screenshot(path=f"screenshots/error-{ts()}.png")
                    except Exception:  # noqa: BLE001
                        pass
                    time.sleep(RETRY_WAIT_SECONDS)
                    # セッション切れに備えてページを作り直して再アクセスする
                    try:
                        page = browser.new_page(viewport={"width": 1280, "height": 800})
                    except Exception:  # noqa: BLE001
                        pass

            if not ok:
                log("このラウンドは失敗しました。次の間隔で再試行します。")

            # 次のクリックまで待機（上限時間を超えないよう細かくチェック）
            target = start + round_no * INTERVAL_SECONDS
            while time.monotonic() < target:
                remaining = target - time.monotonic()
                if start + MAX_DURATION_SECONDS <= time.monotonic():
                    break
                time.sleep(min(5, max(0.1, remaining)))

        browser.close()

    log("完了。ワークフローの後続ステップが次の Actions を起動します。")


if __name__ == "__main__":
    main()
