# 这个是免费翻译字幕的网站 https://www.aitransdub.com/bilibili-subtitles 是不需要登陆的
# 这个是测试的视频链接 https://www.bilibili.com/video/BV1DsnzzwEUF/?spm_id_from=333.1007.top_right_bar_window_history.content.click&vd_source=7610be20b2bed89d17217ffdb79c6054 特点是没有字幕

import requests
from bs4 import BeautifulSoup
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

url = "https://www.aitransdub.com/bilibili-subtitles"
logger.info(f"正在访问: {url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
logger.info(f"状态码: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 查找所有输入框
    inputs = soup.find_all('input')
    logger.info(f"找到 {len(inputs)} 个输入框:")
    
    for i, inp in enumerate(inputs, 1):
        input_type = inp.get('type', '未知')
        placeholder = inp.get('placeholder', '无')
        logger.info(f"  {i}. 类型: {input_type}, 占位符: {placeholder}")
    
    # 特别查找URL相关的输入框
    url_inputs = [inp for inp in inputs if 'url' in str(inp.get('placeholder', '')).lower()]
    
    if url_inputs:
        logger.info("✅ 找到URL输入框!")
        for inp in url_inputs:
            logger.info(f"   占位符: {inp.get('placeholder')}")
    else:
        logger.warning("❌ 未找到明显的URL输入框")
    
    # 查找Generate按钮
    logger.info("正在查找Generate按钮...")
    buttons = soup.find_all('button')
    logger.info(f"找到 {len(buttons)} 个按钮:")
    
    generate_button = None
    for i, btn in enumerate(buttons, 1):
        btn_text = btn.get_text().strip()
        btn_class = btn.get('class', [])
        logger.info(f"  {i}. 按钮文本: '{btn_text}', class: {btn_class}")
        
        # 查找包含"generate"的按钮
        if 'generate' in btn_text.lower():
            generate_button = btn
            logger.info(f"  ✅ 找到Generate按钮: '{btn_text}'")
    
    if generate_button:
        logger.info("✅ 成功找到Generate按钮!")
        logger.info(f"   按钮文本: {generate_button.get_text().strip()}")
        logger.info(f"   按钮class: {generate_button.get('class')}")
        
        # 现在使用Playwright模拟输入和点击（比Selenium更稳定）
        logger.info("开始使用Playwright模拟输入视频URL和点击Generate按钮...")
        try:
            from playwright.sync_api import sync_playwright
            import time
            
            # 测试视频URL
            test_video_url = "https://www.bilibili.com/video/BV1DsnzzwEUF/"
            
            with sync_playwright() as p:
                # 启动浏览器（使用headless模式）
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                )
                page = context.new_page()
                
                try:
                    # 访问网站
                    page.goto(url, wait_until='domcontentloaded')
                    logger.info("Playwright浏览器已访问网站")
                    
                    # 找到URL输入框并输入
                    url_input = page.locator("input[placeholder='Paste video URL here']")
                    url_input.clear()
                    url_input.fill(test_video_url)
                    logger.info(f"已输入视频URL: {test_video_url}")
                    
                    # 找到Generate按钮并点击
                    generate_btn = page.locator("button:has-text('Generate')")
                    generate_btn.click()
                    logger.info("已点击Generate按钮")
                    
                    # 等待页面响应，等待更长时间让后台处理
                    logger.info("等待页面响应...")
                    
                    # 等待可能的字幕内容出现
                    try:
                        # 尝试等待字幕相关元素出现，最多等待30秒
                        page.wait_for_selector('text="subtitle"', timeout=30000)
                        logger.info("检测到字幕相关内容")
                    except:
                        logger.info("30秒内未检测到字幕相关内容，继续检查页面")
                    
                    # 再等待一些时间让内容完全加载
                    time.sleep(10)
                    
                    # 检查URL是否改变
                    current_url = page.url
                    logger.info(f"当前页面URL: {current_url}")
                    
                    # 检查是否有任何加载状态的元素
                    loading_elements = page.query_selector_all('[class*="loading"], [class*="spinner"], .loader')
                    if loading_elements:
                        logger.info(f"发现 {len(loading_elements)} 个加载状态元素，等待加载完成...")
                        time.sleep(15)
                    
                    # 获取页面内容
                    page_title = page.title()
                    page_content = page.content()
                    
                    new_soup = BeautifulSoup(page_content, 'html.parser')
                    
                    print("\n" + "="*50)
                    print("使用Playwright模拟输入视频URL后的新网页内容:")
                    print("="*50)
                    print(f"页面URL: {current_url}")
                    print(f"页面标题: {page_title}")
                    
                    # 查找可能包含字幕的内容
                    # 方法1：查找包含"subtitle"或相关关键词的元素
                    subtitle_elements = new_soup.find_all(text=lambda text: text and any(
                        keyword in text.lower() for keyword in ['subtitle', 'transcript', '字幕', 'caption']
                    ))
                    
                    if subtitle_elements:
                        print("\n找到字幕相关内容:")
                        for i, text in enumerate(subtitle_elements[:5], 1):
                            clean_text = text.strip()
                            if len(clean_text) > 20:
                                print(f"{i}. {clean_text[:200]}...")
                    
                    # 方法2：查找长文本内容（可能是字幕）
                    all_text_elements = new_soup.find_all(['p', 'div', 'span'], string=True)
                    long_texts = []
                    for element in all_text_elements:
                        text = element.get_text().strip()
                        if len(text) > 100 and not any(skip in text.lower() for skip in ['menu', 'button', 'sign in', 'cookie', 'privacy']):
                            long_texts.append(text)
                    
                    if long_texts:
                        print("\n找到长文本内容（可能的字幕）:")
                        for i, text in enumerate(long_texts[:3], 1):
                            print(f"{i}. {text[:300]}...")
                    
                    # 方法3：检查是否有错误信息
                    error_messages = new_soup.find_all(text=lambda text: text and any(
                        keyword in text.lower() for keyword in ['error', 'invalid', 'please enter', 'failed', '错误']
                    ))
                    
                    if error_messages:
                        print("\n发现错误或提示信息:")
                        for i, text in enumerate(error_messages[:3], 1):
                            clean_text = text.strip()
                            if len(clean_text) > 5:
                                print(f"{i}. {clean_text}")
                    
                    # 方法4：查找可能的字幕下载链接或结果区域
                    download_links = new_soup.find_all('a', href=True)
                    subtitle_links = [link for link in download_links if any(
                        keyword in link.get('href', '').lower() or keyword in link.get_text().lower()
                        for keyword in ['subtitle', 'download', 'srt', 'vtt']
                    )]
                    
                    if subtitle_links:
                        print("\n找到可能的字幕下载链接:")
                        for i, link in enumerate(subtitle_links[:3], 1):
                            print(f"{i}. 链接文本: {link.get_text().strip()}")
                            print(f"   链接地址: {link.get('href')}")
                    
                    # 如果都没找到，显示页面的主要结构
                    if not subtitle_elements and not long_texts and not error_messages and not subtitle_links:
                        print("\n页面主要内容:")
                        main_content = new_soup.find('body')
                        if main_content:
                            text_content = main_content.get_text()
                            # 清理文本并只显示有意义的部分
                            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                            meaningful_lines = [line for line in lines if len(line) > 10][:10]
                            for i, line in enumerate(meaningful_lines, 1):
                                print(f"{i}. {line[:200]}...")
                    
                    print("="*50)
                    
                finally:
                    browser.close()
                
        except ImportError:
            logger.error("需要安装playwright: pip install playwright")
            logger.error("安装后还需要运行: playwright install")
        except Exception as e:
            logger.error(f"Playwright操作失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        logger.warning("❌ 未找到Generate按钮")
        # 显示所有按钮文本以便分析
        logger.info("所有按钮的文本内容:")
        for i, btn in enumerate(buttons, 1):
            text = btn.get_text().strip()
            if text:  # 只显示有文本的按钮
                logger.info(f"  {i}. '{text}'")

else:
    logger.error("访问失败")

