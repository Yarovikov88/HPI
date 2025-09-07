#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.parse

BASE_URL = os.getenv("BASE_URL", "http://localhost:3000/api")
TOKEN = os.getenv("TOKEN", "")
DATE = os.getenv("DATE", "2025-09-02")
CATEGORIES = ["problems", "goals", "blockers", "metrics", "achievements"]

if not TOKEN:
    print("[ERR] Не задан TOKEN (экспортируйте переменную окружения TOKEN=...)")
    sys.exit(1)

print(f"Проверяем PRO ответы на дату: {DATE}")
print(f"BASE_URL: {BASE_URL}")

for cat in CATEGORIES:
    url = f"{BASE_URL}/pro/answers/{cat}?" + urllib.parse.urlencode({"date": DATE})
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", "ignore")
            try:
                data = json.loads(raw)
            except Exception:
                print(f"{cat}: не удалось распарсить JSON, ответ:\n{raw}")
                continue
            count = len(data) if isinstance(data, list) else 1
            print(f"{cat}: {count} записей")
            if isinstance(data, list) and data[:1]:
                print("  пример:", json.dumps(data[0], ensure_ascii=False))
            elif isinstance(data, dict):
                print("  ответ:", json.dumps(data, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        print(f"{cat}: HTTP {e.code} — {body}")
    except Exception as e:
        print(f"{cat}: ошибка запроса — {e}") 