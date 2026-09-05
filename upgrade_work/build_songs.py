# -*- coding: utf-8 -*-
"""把诗经/唐诗三百首/宋词三百首 + 补遗名篇 合并为 songs.json（1000 首）"""
import json, re, pathlib
from opencc import OpenCC

base = pathlib.Path(__file__).resolve().parent
data_dir = base / 'data'
cc = OpenCC('t2s')

def load(fn):
    return json.loads((data_dir / fn).read_text(encoding='utf-8'))

shijing = load('_shijing.json')
tang300 = load('_tang300.json')
song300 = load('_song300.json')
bonus = load('_bonus.json')

def first_seg(line):
    """取首句第一分句，去标点，用于词牌标题后缀"""
    for sep in '，。、；！？':
        if sep in line:
            line = line.split(sep)[0]
    return line.strip()

songs = []

# 1) 诗经 305
for it in shijing:
    title = it['title']
    chapter = it['chapter']      # 国风/小雅/大雅/颂
    section = it['section']
    lyrics = '\n'.join(it['content'])
    songs.append({
        'title': title,
        'author': '佚名',
        'tags': ['诗经'],
        'lyrics': lyrics,
        'note': f"《诗经·{chapter}·{section}》",
    })

# 2) 唐诗三百首 366（繁体→简体）
for it in tang300:
    title = cc.convert(it['title'])
    author = cc.convert(it['author'] or '佚名')
    lyrics = '\n'.join(cc.convert(p) for p in it['paragraphs'])
    songs.append({
        'title': title,
        'author': author,
        'tags': ['唐诗'],
        'lyrics': lyrics,
        'note': '选自《唐诗三百首》',
    })

# 3) 宋词三百首 280（标题 = 词牌·首句）
for it in song300:
    rhythmic = it.get('rhythmic', '').strip()
    head = first_seg(it['paragraphs'][0]) if it.get('paragraphs') else ''
    title = f"{rhythmic}·{head}" if (rhythmic and head and head != rhythmic) else (rhythmic or head or '无题')
    author = it.get('author', '') or '佚名'
    lyrics = '\n'.join(it['paragraphs'])
    songs.append({
        'title': title,
        'author': author,
        'tags': ['宋词'],
        'lyrics': lyrics,
        'note': '选自《宋词三百首》',
    })

# 4) 补遗 49
for it in bonus:
    songs.append({
        'title': it['title'],
        'author': it.get('author', '佚名'),
        'tags': it['tags'],
        'lyrics': it['lyrics'],
        'note': '经典名篇补遗',
    })

assert len(songs) == 1000, f'总数={len(songs)}，应为 1000'

# 组装为应用结构
result = []
for i, s in enumerate(songs, 1):
    result.append({
        'id': f'{i:03d}',
        'number': i,
        'title': s['title'],
        'author': s['author'],
        'tags': s['tags'],
        'source': 'seed',
        'copyrightStatus': '公有领域（古籍原文）',
        'lyrics': s['lyrics'],
        'note': s['note'],
    })

out = data_dir / 'songs.json'
out.write_text(json.dumps(result, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

# ---- 校验 ----
bad = []
ids = set()
for s in result:
    if s['id'] in ids: bad.append(f"重复id:{s['id']}")
    ids.add(s['id'])
    if not s['title']: bad.append(f"空标题:{s['id']}")
    if not s['lyrics']: bad.append(f"空正文:{s['id']}")
    if not s['author']: bad.append(f"空作者:{s['id']}")
    if not s['tags']: bad.append(f"空标签:{s['id']}")
n = len(result)
total_chars = sum(len(s['lyrics']) for s in result)
tag_stat = {}
for s in result:
    for t in s['tags']: tag_stat[t] = tag_stat.get(t, 0) + 1
print(f'总数: {n}')
print(f'正文字符合计: {total_chars}')
print(f'标签统计: {tag_stat}')
print(f'编号范围: {result[0]["id"]} ~ {result[-1]["id"]}')
print(f'首条: {result[0]["title"]} | 末条: {result[-1]["title"]}')
print('问题:', bad if bad else '无')
print('songs.json 大小:', out.stat().st_size)
