#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
all_in_one.py
固定路径：输入你的文件存放路径
1) 合并所有 .xlsx，排除 安全审计/扫描/爬虫
2) 用 ip.txt 过滤 & 去重源 IP  ip.txt存放白名单ip或者已经封禁过的ip
3) 按客户端 IP 输出去重域名
"""

import os, warnings, pandas as pd
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings('ignore')
ROOT = Path(r'your_own_path').resolve()  //修改根路径为你自己的路径

# ---------- 1. 合并 ----------
def normalize(df):
    if df is not None and not df.empty:
        df.columns = df.columns.str.strip().str.replace(' ', '').astype(str)
    return df

def process_sheet(args):
    f, sh, excl = args
    try:
        df = pd.read_excel(f, sheet_name=sh, header=0)
        df = normalize(df)
        col = next((c for c in df.columns if '攻击类型' in c or ('攻击' in c and '类型' in c)), None)
        if col is None: return None
        df[col] = df[col].astype(str).str.strip()
        df = df[~df[col].isin(excl)]
        return df if not df.empty else None
    except Exception as e:
        print(f'跳过 {f.name} - {sh}: {e}')
        return None

def merge():
    files = list(ROOT.rglob('*.xlsx'))
    if not files:
        raise FileNotFoundError('未找到任何 .xlsx 文件')
    exclude = ['安全审计', '安全扫描', '网页爬虫']
    tasks = [(f, sh, exclude) for f in files for sh in pd.ExcelFile(f).sheet_names]
    dfs = []
    with ThreadPoolExecutor() as ex:
        for r in ex.map(process_sheet, tasks):
            if r is not None: dfs.append(r)
    merged = ROOT / 'result.xlsx'
    pd.concat(dfs, ignore_index=True).to_excel(merged, index=False)
    print(f'✅ 合并完成 → {merged.name} ({len(dfs)} 个 sheet)')
    return merged

# ---------- 2. IP 黑名单 ----------
def filter_blacklist(src):
    bl_file = ROOT / 'ip.txt'
    if not bl_file.exists():
        raise FileNotFoundError('缺少 ip.txt')
    blacklist = {l.strip() for l in bl_file.open(encoding='utf-8') if l.strip()}
    df = pd.read_excel(src)
    if '源IP' not in df.columns: raise KeyError('无 源IP 列')
    filtered = df[~df['源IP'].isin(blacklist)].drop_duplicates(subset='源IP')
    dst = ROOT / 'filtered_result.xlsx'
    filtered.to_excel(dst, index=False)
    print(f'✅ 黑名单过滤 → {dst.name} ({len(filtered)} 条)')
    return dst

# ---------- 3. 域名去重 ----------
def domain_stats(src):
    df = pd.read_excel(src, usecols=['客户端IP', '域名'], dtype=str)
    ips = df['客户端IP'].dropna().unique()
    result = {ip: sorted(df[df['客户端IP'] == ip]['域名'].dropna().unique()) for ip in ips}
    for ip, doms in result.items():
        print(f'\n客户端IP: {ip}')
        for d in doms: print(f'  - {d}')
    out = ROOT / 'client_ip_domains_unique.xlsx'
    with pd.ExcelWriter(out, engine='openpyxl') as w:
        for ip, doms in result.items():
            pd.Series(doms, name='域名').to_frame().to_excel(
                w, sheet_name=str(ip).replace('.', '_'), index=False)
    print(f'✅ 域名统计 → {out.name}')

# ---------- 主流程 ----------
if __name__ == '__main__':
    merged   = merge()
    filtered = filter_blacklist(merged)
    domain_stats(filtered)
    print('\n🎉 全部完成！结果已保存在', ROOT)
