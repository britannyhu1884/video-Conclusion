"""
手动输入字幕API地址（含auth_key），用requests获取字幕内容。
1. 先用浏览器F12抓到字幕API完整URL（含auth_key），复制到终端。
2. 需手动填入你的B站cookie字符串。
"""

import requests

# 手动填入你的B站cookie字符串
cookie_str = input('请输入你的B站cookie字符串：').strip()

# 手动输入字幕API完整URL（含auth_key）
subtitle_url = input('请输入字幕API完整URL（含auth_key）：').strip()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Cookie": cookie_str
}

resp = requests.get(subtitle_url, headers=headers)
subtitle_data = resp.json()

print('【字幕内容】')
for item in subtitle_data.get('body', []):
    print(f"{item['from']} - {item['to']}: {item['content']}")
