import json
import arxiv
from tqdm import tqdm
from typing import TypedDict
from datetime import datetime, timedelta

client = arxiv.Client()

class Paper(TypedDict, total=False):
    entry_id: str
    title: str
    pdf_url: str
    comment: str
    updated_time: str 
    published_time: str

def fetch_new_papers(max_results: int = 50) -> dict[str, Paper]:
    result: dict[str, Paper] = {}
    
    # 使用ArXiv查询格式进行搜索
    search_query = '(all:"smart contract" OR all:"decentralized finance" OR "all:solidity language") AND (cat:cs.CR OR cat:cs.SE OR cat:cs.LG)'
    
    search = arxiv.Search(
        query=search_query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )

    print(f"正在搜索ArXiv论文，查询: {search_query}")
    print(f"最大结果数: {max_results}")
    
    for paper in tqdm(client.results(search), desc="获取论文"):
        # 验证分类是否符合要求
        if not any(category in ["cs.CR", "cs.SE", "cs.LG"] for category in paper.categories):
            continue
            
        data: Paper = {
            "entry_id": paper.entry_id,
            "pdf_url": paper.pdf_url,
            "title": paper.title,
            "comment": paper.comment,
            "updated_time": paper.updated.isoformat(),
            "published_time": paper.published.isoformat()
        }
        result[paper.entry_id] = data

    return result


def update_paper_lists(filename: str, new_papers: dict[str, Paper]) -> None:
    with open(filename, "r") as f:
        content = f.read()
        papers: dict[str, Paper] = json.loads(content).copy() if content else dict()

    for entry_id, paper in new_papers.items():
        papers[entry_id] = paper
    
    papers = dict(sorted(papers.items(), key=lambda item: item[1]['updated_time'], reverse=True))

    with open(filename, "w") as f:
        json.dump(papers, f, indent = 4)


def display_newest_papers(filename: str) -> None:
    with open(filename, "r") as f:
        papers: dict[str, Paper] = json.load(f)
    
    # 只展示前 20 篇最新的论文，并以输出至 README.md，以表格的形式展示在 GitHub 仓库的首页
    with open("README.md", "w") as f:
        f.write("# arXiv Papers for Smart Contract\n\n")
        f.write(f"Last Updated: {datetime.now().isoformat()}\n\n")
        f.write("## Newest Papers\n\n")
        f.write("|\#|Title|URL|Updated|\n")
        f.write("|---|---|---|---|\n")
        one_month_ago = datetime.now() - timedelta(days=30)
        for i, (entry_id, paper) in enumerate(papers.items()):
            if i >= 50:
                break
            updated_date = paper['updated_time'][:10]  # 只保留到日
            updated_datetime = datetime.fromisoformat(updated_date)
            if updated_datetime >= one_month_ago:
                updated_date = f"🆕 {updated_date}"
            
            f.write(f"|{i + 1}|{paper['title']}|[link]({paper['entry_id']})|{updated_date}|\n")


if __name__ == '__main__':
    print("开始获取ArXiv论文...")
    new_papers = fetch_new_papers(max_results=50)
    print(f"成功获取 {len(new_papers)} 篇论文")
    
    update_paper_lists(filename="papers.json", new_papers=new_papers)
    display_newest_papers("papers.json")
    print("论文列表已更新完成！")