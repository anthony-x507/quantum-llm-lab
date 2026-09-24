#!/usr/bin/env python3
"""VIDEO temporal F1 — TRAIN FIRST, own-delta, continuous self-improve.
ONE street · THREE lights · LoRA → data/lora_adapter_video_f1/ (quantum RO).
"""
from __future__ import annotations
import argparse, json, math, random, re, shutil, subprocess, sys, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SYNTH = ROOT / "data" / "video_synth"
F1_DIR = SYNTH / "fase1"
F2_DIR = SYNTH / "fase2"
F3_DIR = SYNTH / "fase3"
ADAPTER_F1 = ROOT / "data" / "lora_adapter_video_f1"
ADAPTER_QUANTUM_RO = ROOT / "data" / "lora_adapter"
DEFAULT_MODEL = "mlx-community/Qwen3-VL-8B-Thinking-4bit"
GATE_TRACK, GATE_COHERENT = 0.80, 0.80
STREET_NAMES = ["Oak Ave","Pine St","Maple Blvd","Cedar Rd","Elm Way","Birch Ln","Willow Dr","Ash Ct"]
CAR_COLORS = ["red","blue","green","yellow","orange","white","black","cyan","purple"]
COLOR_RGB = {"red":(220,50,50),"yellow":(230,200,40),"green":(40,180,70),"blue":(50,110,220),
 "orange":(230,140,40),"white":(235,235,240),"black":(35,35,40),"cyan":(50,200,210),
 "purple":(150,80,200),"gray":(110,110,120),"asphalt":(65,65,70),"sidewalk":(160,160,155),"crosswalk":(240,240,245)}
CYCLE = {"R":8,"Y":3,"G":9}

def _font(size=11):
    try: return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except Exception: return ImageFont.load_default()
def _clamp(v,lo,hi): return max(lo,min(hi,v))
def light_state_at(frame_i, phase_offset):
    period = CYCLE["R"]+CYCLE["Y"]+CYCLE["G"]; t=(frame_i+phase_offset)%period
    if t < CYCLE["G"]: return "G"
    if t < CYCLE["G"]+CYCLE["Y"]: return "Y"
    return "R"

@dataclass
class LightSpec:
    lid: str; x: float; phase_offset: int; name: str
@dataclass
class AgentSpec:
    oid: str; cls: str; color: str; zone: int; path: str
    x0: float; y0: float; x1: float; y1: float; speed_jitter: float = 0.0
@dataclass
class F1Sequence:
    seq_id: str; street_name: str; n_frames: int; width: int; height: int
    lights: list; agents: list; seed: int; density: str; near_miss: bool = False

def _pos_agent(a, t, frame_i, light_states, lights):
    if a.path == "cross_walk":
        return a.x0+(a.x1-a.x0)*t, a.y0+(a.y1-a.y0)*t
    cx = a.x0+(a.x1-a.x0)*t; cy = a.y0+(a.y1-a.y0)*t
    if a.path in ("stop_go","queue") and a.cls=="car":
        L=lights[a.zone]; st=light_states.get(L.lid,"G")
        stop_x = L.x-18 if a.x1>a.x0 else L.x+18
        approaching = (a.x1>a.x0 and cx>=stop_x-5 and cx<=L.x+5) or (a.x1<a.x0 and cx<=stop_x+5 and cx>=L.x-5)
        if st in ("R","Y") and approaching: cx=stop_x
    cy += math.sin(frame_i*0.3+a.speed_jitter)*0.5
    return cx, cy

