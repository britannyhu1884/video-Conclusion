#!/usr/bin/env python3
"""
Bilibili视频字幕提取器
使用AITransDub网站提取Bilibili视频字幕
"""

import logging
import time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('subtitle_extractor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BilibiliSubtitleExtractor:
    def __init__(self):
        self.base_url = "https://www.aitransdub.com/bilibili-subtitles"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def detect_video_platform(self, url: str) -> str:
        """检测视频平台"""
        if 'bilibili.com' in url:
            return 'bilibili'
        elif 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'xiaohongshu.com' in url or 'xhs.app' in url:
            return 'xiaohongshu'
        else:
            return 'unknown'
    
    def extract_bilibili_subtitles(self, video_url: str) -> Dict:
        """从Bilibili视频提取字幕"""
        logger.info(f"开始提取Bilibili视频字幕: {video_url}")
        
        try:
            with sync_playwright() as p:
                # 启动浏览器
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # 访问网站
                logger.info("访问AITransDub网站...")
                page.goto(self.base_url, timeout=30000)
                
                # 输入视频URL
                logger.info("输入视频URL...")
                url_input = page.locator("input[placeholder='Paste video URL here']")
                url_input.clear()
                url_input.fill(video_url)
                
                # 点击Generate按钮
                logger.info("点击Generate按钮...")
                generate_btn = page.locator("button:has-text('Generate')")
                generate_btn.click()
                
                # 等待页面跳转到结果页面
                logger.info("等待页面处理...")
                # 等待URL变化或特定内容出现
                try:
                    page.wait_for_url("**/video/**", timeout=90000)  # 增加到90秒
                except:
                    # 如果URL没有变化，等待一段时间让页面处理
                    logger.info("URL未变化，等待更长时间...")
                    time.sleep(60)  # 增加到60秒
                
                current_url = page.url
                logger.info(f"页面跳转到: {current_url}")
                
                # 检查是否成功跳转到视频页面
                if '/video/' not in current_url:
                    raise Exception("页面未跳转到视频页面，可能处理失败")
                
                # 对于长视频，需要等待更长时间让字幕完全加载
                logger.info("等待字幕内容完全加载...")
                time.sleep(30)  # 增加等待时间
                
                # 尝试滚动页面以触发更多内容加载
                logger.info("滚动页面以加载更多内容...")
                for i in range(5):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(3)
                    page.evaluate("window.scrollTo(0, 0)")
                    time.sleep(2)
                
                # 获取页面内容
                page_content = page.content()
                browser.close()
                
                # 解析字幕内容
                subtitles = self._parse_subtitle_content(page_content, current_url)
                
                return {
                    'success': True,
                    'video_url': video_url,
                    'result_url': current_url,
                    'video_id': current_url.split('/video/')[-1],
                    'subtitles': subtitles,
                    'subtitle_count': len(subtitles)
                }
                
        except Exception as e:
            logger.error(f"字幕提取失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'video_url': video_url
            }
    
    def _parse_subtitle_content(self, html_content: str, page_url: str) -> List[str]:
        """解析HTML内容提取字幕文本"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 获取所有文本内容
        all_texts = soup.find_all(text=True)
        logger.info(f"网页总共找到 {len(all_texts)} 个文本元素")
        
        # 先用宽松的条件收集所有可能的字幕
        potential_subtitles = []
        for text in all_texts:
            cleaned = text.strip()
            if len(cleaned) > 3:  # 非常宽松的长度要求
                potential_subtitles.append(cleaned)
        
        logger.info(f"长度>3的文本有 {len(potential_subtitles)} 个")
        
        # 保存调试信息到文件
        debug_file = f"debug_content_{int(time.time())}.txt"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write("=== 所有可能的字幕内容 ===\n\n")
            for i, text in enumerate(potential_subtitles[:100], 1):  # 只写前100个避免文件太大
                f.write(f"[{i:03d}] {text}\n\n")
        
        logger.info(f"调试信息已保存到: {debug_file}")
        
        # 现在用更宽松的过滤条件，并寻找真正的字幕内容
        subtitle_texts = []
        
        # 首先用非常宽松的条件收集所有可能的内容
        for text in potential_subtitles:
            if (len(text) > 5 and  # 很低的长度要求
                not text.startswith(('[', '{', '<', '/*', 'function', 'window.', 'var ', 'const ', 'let ')) and
                not any(skip in text.lower() for skip in [
                    'class:', 'style:', 'onclick', 'href=', 'src=', 'datalayer',
                    'gtag', 'plausible', '-webkit-', '-moz-', 'rgba(', 'margin:',
                    'padding:', 'border:', 'background:', 'font-', 'color:',
                    'display:', 'position:', 'width:', 'height:', 'transition:'
                ]) and
                not re.search(r'px|em|rem|vh|vw|%|rgb|rgba|#[0-9a-fA-F]', text) and  # 不包含CSS单位
                not re.search(r'[{}();=]', text)):  # 不包含代码符号
                
                subtitle_texts.append(text)
        
        logger.info(f"初步过滤后有 {len(subtitle_texts)} 段内容")
        
        # 寻找真正的字幕内容开始位置（通常是连续的、有意义的句子）
        real_subtitle_start = 0
        chinese_count = 0
        
        for i, text in enumerate(subtitle_texts):
            # 统计包含中文的连续文本
            if re.search(r'[\u4e00-\u9fff]', text) and len(text) > 10:
                chinese_count += 1
                if chinese_count >= 3:  # 连续3个中文文本，认为开始了真正的字幕
                    real_subtitle_start = max(0, i - 5)  # 往前取5个作为缓冲
                    logger.info(f"检测到真正的字幕内容从第 {real_subtitle_start} 个开始")
                    break
            else:
                chinese_count = 0
        
        # 如果没找到中文字幕，尝试寻找英文字幕模式
        if real_subtitle_start == 0:
            sentence_count = 0
            for i, text in enumerate(subtitle_texts):
                # 寻找像句子的英文内容
                if (len(text) > 15 and 
                    len(text.split()) > 3 and
                    not any(nav in text.lower() for nav in ['transcript', 'download', 'subtitle', 'menu', 'sign', 'cookie']) and
                    ('.' in text or ',' in text or text[0].isupper())):
                    sentence_count += 1
                    if sentence_count >= 5:  # 连续5个句子样式的文本
                        real_subtitle_start = max(0, i - 10)
                        logger.info(f"检测到英文字幕内容从第 {real_subtitle_start} 个开始")
                        break
                else:
                    sentence_count = 0
        
        # 从检测到的位置开始提取字幕
        final_subtitles = subtitle_texts[real_subtitle_start:]
        
        # 最后清理：移除明显的网页元素
        cleaned_subtitles = []
        for text in final_subtitles:
            # 跳过明显的网页导航和无关内容
            if not any(pattern in text.lower() for pattern in [
                'transcript & subtitles', 'youtube transcript', 'bilibili subtitles',
                'video downloader', 'text to speech', 'ai-powered video',
                'copyright', 'privacy policy', 'terms & conditions',
                'chrome web store', 'edge add-ons', 'thumbnail downloader'
            ]):
                cleaned_subtitles.append(text)
        
        logger.info(f"最终提取到 {len(cleaned_subtitles)} 段纯净字幕内容")
        return cleaned_subtitles
    
    def save_subtitles(self, result: Dict, output_file: str = None) -> str:
        """保存字幕到文件"""
        if not result['success']:
            logger.error("无法保存字幕：提取失败")
            return None
            
        if not output_file:
            video_id = result.get('video_id', 'unknown')
            output_file = f"subtitles_{video_id}_{int(time.time())}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("Bilibili视频字幕提取结果\n")
                f.write("="*60 + "\n")
                f.write(f"视频URL: {result['video_url']}\n")
                f.write(f"结果页面: {result['result_url']}\n")
                f.write(f"视频ID: {result['video_id']}\n")
                f.write(f"提取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"字幕段数: {result['subtitle_count']}\n")
                f.write("="*60 + "\n\n")
                
                for i, subtitle in enumerate(result['subtitles'], 1):
                    f.write(f"[{i:03d}] {subtitle}\n\n")
            
            logger.info(f"✅ 字幕已保存到: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"保存字幕文件失败: {str(e)}")
            return None
    

    
    def process_video(self, video_url: str) -> Dict:
        """处理视频：提取字幕"""
        logger.info(f"开始处理视频: {video_url}")
        
        # 检测平台
        platform = self.detect_video_platform(video_url)
        logger.info(f"检测到视频平台: {platform}")
        
        if platform != 'bilibili':
            logger.warning(f"当前只支持Bilibili平台，检测到的平台: {platform}")
            # 可以扩展支持其他平台
        
        # 提取字幕
        result = self.extract_bilibili_subtitles(video_url)
        
        if result['success']:
            # 保存字幕
            subtitle_file = self.save_subtitles(result)
            result['subtitle_file'] = subtitle_file
            
            # 显示结果
            self._display_results(result)
        
        return result
    
    def _display_results(self, result: Dict):
        """显示提取结果"""
        print("\n" + "="*80)
        print("🎉 视频字幕提取完成！")
        print("="*80)
        print(f"📹 视频URL: {result['video_url']}")
        print(f"🆔 视频ID: {result['video_id']}")
        print(f"📝 字幕段数: {result['subtitle_count']}")
        print(f"💾 保存文件: {result.get('subtitle_file', '未保存')}")
        
        if result['subtitles']:
            print(f"\n📋 字幕内容预览（前5段）:")
            print("-" * 80)
            for i, text in enumerate(result['subtitles'][:5], 1):
                print(f"{i:2d}. {text[:150]}{'...' if len(text) > 150 else ''}")
                print()
            
            if len(result['subtitles']) > 5:
                print(f"... 还有 {len(result['subtitles']) - 5} 段字幕内容")
        
        print("="*80)

def main():
    """主函数"""
    print("="*60)
    print("🎬 Bilibili视频字幕提取器")
    print("="*60)
    
    # 获取用户输入
    video_url = input("\n📹 请输入Bilibili视频URL (回车使用默认测试视频): ").strip()
    if not video_url:
        video_url = "https://www.bilibili.com/video/BV1DsnzzwEUF/"
        print(f"使用默认测试视频: {video_url}")
    
    # 初始化提取器
    extractor = BilibiliSubtitleExtractor()
    
    # 处理视频
    print(f"\n🚀 开始处理视频...")
    result = extractor.process_video(video_url)
    
    if result['success']:
        print(f"\n✅ 字幕提取成功！共提取到 {result['subtitle_count']} 段字幕")
        print(f"📁 字幕文件已保存到: {result.get('subtitle_file')}")
    else:
        print(f"\n❌ 字幕提取失败: {result.get('error', '未知错误')}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()