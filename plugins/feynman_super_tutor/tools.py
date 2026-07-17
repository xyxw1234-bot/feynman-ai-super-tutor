import html
import json
import os
import re
import time
import hashlib
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


def _assets_dir() -> Path:
    p = _vault() / "visual_assets"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _asset_index_path() -> Path:
    return _vault() / "visual_assets_index.jsonl"


def _load_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows


def _load_cards(learner_id="default"):
    return _load_jsonl(_cards_path(learner_id))


def _append_jsonl(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _slug(text: str) -> str:
    raw = (text or "asset").strip()
    safe = re.sub(r"[^a-zA-Z0-9_\-\u4e00-\u9fff]", "_", raw)[:40].strip("_") or "asset"
    digest = hashlib.sha1((raw + str(time.time())).encode("utf-8")).hexdigest()[:8]
    return f"{safe}_{digest}"


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def feynman_save_learning_card(args: dict, **kwargs) -> str:
    try:
        learner = (args.get("learner_id") or "default").strip() or "default"
        card = {
            "created_at": _now(),
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
        misconceptions, boundaries, next_q = [], [], []
        for c in recent:
            misconceptions += c.get("misconceptions") or []
            if c.get("current_boundary"):
                boundaries.append(c["current_boundary"])
            next_q += c.get("next_questions") or []
        return json.dumps({"success": True, "learner_id": learner, "total_cards": len(cards), "recent_topics": [c.get("topic") for c in recent], "recent_misconceptions": misconceptions[-8:], "current_boundaries": boundaries[-5:], "next_questions": next_q[-8:]}, ensure_ascii=False)
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
        plan = []
        for i in range(days):
            if i == 0:
                focus = [c.get("topic") for c in cards[-3:]]
            elif i % 2 == 1:
                focus = [c.get("topic") for c in cards if c.get("misconceptions")][-3:]
            else:
                focus = [c.get("topic") for c in cards[max(0, len(cards)-i-3):len(cards)-i] if c.get("topic")]
            plan.append({"day": i + 1, "focus_topics": [x for x in focus if x], "method": "先回讲2分钟，再做1个变式，再更新错因卡"})
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
        chunks, cur, count = [], [], 0
        for s in _sentences(text):
            cur.append(s)
            count += len(s)
            if count >= 500:
                chunks.append("".join(cur)); cur = []; count = 0
        if cur:
            chunks.append("".join(cur))
        topics = []
        for idx, ch in enumerate(chunks[:12], 1):
            first = re.split(r"[。！？；;，,]", ch)[0][:40]
            keywords = re.findall(r"[\u4e00-\u9fff]{2,8}", ch)
            freq = {}
            for k in keywords:
                if k in {"这个", "我们", "他们", "学生", "老师", "可以", "因为", "所以"}:
                    continue
                freq[k] = freq.get(k, 0) + 1
            top = sorted(freq, key=lambda item: freq[item], reverse=True)[:5]
            topics.append({"index": idx, "topic_hint": first or (top[0] if top else f"话题{idx}"), "keywords": top, "feynman_prompt": f"请你用自己的话讲：{first or title} 到底在解决什么问题？", "approx_chars": len(ch)})
        record = {"created_at": _now(), "title": title, "source": args.get("source", ""), "subject": args.get("subject", ""), "grade": args.get("grade", ""), "topics": topics}
        _append_jsonl(_material_path(), record)
        return json.dumps({"success": True, "title": title, "topic_count": len(topics), "topics": topics}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


_VISUAL_KEYWORDS = {
    "graph": ["函数", "图像", "斜率", "截距", "抛物线", "曲线", "坐标", "变化率", "参数"],
    "space": ["几何", "立体", "辅助线", "三视图", "旋转", "截面", "角度", "相似", "圆", "对称"],
    "force": ["力", "受力", "方向", "合力", "摩擦", "重力", "弹力", "杠杆", "压强"],
    "buoyancy": ["浮力", "排开", "液体密度", "阿基米德"],
    "circuit": ["电路", "电流", "电压", "串联", "并联", "开关", "灯泡"],
    "chemistry": ["化学", "粒子", "分子", "原子", "反应", "溶解", "过滤", "酸碱", "离子"],
    "process": ["实验", "操作", "步骤", "变量", "控制变量", "过程", "现象"],
}


def feynman_assess_visual_need(args: dict, **kwargs) -> str:
    try:
        text = " ".join(str(args.get(k, "")) for k in ["subject", "grade", "topic", "learner_message", "observed_gap"])
        text += " " + " ".join(args.get("last_attempts") or [])
        scores = {k: sum(1 for w in ws if w in text) for k, ws in _VISUAL_KEYWORDS.items()}
        total = sum(scores.values())
        attempts = len(args.get("last_attempts") or [])
        if total == 0 and attempts < 2:
            level, asset, ask = "none", "text_first", "先继续文字追问，不急着生成素材。"
        elif scores.get("graph") or scores.get("buoyancy") or scores.get("circuit") or scores.get("force") or attempts >= 2:
            level, asset, ask = "strong", "interactive_h5", "可自然说明：这个点靠操作更直观，我可以做一个小互动页，你拖一拖再回来讲。"
        elif scores.get("space") or scores.get("chemistry") or scores.get("process"):
            level, asset, ask = "medium", "step_diagram_or_h5", "可先问学生要图示还是互动页；若已多轮卡住，直接做一个聚焦素材。"
        else:
            level, asset, ask = "light", "diagram", "优先一张简图或步骤图，不必做复杂页面。"
        reasons = [f"{k}:{v}" for k, v in scores.items() if v]
        if attempts >= 2:
            reasons.append("多轮文字表达仍不稳")
        if args.get("observed_gap"):
            reasons.append("已有明确学习断点")
        return json.dumps({"success": True, "visual_need": level, "recommended_asset": asset, "scores": scores, "reasons": reasons, "teacher_move": ask, "rule": "视觉素材只是帮助学生重新讲清楚的脚手架，不替代费曼回讲。"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def feynman_generate_interactive_h5_brief(args: dict, **kwargs) -> str:
    try:
        topic = args.get("topic", "当前知识点")
        return json.dumps({"success": True, "asset_type": args.get("asset_type", "interactive_h5"), "title": f"{topic}｜费曼互动小实验", "learning_goal": args.get("learning_goal", "让学习者通过操作观察核心变量关系，并能用自己的话复述"), "learner_gap": args.get("learner_gap", "文字解释不足以形成稳定直观"), "design_rules": ["浅色背景，移动端优先，一屏看懂任务", "只围绕一个知识点，不做大而全页面", "必须有可操作控件、即时反馈、观察任务、回到聊天复述的问题", "不能出现内部路径、测试词、版权不明素材", "生成后先做静态检查、浏览器预览和移动端宽度检查，再发给学生"], "variables": args.get("key_variables") or [], "must_not_do": args.get("must_not_do") or ["不要替代学生思考", "不要把H5当最终答案", "不要未经测试直接发链接"], "return_to_feynman_prompt": f"看完后请回到聊天，用自己的话讲：{topic} 的关键关系是什么？"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def _page(title: str, goal: str, body: str, script: str, prompt_back: str) -> str:
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1"><title>{html.escape(title)}</title><style>
:root{{--bg:#f7fbff;--card:#fff;--ink:#17324d;--muted:#5d7186;--brand:#2f80ed;--ok:#12a87a;--warn:#ff9f1a}}*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;background:linear-gradient(180deg,#f7fbff,#eef7ff);color:var(--ink)}}main{{max-width:960px;margin:0 auto;padding:16px 12px 28px}}.hero,.stage,.panel{{background:var(--card);border:1px solid #dfefff;border-radius:20px;padding:16px;box-shadow:0 10px 28px rgba(47,128,237,.08)}}h1{{font-size:22px;margin:0 0 8px}}.goal,.small{{color:var(--muted);line-height:1.6}}.lab{{margin-top:14px;display:grid;grid-template-columns:minmax(0,1fr) 286px;gap:14px}}svg,canvas{{width:100%;max-height:430px;display:block;background:#fbfdff;border-radius:14px;border:1px solid #e6f1fb}}label{{display:block;font-weight:700;margin:10px 0 6px}}input[type=range]{{width:100%;accent-color:var(--brand)}}.value{{color:var(--brand);font-weight:800}}.task{{margin-top:14px;padding:14px;background:#fff8e7;border:1px solid #ffe0a3;border-radius:16px;line-height:1.65}}.feedback{{margin-top:10px;color:var(--ok);font-weight:800;min-height:24px}}button{{width:100%;border:0;background:var(--brand);color:white;border-radius:14px;padding:12px 14px;font-size:16px;font-weight:800;margin-top:12px}}@media(max-width:760px){{.lab{{grid-template-columns:1fr}}h1{{font-size:20px}}main{{padding:12px 10px 22px}}}}
</style></head><body><main data-feynman-h5="1" data-qa-required="viewport,interaction,feedback,prompt-back"><section class="hero"><h1>{html.escape(title)}</h1><p class="goal">{html.escape(goal)}</p></section><section class="lab">{body}</section><section class="task"><b>回到聊天前的小任务：</b>{html.escape(prompt_back)}</section></main><script>{script}</script></body></html>'''


def _linear():
    body = '<div class="stage"><canvas id="canvas" width="720" height="460" aria-label="一次函数图像互动区"></canvas><div class="feedback" id="fb"></div></div><div class="panel"><label>斜率 k：<span class="value" id="kv">1</span></label><input id="k" type="range" min="-4" max="4" step="0.5" value="1"><label>截距 b：<span class="value" id="bv">0</span></label><input id="b" type="range" min="-5" max="5" step="0.5" value="0"><button onclick="challenge()">给我一个观察任务</button><p class="small">拖动 k 和 b，观察直线倾斜程度、方向和与 y 轴交点。</p></div>'
    script = """const c=document.getElementById('canvas'),ctx=c.getContext('2d'),kEl=document.getElementById('k'),bEl=document.getElementById('b'),kv=document.getElementById('kv'),bv=document.getElementById('bv'),fb=document.getElementById('fb');function mx(x){return c.width/2+x*55}function my(y){return c.height/2-y*35}function draw(){let k=parseFloat(kEl.value),b=parseFloat(bEl.value);kv.textContent=k;bv.textContent=b;ctx.clearRect(0,0,c.width,c.height);ctx.lineWidth=1;ctx.strokeStyle='#d9e8f7';for(let x=-6;x<=6;x++){ctx.beginPath();ctx.moveTo(mx(x),0);ctx.lineTo(mx(x),c.height);ctx.stroke()}for(let y=-6;y<=6;y++){ctx.beginPath();ctx.moveTo(0,my(y));ctx.lineTo(c.width,my(y));ctx.stroke()}ctx.strokeStyle='#71879c';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,my(0));ctx.lineTo(c.width,my(0));ctx.stroke();ctx.beginPath();ctx.moveTo(mx(0),0);ctx.lineTo(mx(0),c.height);ctx.stroke();ctx.strokeStyle='#2f80ed';ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(mx(-6),my(k*(-6)+b));ctx.lineTo(mx(6),my(k*6+b));ctx.stroke();ctx.fillStyle='#12a87a';ctx.beginPath();ctx.arc(mx(0),my(b),7,0,Math.PI*2);ctx.fill();fb.textContent=`现在 y=${k}x+${b}。k 控制倾斜方向和陡峭程度，b 控制与 y 轴交点。`;}function challenge(){const arr=['把 k 调成负数：直线方向发生了什么？','只改变 b：直线是旋转还是平移？','把 k 变大：同样向右走 1 格，y 的变化更大还是更小？'];fb.textContent=arr[Math.floor(Math.random()*arr.length)];}kEl.oninput=bEl.oninput=draw;draw();"""
    return body, script


def _quadratic():
    body = '<div class="stage"><canvas id="canvas" width="720" height="460" aria-label="二次函数图像互动区"></canvas><div class="feedback" id="fb"></div></div><div class="panel"><label>开口 a：<span class="value" id="av">1</span></label><input id="a" type="range" min="-3" max="3" step="0.5" value="1"><label>左右平移 h：<span class="value" id="hv">0</span></label><input id="h" type="range" min="-4" max="4" step="0.5" value="0"><label>上下平移 k：<span class="value" id="kv">0</span></label><input id="k" type="range" min="-5" max="5" step="0.5" value="0"><button onclick="challenge()">给我一个观察任务</button><p class="small">观察 y=a(x-h)²+k 中 a、h、k 分别控制什么。</p></div>'
    script = """const c=document.getElementById('canvas'),ctx=c.getContext('2d'),aEl=document.getElementById('a'),hEl=document.getElementById('h'),kEl=document.getElementById('k'),av=document.getElementById('av'),hv=document.getElementById('hv'),kv=document.getElementById('kv'),fb=document.getElementById('fb');function mx(x){return c.width/2+x*55}function my(y){return c.height/2-y*35}function draw(){let a=parseFloat(aEl.value)||0.5,h=parseFloat(hEl.value),k=parseFloat(kEl.value);av.textContent=a;hv.textContent=h;kv.textContent=k;ctx.clearRect(0,0,c.width,c.height);ctx.strokeStyle='#d9e8f7';ctx.lineWidth=1;for(let x=-6;x<=6;x++){ctx.beginPath();ctx.moveTo(mx(x),0);ctx.lineTo(mx(x),c.height);ctx.stroke()}for(let y=-6;y<=6;y++){ctx.beginPath();ctx.moveTo(0,my(y));ctx.lineTo(c.width,my(y));ctx.stroke()}ctx.strokeStyle='#71879c';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,my(0));ctx.lineTo(c.width,my(0));ctx.stroke();ctx.beginPath();ctx.moveTo(mx(0),0);ctx.lineTo(mx(0),c.height);ctx.stroke();ctx.strokeStyle='#2f80ed';ctx.lineWidth=4;ctx.beginPath();for(let i=0;i<=240;i++){let x=-6+i*12/240,y=a*(x-h)*(x-h)+k;if(i===0)ctx.moveTo(mx(x),my(y));else ctx.lineTo(mx(x),my(y));}ctx.stroke();ctx.fillStyle='#12a87a';ctx.beginPath();ctx.arc(mx(h),my(k),8,0,Math.PI*2);ctx.fill();fb.textContent=`顶点在 (${h}, ${k})。a 的正负决定开口方向，绝对值影响开口宽窄。`;}function challenge(){const arr=['只调 h，顶点往哪边走？','把 a 调成负数，开口发生了什么？','只调 k，图像整体怎样移动？'];fb.textContent=arr[Math.floor(Math.random()*arr.length)];}aEl.oninput=hEl.oninput=kEl.oninput=draw;draw();"""
    return body, script


def _buoyancy():
    body = '<div class="stage"><svg id="svg" viewBox="0 0 720 460" role="img" aria-label="浮力互动示意图"></svg><div class="feedback" id="fb"></div></div><div class="panel"><label>液体密度 ρ：<span class="value" id="rv">1.0</span></label><input id="rho" type="range" min="0.5" max="2.0" step="0.1" value="1"><label>排开体积 V：<span class="value" id="vv">50</span></label><input id="vol" type="range" min="20" max="100" step="5" value="50"><button onclick="challenge()">给我一个观察任务</button><p class="small">浮力大小与液体密度、排开液体体积有关。箭头长度表示相对大小。</p></div>'
    script = """const svg=document.getElementById('svg'),rho=document.getElementById('rho'),vol=document.getElementById('vol'),rv=document.getElementById('rv'),vv=document.getElementById('vv'),fb=document.getElementById('fb');function draw(){let r=parseFloat(rho.value),v=parseFloat(vol.value),f=r*v;rv.textContent=r.toFixed(1);vv.textContent=v;let arrow=Math.min(190,40+f);svg.innerHTML=`<rect x="40" y="100" width="640" height="300" rx="22" fill="#dff4ff" stroke="#bfe5fa"/><path d="M40 160 Q180 135 320 160 T680 160" fill="none" stroke="#68b9e8" stroke-width="5"/><rect x="300" y="${260-v}" width="120" height="${v+80}" rx="16" fill="#ffcf75" stroke="#c98a24"/><line x1="360" y1="${260-v}" x2="360" y2="${260-v-arrow}" stroke="#12a87a" stroke-width="8"/><text x="385" y="${250-v-arrow}" font-size="26" fill="#0b8f68" font-weight="800">浮力 ↑</text><text x="54" y="435" font-size="22" fill="#17324d">F浮 ≈ ρ液 × g × V排　当前相对值：${f.toFixed(1)}</text>`;fb.textContent='观察：ρ 或 V 变大，浮力箭头会变长。';}function challenge(){const arr=['只调液体密度，排开体积不变，浮力怎么变？','只调排开体积，液体密度不变，浮力怎么变？','为什么同一个物体在盐水里可能更容易浮起来？'];fb.textContent=arr[Math.floor(Math.random()*arr.length)];}rho.oninput=vol.oninput=draw;draw();"""
    return body, script


def _force():
    body = '<div class="stage"><svg id="svg" viewBox="0 0 720 460" role="img" aria-label="受力分析互动区"></svg><div class="feedback" id="fb"></div></div><div class="panel"><label>水平拉力：<span class="value" id="pv">50</span></label><input id="pull" type="range" min="0" max="100" value="50"><label>摩擦力：<span class="value" id="fv">30</span></label><input id="fr" type="range" min="0" max="100" value="30"><button onclick="challenge()">给我一个观察任务</button><p class="small">比较左右方向的力，观察合力方向。这里只做简化模型。</p></div>'
    script = """const svg=document.getElementById('svg'),pull=document.getElementById('pull'),fr=document.getElementById('fr'),pv=document.getElementById('pv'),fv=document.getElementById('fv'),fb=document.getElementById('fb');function arr(x1,y1,x2,y2,c,label){return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${c}" stroke-width="8"/><text x="${x2+8}" y="${y2-8}" font-size="22" fill="${c}" font-weight="800">${label}</text>`}function draw(){let p=+pull.value,f=+fr.value;pv.textContent=p;fv.textContent=f;let net=p-f;svg.innerHTML=`<rect x="70" y="315" width="580" height="24" rx="12" fill="#d7e9f7"/><rect x="285" y="205" width="150" height="95" rx="18" fill="#ffd480" stroke="#c98a24"/>${arr(360,205,360,120,'#6f7f90','支持力')}${arr(360,300,360,390,'#6f7f90','重力')}${arr(435,252,435+p*2,252,'#2f80ed','拉力')}${arr(285,270,285-f*2,270,'#ff8a3d','摩擦')}${arr(360,180,360+net*2,180,net>=0?'#12a87a':'#d94b5f','合力')}`;fb.textContent=net>0?'合力向右，物体倾向向右加速。':net<0?'合力向左，物体倾向向左加速。':'左右平衡，水平方向合力为零。';}function challenge(){fb.textContent='请把拉力和摩擦力调成相等，观察合力箭头会怎样。'}pull.oninput=fr.oninput=draw;draw();"""
    return body, script


def _circuit():
    body = '<div class="stage"><svg id="svg" viewBox="0 0 720 460" role="img" aria-label="电路互动区"></svg><div class="feedback" id="fb"></div></div><div class="panel"><label>开关状态：<span class="value" id="sv">闭合</span></label><input id="sw" type="range" min="0" max="1" step="1" value="1"><label>电阻大小：<span class="value" id="rv">50</span></label><input id="res" type="range" min="20" max="100" value="50"><button onclick="challenge()">给我一个观察任务</button><p class="small">闭合回路才有持续电流；电阻越大，简化模型中灯越暗。</p></div>'
    script = """const svg=document.getElementById('svg'),sw=document.getElementById('sw'),res=document.getElementById('res'),sv=document.getElementById('sv'),rv=document.getElementById('rv'),fb=document.getElementById('fb');function draw(){let on=+sw.value===1,r=+res.value;sv.textContent=on?'闭合':'断开';rv.textContent=r;let bright=on?Math.max(.25,1-r/130):.08;svg.innerHTML=`<rect x="150" y="130" width="420" height="220" rx="32" fill="none" stroke="#2f80ed" stroke-width="8" stroke-dasharray="${on?'0':'22 18'}"/><rect x="120" y="210" width="70" height="60" rx="8" fill="#17324d"/><text x="128" y="250" font-size="24" fill="white">电源</text><circle cx="520" cy="240" r="58" fill="rgba(255,196,61,${bright})" stroke="#c98a24" stroke-width="6"/><text x="489" y="248" font-size="24" fill="#17324d">灯泡</text><line x1="300" y1="130" x2="360" y2="${on?130:95}" stroke="#ff8a3d" stroke-width="8"/><text x="290" y="82" font-size="24" fill="#17324d">开关</text>`;fb.textContent=on?`回路闭合，有电流。电阻越大，灯越暗。`:'回路断开，灯不亮。先想一想：电流路径在哪里断了？';}function challenge(){fb.textContent='把开关断开再闭合，说明为什么不是“电到灯泡就亮”，而是要形成完整回路。'}sw.oninput=res.oninput=draw;draw();"""
    return body, script


def _chemistry():
    body = '<div class="stage"><svg id="svg" viewBox="0 0 720 460" role="img" aria-label="粒子变化互动区"></svg><div class="feedback" id="fb"></div></div><div class="panel"><label>反应进度：<span class="value" id="pv">0</span>%</label><input id="prog" type="range" min="0" max="100" value="0"><button onclick="challenge()">给我一个观察任务</button><p class="small">用粒子模型看“原子重新组合”。这是简化示意，不代表真实比例和空间结构。</p></div>'
    script = """const svg=document.getElementById('svg'),prog=document.getElementById('prog'),pv=document.getElementById('pv'),fb=document.getElementById('fb');function dot(x,y,c,t){return `<circle cx="${x}" cy="${y}" r="22" fill="${c}"/><text x="${x-7}" y="${y+7}" font-size="20" fill="white" font-weight="800">${t}</text>`}function draw(){let p=+prog.value;pv.textContent=p;let mix=p/100;let left=220-mix*70,right=500+mix*20;svg.innerHTML=`<text x="70" y="55" font-size="24" fill="#17324d">反应前：粒子接触</text><text x="430" y="55" font-size="24" fill="#17324d">反应后：重新组合</text>${dot(left,180,'#2f80ed','A')}${dot(left+55,180,'#2f80ed','A')}${dot(left,250,'#ff8a3d','B')}${dot(left+55,250,'#ff8a3d','B')}<path d="M330 220 L410 220" stroke="#12a87a" stroke-width="8"/><text x="344" y="200" font-size="22" fill="#12a87a">进度 ${p}%</text>${dot(right,180,'#2f80ed','A')}${dot(right+48,180,'#ff8a3d','B')}${dot(right,265,'#2f80ed','A')}${dot(right+48,265,'#ff8a3d','B')}`;fb.textContent='观察：化学反应中原子种类没有凭空消失，而是重新组合成新粒子。';}function challenge(){fb.textContent='请解释：为什么反应前后原子种类和个数要守恒？'}prog.oninput=draw;draw();"""
    return body, script


def _generic():
    body = '<div class="stage"><svg id="svg" viewBox="0 0 720 460" role="img" aria-label="互动学习示意图"></svg><div class="feedback" id="fb"></div></div><div class="panel"><label>变量 A：<span class="value" id="av">50</span></label><input id="a" type="range" min="0" max="100" value="50"><label>变量 B：<span class="value" id="bv">50</span></label><input id="b" type="range" min="0" max="100" value="50"><button onclick="challenge()">给我一个观察任务</button><p class="small">通用脚手架：正式发送前应按具体知识点改写变量、反馈与图示。</p></div>'
    script = """const svg=document.getElementById('svg'),a=document.getElementById('a'),b=document.getElementById('b'),av=document.getElementById('av'),bv=document.getElementById('bv'),fb=document.getElementById('fb');function draw(){let x=+a.value,y=+b.value;av.textContent=x;bv.textContent=y;svg.innerHTML=`<rect x="60" y="80" width="600" height="300" rx="26" fill="#eef8ff" stroke="#cfe8ff"/><circle cx="${120+x*5}" cy="240" r="42" fill="#2f80ed" opacity=".85"/><rect x="300" y="${340-y*2}" width="120" height="${y*2}" rx="16" fill="#12a87a" opacity=".85"/><text x="70" y="430" font-size="24" fill="#17324d">拖动变量，观察图形变化，再用自己的话解释规律。</text>`;fb.textContent='已经更新图示。请观察哪个量改变了，结果怎样变。';}function challenge(){fb.textContent='请只改变一个变量，观察结果是否变化，并回到聊天里解释原因。'}a.oninput=b.oninput=draw;draw();"""
    return body, script


def feynman_create_interactive_h5(args: dict, **kwargs) -> str:
    try:
        title = args.get("title") or f"{args.get('topic', '知识点')}｜费曼互动小实验"
        topic = args.get("topic") or title
        subject = args.get("subject", "")
        grade = args.get("grade", "")
        goal = args.get("learning_goal") or "通过操作观察规律，再回到聊天用自己的话讲清楚。"
        it = args.get("interaction_type") or "generic_slider"
        prompt = args.get("prompt_back") or f"请回到聊天，用自己的话讲：{topic} 的关键规律是什么？"
        body, script = {
            "linear_function": _linear,
            "function_graph": _linear,
            "quadratic_function": _quadratic,
            "buoyancy": _buoyancy,
            "force_diagram": _force,
            "circuit": _circuit,
            "chemistry_particles": _chemistry,
        }.get(it, _generic)()
        page = _page(title, goal, body, script, prompt)
        asset_id = _slug(topic)
        d = _assets_dir() / asset_id
        d.mkdir(parents=True, exist_ok=True)
        html_path = d / "index.html"
        html_path.write_text(page, encoding="utf-8")
        meta = {"created_at": _now(), "asset_id": asset_id, "title": title, "subject": subject, "grade": grade, "topic": topic, "interaction_type": it, "file_path": str(html_path), "prompt_back": prompt, "status": "local_generated_needs_preview_and_public_deploy"}
        (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        _append_jsonl(_asset_index_path(), meta)
        return json.dumps({"success": True, "asset_id": asset_id, "file_path": str(html_path), "meta_path": str(d / "meta.json"), "next_required_steps": ["run feynman_check_visual_asset", "open the HTML in a real browser", "test phone width and all controls", "deploy to a stable public URL before sending", "ask the learner to return and explain observations"]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def feynman_check_visual_asset(args: dict, **kwargs) -> str:
    try:
        p = Path(args.get("file_path") or "")
        if not p.exists():
            return json.dumps({"success": False, "passed": False, "errors": ["file_not_found"]}, ensure_ascii=False)
        text = p.read_text(encoding="utf-8", errors="ignore")
        errors, warnings = [], []
        checks = {
            "has_viewport": "viewport" in text,
            "has_feynman_marker": "data-feynman-h5" in text,
            "has_interaction": (("input" in text and "range" in text) or "button" in text or "canvas" in text or "svg" in text),
            "has_feedback": "feedback" in text or "观察" in text,
            "has_prompt_back": "回到聊天" in text or "用自己的话" in text,
            "light_background": "#f7fbff" in text or "#ffffff" in text or "#fff" in text,
            "mobile_css": "@media" in text,
        }
        for k, v in checks.items():
            if not v:
                errors.append(k)
        banned = ["TO" + "DO", "仅供" + "测试", "127.0.0.1", "api" + "_key", "sec" + "ret", "trace" + "back"]
        for b in banned:
            if b in text:
                errors.append(f"banned_text:{b}")
        if len(text) < 3500:
            warnings.append("html_may_be_too_short_for_rich_interaction")
        for e in args.get("expected_interactions") or []:
            if e and e not in text:
                warnings.append(f"expected_interaction_not_found:{e}")
        return json.dumps({"success": True, "passed": not errors, "checks": checks, "errors": errors, "warnings": warnings, "required_next": ["browser_preview", "mobile_width_preview", "subject_accuracy_review", "public_url_200_check"], "note": "Static check only. Public delivery requires browser/mobile preview and subject accuracy review."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "passed": False, "error": str(e)}, ensure_ascii=False)


def feynman_list_visual_assets(args: dict, **kwargs) -> str:
    try:
        learner = (args.get("learner_id") or "").strip()
        subject = (args.get("subject") or "").strip()
        topic = (args.get("topic") or "").strip()
        limit = max(1, min(100, int(args.get("limit") or 20)))
        rows = _load_jsonl(_asset_index_path())
        if learner:
            rows = [r for r in rows if r.get("learner_id") == learner]
        if subject:
            rows = [r for r in rows if subject in r.get("subject", "")]
        if topic:
            rows = [r for r in rows if topic in r.get("topic", "")]
        return json.dumps({"success": True, "count": len(rows), "assets": rows[-limit:]}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