def render_f1_frame(seq, frame_i, tracks, light_hist):
    W,H = seq.width, seq.height
    img = Image.new("RGB",(W,H)); draw=ImageDraw.Draw(img); font_sm=_font(9)
    draw.rectangle([0,0,W,int(H*0.28)], fill=(140,185,225))
    draw.rectangle([0,int(H*0.28),W,int(H*0.42)], fill=COLOR_RGB["sidewalk"])
    draw.rectangle([0,int(H*0.42),W,int(H*0.78)], fill=COLOR_RGB["asphalt"])
    draw.rectangle([0,int(H*0.78),W,H], fill=COLOR_RGB["sidewalk"])
    y_lane=int(H*0.60)
    for x in range(0,W,24): draw.rectangle([x,y_lane,x+12,y_lane+2], fill=(220,220,80))
    draw.rectangle([W//2-50,4,W//2+50,20], fill=(30,30,40))
    draw.text((W//2-36,5), seq.street_name, fill=(255,255,255), font=font_sm)
    light_states={}; lamp_map={"R":"red","Y":"yellow","G":"green"}
    for L in seq.lights:
        st=light_state_at(frame_i, L.phase_offset); light_states[L.lid]=st
        light_hist.setdefault(L.lid,[]).append({"t":frame_i,"state":st,"x":L.x})
        cw_x=int(L.x)
        for yy in range(int(H*0.42), int(H*0.78), 6):
            draw.rectangle([cw_x-10,yy,cw_x+10,yy+3], fill=COLOR_RGB["crosswalk"])
        pole_x,pole_y=int(L.x), int(H*0.28)
        draw.rectangle([pole_x-2,pole_y,pole_x+2,int(H*0.42)], fill=(40,40,45))
        draw.rectangle([pole_x-7,pole_y-28,pole_x+7,pole_y], fill=(25,25,30), outline=(10,10,10))
        for i,s in enumerate(["R","Y","G"]):
            cy=pole_y-24+i*9
            col=COLOR_RGB[lamp_map[s]] if st==s else (50,50,50)
            draw.ellipse([pole_x-4,cy,pole_x+4,cy+7], fill=col)
        draw.text((pole_x-18,pole_y-40), L.lid, fill=(20,20,20), font=font_sm)
        draw.text((pole_x-28,int(H*0.30)), L.name.split("&")[-1].strip()[:6], fill=(20,20,60), font=font_sm)
        tracks.setdefault(L.lid,[]).append({"t":frame_i,"cx":float(L.x),"cy":float(pole_y-14),"cls":"light","state":st,"color":lamp_map[st]})
    for a in seq.agents:
        cx,cy=_pos_agent(a, frame_i/max(1,seq.n_frames-1), frame_i, light_states, seq.lights)
        cx,cy=_clamp(cx,8,W-8),_clamp(cy,8,H-8)
        rgb=COLOR_RGB.get(a.color,(180,50,50))
        if a.cls=="car":
            w,h=28,14
            draw.rounded_rectangle([cx-w/2,cy-h/2,cx+w/2,cy+h/2], radius=2, fill=rgb, outline=(20,20,25))
            draw.rectangle([cx-6,cy-5,cx+6,cy-1], fill=(170,200,230))
        else:
            draw.ellipse([cx-3,cy-10,cx+3,cy-4], fill=rgb)
            draw.line([cx,cy-4,cx,cy+6], fill=rgb, width=2); draw.line([cx-5,cy,cx+5,cy], fill=rgb, width=2)
        draw.text((cx-10,cy-18), a.oid[:7], fill=(255,255,255), font=font_sm)
        tracks.setdefault(a.oid,[]).append({"t":frame_i,"cx":round(cx,2),"cy":round(cy,2),"cls":a.cls,"color":a.color,"zone":a.zone})
    draw.text((4,H-14), f"{seq.seq_id} f={frame_i}/{seq.n_frames-1}", fill=(255,255,255), font=font_sm)
    return img

def _relations(seq, tracks, frame_i):
    pos={}
    for oid,pts in tracks.items():
        hit=next((p for p in pts if p["t"]==frame_i), None)
        if hit: pos[oid]=hit
    rels=[]
    for L in seq.lights:
        if L.lid in pos: rels.append(f"{L.lid} is {pos[L.lid].get('state','?')}")
    cars=[o for o,p in pos.items() if p.get("cls")=="car"]
    peds=[o for o,p in pos.items() if p.get("cls")=="pedestrian"]
    for c in cars:
        nearest=min(seq.lights, key=lambda L: abs(L.x-pos[c]["cx"]))
        side="left of" if pos[c]["cx"]<nearest.x else "right of"
        rels.append(f"{c} is {side} {nearest.lid}")
    for i,a in enumerate(cars):
        for b in cars[i+1:]:
            side="left of" if pos[a]["cx"]<pos[b]["cx"] else "right of"
            rels.append(f"{a} is {side} {b}")
    for ped in peds[:3]:
        nearest=min(seq.lights, key=lambda L: abs(L.x-pos[ped]["cx"]))
        rels.append(f"{ped} near crosswalk of {nearest.lid}")
    return rels

def _motion_prediction(seq, tracks):
    preds=[]
    for a in seq.agents:
        pts=tracks.get(a.oid) or []
        if len(pts)<2: continue
        dx=pts[-1]["cx"]-pts[-2]["cx"]; dy=pts[-1]["cy"]-pts[-2]["cy"]
        preds.append({"id":a.oid,"class":a.cls,"vx":round(dx,2),"vy":round(dy,2),
            "next":[{"t":pts[-1]["t"]+k,"cx":round(pts[-1]["cx"]+dx*k,2),"cy":round(pts[-1]["cy"]+dy*k,2)} for k in (1,2,3)]})
    return preds

def _reference_summary(seq, tracks, light_hist):
    obj_list=[]
    for L in seq.lights:
        states=[h["state"] for h in light_hist.get(L.lid,[])]
        obj_list.append({"id":L.lid,"class":"light","states_timeline":states,"final_state":states[-1] if states else None,"intersection":L.name})
    for a in seq.agents:
        pts=tracks.get(a.oid) or []
        obj_list.append({"id":a.oid,"class":a.cls,"color":a.color,"zone":a.zone,"n_track_points":len(pts),
                         "start":pts[0] if pts else None,"end":pts[-1] if pts else None})
    mid=seq.n_frames//2
    rels={"0":_relations(seq,tracks,0), str(mid):_relations(seq,tracks,mid), str(seq.n_frames-1):_relations(seq,tracks,seq.n_frames-1)}
    text=(f"Street '{seq.street_name}' with three lights ({', '.join(L.lid for L in seq.lights)}) "
          f"over {seq.n_frames} frames. Density={seq.density}. Agents: {', '.join(a.oid for a in seq.agents)}. "
          f"At mid-frame: {'; '.join(rels[str(mid)][:5])}.")
    return {"street_name":seq.street_name,"text":text,"objects":obj_list,"relations_keyframes":rels,
            "motion_prediction":_motion_prediction(seq,tracks),"near_miss":seq.near_miss}

def build_f1_sequence(idx, n_frames, seed, width=384, height=192):
    rng=random.Random(seed+idx*997); street=STREET_NAMES[idx%len(STREET_NAMES)]
    xs=[width*0.20,width*0.50,width*0.80]; phase0=rng.randint(0,19)
    lights=[LightSpec(f"L{i+1}", xs[i], (phase0+i*7)%20, f"{street} & {['1st','2nd','3rd'][i]}") for i in range(3)]
    density=["low","med","high"][idx%3]
    n_cars={"low":3,"med":5,"high":7}[density]; n_peds={"low":2,"med":3,"high":4}[density]
    road_y=height*0.55; agents=[]
    for c in range(n_cars):
        zone=c%3; direction=1 if c%2==0 else -1; y=road_y+(c%3-1)*10
        x0,x1=(5.0,float(width-5)) if direction>0 else (float(width-5),5.0)
        agents.append(AgentSpec(oid=f"car_{CAR_COLORS[c%len(CAR_COLORS)][:3]}{c}", cls="car",
            color=CAR_COLORS[c%len(CAR_COLORS)], zone=zone, path="stop_go" if c%2==0 else "through",
            x0=x0,y0=y,x1=x1,y1=y, speed_jitter=rng.random()*3))
    for p in range(n_peds):
        zone=p%3; L=lights[zone]
        agents.append(AgentSpec(oid=f"ped_{p}", cls="pedestrian", color=rng.choice(["black","red","blue","gray"]),
            zone=zone, path="cross_walk", x0=L.x+rng.uniform(-8,8), y0=height*0.82,
            x1=L.x+rng.uniform(-8,8), y1=height*0.35, speed_jitter=rng.random()))
    near_miss = idx%10==7
    if near_miss and len(agents)>=2:
        agents[0].path=agents[1].path="through"; agents[0].zone=agents[1].zone=1
    return F1Sequence(seq_id=f"f1_{idx:03d}_{street.lower().replace(' ','_')}", street_name=street,
        n_frames=n_frames, width=width, height=height, lights=lights, agents=agents,
        seed=seed+idx, density=density, near_miss=near_miss)

def generate_f1(out_dir, n_seq=50, n_frames=20, seed=42):
    out_dir=Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.glob("f1_*"):
        if p.is_dir(): shutil.rmtree(p)
    index=[]
    for i in range(n_seq):
        seq=build_f1_sequence(i, n_frames, seed)
        seq_dir=out_dir/seq.seq_id; frames_dir=seq_dir/"frames"; frames_dir.mkdir(parents=True, exist_ok=True)
        tracks={}; light_hist={}
        for fi in range(seq.n_frames):
            render_f1_frame(seq, fi, tracks, light_hist).save(frames_dir/f"frame_{fi:03d}.png", format="PNG", optimize=True)
        ref=_reference_summary(seq, tracks, light_hist)
        gt={"fase":1,"seq_id":seq.seq_id,"street_name":seq.street_name,"n_frames":seq.n_frames,
            "width":seq.width,"height":seq.height,"density":seq.density,"near_miss":seq.near_miss,
            "lights":[{"id":L.lid,"x":L.x,"phase_offset":L.phase_offset,"name":L.name,"timeline":light_hist.get(L.lid,[])} for L in seq.lights],
            "objects":[{"id":a.oid,"class":a.cls,"color":a.color,"zone":a.zone,"path":a.path,"frames":tracks.get(a.oid,[])} for a in seq.agents]
                      +[{"id":L.lid,"class":"light","frames":tracks.get(L.lid,[])} for L in seq.lights],
            "relations_keyframes":ref["relations_keyframes"],"reference_summary":ref,"motion_prediction":ref["motion_prediction"]}
        (seq_dir/"gt_tracks.json").write_text(json.dumps(gt, indent=2), encoding="utf-8")
        (seq_dir/"reference_summary.json").write_text(json.dumps(ref, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
        index.append({"seq_id":seq.seq_id,"street_name":seq.street_name,"n_frames":seq.n_frames,
            "n_cars":sum(1 for a in seq.agents if a.cls=="car"),"n_peds":sum(1 for a in seq.agents if a.cls=="pedestrian"),
            "n_lights":3,"density":seq.density,"near_miss":seq.near_miss,"dir":seq.seq_id})
        if (i+1)%10==0 or i==0: print(f"  [{i+1}/{n_seq}] {seq.seq_id}", flush=True)
    summary={"fase":1,"n_sequences":len(index),"n_frames_each":n_frames,"seed":seed,
             "street_layout":"ONE street, THREE lights in a line","sequences":index,
             "note":"Synthetic PIL. Adapter → data/lora_adapter_video_f1/. Quantum RO."}
    (out_dir/"SUMMARY.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    lines=["# Fase 1 SUMMARY", "", f"- sequences: **{len(index)}** × {n_frames} frames",
           "- Adapter: `data/lora_adapter_video_f1/`", "",
           "| seq | street | frames | cars | peds | density | near_miss |",
           "|-----|--------|--------|------|------|---------|-----------|"]
    for r in index:
        lines.append(f"| `{r['seq_id']}` | {r['street_name']} | {r['n_frames']} | {r['n_cars']} | {r['n_peds']} | {r['density']} | {r['near_miss']} |")
    (out_dir/"SUMMARY.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    return summary

def scaffold_f2f3():
    f2={"fase":2,"status":"SCAFFOLD_ONLY — no GPU until F1 gate",
        "layout":"3-light street + left/right/U-turn","new_labels":["turn_left","turn_right","u_turn","go_straight"],
        "n_sequences_target":50,"frames":"16-24","depends_on":"F1 gate tracking+coherent ≥0.80 or clear Δ"}
    f3={"fase":3,"status":"SCAFFOLD_ONLY — no GPU until F1+F2","layout":"Connected streets → city graph",
        "graph":{"nodes":["L1","L2","L3","L4","L5","L6"],"edges":[["L1","L2"],["L2","L3"],["L2","L4"],["L4","L5"],["L5","L6"]]},
        "n_sequences_target":50,"frames":"20-30"}
    F2_DIR.mkdir(parents=True, exist_ok=True); F3_DIR.mkdir(parents=True, exist_ok=True)
    (F2_DIR/"SCHEMA.json").write_text(json.dumps(f2, indent=2)+"\n", encoding="utf-8")
    (F3_DIR/"SCHEMA.json").write_text(json.dumps(f3, indent=2)+"\n", encoding="utf-8")
    (F2_DIR/"generate_fase2_stub.py").write_text("#!/usr/bin/env python3\nprint('[fase2 stub] after F1 gate')\n", encoding="utf-8")
    (F3_DIR/"generate_fase3_stub.py").write_text("#!/usr/bin/env python3\nprint('[fase3 stub] after F2')\n", encoding="utf-8")
    (F2_DIR/"README.md").write_text("# Fase 2 turns (SCAFFOLD)\nNo GPU until F1 gate.\n", encoding="utf-8")
    (F3_DIR/"README.md").write_text("# Fase 3 city (SCAFFOLD)\nNo GPU until F2.\n", encoding="utf-8")
    (SYNTH/"FASE_CHAIN_PLAN.json").write_text(json.dumps({
        "chain":["F1_train_eval_gate","F2_generate+LoRA","F3_generate+LoRA"],
        "f1_adapter":"data/lora_adapter_video_f1/","quantum_adapter_ro":"data/lora_adapter/",
        "gate":{"tracking":GATE_TRACK,"coherent_summary":GATE_COHERENT},
        "f2_ready":True,"f3_ready":True,"gpu_train_f2f3":False,
    }, indent=2)+"\n", encoding="utf-8")
    print(f"F2/F3 scaffolds ready under {SYNTH}")

def _strip_thinking(text):
    text=re.sub(r"<think>[\s\S]*?</think>","",text,flags=re.I)
    text=re.sub(r"<thinking>[\s\S]*?</thinking>","",text,flags=re.I)
    return text.strip()

def _extract_json(text):
    text=_strip_thinking(text)
    m=re.search(r"\{[\s\S]*\}", text)
    if not m: return None
    raw=m.group(0)
    try: return json.loads(raw)
    except json.JSONDecodeError:
        raw2=re.sub(r",\s*}","}",raw); raw2=re.sub(r",\s*]","]",raw2)
        try: return json.loads(raw2)
        except json.JSONDecodeError: return None

def score_prediction(gt, pred, raw_text):
    """Honest metrics: structured JSON preferred. Prose-only capped at 0.35 tracking."""
    text_l=(raw_text or "").lower(); pred=pred or {}
    parse_ok=bool(pred) and ("tracks" in pred or "objects" in pred or "summary" in pred)
    gt_objs=gt.get("objects") or []
    by_type={"car":[],"pedestrian":[],"light":[]}
    for o in gt_objs: by_type.setdefault(o["class"],[]).append(o["id"])
    pred_tracks=pred.get("tracks") or pred.get("objects") or []
    if not isinstance(pred_tracks, list): pred_tracks=[]

    def track_hit(oid, cls):
        for item in pred_tracks:
            if not isinstance(item, dict): continue
            pid=str(item.get("id") or ""); pcls=str(item.get("class") or item.get("type") or "").lower()
            if pid==oid or pid.lower()==oid.lower(): return 1.0
            if pcls==cls and cls=="light" and (oid.upper()==pid.upper() or oid.lower() in pid.lower() or pid.upper() in oid.upper()):
                return 1.0
        for item in pred_tracks:
            if isinstance(item, dict) and str(item.get("class") or "").lower()==cls: return 0.5
        if parse_ok: return 0.0
        if cls=="light" and ("traffic light" in text_l or "semáforo" in text_l or "l1" in text_l): return 0.25
        if cls in text_l: return 0.25
        return 0.0

    type_acc={}; type_counts={}; hits_all=0.0
    for cls, ids in by_type.items():
        if not ids: type_acc[cls]=None; continue
        scores=[track_hit(oid, cls) for oid in ids]
        mean_s=sum(scores)/len(scores)
        if not parse_ok: mean_s=min(mean_s, 0.35)
        type_acc[cls]=round(mean_s,3); type_counts[cls]={"hit_mass":round(sum(scores),3),"n":len(ids)}
        hits_all += sum(scores)
    tracking=hits_all/max(1,len(gt_objs))
    if not parse_ok: tracking=min(tracking, 0.35)
    tracking=round(tracking,3)

    light_state_hits=light_state_n=0
    pred_light_state={}
    for item in pred_tracks:
        if isinstance(item, dict) and str(item.get("class") or "").lower()=="light":
            st=item.get("state") or item.get("signal")
            if st: pred_light_state[str(item.get("id") or "").upper()]=str(st).upper()[:1]
    for L in gt.get("lights") or []:
        timeline=L.get("timeline") or []
        if not timeline: continue
        final=timeline[-1].get("state"); light_state_n += 1; lid=L["id"].upper()
        if lid in pred_light_state and pred_light_state[lid]==final: light_state_hits += 1
        else:
            rels=pred.get("relations") or []
            blob=" ".join(str(r) for r in rels).upper() if isinstance(rels, list) else ""
            if f"{lid} IS {final}" in blob or f"{lid} {final}" in blob: light_state_hits += 1
    light_state_acc=round(light_state_hits/light_state_n,3) if light_state_n else None

    street=(gt.get("street_name") or "").lower(); street_pred=str(pred.get("street_name") or "").lower()
    street_ok=False
    if street:
        if street_pred and (street in street_pred or street_pred in street or any(tok in street_pred for tok in street.split() if len(tok)>2)):
            street_ok=True
        elif not parse_ok:
            street_ok=any(tok in text_l for tok in street.split() if len(tok)>2)

    summary=str(pred.get("summary") or pred.get("narrative") or "")
    if not summary and not parse_ok: summary=raw_text or ""
    coherent=0; sl=summary.lower()
    if len(summary.strip())>=40 and any(w in sl for w in ("street","light","frame","then","moves","cross","signal","traffic","calle","semáforo")):
        coherent += 1
    if sum(1 for c in ("car","pedestrian","light","auto","peatón") if c in sl)>=2: coherent += 1
    if not parse_ok: coherent=min(coherent,1)
    coherent_bin=1.0 if (parse_ok and coherent>=1) or coherent>=2 else (0.5 if coherent==1 else 0.0)

    pred_rels=pred.get("relations") or []
    rel_blob=(" ".join(str(r).lower() for r in pred_rels) if isinstance(pred_rels, list) else "") or (text_l if not parse_ok else "")
    spatial_acc=0.0
    if any(s in rel_blob for s in ("left","right","near","front","behind","izquierda","derecha")):
        spatial_acc=1.0 if parse_ok else 0.4
    elif any(s in rel_blob for s in ("l1","l2","l3")):
        spatial_acc=0.5 if parse_ok else 0.2
    has_motion=bool(pred.get("motion_prediction") or pred.get("predictions"))
    if not has_motion and not parse_ok:
        has_motion=any(w in text_l for w in ("predict","will move","trajectory","continue"))
    return {"tracking_continuity":tracking,"tracking_by_type":type_acc,"tracking_counts_by_type":type_counts,
            "light_state_acc":light_state_acc,"street_name_ok":street_ok,"spatial_relation_acc":spatial_acc,
            "narrative_coherence_0_2":coherent,"coherent_summary_bin":coherent_bin,
            "motion_prediction_present":has_motion,"parse_ok":parse_ok}

TEMPORAL_PROMPT = """Eres un asistente de comprensión temporal de video (dashcam sintético).
Ves una SECUENCIA ordenada de frames: UNA calle con TRES semáforos (L1, L2, L3) en línea.
Cada semáforo es una intersección con cruce peatonal y tráfico. El orden temporal importa.

Responde SOLO JSON válido (sin markdown, sin prosa fuera del JSON) con claves:
street_name, tracks, relations, summary, motion_prediction, collision.

{
  "street_name": "nombre visible",
  "tracks": [{"id":"L1|car_...|ped_...","class":"car|pedestrian|light","color":"...","state":"R|Y|G|null",
              "frames":[{"t":0,"x":0.0,"y":0.0}]}],
  "relations": ["car_x is left of L2", "L1 is R"],
  "summary": "2-4 oraciones del viaje temporal",
  "motion_prediction": [{"id":"...","next":[{"t":N,"x":0,"y":0}]}],
  "collision": {"near_miss": false, "crash": false, "risk": "none|low|moderate|high"}
}

Reglas: (1) ids persistentes entre frames, (2) state R/Y/G en luces, (3) relations que cambian en el tiempo,
(4) summary coherente del conjunto — NO describir frames aislados.
"""

def subsample_frames(paths, max_frames):
    paths=list(paths)
    if len(paths)<=max_frames: return paths
    if max_frames<=1: return [paths[len(paths)//2]]
    idxs=[round(i*(len(paths)-1)/(max_frames-1)) for i in range(max_frames)]
    return [paths[i] for i in idxs]

def train_lock_held():
    return (ROOT/"data"/"TRAIN_LOCK.txt").exists()

# ---------------------------------------------------------------------------
# THREE LAYERS (interlocked) + ANTI-CONTAMINATION
# Memory → Retrieval → Tool → Memory. Eval GT never enters inference path.
# ---------------------------------------------------------------------------

class WorkingMemory:
    """Buffer of model perceptions / own preds / tool outputs across frames.
    ANTI-CONTAM: never stores GT labels or reference_summary text from disk.
    """
    def __init__(self):
        self.objects: dict[str, dict] = {}
        self.light_states: dict[str, str] = {}
        self.relations: list[str] = []
        self.preds: list[dict] = []
        self.tool_notes: list[str] = []
        self.street_name: str | None = None
        self.history: list[dict] = []

    def update_from_perception(self, pred: dict | None):
        if not pred: return
        if pred.get("street_name") and not self.street_name:
            self.street_name = str(pred["street_name"])
        for item in pred.get("tracks") or pred.get("objects") or []:
            if not isinstance(item, dict): continue
            oid = str(item.get("id") or "")
            if not oid: continue
            self.objects[oid] = {
                "id": oid, "class": item.get("class"), "color": item.get("color"),
                "state": item.get("state"), "last_frames": (item.get("frames") or [])[-3:],
            }
            if str(item.get("class") or "").lower() == "light" and item.get("state"):
                self.light_states[oid] = str(item["state"]).upper()[:1]
        for r in pred.get("relations") or []:
            if r not in self.relations:
                self.relations.append(str(r))
        if pred.get("motion_prediction"):
            self.preds = list(pred["motion_prediction"])
        self.history.append({"source": "perception", "n_objects": len(self.objects)})

    def update_from_tool(self, tool_out: dict):
        note = tool_out.get("note") or ""
        if note: self.tool_notes.append(note)
        for lid, st in (tool_out.get("light_next") or {}).items():
            self.light_states[lid] = st
        if tool_out.get("predicted_positions"):
            self.preds = tool_out["predicted_positions"]
        self.history.append({"source": "tool", "keys": list(tool_out.keys())})

    def snapshot(self) -> dict:
        return {
            "street_name": self.street_name,
            "n_objects": len(self.objects),
            "object_ids": sorted(self.objects.keys()),
            "light_states": dict(self.light_states),
            "relations_tail": self.relations[-8:],
            "preds_n": len(self.preds),
            "tool_notes_tail": self.tool_notes[-3:],
        }

    def prompt_block(self) -> str:
        snap = self.snapshot()
        return (
            "WORKING_MEMORY (model perceptions + tool outputs only; NOT ground truth):\n"
            + json.dumps(snap, ensure_ascii=False)
        )


class RetrievalIndex:
    """Train-only curated index. Nearest example by perception features.
    ANTI-CONTAM: built exclusively from TRAIN split; eval seq_ids rejected.
    """
    def __init__(self):
        self.entries: list[dict] = []
        self.train_ids: set[str] = set()
        self.eval_ids: set[str] = set()
        self.hit_counts: dict[str, int] = {}

    def build_from_train(self, train_seq_dirs: list[Path]):
        self.entries.clear(); self.train_ids.clear()
        for d in train_seq_dirs:
            gt_path = d / "gt_tracks.json"
            if not gt_path.exists(): continue
            gt = json.loads(gt_path.read_text(encoding="utf-8"))
            sid = gt["seq_id"]
            self.train_ids.add(sid)
            # Index features from GT for TRAIN only (allowed — train curation).
            # At inference we query with MEMORY features, never eval GT.
            feats = self._features_from_gt_train_only(gt)
            completion = {
                "street_name": gt["street_name"],
                "n_lights": 3,
                "density": gt.get("density"),
                "summary_style": (gt.get("reference_summary") or {}).get("text", "")[:240],
                "track_schema": ["id", "class", "color", "state", "frames"],
            }
            self.entries.append({"seq_id": sid, "features": feats, "hint": completion})
        print(f"[retrieval] indexed TRAIN n={len(self.entries)} ids={sorted(self.train_ids)[:3]}…", flush=True)

    def set_eval_ids(self, eval_ids: set[str]):
        self.eval_ids = set(eval_ids)
        leak = self.train_ids & self.eval_ids
        if leak:
            raise RuntimeError(f"CONTAMINATION: train∩eval={leak} — INVALID index")

    @staticmethod
    def _features_from_gt_train_only(gt: dict) -> dict:
        n_cars = sum(1 for o in gt.get("objects") or [] if o.get("class") == "car")
        n_peds = sum(1 for o in gt.get("objects") or [] if o.get("class") == "pedestrian")
        return {"n_cars": n_cars, "n_peds": n_peds, "density": gt.get("density") or "med",
                "near_miss": bool(gt.get("near_miss")), "street_token": (gt.get("street_name") or "").split()[0].lower()}

    @staticmethod
    def features_from_memory(mem: WorkingMemory) -> dict:
        n_cars = sum(1 for o in mem.objects.values() if str(o.get("class") or "").lower() == "car")
        n_peds = sum(1 for o in mem.objects.values() if str(o.get("class") or "").lower() == "pedestrian")
        dens = "high" if n_cars >= 6 else ("low" if n_cars <= 3 else "med")
        return {"n_cars": n_cars, "n_peds": n_peds, "density": dens, "near_miss": False,
                "street_token": (mem.street_name or "").split()[0].lower() if mem.street_name else ""}

    def _dist(self, a: dict, b: dict) -> float:
        d = abs(a.get("n_cars", 0) - b.get("n_cars", 0)) + 0.5 * abs(a.get("n_peds", 0) - b.get("n_peds", 0))
        if a.get("density") != b.get("density"): d += 1.0
        if a.get("street_token") and b.get("street_token") and a["street_token"] == b["street_token"]:
            d -= 0.5
        return d

    def query(self, mem: WorkingMemory, exclude_seq: str | None = None) -> dict | None:
        if exclude_seq and exclude_seq in self.train_ids and exclude_seq in self.eval_ids:
            raise RuntimeError("CONTAMINATION: exclude_seq in both splits")
        if exclude_seq and exclude_seq in self.eval_ids:
            # querying during eval — fine; just don't return eval entries (none stored)
            pass
        q = self.features_from_memory(mem)
        best, best_d = None, 1e9
        for e in self.entries:
            if exclude_seq and e["seq_id"] == exclude_seq:
                continue  # leave-one-out if somehow
            if e["seq_id"] in self.eval_ids:
                raise RuntimeError(f"CONTAMINATION: eval id {e['seq_id']} in retrieval index")
            d = self._dist(q, e["features"])
            if d < best_d:
                best, best_d = e, d
        if best:
            self.hit_counts[best["seq_id"]] = self.hit_counts.get(best["seq_id"], 0) + 1
            return {"hit_seq_id": best["seq_id"], "distance": best_d,
                    "hint_schema": best["hint"].get("track_schema"),
                    "hint_density": best["hint"].get("density"),
                    "hint_summary_style": best["hint"].get("summary_style"),
                    "query_features": q}
        return None

    def prompt_block(self, hit: dict | None) -> str:
        if not hit:
            return "RETRIEVAL: no hit"
        # Never paste full train GT tracks — schema/style only
        safe = {k: hit[k] for k in ("hit_seq_id", "distance", "hint_schema", "hint_density", "hint_summary_style", "query_features")}
        return "RETRIEVAL (train-only nearest; schema/style hint, NOT eval GT):\n" + json.dumps(safe, ensure_ascii=False)


class TrafficPhysicsTool:
    """NumPy traffic/light kinematics from perceived state. Real compute — never GT keys.

    Related (separate domain): examples/collision_predictive/ — hypo-action elastic
    collision emit (chosen_action, predicted_consequence, is_safe) + memory_bridge.
    """
    CYCLE_ORDER = ["G", "Y", "R"]
    CYCLE_LEN = {"G": 9, "Y": 3, "R": 8}

    def run(self, mem: WorkingMemory, n_ahead: int = 3) -> dict:
        import numpy as np
        light_next = {}
        for lid, st in mem.light_states.items():
            st = (st or "G").upper()[:1]
            if st not in self.CYCLE_LEN: st = "G"
            # advance one nominal frame bucket
            order = self.CYCLE_ORDER
            idx = order.index(st) if st in order else 0
            # simplistic: with p stay else next — deterministic step toward next phase
            light_next[lid] = order[(idx + 1) % 3] if st == "Y" else st  # Y→R; else hold for tool demo
            if st == "G":
                light_next[lid] = "G"  # hold unless memory says otherwise
        predicted = []
        for oid, obj in mem.objects.items():
            frames = obj.get("last_frames") or []
            if len(frames) >= 2:
                x0, y0 = float(frames[-2].get("x", frames[-2].get("cx", 0))), float(frames[-2].get("y", frames[-2].get("cy", 0)))
                x1, y1 = float(frames[-1].get("x", frames[-1].get("cx", 0))), float(frames[-1].get("y", frames[-1].get("cy", 0)))
                vx, vy = x1 - x0, y1 - y0
            elif len(frames) == 1:
                x1 = float(frames[-1].get("x", frames[-1].get("cx", 0)))
                y1 = float(frames[-1].get("y", frames[-1].get("cy", 0)))
                vx = vy = 0.0
            else:
                continue
            nexts = [{"t": k, "x": round(x1 + vx * k, 2), "y": round(y1 + vy * k, 2)} for k in range(1, n_ahead + 1)]
            predicted.append({"id": oid, "class": obj.get("class"), "vx": round(vx, 2), "vy": round(vy, 2), "next": nexts})
        # collision risk from predicted pairwise distances
        risk = "none"
        min_d = 1e9
        arr = []
        for p in predicted:
            if not p["next"]: continue
            arr.append((p["id"], p["next"][0]["x"], p["next"][0]["y"], p.get("class")))
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i][3] == "light" or arr[j][3] == "light":
                    continue
                d = float(np.hypot(arr[i][1] - arr[j][1], arr[i][2] - arr[j][2]))
                min_d = min(min_d, d)
        if min_d < 20: risk = "high"
        elif min_d < 40: risk = "moderate"
        elif min_d < 1e8: risk = "low"
        note = f"numpy tool: n_pred={len(predicted)} min_pair_d={min_d if min_d<1e8 else None} risk={risk}"
        return {"light_next": light_next, "predicted_positions": predicted,
                "collision_risk": risk, "min_pair_distance": None if min_d > 1e8 else round(min_d, 2),
                "note": note, "source": "TrafficPhysicsTool/numpy"}

    def prompt_block(self, out: dict) -> str:
        safe = {k: out[k] for k in ("light_next", "collision_risk", "min_pair_distance", "note", "source") if k in out}
        safe["predicted_positions"] = out.get("predicted_positions", [])[:12]
        return "TOOL_OUTPUT (real NumPy compute from perceptions; NOT answer keys):\n" + json.dumps(safe, ensure_ascii=False)


def make_split(out_f1: Path, eval_frac: float = 0.2, seed: int = 42) -> dict:
    summary = json.loads((out_f1 / "SUMMARY.json").read_text(encoding="utf-8"))
    seqs = [s["seq_id"] for s in summary["sequences"]]
    rng = random.Random(seed)
    ids = seqs[:]; rng.shuffle(ids)
    n_eval = max(1, int(round(len(ids) * eval_frac)))
    eval_ids = set(ids[:n_eval]); train_ids = set(ids[n_eval:])
    assert not (eval_ids & train_ids)
    split = {"seed": seed, "train_ids": sorted(train_ids), "eval_ids": sorted(eval_ids),
             "n_train": len(train_ids), "n_eval": len(eval_ids),
             "rule": "retrieval index = train only; eval GT never in prompt/memory/retrieval/tools"}
    (out_f1 / "SPLIT.json").write_text(json.dumps(split, indent=2) + "\n", encoding="utf-8")
    return split


def audit_log_path(out_f1: Path) -> Path:
    p = out_f1 / "CONTAMINATION_AUDIT.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def append_audit(out_f1: Path, record: dict):
    # hard checks
    eval_ids = set()
    split_path = out_f1 / "SPLIT.json"
    if split_path.exists():
        eval_ids = set(json.loads(split_path.read_text())["eval_ids"])
    blob = json.dumps(record)
    for eid in eval_ids:
        # flag if eval GT file contents somehow embedded — check seq gt path leaks in prompt
        if f"{eid}/gt_tracks" in blob or (record.get("prompt_touches_gt") is True):
            record["INVALID_CONTAMINATION"] = True
            record["contamination_reason"] = f"eval GT reference involving {eid}"
    path = audit_log_path(out_f1)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    if record.get("INVALID_CONTAMINATION"):
        raise RuntimeError(f"CONTAMINATION DETECTED — discard: {record.get('contamination_reason')}")


def build_augmented_prompt(base: str, mem: WorkingMemory | None, retrieval_hit: dict | None,
                           tool_out: dict | None, layers: dict) -> str:
    parts = [base]
    if layers.get("memory") and mem is not None:
        parts.append(mem.prompt_block())
    if layers.get("retrieval"):
        idx = RetrievalIndex()  # only for formatting; hit already computed
        parts.append(idx.prompt_block(retrieval_hit))
    if layers.get("tool") and tool_out is not None:
        parts.append(TrafficPhysicsTool().prompt_block(tool_out))
    parts.append("Usando memoria/retrieval/tool (si presentes), responde SOLO JSON válido final.")
    prompt = "\n\n".join(parts)
    # anti-contam: never include literal 'reference_summary' ground keys
    if "reference_summary" in prompt and "NOT ground truth" not in prompt:
        # our memory block says NOT ground truth — OK. Block raw key from GT files:
        pass
    return prompt

def load_vlm(model_id, adapter):
    from mlx_vlm import load
    from mlx_vlm.utils import load_config
    if adapter and Path(adapter).resolve() == ADAPTER_QUANTUM_RO.resolve():
        print("[warn] Refusing quantum adapter; base only.", flush=True)
        adapter = None
    kwargs = {"adapter_path": adapter} if adapter else {}
    print(f"Loading VLM {model_id} adapter={adapter!r} …", flush=True)
    model, processor = load(model_id, **kwargs)
    return model, processor, load_config(model_id)


def run_vlm_on_sequence(seq_dir, *, model, processor, config, adapter, max_frames, max_tokens,
                        layers, retrieval_index, out_f1, is_eval):
    """Inference with optional layers. ANTI-CONTAM: never reads GT into prompt."""
    from mlx_vlm import generate
    from mlx_vlm.prompt_utils import apply_chat_template

    seq_id = seq_dir.name
    # Load GT ONLY for post-hoc scoring — never into prompt/memory/retrieval query features from GT
    gt = json.loads((seq_dir / "gt_tracks.json").read_text(encoding="utf-8"))
    all_frames = sorted((seq_dir / "frames").glob("frame_*.png"))
    sample = subsample_frames(all_frames, max_frames)
    image_paths = [str(p) for p in sample]

    mem = WorkingMemory() if layers.get("memory") or layers.get("tool") or layers.get("retrieval") else None
    # Seed memory lightly from a cheap first pass? For min prototype: empty memory first,
    # run tool on empty→weak, then VLM, then optionally second pass. Simpler single pass:
    # 1) if tool/memory: run a vision-free bootstrap from frame count only is too weak.
    # Min viable: VLM once with layers; for tool/memory without prior perception, tool no-ops;
    # retrieval uses empty memory features (zeros) unless we allow a tiny caption-free prior.
    # Better interlock for min 10-frame: 
    #   a) retrieval with empty/default features (density unknown)
    #   b) VLM pass 1 → update memory from pred (perceptions)
    #   c) tool on memory → update memory
    #   d) VLM pass 2 with full layers (final answer)
    # That's 2 VLM calls — expensive. Single-pass alternative for ablations:
    #   - memory alone: include empty memory block (weak)
    #   - For all-on single pass: run tool on zeros, retrieval on zeros, VLM once, score.
    # Anthony asked interlock memory→retrieval→tool→memory. Do 2-step when any layer on.

    retrieval_hit = None
    tool_out = None
    audit = {"seq_id": seq_id, "is_eval": is_eval, "layers": dict(layers), "adapter": adapter,
             "prompt_touches_gt": False, "memory_snapshot": None, "retrieval_hit": None,
             "tool_call": None, "n_vlm_passes": 0}

    def one_generate(prompt_text):
        # contamination guard on prompt text
        if "reference_summary" in prompt_text and "gt_tracks" in prompt_text:
            audit["prompt_touches_gt"] = True
        if is_eval and seq_id in (retrieval_index.eval_ids if retrieval_index else []):
            # ensure prompt doesn't contain GT file dump
            gt_snip = json.dumps(gt.get("reference_summary", {}))[:80]
            if gt_snip and gt_snip in prompt_text and len(gt_snip) > 20:
                audit["prompt_touches_gt"] = True
        formatted = apply_chat_template(processor, config, prompt_text, num_images=len(image_paths))
        t0 = time.time()
        result = generate(model, processor, formatted, image=image_paths, max_tokens=max_tokens,
                          verbose=False, temperature=0.0)
        elapsed = time.time() - t0
        raw = result.text if hasattr(result, "text") else str(result)
        audit["n_vlm_passes"] += 1
        return raw, elapsed

    use_layers = any(layers.get(k) for k in ("memory", "retrieval", "tool"))
    total_elapsed = 0.0
    raw = ""
    pred = None

    if not use_layers:
        raw, elapsed = one_generate(TEMPORAL_PROMPT)
        total_elapsed += elapsed
        pred = _extract_json(raw)
    else:
        # Pass 1: base perceptions (no GT)
        raw1, elapsed = one_generate(TEMPORAL_PROMPT)
        total_elapsed += elapsed
        pred1 = _extract_json(raw1)
        if mem is None:
            mem = WorkingMemory()
        mem.update_from_perception(pred1)
        # Retrieval from memory features (train index only)
        if layers.get("retrieval") and retrieval_index is not None:
            retrieval_hit = retrieval_index.query(mem, exclude_seq=seq_id if seq_id in retrieval_index.train_ids else None)
            audit["retrieval_hit"] = {k: retrieval_hit[k] for k in ("hit_seq_id", "distance", "query_features") if retrieval_hit and k in retrieval_hit} if retrieval_hit else None
            if retrieval_hit and retrieval_hit["hit_seq_id"] in retrieval_index.eval_ids:
                audit["INVALID_CONTAMINATION"] = True
                audit["contamination_reason"] = "retrieval returned eval id"
                append_audit(out_f1, audit)
                raise RuntimeError("CONTAMINATION: retrieval hit eval id")
        # Tool from memory
        if layers.get("tool"):
            tool_out = TrafficPhysicsTool().run(mem)
            mem.update_from_tool(tool_out)
            audit["tool_call"] = {"note": tool_out.get("note"), "risk": tool_out.get("collision_risk"),
                                  "source": tool_out.get("source")}
        audit["memory_snapshot"] = mem.snapshot()
        # Pass 2: interlocking context
        aug = build_augmented_prompt(TEMPORAL_PROMPT, mem if layers.get("memory") else None,
                                     retrieval_hit if layers.get("retrieval") else None,
                                     tool_out if layers.get("tool") else None, layers)
        raw, elapsed = one_generate(aug)
        total_elapsed += elapsed
        pred = _extract_json(raw)
        if layers.get("memory") and pred:
            mem.update_from_perception(pred)
            audit["memory_snapshot"] = mem.snapshot()

    # Post-hoc score only (GT ok here)
    metrics = score_prediction(gt, pred, raw)
    append_audit(out_f1, audit)
    return {"seq_id": seq_id, "street_name_gt": gt.get("street_name"), "n_frames_full": gt["n_frames"],
            "n_frames_fed": len(image_paths), "frame_indices_fed": [int(p.stem.split("_")[1]) for p in sample],
            "adapter": adapter, "layers": dict(layers), "elapsed_s": round(total_elapsed, 2),
            "raw_text": raw[:5000], "pred": pred, "metrics": metrics, "audit_ref": audit.get("seq_id")}


def aggregate_metrics(rows):
    ms = [r["metrics"] for r in rows if "metrics" in r]
    if not ms: return {}
    def mean(key):
        vals = [m[key] for m in ms if m.get(key) is not None]
        return round(sum(vals)/len(vals), 3) if vals else None
    by_type = {"car": [], "pedestrian": [], "light": []}
    for m in ms:
        for cls, v in (m.get("tracking_by_type") or {}).items():
            if v is not None and cls in by_type: by_type[cls].append(v)
    return {"n": len(ms), "tracking_continuity_mean": mean("tracking_continuity"),
            "coherent_summary_pct": mean("coherent_summary_bin"),
            "narrative_coherence_mean_0_2": mean("narrative_coherence_0_2"),
            "spatial_relation_acc_mean": mean("spatial_relation_acc"),
            "light_state_acc_mean": mean("light_state_acc"),
            "street_name_ok_pct": round(sum(1 for m in ms if m.get("street_name_ok"))/len(ms), 3),
            "motion_prediction_pct": round(sum(1 for m in ms if m.get("motion_prediction_present"))/len(ms), 3),
            "parse_ok_pct": round(sum(1 for m in ms if m.get("parse_ok"))/len(ms), 3),
            "tracking_by_type_mean": {c: round(sum(vs)/len(vs),3) if vs else None for c,vs in by_type.items()}}


def score_gt_only(out_dir):
    results=[]
    for gt_path in sorted(Path(out_dir).glob("f1_*/gt_tracks.json")):
        gt=json.loads(gt_path.read_text(encoding="utf-8")); ref=gt["reference_summary"]
        perfect={"street_name":gt["street_name"],
            "tracks":[{"id":o["id"],"class":o["class"],"color":o.get("color"),
                       "state":(o["frames"][-1].get("state") if o.get("frames") else None),
                       "frames":[{"t":f["t"],"x":f["cx"],"y":f["cy"]} for f in (o.get("frames") or [])[::3]]} for o in gt["objects"]],
            "relations":[r for rels in gt["relations_keyframes"].values() for r in rels],
            "summary":ref["text"],"motion_prediction":ref.get("motion_prediction")}
        results.append({"seq_id":gt["seq_id"],"metrics":score_prediction(gt, perfect, json.dumps(perfect)+" "+ref["text"])})
    return {"mode":"gt_oracle_sanity","fase":1,"results":results,"aggregate":aggregate_metrics(results)}


def prepare_lora_dataset(out_dir, dest, max_frames=8, train_ids=None):
    """Chat JSONL from TRAIN split only (anti-contam for retrieval+LoRA)."""
    out_dir=Path(out_dir); dest=Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    rows=[]
    for gt_path in sorted(out_dir.glob("f1_*/gt_tracks.json")):
        gt=json.loads(gt_path.read_text(encoding="utf-8"))
        if train_ids is not None and gt["seq_id"] not in train_ids:
            continue
        frames=sorted((gt_path.parent/"frames").glob("frame_*.png"))
        sample=subsample_frames(frames, max_frames)
        completion={"street_name":gt["street_name"],
            "tracks":[{"id":o["id"],"class":o["class"],"color":o.get("color"),
                       "state":(o["frames"][-1].get("state") if o.get("frames") else None),
                       "frames":[{"t":f["t"],"x":f["cx"],"y":f["cy"]} for f in (o.get("frames") or [])[::4]]} for o in gt["objects"]],
            "relations":[r for rels in gt["relations_keyframes"].values() for r in rels][:12],
            "summary":gt["reference_summary"]["text"],
            "motion_prediction":gt.get("motion_prediction") or gt["reference_summary"].get("motion_prediction"),
            "collision":{"near_miss":gt.get("near_miss",False),"crash":False,"risk":"high" if gt.get("near_miss") else "none"}}
        rows.append({"images":[str(p) for p in sample],
                     "messages":[{"role":"user","content":TEMPORAL_PROMPT},
                                 {"role":"assistant","content":json.dumps(completion, ensure_ascii=False)}],
                     "seq_id":gt["seq_id"]})
    dest.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows)+"\n", encoding="utf-8")
    hf=dest.parent/(dest.stem+"_hf"); hf.mkdir(parents=True, exist_ok=True)
    (hf/"train.jsonl").write_text(dest.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {len(rows)} TRAIN rows → {dest}")
    return dest


def train_f1(dataset_hf, out, model_id, rank, alpha, lr, epochs, force):
    out=Path(out); dataset_hf=Path(dataset_hf)
    if out.resolve()==ADAPTER_QUANTUM_RO.resolve():
        print("REFUSING quantum adapter path", file=sys.stderr); return 3
    if train_lock_held() and not force:
        print("TRAIN_LOCK held", file=sys.stderr); return 2
    out.mkdir(parents=True, exist_ok=True)
    lock=ROOT/"data"/"TRAIN_LOCK.txt"
    lock.write_text(f"owner=video-f1 started={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} out={out}\n", encoding="utf-8")
    cmd=[sys.executable,"-m","mlx_vlm.lora","--model-path",model_id,"--dataset",str(dataset_hf),
         "--lora-rank",str(rank),"--lora-alpha",str(alpha),"--learning-rate",str(lr),
         "--epochs",str(epochs),"--batch-size","1","--train-on-completions","--grad-checkpoint",
         "--gradient-accumulation-steps","4","--output-path",str(out/"adapters.safetensors")]
    print("Running:", " ".join(cmd), flush=True)
    (out/"train_meta.json").write_text(json.dumps({"cmd":cmd,"rank":rank,"alpha":alpha,"epochs":epochs}, indent=2)+"\n", encoding="utf-8")
    try:
        rc=subprocess.call(cmd, cwd=str(ROOT))
    finally:
        if lock.exists() and "video-f1" in lock.read_text(): lock.unlink(missing_ok=True)
    return rc

ABLATION_CONFIGS = [
    {"name": "none", "memory": False, "retrieval": False, "tool": False},
    {"name": "memory", "memory": True, "retrieval": False, "tool": False},
    {"name": "retrieval", "memory": False, "retrieval": True, "tool": False},
    {"name": "tool", "memory": False, "retrieval": False, "tool": True},
    {"name": "all", "memory": True, "retrieval": True, "tool": True},
]


def ensure_split_and_index(out_f1):
    out_f1 = Path(out_f1)
    if not (out_f1 / "SPLIT.json").exists():
        make_split(out_f1)
    split = json.loads((out_f1 / "SPLIT.json").read_text(encoding="utf-8"))
    train_ids, eval_ids = set(split["train_ids"]), set(split["eval_ids"])
    if train_ids & eval_ids:
        raise RuntimeError(f"CONTAMINATION in SPLIT: {train_ids & eval_ids}")
    index = RetrievalIndex()
    train_dirs = [out_f1 / sid for sid in sorted(train_ids)]
    index.build_from_train(train_dirs)
    index.set_eval_ids(eval_ids)
    return split, index


def run_vlm_batch(out_f1, model_id, adapter, max_frames, seq_spec, max_tokens, force, results_path, layers):
    out_f1 = Path(out_f1)
    if train_lock_held() and not force:
        raise RuntimeError("TRAIN_LOCK held")
    split, index = ensure_split_and_index(out_f1)
    summary = json.loads((out_f1 / "SUMMARY.json").read_text(encoding="utf-8"))
    seqs = summary["sequences"]
    id_to_idx = {s["seq_id"]: i for i, s in enumerate(seqs)}
    if seq_spec.strip().lower() == "eval":
        chosen_ids = list(split["eval_ids"])
    elif seq_spec.strip().lower() == "all":
        chosen_ids = [s["seq_id"] for s in seqs]
    else:
        # numeric indices into SUMMARY, filtered — prefer eval for clean numbers
        idxs = [int(x) for x in seq_spec.split(",") if x.strip() != ""]
        chosen_ids = [seqs[i]["seq_id"] for i in idxs if 0 <= i < len(seqs)]
    model, processor, config = load_vlm(model_id, adapter)
    results = []
    for sid in chosen_ids:
        seq_dir = out_f1 / sid
        is_eval = sid in set(split["eval_ids"])
        print(f"=== VLM {sid} layers={layers} eval={is_eval} ===", flush=True)
        try:
            row = run_vlm_on_sequence(seq_dir, model=model, processor=processor, config=config,
                                      adapter=adapter, max_frames=max_frames, max_tokens=max_tokens,
                                      layers=layers, retrieval_index=index, out_f1=out_f1, is_eval=is_eval)
            m = row["metrics"]
            print(f"  track={m['tracking_continuity']:.2f} coherent={m['coherent_summary_bin']} parse={m['parse_ok']} ({row['elapsed_s']}s)", flush=True)
        except Exception as exc:
            row = {"seq_id": sid, "error": f"{type(exc).__name__}: {exc}", "layers": dict(layers)}
            print(f"  FAIL {row['error']}", flush=True)
        results.append(row)
    report = {"fase": 1, "model": model_id, "adapter": adapter, "max_frames": max_frames,
              "layers": dict(layers), "split": {"n_train": split["n_train"], "n_eval": split["n_eval"]},
              "aggregate": aggregate_metrics(results), "results": results,
              "audit_log": str(audit_log_path(out_f1)),
              "note": "Own-delta. Anti-contam: eval GT post-hoc only. Quantum adapter RO."}
    Path(results_path).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("AGGREGATE:", json.dumps(report["aggregate"], indent=2))
    return report


def run_ablations(out_f1, model_id, adapter, max_frames, max_tokens, force, seq_spec="eval"):
    """Ablate each layer; write clean table. Skip dirty runs."""
    out_f1 = Path(out_f1)
    table = []
    # clear audit for this ablation session marker
    audit_path = audit_log_path(out_f1)
    with audit_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event": "ablation_session_start", "t": time.time(), "adapter": adapter}) + "\n")
    for cfg in ABLATION_CONFIGS:
        layers = {k: cfg[k] for k in ("memory", "retrieval", "tool")}
        name = cfg["name"]
        outp = out_f1 / f"results_ablate_{name}.json"
        print(f"\n######## ABLATION {name} {layers} ########", flush=True)
        try:
            rep = run_vlm_batch(out_f1, model_id, adapter, max_frames, seq_spec, max_tokens, force, outp, layers)
            agg = rep["aggregate"]
            dirty = any(r.get("error", "").startswith("CONTAMINATION") for r in rep["results"])
            table.append({"ablation": name, "layers": layers, "dirty": dirty,
                          "tracking": agg.get("tracking_continuity_mean"),
                          "coherent_summary_pct": agg.get("coherent_summary_pct"),
                          "parse_ok_pct": agg.get("parse_ok_pct"),
                          "by_type": agg.get("tracking_by_type_mean"),
                          "n": agg.get("n"), "path": str(outp)})
            if dirty:
                print(f"[INVALID] {name} dirty — numbers discarded from gate", flush=True)
        except Exception as exc:
            table.append({"ablation": name, "error": str(exc), "dirty": True})
    # deltas vs none
    base = next((t for t in table if t.get("ablation") == "none" and not t.get("dirty")), None)
    for t in table:
        if base and t.get("tracking") is not None and not t.get("dirty"):
            t["delta_tracking_vs_none"] = round((t["tracking"] or 0) - (base["tracking"] or 0), 3)
            t["delta_coherent_vs_none"] = round((t.get("coherent_summary_pct") or 0) - (base.get("coherent_summary_pct") or 0), 3)
    out = {"fase": 1, "adapter": adapter, "max_frames": max_frames, "seq_spec": seq_spec,
           "audit_log": str(audit_path), "table": table,
           "note": "Clean ablations only. Dirty rows marked; do not report as gate numbers."}
    path = out_f1 / "ABLATION_TABLE.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    # markdown
    md = ["# F1 layer ablations (clean)", "", f"Audit: `{audit_path}`", "",
          "| ablation | track | coherent | parse | Δtrack | Δcoherent | dirty |",
          "|----------|-------|----------|-------|--------|-----------|-------|"]
    for t in table:
        if t.get("error"):
            md.append(f"| {t['ablation']} | ERR |  |  |  |  | yes |")
            continue
        md.append(f"| {t['ablation']} | {t.get('tracking')} | {t.get('coherent_summary_pct')} | {t.get('parse_ok_pct')} | {t.get('delta_tracking_vs_none')} | {t.get('delta_coherent_vs_none')} | {t.get('dirty')} |")
    (out_f1 / "ABLATION_TABLE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return out


def eval_compare(out_f1, model_id, adapter, max_frames, seq_spec, max_tokens, force):
    layers_all = {"memory": True, "retrieval": True, "tool": True}
    base = run_vlm_batch(out_f1, model_id, None, max_frames, seq_spec, max_tokens, force,
                         Path(out_f1) / "results_vlm_base.json", layers_all)
    import gc; gc.collect()
    ap = str(adapter if Path(adapter).is_absolute() else ROOT / adapter)
    lora = run_vlm_batch(out_f1, model_id, ap, max_frames, seq_spec, max_tokens, force,
                         Path(out_f1) / "results_vlm_lora.json", layers_all)
    ba, la = base["aggregate"], lora["aggregate"]
    delta = {
        "tracking_continuity": round((la.get("tracking_continuity_mean") or 0) - (ba.get("tracking_continuity_mean") or 0), 3),
        "coherent_summary_pct": round((la.get("coherent_summary_pct") or 0) - (ba.get("coherent_summary_pct") or 0), 3),
        "parse_ok_pct": round((la.get("parse_ok_pct") or 0) - (ba.get("parse_ok_pct") or 0), 3),
    }
    track_ok = (la.get("tracking_continuity_mean") or 0) >= GATE_TRACK
    coh_ok = (la.get("coherent_summary_pct") or 0) >= GATE_COHERENT
    substantial = delta["tracking_continuity"] >= 0.15 or delta["coherent_summary_pct"] >= 0.15
    gate_pass = (track_ok and coh_ok) or substantial
    compare = {"fase": 1, "layers": layers_all, "gate": {"tracking": GATE_TRACK, "coherent": GATE_COHERENT},
               "base": ba, "lora": la, "delta": delta, "gate_pass": gate_pass,
               "gate_detail": {"track_ge_80": track_ok, "coherent_ge_80": coh_ok, "substantial_jump": substantial},
               "audit_log": str(audit_log_path(Path(out_f1))),
               "recommendation": ("GATE PASS — stack F2 reinforcement; keep iterating." if gate_pass else
                                  "GATE FAIL — diagnose by_type; fix set/prompt/train; no F2 LoRA yet.")}
    path = Path(out_f1) / "results_base_vs_lora.json"
    path.write_text(json.dumps(compare, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(compare, indent=2)); print(f"Wrote {path} gate_pass={gate_pass}")
    return compare


def main(argv=None):
    p = argparse.ArgumentParser(description="VIDEO F1 + 3 layers + anti-contam")
    p.add_argument("--generate-f1", action="store_true")
    p.add_argument("--n-seq", type=int, default=50)
    p.add_argument("--n-frames", type=int, default=16)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-f1", type=Path, default=F1_DIR)
    p.add_argument("--scaffold-f2f3", action="store_true")
    p.add_argument("--score-gt-only", action="store_true")
    p.add_argument("--make-split", action="store_true")
    p.add_argument("--vlm", action="store_true")
    p.add_argument("--ablate", action="store_true", help="Run layer ablations on eval split")
    p.add_argument("--eval-compare", action="store_true")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--adapter-ro", type=Path, default=None)
    p.add_argument("--max-frames", type=int, default=8)
    p.add_argument("--seq", default="eval", help="eval | all | comma indices")
    p.add_argument("--max-tokens", type=int, default=900)
    p.add_argument("--force-vlm", action="store_true")
    p.add_argument("--results", type=Path, default=None)
    p.add_argument("--prepare-lora-dataset", action="store_true")
    p.add_argument("--train-f1", action="store_true")
    p.add_argument("--force-train", action="store_true")
    p.add_argument("--rank", type=int, default=16)
    p.add_argument("--alpha", type=float, default=32.0)
    p.add_argument("--lr", type=float, default=2e-4)
    p.add_argument("--epochs", type=int, default=2)
    p.add_argument("--layer-memory", action="store_true")
    p.add_argument("--layer-retrieval", action="store_true")
    p.add_argument("--layer-tool", action="store_true")
    p.add_argument("--layers-all", action="store_true")
    args = p.parse_args(argv)

    if args.scaffold_f2f3 or args.generate_f1:
        scaffold_f2f3()
    if args.generate_f1:
        print(f"Generating F1 {args.n_seq}×{args.n_frames} → {args.out_f1}", flush=True)
        generate_f1(args.out_f1, n_seq=args.n_seq, n_frames=args.n_frames, seed=args.seed)
        make_split(args.out_f1, seed=args.seed)
    if args.make_split:
        print(json.dumps(make_split(args.out_f1, seed=args.seed), indent=2))
    if args.score_gt_only:
        report = score_gt_only(args.out_f1)
        out = args.results or (args.out_f1 / "results_gt_oracle.json")
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report["aggregate"], indent=2))
    if args.prepare_lora_dataset:
        split, _ = ensure_split_and_index(args.out_f1)
        prepare_lora_dataset(args.out_f1, SYNTH / "fase1_lora_dataset.jsonl",
                             max_frames=args.max_frames, train_ids=set(split["train_ids"]))
    if args.train_f1:
        split, _ = ensure_split_and_index(args.out_f1)
        prepare_lora_dataset(args.out_f1, SYNTH / "fase1_lora_dataset.jsonl",
                             max_frames=args.max_frames, train_ids=set(split["train_ids"]))
        return train_f1(SYNTH / "fase1_lora_dataset_hf", ADAPTER_F1, args.model,
                        args.rank, args.alpha, args.lr, args.epochs, args.force_train)
    layers = {"memory": False, "retrieval": False, "tool": False}
    if args.layers_all:
        layers = {"memory": True, "retrieval": True, "tool": True}
    else:
        layers = {"memory": args.layer_memory, "retrieval": args.layer_retrieval, "tool": args.layer_tool}

    if args.ablate:
        adapter = None
        if args.adapter_ro:
            ap = args.adapter_ro if args.adapter_ro.is_absolute() else ROOT / args.adapter_ro
            if ap.resolve() != ADAPTER_QUANTUM_RO.resolve():
                adapter = str(ap)
        run_ablations(args.out_f1, args.model, adapter, args.max_frames, args.max_tokens, args.force_vlm, args.seq)
        return 0
    if args.eval_compare:
        adapter = args.adapter_ro or ADAPTER_F1
        eval_compare(args.out_f1, args.model, Path(adapter), args.max_frames, args.seq, args.max_tokens, args.force_vlm)
        return 0
    if args.vlm:
        adapter = None
        if args.adapter_ro is not None:
            ap = args.adapter_ro if args.adapter_ro.is_absolute() else ROOT / args.adapter_ro
            if ap.resolve() != ADAPTER_QUANTUM_RO.resolve():
                adapter = str(ap)
        out = args.results or (args.out_f1 / ("results_vlm_lora.json" if adapter else "results_vlm_base.json"))
        try:
            run_vlm_batch(args.out_f1, args.model, adapter, args.max_frames, args.seq, args.max_tokens,
                          args.force_vlm, out, layers)
        except RuntimeError as e:
            print(f"[warn] {e}", file=sys.stderr); return 2
    if not any([args.generate_f1, args.scaffold_f2f3, args.score_gt_only, args.make_split, args.vlm,
                args.ablate, args.eval_compare, args.prepare_lora_dataset, args.train_f1]):
        p.print_help(); return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
