from bilibili_comment_spider import BilibiliCommentSpider
import sys
import time
import random
import re

COOKIE = ""

def extract_bvid(input_str):
    """
    从输入字符串中提取BV号
    支持格式：
    - BV号: BV1ofR5B6E72
    - 完整URL: https://www.bilibili.com/video/BV1ofR5B6E72/?spm_id_from=...
    - 短链接: https://b23.tv/BV1ofR5B6E72
    """
    input_str = input_str.strip()
    
    # 如果输入已经是纯BV号，直接返回
    if re.match(r'^BV[a-zA-Z0-9]+$', input_str):
        return input_str
    
    # 从URL中提取BV号
    # 匹配模式：/video/BVxxxxxx 或 /BVxxxxxx
    patterns = [
        r'/video/(BV[a-zA-Z0-9]+)',
        r'/(BV[a-zA-Z0-9]+)',
        r'bilibili\.com/video/(BV[a-zA-Z0-9]+)',
        r'b23\.tv/(BV[a-zA-Z0-9]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, input_str)
        if match:
            bvid = match.group(1)
            print(f"[+] 从链接中提取BV号: {bvid}")
            return bvid
    
    # 如果都没匹配到，返回原始输入（可能是错误的BV号）
    return input_str

def crawl_comments(bvid, max_pages=10, sort=0, output_file=None, safe_mode=True):
    spider = BilibiliCommentSpider(cookie=COOKIE)
    
    if safe_mode:
        spider.min_interval = random.uniform(2.5, 4.0)
        spider.max_interval = random.uniform(5.0, 8.0)
        print(f"[安全模式] 请求间隔: {spider.min_interval:.1f}-{spider.max_interval:.1f}秒")
    
    if output_file is None:
        output_file = f"comments_{bvid}.csv"
    
    comments = spider.get_all_comments(
        bvid=bvid,
        max_pages=max_pages,
        sort=sort,
        output_file=output_file
    )
    
    return comments

def print_safety_tips():
    print("\n" + "="*60)
    print("[!] 安全提示")
    print("="*60)
    print("为降低被封号风险，已采取以下措施：")
    print("[+] 随机延迟时间 (2-8秒)")
    print("[+] 随机User-Agent轮换")
    print("[+] 请求频率限制")
    print("[+] 自动重试机制")
    print("[+] 错误码-412自动等待")
    print("\n建议：")
    print("* 每次爬取不超过50页")
    print("* 每天爬取不超过5个视频")
    print("* 避免短时间内频繁请求")
    print("* 使用小号进行测试")
    print("="*60 + "\n")

if __name__ == "__main__":
    print_safety_tips()
    
    if len(sys.argv) > 1:
        input_str = sys.argv[1]
        bvid = extract_bvid(input_str)
        max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        
        if max_pages > 50:
            print("[!] 警告：页数过多可能增加风险，建议不超过50页")
            confirm = input("是否继续？(y/n): ").strip().lower()
            if confirm != 'y':
                print("已取消")
                sys.exit(0)
        
        output_file = sys.argv[3] if len(sys.argv) > 3 else None
    else:
        print("=" * 60)
        print("B站评论爬取工具 (安全增强版)")
        print("=" * 60)
        print("\n支持输入格式：")
        print("1. BV号: BV1ofR5B6E72")
        print("2. 完整链接: https://www.bilibili.com/video/BV1ofR5B6E72/...")
        print("3. 短链接: https://b23.tv/BV1ofR5B6E72")
        print("-" * 60)
        
        input_str = input("\n请输入视频BV号或链接: ").strip()
        if not input_str:
            print("输入不能为空")
            sys.exit(1)
        
        bvid = extract_bvid(input_str)
        
        try:
            max_pages = int(input("爬取页数 (建议<=50, 默认10): ") or "10")
            if max_pages > 50:
                print("[!] 警告：页数过多可能增加风险")
        except:
            max_pages = 10
        
        print("\n排序方式:")
        print("0 - 按热度排序")
        print("1 - 按时间排序")
        sort_choice = input("选择排序 (默认0): ").strip()
        sort = int(sort_choice) if sort_choice in ['0', '1'] else 0
        
        output_file = input("输出文件名 (默认: comments_BV号.csv): ").strip()
        if not output_file:
            output_file = f"comments_{bvid}.csv"
        if not output_file.endswith(".csv"):
            output_file += ".csv"
    
    print(f"\n开始爬取视频 {bvid} 的评论...")
    print(f"预计耗时: {max_pages * 5}-{max_pages * 10} 秒")
    
    start_time = time.time()
    comments = crawl_comments(bvid, max_pages, sort if 'sort' in locals() else 0, output_file)
    elapsed_time = time.time() - start_time
    
    if comments:
        print(f"\n[+] 成功！共获取 {len(comments)} 条评论")
        print(f"[+] 耗时: {elapsed_time:.1f} 秒")
        print(f"[+] 已保存到: {output_file if 'output_file' in locals() else f'comments_{bvid}.csv'}")
        print(f"\n[*] 提示: 建议间隔30分钟后再爬取其他视频")
    else:
        print("\n[X] 未能获取评论，请检查BV号或网络连接")
