"""Synchronize public toinfo.work pet listing without inventing S-rank decimal baselines."""
import json, os, re, time, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'data/pets.json'
BASE='https://toinfo.work'

def get_html(url):
    req=urllib.request.Request(url,headers={'User-Agent':'EdenPetCatalog/1.0 (manual admin update; contact site owner for permission)','Accept':'text/html'})
    with urllib.request.urlopen(req,timeout=25) as response:
        if response.status!=200: raise ValueError(f'HTTP {response.status}: {url}')
        raw=response.read(5_000_000)
        return raw.decode('utf-8',errors='replace')

def parse_listing(html):
    soup=BeautifulSoup(html,'html.parser')
    result={}
    for a in soup.select('a.item-box[href]'):
        href=a.get('href','')
        m=re.search(r'/pet/(\d+)',href)
        if not m: continue
        title=a.select_one('.title')
        if not title: continue
        name=title.get_text(' ',strip=True)
        if not name: continue
        specs={}
        for item in a.select('.spec'):
            label=item.select_one('.lb'); value=item.select_one('.tx')
            if label and value: specs[label.get_text(' ',strip=True)]=value.get_text(' ',strip=True)
        try:
            initial=[int(x) for x in specs['초기치'].split()]
            if len(initial)!=4: continue
            growth=[float(specs[k]) for k in ('내구력','공격력','방어력','순발력')]
            total=float(specs['전체성장률'])
            if any(x<0 for x in initial+growth) or not 0<total<20: continue
        except (KeyError,ValueError): continue
        attrs={}
        for attr in a.select('.attr-label'):
            match=re.search(r'([지수화풍])\s*\(\s*(\d+)\s*\)',attr.get_text(' ',strip=True))
            if match: attrs[match.group(1)]=int(match.group(2))
        img=a.select_one('img[src]')
        get=a.select_one('.get'); grade=a.select_one('.grade')
        result[m.group(1)]={'id':m.group(1),'name':name,'initial':initial,'growth':growth,'total':total,'attrs':attrs,'image':urljoin(BASE,img['src']) if img else None,'source':re.sub(r'^획득\s*방법\s*:\s*','',get.get_text(' ',strip=True)) if get else '', 'tier':re.sub(r'^페트\s*등급\s*:\s*','',grade.get_text(' ',strip=True)) if grade else '일반','ride':specs.get('탑승')=='가능','skillSlots':int(specs['기술창']) if specs.get('기술창','').isdigit() else None}
    return result

def last_page(html):
    soup=BeautifulSoup(html,'html.parser'); nums=[1]
    for a in soup.select('a[href]'):
        for m in re.finditer(r'/pet/page/(\d+)',a.get('href','')): nums.append(int(m.group(1)))
    return max(nums)

def crawl(fetch=get_html):
    first=fetch(BASE+'/pet')
    pages=last_page(first)
    if pages>200: raise ValueError('Unexpected page count')
    found=parse_listing(first)
    if len(found)<5: raise ValueError('First page has too few pets: refusing update')
    for page in range(2,pages+1):
        html=fetch(f'{BASE}/pet/page/{page}')
        entries=parse_listing(html)
        if not entries: raise ValueError(f'Page {page} has no parsable pets: refusing update')
        found.update(entries)
        time.sleep(0.35)
    return found,pages

def replace_catalog(found, target=TARGET):
    # The toinfo.work catalog is the sole source. Never merge the old 487-pet database.
    if len(found) < 100:
        raise ValueError(f'Only {len(found)} pets: refusing incomplete catalog')
    pets=[]
    for r in found.values():
        pets.append({
            'name':r['name'], 'toinfoId':r['id'], 'toinfoInitial':r['initial'],
            'toinfoGrowth':r['growth'], 'hp':[r['initial'][0],r['growth'][0]],
            'atk':[r['initial'][1],r['growth'][1]], 'def':[r['initial'][2],r['growth'][2]],
            'agi':[r['initial'][3],r['growth'][3]], 'baselineVerified':False,
            'total':r['total'], 'attrs':r['attrs'], 'image':r['image'],
            'source':r['source'], 'tier':r['tier'], 'ride':r['ride'],
            'skillSlots':r['skillSlots']
        })
    catalog={'source':BASE+'/pet','snapshot':'live-sync','complete':True,'total':len(pets),'updatedAt':datetime.now(timezone.utc).isoformat(),'pets':pets}
    output=json.dumps(catalog,ensure_ascii=False,indent=2)+'\n'
    if not target.exists() or target.read_text(encoding='utf-8')!=output:
        target.write_text(output,encoding='utf-8')
    return {'total':len(pets),'complete':True}

def main():
    found,pages=crawl()
    print(json.dumps({'pages':pages,**replace_catalog(found)},ensure_ascii=False))

if __name__=='__main__': main()
