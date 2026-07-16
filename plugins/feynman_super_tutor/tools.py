import json, os, re, time
from pathlib import Path


def _home() -> Path:
    return Path(os.environ.get("HERMES_HOME") or os.environ.get("HOME") or ".").expanduser()


def _vault() -> Path:
    p = _home() / "data" / "feynman_super_tutor"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _cards_path(learner_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]", "_", learner_id or "default")[:64]
    return _vault() / f"{safe}.learning_cards.jsonl"


def _material_path() -> Path:
    return _vault() / "materials.jsonl"


def _load_cards(learner_id="default"):
    p = _cards_path(learner_id)
    if not p.exists():
        return []
    rows=[]
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        try: rows.append(json.loads(line))
        except Exception: pass
    return rows


def _append_jsonl(path: Path, obj: dict):
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def feynman_save_learning_card(args: dict, **kwargs) -> str:
    try:
        learner = (args.get("learner_id") or "default").strip() or "default"
        card = {
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "learner_id": learner,
            "subject": args.get("subject", ""),
            "grade": args.get("grade", ""),
            "topic": args.get("topic", ""),
            "mastered": args.get("mastered") or [],
            "misconceptions": args.get("misconceptions") or [],
            "current_boundary": args.get("current_boundary", ""),
            "next_questions": args.get("next_questions") or [],
            "evidence": args.get("evidence") or [],
        }
        _append_jsonl(_cards_path(learner), card)
        return json.dumps({"success": True, "saved": True, "topic": card["topic"], "card_count": len(_load_cards(learner))}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def feynman_read_learning_profile(args: dict, **kwargs) -> str:
    try:
        learner = (args.get("learner_id") or "default").strip() or "default"
        subject = (args.get("subject") or "").strip()
        topic = (args.get("topic") or "").strip()
        limit = int(args.get("limit") or 10)
        cards = _load_cards(learner)
        if subject:
            cards = [c for c in cards if subject in c.get("subject", "")]
        if topic:
            cards = [c for c in cards if topic in c.get("topic", "")]
        recent = cards[-limit:]
        misconceptions=[]; boundaries=[]; next_q=[]
        for c in recent:
            misconceptions += c.get("misconceptions") or []
            if c.get("current_boundary"): boundaries.append(c["current_boundary"])
            next_q += c.get("next_questions") or []
        return json.dumps({
            "success": True,
            "learner_id": learner,
            "total_cards": len(cards),
            "recent_topics": [c.get("topic") for c in recent],
            "recent_misconceptions": misconceptions[-8:],
            "current_boundaries": boundaries[-5:],
            "next_questions": next_q[-8:]
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def feynman_generate_review_plan(args: dict, **kwargs) -> str:
    try:
        learner = (args.get("learner_id") or "default").strip() or "default"
        subject = (args.get("subject") or "").strip()
        days = max(1, min(30, int(args.get("days") or 7)))
        cards = _load_cards(learner)
        if subject:
            cards = [c for c in cards if subject in c.get("subject", "")]
        cards = cards[-20:]
        plan=[]
        for i in range(days):
            focus=[]
            # simple spaced cycle: new/recent on day 1, misconceptions every other day
            if i == 0:
                focus = [c.get("topic") for c in cards[-3:]]
            elif i % 2 == 1:
                focus = [c.get("topic") for c in cards if c.get("misconceptions")][-3:]
            else:
                focus = [c.get("topic") for c in cards[max(0, len(cards)-i-3):len(cards)-i] if c.get("topic")]
            plan.append({"day": i+1, "focus_topics": [x for x in focus if x], "method": "先回讲2分钟，再做1个变式，再更新错因卡"})
        return json.dumps({"success": True, "days": days, "plan": plan}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def _sentences(text: str):
    parts = re.split(r"(?<=[。！？!?；;\n])", text)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def feynman_ingest_material(args: dict, **kwargs) -> str:
    try:
        text = (args.get("text") or "").strip()
        title = (args.get("title") or "未命名材料").strip()
        if len(text) < 20:
            return json.dumps({"success": False, "error": "材料文本过短，无法生成话题地图"}, ensure_ascii=False)
        sents = _sentences(text)
        chunks=[]
        cur=[]; count=0
        for s in sents:
            cur.append(s); count += len(s)
            if count >= 500:
                chunks.append("".join(cur)); cur=[]; count=0
        if cur: chunks.append("".join(cur))
        topics=[]
        for idx,ch in enumerate(chunks[:12],1):
            # heuristic topic title from frequent Chinese noun-ish spans / first clause
            first = re.split(r"[。！？；;，,]", ch)[0][:40]
            keywords = re.findall(r"[\u4e00-\u9fff]{2,8}", ch)
            freq={}
            for k in keywords:
                if k in {"这个","我们","他们","学生","老师","可以","因为","所以"}: continue
                freq[k]=freq.get(k,0)+1
            top=sorted(freq, key=freq.get, reverse=True)[:5]
            topics.append({"index": idx, "topic_hint": first or (top[0] if top else f"话题{idx}"), "keywords": top, "feynman_prompt": f"请你用自己的话讲：{first or title} 到底在解决什么问题？", "approx_chars": len(ch)})
        record={"created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "title": title, "source": args.get("source",""), "subject": args.get("subject",""), "grade": args.get("grade",""), "topics": topics}
        _append_jsonl(_material_path(), record)
        return json.dumps({"success": True, "title": title, "topic_count": len(topics), "topics": topics}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
