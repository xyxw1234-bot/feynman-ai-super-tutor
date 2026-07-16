#!/usr/bin/env python3
"""Lightweight standalone material-to-topic-map helper.
Reads UTF-8 text from a file and prints a Feynman topic map JSON.
"""
import argparse, json, re
from pathlib import Path


def topic_map(text, title="material"):
    parts=[p.strip() for p in re.split(r"(?<=[。！？!?；;\n])", text) if len(p.strip())>=8]
    chunks=[]; cur=[]; n=0
    for p in parts:
        cur.append(p); n+=len(p)
        if n>=500:
            chunks.append("".join(cur)); cur=[]; n=0
    if cur: chunks.append("".join(cur))
    topics=[]
    for i,ch in enumerate(chunks[:20],1):
        first=re.split(r"[。！？；;，,]", ch)[0][:60]
        kws=re.findall(r"[\u4e00-\u9fff]{2,8}", ch)
        freq={}
        for k in kws: freq[k]=freq.get(k,0)+1
        topics.append({"index":i,"topic_hint":first or f"话题{i}","keywords":sorted(freq,key=freq.get,reverse=True)[:6],"prompt":f"请你用自己的话讲：{first or title} 是什么意思？"})
    return {"title":title,"topic_count":len(topics),"topics":topics}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--title', default='material')
    args=ap.parse_args()
    text=Path(args.file).read_text(encoding='utf-8')
    print(json.dumps(topic_map(text,args.title), ensure_ascii=False, indent=2))
if __name__=='__main__': main()
