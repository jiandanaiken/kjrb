#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科技新闻日报聚合系统 - 使用多个免费信息源
收集全球科技新闻，按重要度排序，生成日报
支持中英文混合新闻源 + 自动翻译
"""

import os
import json
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple
from collections import defaultdict
import time
from dotenv import load_dotenv

load_dotenv()

class TranslationHelper:
    """翻译辅助类 - 使用 Google Translate API"""
    
    def __init__(self):
        self.cache = {}
        self.translator_available = False
        try:
            from google.cloud import translate_v2
            self.translator = translate_v2.Client()
            self.translator_available = True
            print("✅ Google Translate API 已就绪")
        except:
            try:
                import translators
                self.trans = translators
                self.translator_available = True
                print("✅ 在线翻译服务已就绪")
            except:
                print("⚠️ 翻译服务不可用，将使用简单翻译")
                self.translator_available = False
    
    def detect_language(self, text: str) -> str:
        """检测文本语言"""
        if not text:
            return 'unknown'
        
        # 简单的中文检测
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        
        if chinese_count / len(text) > 0.3:  # 超过30%是中文字符
            return 'zh'
        else:
            return 'en'
    
    def translate(self, text: str, target_lang: str = 'zh') -> str:
        """翻译文本"""
        if not text:
            return text
        
        # 检查缓存
        cache_key = f"{text[:50]}_{target_lang}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # 尝试使用在线翻译服务
            translated = self._translate_online(text, target_lang)
            self.cache[cache_key] = translated
            return translated
        except:
            # 降级方案：返回原文
            return text
    
    def _translate_online(self, text: str, target_lang: str) -> str:
        """使用在线翻译服务"""
        try:
            # 使用免费的翻译API
            from translators import google
            result = google(text, from_language='en', to_language='zh')
            return result if result else text
        except:
            try:
                # 备用方案：使用更简单的 API
                url = "https://api.mymemory.translated.net/get"
                params = {
                    'q': text[:500],  # API 限制
                    'langpair': f'en|{target_lang}'
                }
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    result = response.json()
                    if result['responseStatus'] == 200:
                        return result['responseData']['translatedText']
            except:
                pass
            
            return text


class NewsAggregator:
    """新闻聚合器 - 支持多个信息源"""
    
    # RSS 源配置（最稳定的科技新闻源）
    RSS_FEEDS = {
        '国际学术/科学': [
            ('Nature', 'https://www.nature.com/nature.rss'),
            ('Science Magazine', 'https://www.science.org/action/showFeed?type=etoc&feed=rss'),
            ('ArXiv - AI/ML', 'https://arxiv.org/list/cs.AI/rss'),
            ('ArXiv - Physics', 'https://arxiv.org/list/physics.gen-ph/rss'),
            ('Phys.org', 'https://phys.org/rss-feed/'),
            ('ScienceDaily', 'https://www.sciencedaily.com/rss/all.xml'),
        ],
        '国际工程/技术': [
            ('IEEE Spectrum', 'https://spectrum.ieee.org/feed/rss'),
            ('MIT News', 'https://news.mit.edu/rss/feed.xml'),
            ('Stanford News', 'https://news.stanford.edu/news_type/research/feed/'),
        ],
        '国际科技媒体': [
            ('TechCrunch', 'https://techcrunch.com/feed/'),
            ('The Verge', 'https://www.theverge.com/rss/index.xml'),
            ('Hacker News', 'https://news.ycombinator.com/rss'),
        ],
        '国际综合新闻': [
            ('BBC Science', 'http://feeds.bbc.co.uk/news/science_and_environment/rss.xml'),
            ('Reuters Technology', 'https://www.reutersagency.com/feed/?taxonomy=best-topics&clientId=51&redirectTo=https%3A%2F%2Fwww.reuters.com'),
        ],
        '中文科技媒体': [
            ('36氪', 'https://www.36kr.com/feed'),
            ('机器之心', 'https://www.jiqizhixin.com/rss'),
            ('InfoQ', 'https://www.infoq.cn/feed'),
        ],
        '中文科学资讯': [
            ('科学网新闻', 'http://news.sciencenet.cn/rss.xml'),
            ('果壳网', 'https://www.guokr.com/rss/'),
            ('新浪科技', 'https://feed.sina.com.cn/tech/rss/techweb_pure.xml'),
        ]
    }
    
    def __init__(self):
        self.articles = []
        self.seen_titles: Set[str] = set()
        self.translator = TranslationHelper()
        
        # 新闻分类映射（支持中英文）
        self.categories = {
            'AI': ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 
                   'GPT', 'ChatGPT', 'LLM', 'transformer', 'neural', 'algorithm', 'ai', '人工智能', 
                   '机器学习', '深度学习', '神经网络', 'ChatGPT', 'GPT'],
            '机器人': ['robot', 'robotics', 'autonomous', 'drone', 'automation', '机器人', '自动化', '无人机'],
            '基础科学': ['physics', 'chemistry', 'biology', 'quantum', '量子', '科学', 'science',
                       'breakthrough', 'discovery', '突破', '发现', '科研'],
            '物理': ['particle', 'relativity', 'cosmology', 'astrophysics', 'dark matter', 'quantum',
                    'photon', 'electron', 'physics', '���理', '粒子', '宇宙', '黑洞'],
            '生物': ['biology', 'genetics', 'protein', 'cell', 'DNA', 'RNA', 'gene', 'biological',
                    '生物', '遗传', '基因', '蛋白质', '细胞'],
            '化学': ['chemistry', 'chemical', 'molecule', 'compound', 'material', '化学', '分子', '材料'],
            '医疗': ['medical', 'healthcare', 'drug', 'vaccine', 'disease', 'cancer', 'health',
                    'therapy', 'treatment', 'medicine', '医学', '医疗', '疫苗', '癌症', '药物'],
            '航空航天': ['space', 'aerospace', 'satellite', 'NASA', 'SpaceX', 'astronaut', '火箭',
                       'spacecraft', 'orbit', 'mission', '航天', '航空', '卫星', '太空'],
            '心理学': ['psychology', 'mental health', 'neuroscience', 'brain', 'cognitive',
                     '心理', '神经', '大脑', '认知'],
            '社会学': ['social', 'sociology', 'human behavior', 'society', '社会', '人文'],
            '信息工程': ['computer', 'software', 'technology', 'cybersecurity', 'data', 
                       'internet', 'cloud', 'network', '计算机', '软件', '安全', '互联网', '云计算'],
        }
    
    def fetch_rss_feeds(self) -> List[Dict]:
        """从 RSS 源获取新闻"""
        articles = []
        total_feeds = sum(len(feeds) for feeds in self.RSS_FEEDS.values())
        processed = 0
        
        for category, feeds in self.RSS_FEEDS.items():
            print(f"\n📚 {category}:")
            
            for feed_name, feed_url in feeds:
                processed += 1
                try:
                    print(f"  ⏳ [{processed}/{total_feeds}] 读取 {feed_name}...", end=' ', flush=True)
                    
                    # 解析 RSS 源
                    feed = feedparser.parse(feed_url)
                    
                    if feed.bozo:
                        print(f"⚠️ 解析警告")
                        continue
                    
                    entries_count = 0
                    for entry in feed.entries[:10]:  # 每个源取前10条
                        try:
                            title = entry.get('title', '').strip()
                            
                            # 去重
                            if not title or title in self.seen_titles:
                                continue
                            
                            self.seen_titles.add(title)
                            
                            # 提取信息
                            link = entry.get('link', '')
                            summary = entry.get('summary', '')
                            
                            # 清理 HTML 标签
                            if '<' in summary:
                                import re
                                summary = re.sub('<[^<]+?>', '', summary)
                            
                            summary = summary[:300].strip()
                            
                            # 获取发布时间
                            pub_date = entry.get('published', '')
                            
                            # 检测原始语言
                            original_lang = self.translator.detect_language(title)
                            
                            article = {
                                'title': title,
                                'url': link,
                                'description': summary,
                                'source': {'name': feed_name},
                                'published_at': pub_date,
                                'category': '',
                                'importance': 0,
                                'original_lang': original_lang,
                                'translated_title': title,
                                'translated_description': summary,
                            }
                            
                            articles.append(article)
                            entries_count += 1
                        except Exception as e:
                            continue
                    
                    if entries_count > 0:
                        print(f"✓ {entries_count} 条")
                    else:
                        print(f"✗ 无有效条目")
                    
                    # 控制请求频率
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"✗ 错误: {str(e)[:50]}")
                    continue
        
        return articles
    
    def fetch_reddit_science(self) -> List[Dict]:
        """从 Reddit r/science 获取热门科技新闻"""
        articles = []
        
        try:
            print("\n🔗 Reddit r/science:")
            print("  ⏳ 读取热门话题...", end=' ', flush=True)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'
            }
            
            # 获取 Reddit 热门帖子
            url = 'https://www.reddit.com/r/science/hot.json?limit=30'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                entries_count = 0
                
                for post in data['data']['children'][:15]:
                    try:
                        post_data = post['data']
                        title = post_data.get('title', '').strip()
                        
                        if not title or title in self.seen_titles:
                            continue
                        
                        self.seen_titles.add(title)
                        
                        original_lang = self.translator.detect_language(title)
                        
                        article = {
                            'title': title,
                            'url': f"https://reddit.com{post_data.get('permalink', '')}",
                            'description': post_data.get('selftext', '')[:300],
                            'source': {'name': 'Reddit - r/science'},
                            'published_at': '',
                            'category': '',
                            'importance': 0,
                            'original_lang': original_lang,
                            'translated_title': title,
                            'translated_description': post_data.get('selftext', '')[:300],
                        }
                        
                        articles.append(article)
                        entries_count += 1
                    except:
                        continue
                
                print(f"✓ {entries_count} 条")
            else:
                print(f"✗ 失败 (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"✗ 错误: {str(e)[:50]}")
        
        return articles
    
    def translate_articles(self, articles: List[Dict]) -> List[Dict]:
        """翻译英文文章"""
        print("\n🌐 翻译英文新闻中...")
        translated_count = 0
        
        for article in articles:
            if article.get('original_lang') == 'en':
                try:
                    # 翻译标题
                    translated_title = self.translator.translate(article['title'], 'zh-CN')
                    if translated_title and translated_title != article['title']:
                        article['translated_title'] = translated_title
                        translated_count += 1
                    
                    # 翻译描述
                    if article.get('description'):
                        translated_desc = self.translator.translate(article['description'][:200], 'zh-CN')
                        if translated_desc:
                            article['translated_description'] = translated_desc
                except:
                    pass
        
        print(f"  ✓ 完成翻译 ({translated_count} 篇)")
        return articles
    
    def categorize_article(self, title: str, description: str = '') -> str:
        """根据标题和描述分类文章"""
        text = (title + ' ' + description).lower()
        
        # 按权重排序分类
        category_weights = defaultdict(int)
        
        for category, keywords in self.categories.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    category_weights[category] += 1
        
        if category_weights:
            return max(category_weights, key=category_weights.get)
        
        return '信息工程'  # 默认分类
    
    def calculate_importance(self, article: Dict) -> int:
        """计算新闻重要���评分 (1-100)"""
        score = 50  # 基础分
        
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        source_name = article.get('source', {}).get('name', '').lower()
        
        # 权威源加分
        authority_boost = {
            'nature': 20,
            'science': 18,
            'ieee': 15,
            'arxiv': 12,
            'mit': 12,
            'stanford': 10,
            'nasa': 12,
            'spacex': 10,
            '36氪': 10,
            '机器之心': 12,
            'infoq': 10,
            '科学网': 12,
            '果壳': 8,
        }
        
        for source, boost in authority_boost.items():
            if source in source_name:
                score += boost
                break
        
        # 关键词加分
        important_keywords = {
            'breakthrough': 15, '突破': 15,
            'discover': 12, '发现': 12,
            'first': 10, '首次': 10, '首个': 10,
            'new': 5, '新': 5, '最新': 8,
            'record': 8, '记录': 8,
            'revolutionary': 12, '革命': 12,
            'award': 10, '获奖': 10, '获得': 5,
            'nobel': 20, '诺贝尔': 20,
        }
        
        for keyword, points in important_keywords.items():
            if keyword in title:
                score += points
                break
        
        # 时间权重（最近的新闻加分）
        try:
            if article.get('published_at'):
                score += 5
        except:
            pass
        
        return min(score, 100)
    
    def fetch_and_aggregate(self) -> List[Dict]:
        """获取并聚合新闻"""
        print("\n" + "="*60)
        print("科技新闻日报系统 - 聚合中")
        print("="*60)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_articles = []
        
        # 从 RSS 源获取
        rss_articles = self.fetch_rss_feeds()
        all_articles.extend(rss_articles)
        
        # 从 Reddit 获取
        reddit_articles = self.fetch_reddit_science()
        all_articles.extend(reddit_articles)
        
        print(f"\n📊 总共获取: {len(all_articles)} 条新闻")
        
        # 翻译英文新闻
        all_articles = self.translate_articles(all_articles)
        
        # 为每条新闻计算分类和重要性
        for article in all_articles:
            article['category'] = self.categorize_article(
                article.get('title', ''),
                article.get('description', '')
            )
            article['importance'] = self.calculate_importance(article)
        
        # 按重要度排序并限制为20条
        all_articles.sort(key=lambda x: x['importance'], reverse=True)
        self.articles = all_articles[:20]
        
        print(f"✓ 选出重要度最高的 {len(self.articles)} 条新闻")
        
        return self.articles
    
    def generate_html_report(self) -> str:
        """生成 HTML 格式的报告"""
        today = datetime.now().strftime('%Y年%m月%d日')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', 'PingFang SC', sans-serif;
                    line-height: 1.6; 
                    color: #333;
                    background: #f5f5f5;
                }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
                .header p {{ opacity: 0.95; font-size: 16px; }}
                .news-item {{ 
                    background: white;
                    border-left: 5px solid #667eea;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    transition: box-shadow 0.3s;
                }}
                .news-item:hover {{ box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
                .news-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
                .category {{ 
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 500;
                }}
                .importance {{ 
                    color: #e74c3c;
                    font-weight: bold;
                    font-size: 14px;
                }}
                .title {{ 
                    font-size: 18px;
                    font-weight: 600;
                    margin: 12px 0;
                    color: #2c3e50;
                    line-height: 1.4;
                }}
                .title a {{ 
                    color: #667eea;
                    text-decoration: none;
                    word-break: break-word;
                }}
                .title a:hover {{ text-decoration: underline; }}
                .original-title {{
                    font-size: 13px;
                    color: #999;
                    margin-top: 6px;
                    padding-top: 6px;
                    border-top: 1px solid #eee;
                    font-style: italic;
                }}
                .summary {{ 
                    color: #555;
                    margin: 12px 0;
                    line-height: 1.6;
                    font-size: 14px;
                }}
                .meta {{ 
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-top: 12px;
                    padding-top: 12px;
                    border-top: 1px solid #eee;
                    font-size: 12px;
                    color: #7f8c8d;
                }}
                .source-name {{ font-weight: 600; }}
                .read-more {{ 
                    display: inline-block;
                    color: #667eea;
                    text-decoration: none;
                    font-weight: 500;
                }}
                .read-more:hover {{ text-decoration: underline; }}
                .index {{ 
                    display: inline-block;
                    background: #667eea;
                    color: white;
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    text-align: center;
                    line-height: 32px;
                    font-weight: bold;
                    margin-right: 12px;
                }}
                .footer {{ 
                    margin-top: 40px;
                    padding: 20px;
                    border-top: 2px solid #ddd;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                    background: white;
                    border-radius: 4px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌍 科技新闻日报</h1>
                    <p>{today} | 精选全球中英文科技资讯（自动翻译）</p>
                </div>
        """
        
        for idx, article in enumerate(self.articles, 1):
            category = article.get('category', '未分类')
            translated_title = article.get('translated_title', 'No Title')
            original_title = article.get('title', '')
            url = article.get('url', '#')
            source_name = article.get('source', {}).get('name', 'Unknown Source')
            translated_desc = article.get('translated_description', '')
            importance = article.get('importance', 50)
            original_lang = article.get('original_lang', 'unknown')
            
            # 清理描述
            if not translated_desc:
                translated_desc = '暂无摘要'
            elif len(translated_desc) > 250:
                translated_desc = translated_desc[:250] + '...'
            
            # 如果是英文翻译的，显示原标题
            original_title_html = ''
            if original_lang == 'en' and original_title != translated_title:
                original_title_html = f'<div class="original-title">📌 原文标题: {original_title}</div>'
            
            html += f"""
                <div class="news-item">
                    <div class="news-header">
                        <div>
                            <span class="index">{idx}</span>
                            <span class="category">{category}</span>
                        </div>
                        <div class="importance">重要度: {importance}/100</div>
                    </div>
                    <div class="title">
                        <a href="{url}" target="_blank" style="word-break: break-word;">{translated_title}</a>
                    </div>
                    {original_title_html}
                    <div class="summary">{translated_desc}</div>
                    <div class="meta">
                        <div>来源: <span class="source-name">{source_name}</span></div>
                        <a href="{url}" target="_blank" class="read-more">查看原文 →</a>
                    </div>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>✨ 此日报由 kjrb 科技新闻聚合系统自动生成</p>
                    <p style="margin-top: 8px; opacity: 0.7;">每日 9:00 自动发送 | 聚合全球权威媒体、学术机构及中文科技媒体新闻 | 英文新闻自动翻译成中文</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, html_content: str) -> str:
        """保存报告到文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir = 'reports'
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(report_dir, f'report_{timestamp}.html')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return report_path
    
    def send_email(self, html_content: str, recipient_email: str) -> bool:
        """发送邮件"""
        try:
            sender_email = os.getenv('SENDER_EMAIL', '')
            smtp_password = os.getenv('SMTP_PASSWORD', '')
            
            if not sender_email or not smtp_password:
                print("⚠️ 邮件环境变量未配置，跳过发送")
                print(f"   需要设置: SENDER_EMAIL, SMTP_PASSWORD")
                return False
            
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # 创建邮件
            message = MIMEMultipart('alternative')
            today = datetime.now().strftime('%Y年%m月%d日')
            message['Subject'] = f'📰 科技新闻日报 - {today}'
            message['From'] = sender_email
            message['To'] = recipient_email
            
            # 纯文本版本
            text_version = "请使用支持 HTML 的邮件客户端查看此邮件"
            part1 = MIMEText(text_version, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            message.attach(part1)
            message.attach(part2)
            
            # 发送邮件
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, smtp_password)
                server.send_message(message)
            
            print(f"✅ 邮件已成功发送到: {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ SMTP 认证失败 - 检查邮箱和应用专用密码")
            return False
        except Exception as e:
            print(f"❌ 发送邮件失败: {e}")
            return False
    
    def run(self):
        """运行聚合和发送流程"""
        print("\n")
        
        # 获取和聚合新闻
        articles = self.fetch_and_aggregate()
        
        if not articles:
            print("❌ 未获取到任何新闻，请检查网络连接或信息源")
            return
        
        # 生成报告
        html_report = self.generate_html_report()
        
        # 保存报告
        report_path = self.save_report(html_report)
        print(f"\n✅ 报告已保存: {report_path}")
        
        # 发送邮件
        target_email = os.getenv('TARGET_EMAIL', '70110@163.com')
        self.send_email(html_report, target_email)
        
        print("\n" + "="*60)
        print("✅ 完成！")
        print("="*60)


if __name__ == '__main__':
    aggregator = NewsAggregator()
    aggregator.run()
