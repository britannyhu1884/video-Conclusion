import requests
import json
from playwright.sync_api import sync_playwright

# 手动填入你的B站cookie字符串
cookies = "buvid3=5DCB2F31-20C2-DBDB-7E8E-F6CF90813A0763362infoc; b_nut=1755263163; _uuid=A6FAF1AB-A22E-AE69-F251-CE23FFEBE10CC63618infoc; buvid_fp=91c86df4b38661d2124482387a0cdae0; enable_web_push=DISABLE; buvid4=52DF1AB6-ADD6-BB38-19D1-766FC12E1F0D64130-025081521-04drIyel8LnEfaL2AzNQUg%3D%3D; rpdid=|(J|)J|kY)mJ0J'u~lY)kR~Rk; SESSDATA=c2fb3495%2C1772376783%2C3425a%2A91CjA-4-mjOM0PWZLv06SZDJNuh7XmHgufxQET_U27hvvuGkn6kAuh2xTiBvIguKI7q4ISVmszYnFGdERBSUN3dWstejhlWnZUbWJ5ZmpUSWotQ0U0U1Jhbm5wOXo4TDM4UEhEY0dnLUF3azFJaUUtSFN1Y005UU5Ec2l1TUxUWmtWM0pTU1k5NXV3IIEC; bili_jct=89c7be0e8240fc3b1ab0f94de166b8cd; DedeUserID=13205061; DedeUserID__ckMd5=df2fee09c6521c0b; sid=7zhol0jo; CURRENT_QUALITY=80; theme-tip-show=SHOWED; theme-avatar-tip-show=SHOWED; share_source_origin=WEIXIN; bsource=share_source_weixinchat; home_feed_column=5; browser_resolution=1512-767; bp_t_offset_13205061=1128615872361922560; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjI3ODA1MTEsImlhdCI6MTc2MjUyMTI1MSwicGx0IjotMX0.Dpz-75hhpPTslDElaLTWpSSwgCOfbclljvsTfJi8ypk; bili_ticket_expires=1762780451; b_lsid=798943910_19A67F92594; CURRENT_FNVAL=4048"
bvid = input("请输入B站视频的bvid: ")
subtitle_url = input("请输入字幕的url: ")

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Cookie": cookies
}  

# 获取视频信息的API地址
# 为什么你可以知道用这个url可以获取api呢？因为你可以通过浏览器的开发者工具，网络请求，XHR，找到这个请求地址
api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
resp = requests.get(api_url, headers=headers)
data = resp.json()
# print(json.dumps(data, indent=4, ensure_ascii=False))  # 美化输出JSON数据
print("/n-----------------/n")
# print("cid:", data['data']['cid']) # 输出cid
cid = data['data']['cid']
for sub in data['data']['subtitle']['list']:
    print(sub)
subtitle_id = data['data']['subtitle']['list'][2]['id_str']
print("subtitle_id:", subtitle_id) # 输出字幕ID
print("cid:", cid) # 输出cid

# 获取字幕的API地址，为什么你知道这个url可以获取字幕呢？同样是通过浏览器的开发者工具，网络请求，XHR，找到这个请求地址
resp = requests.get(subtitle_url, headers=headers)
# print(resp.text)
subtitle_data = resp.json()
# 打印所有字幕内容
all_content = ";".join(item['content'] for item in subtitle_data['body'])

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(all_content)

print("字幕内容已写入 output.txt")
