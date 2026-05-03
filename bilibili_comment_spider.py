import requests
import json
import time
import csv
import random
from typing import List, Dict, Optional
from datetime import datetime


class BilibiliCommentSpider:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    ]

    def __init__(self, cookie: str = ""):
        self.headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Referer": "https://www.bilibili.com",
            "Origin": "https://www.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        if cookie:
            self.headers["Cookie"] = cookie
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.debug = False
        self.request_count = 0
        self.last_request_time = 0
        self.min_interval = 2
        self.max_interval = 5

    def _random_delay(self, min_seconds: float = 1.0, max_seconds: float = 3.0):
        delay = random.uniform(min_seconds, max_seconds)
        if self.debug:
            print(f"[反爬] 等待 {delay:.2f} 秒...")
        time.sleep(delay)

    def _check_rate_limit(self):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last + random.uniform(0.5, 1.5)
            if self.debug:
                print(f"[反爬] 请求过快，等待 {wait_time:.2f} 秒...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()

    def _rotate_user_agent(self):
        new_ua = random.choice(self.USER_AGENTS)
        self.session.headers["User-Agent"] = new_ua
        if self.debug:
            print(f"[反爬] 更换User-Agent")

    def _make_request(self, url: str, params: Dict = None, max_retries: int = 3) -> Optional[Dict]:
        for attempt in range(max_retries):
            try:
                self._check_rate_limit()
                
                if self.request_count > 0 and self.request_count % 10 == 0:
                    self._rotate_user_agent()
                
                response = self.session.get(url, params=params, timeout=15)
                response.raise_for_status()
                
                self.request_count += 1
                
                data = response.json()
                
                if data.get("code") == -412:
                    print(f"[!] 请求被拦截 (错误码 -412)，等待更长时间后重试...")
                    time.sleep(random.uniform(10, 20))
                    continue
                
                return data
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * random.uniform(3, 6)
                    print(f"[!] 请求失败 (尝试 {attempt + 1}/{max_retries})，等待 {wait_time:.1f} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"[X] 请求失败: {str(e)}")
                    return None
        
        return None

    def get_video_info(self, bvid: str) -> Optional[Dict]:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        data = self._make_request(url)
        
        if data and data["code"] == 0:
            return data["data"]
        elif data:
            print(f"获取视频信息失败: {data.get('message', '未知错误')}")
        
        return None

    def get_comments(
        self, oid: int, comment_type: int = 1, sort: int = 0, page: int = 1, page_size: int = 20
    ) -> Optional[Dict]:
        url = "https://api.bilibili.com/x/v2/reply"
        params = {
            "type": comment_type,
            "oid": oid,
            "sort": sort,
            "pn": page,
            "ps": page_size,
            "mode": 3,
        }

        data = self._make_request(url, params)
        
        if data:
            if self.debug:
                print(f"[DEBUG] API响应: code={data.get('code')}, message={data.get('message')}")
                print(f"[DEBUG] data键: {list(data.keys())}")
                if 'data' in data and isinstance(data['data'], dict):
                    print(f"[DEBUG] data.replies: {type(data['data'].get('replies'))}")
            
            if data["code"] == 0:
                return data["data"]
            else:
                print(f"获取评论失败: {data.get('message', '未知错误')} (错误码: {data.get('code')})")
        
        return None

    def parse_comment(self, comment_data: Dict) -> Dict:
        member = comment_data.get("member", {})
        content = comment_data.get("content", {})

        return {
            "评论ID": comment_data.get("rpid", ""),
            "用户名": member.get("uname", ""),
            "用户等级": member.get("level_info", {}).get("current_level", ""),
            "评论内容": content.get("message", ""),
            "点赞数": comment_data.get("like", 0),
            "回复数": comment_data.get("rcount", 0),
            "评论时间": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(comment_data.get("ctime", 0))
            ),
            "IP属地": comment_data.get("reply_control", {}).get("location", ""),
        }

    def get_all_comments(
        self,
        bvid: str,
        max_pages: int = 10,
        sort: int = 0,
        save_to_csv: bool = True,
        output_file: str = "bilibili_comments.csv",
    ) -> List[Dict]:
        print(f"正在获取视频信息...")
        video_info = self.get_video_info(bvid)
        if not video_info:
            print("无法获取视频信息，请检查BV号是否正确")
            return []

        aid = video_info["aid"]
        title = video_info["title"]
        print(f"视频标题: {title}")
        print(f"视频AV号: {aid}")
        print(f"播放量: {video_info['stat']['view']}")
        print(f"弹幕数: {video_info['stat']['danmaku']}")
        print("-" * 50)

        all_comments = []
        page = 1
        consecutive_failures = 0
        max_consecutive_failures = 3

        while page <= max_pages:
            print(f"正在获取第 {page} 页评论...")
            
            data = self.get_comments(aid, sort=sort, page=page)

            if not data:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    print(f"连续失败 {max_consecutive_failures} 次，停止爬取")
                    break
                
                wait_time = random.uniform(5, 10)
                print(f"等待 {wait_time:.1f} 秒后继续...")
                time.sleep(wait_time)
                continue
            
            consecutive_failures = 0
            replies = data.get("replies")
            
            if self.debug:
                print(f"[DEBUG] replies类型: {type(replies)}, 是否为None: {replies is None}")
                if replies:
                    print(f"[DEBUG] replies数量: {len(replies)}")
            
            if replies is None:
                if page == 1:
                    print("未获取到评论，可能原因：")
                    print("1. 视频没有评论")
                    print("2. 需要登录Cookie才能访问")
                    print("3. API访问限制")
                    print("\n建议：重新运行程序并选择使用Cookie")
                else:
                    print("已获取所有评论")
                break

            for reply in replies:
                comment_info = self.parse_comment(reply)
                comment_info["视频标题"] = title
                comment_info["BV号"] = bvid
                all_comments.append(comment_info)

            print(f"  [+] 成功获取 {len(replies)} 条评论 (总计: {len(all_comments)})")
            
            page += 1
            
            if page <= max_pages:
                self._random_delay(self.min_interval, self.max_interval)

        print(f"\n总共获取 {len(all_comments)} 条评论")

        if save_to_csv and all_comments:
            self.save_to_csv(all_comments, output_file)

        return all_comments

    def save_to_csv(self, comments: List[Dict], filename: str):
        if not comments:
            return

        fieldnames = [
            "视频标题",
            "BV号",
            "评论ID",
            "用户名",
            "用户等级",
            "评论内容",
            "点赞数",
            "回复数",
            "评论时间",
            "IP属地",
        ]

        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(comments)

        print(f"评论已保存到 {filename}")

    def get_replies(self, oid: int, root_id: int, page: int = 1) -> Optional[Dict]:
        url = "https://api.bilibili.com/x/v2/reply/reply"
        params = {"type": 1, "oid": oid, "root": root_id, "pn": page, "ps": 20}

        data = self._make_request(url, params)
        
        if data and data["code"] == 0:
            return data["data"]
        elif data:
            print(f"获取回复失败: {data.get('message', '未知错误')}")
        
        return None
