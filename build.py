"""Generate the static site from shared templates and article data."""
from pathlib import Path
import json,html,re
from xml.sax.saxutils import escape
R=Path(__file__).resolve().parent
articles=json.loads((R/'content/articles.json').read_text())
credits={x['path']:x for x in json.loads((R/'data/image-credits.json').read_text())}
header=(R/'templates/header.html').read_text()
footer=(R/'templates/footer.html').read_text()
e=html.escape
def header_for(path):
 active = '/news/' if path.startswith('/news/') else '/about/' if path.startswith('/about/') else '/'
 return header.replace('<a href="'+active+'">', '<a href="'+active+'" aria-current="page" class="on">')

def write(path,text):
 p=R/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
def cards(items):
 return '<div class="cards">'+''.join(f'<a class="card" href="/news/{a["slug"]}/"><picture class="archive-photo"><img loading="lazy" src="/{a["image"]}" alt="{e(credits[a["image"]]["caption"])}"></picture><div><span>{a["category"]}</span><h2>{a["title"]}</h2><p>{a["description"]}</p></div></a>' for a in items)+'</div>'
def page(title,desc,path,body,structured=None):
 url='https://chinabsr.org'+path
 ld='<script type="application/ld+json">'+json.dumps(structured,ensure_ascii=False).replace('<','\\u003c')+'</script>' if structured else ''
 return f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} · 中国蓝天视界</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><link rel="icon" type="image/png" href="/assets/china-bsr-avatar.png"><link rel="apple-touch-icon" href="/assets/china-bsr-avatar.png"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{url}"><meta property="og:type" content="article"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/navigation.css"><script src="/assets/navigation.js" defer></script>{ld}</head><body>{header_for(path)}<main class="wrap content">{body}</main>{footer}</body></html>'
css='''*{box-sizing:border-box}body{margin:0;color:#16354b;background:#f6f8f9;font:1rem/1.85 system-ui,"Microsoft YaHei",sans-serif}.wrap{width:min(90%,72rem);margin:auto}header{border-bottom:1px solid #ccd8df}header .wrap,.foot{display:flex;justify-content:space-between;gap:1.5rem;padding:1.2rem 0;align-items:center}.brand{font-size:1.25rem;font-weight:750;text-decoration:none}.brand span{color:#087ba7}nav{display:flex;gap:1.2rem}a{color:#075c91;text-underline-offset:.2em}a:focus-visible,button:focus-visible{outline:3px solid #d67b20;outline-offset:3px}.content{padding:2.5rem 0 4rem}h1{font-size:clamp(1.9rem,4vw,3rem);line-height:1.4}h2{font-size:1.4rem;line-height:1.5}.lead{font-size:1.1rem;color:#496373}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}.card{background:white;border:1px solid #dce5ea;border-radius:.6rem;overflow:hidden;text-decoration:none;color:inherit}.card img{width:100%;height:200px;object-fit:cover}.card div{padding:1.1rem}.card h2{font-size:1.15rem}.card p{color:#496373}.card span,.meta{color:#526979;font-size:.9rem}.article{max-width:48rem;margin:auto}.article p{line-height:2}.article figure{margin:2rem 0}.article img{width:100%;max-height:480px;object-fit:cover}.article figcaption{font-size:.85rem;color:#526979}.sources,.related{border-top:1px solid #ccd8df;margin-top:2rem;padding-top:1rem}.filters{display:flex;gap:.7rem;flex-wrap:nowrap;overflow-x:auto;max-width:100%;margin:1.5rem 0;padding-bottom:.35rem;-webkit-overflow-scrolling:touch}.filters button{flex:0 0 auto;white-space:nowrap}.filters button{font:inherit;border:1px solid #b5c8d3;padding:.4rem .9rem;border-radius:2rem;background:white;color:#16354b;cursor:pointer}.filters button[aria-pressed=true]{background:#16354b;color:white}footer{background:#102739;color:#cbdce6;padding:1rem 0 1.5rem}footer a{color:white}.foot nav{display:grid}.footnote{font-size:.9rem;border-top:1px solid #375367;padding-top:1rem}.home-news{padding:3rem 0}.card[hidden]{display:none}@media(max-width:800px){.cards{grid-template-columns:repeat(2,1fr)}}@media(max-width:550px){.cards{grid-template-columns:1fr}header .wrap,.foot{align-items:flex-start;flex-direction:column;gap:.6rem}nav{gap:1rem}.content{padding-top:1.5rem}}'''
css += '.latest-news{padding:0;list-style:none}.latest-news li{display:flex;gap:1em;align-items:baseline;padding:.6em 0;border-bottom:1px solid #dce5ea}.latest-news time,.news-list time{white-space:nowrap;color:#526979;font-size:.85rem}.news-list:has(.card:not([hidden])){margin-bottom:1.5rem}'
css += '.photo-feature{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);align-items:center;margin:1rem 0 1.5rem}.photo-feature img{display:block;height:auto}.photo-feature h2{font-size:clamp(1.15rem,2vw,1.65rem)}@media(max-width:600px){.photo-feature{grid-template-columns:1fr}}'
css += '.story-nav{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));margin:2rem 0;border-block:1px solid #ccd8df}.story-nav a{padding:.85rem 0;text-decoration:none}.story-nav a:hover,.story-nav a:focus-visible{text-decoration:underline}.story-nav small{display:block;color:#526979}.story-nav [rel=next]{grid-column:2}.news-list img{height:auto;aspect-ratio:1080/560;object-fit:contain;display:block}@media(max-width:600px){.story-nav{grid-template-columns:1fr;gap:0}.story-nav [rel=next]{grid-column:auto}}'
css += '.archive-photo{position:relative;display:block}.archive-photo img{display:block}.archive-photo::after,.hero::after{content:"中国蓝天视界 · chinaBSR.org";position:absolute;top:.65rem;left:.75rem;z-index:1;color:white;background:rgba(9,29,45,.65);padding:.12rem .43rem;border-radius:.18rem;font:600 clamp(.68rem,1.1vw,.84rem)/1.5 system-ui,sans-serif;white-space:nowrap;pointer-events:none}'
write('assets/site.css',css)
news = sorted(json.loads((R/'content/news.json').read_text()), key=lambda a: a['when'], reverse=True)
catalog = {a['slug']: a for a in articles + news}
if len(catalog) != len(articles) + len(news):
 raise ValueError('Duplicate article slug')

def paragraph(a, value):
 text = e(value)
 if 'inline' in a:
  phrase, target = a['inline']
  text = text.replace(e(phrase), f'<a href="/news/{target}/">{e(phrase)}</a>', 1)
 return text

def article_footer(a, sequence):
 i = sequence.index(a)
 used = {a['slug']}
 if 'inline' in a:
  phrase, target = a['inline']
  if target not in catalog or target in used:
   raise ValueError(a['slug'])
  used.add(target)
 neighbors = []
 for position, label, direction in [(i-1,'上一篇','prev'),(i+1,'下一篇','next')]:
  if 0 <= position < len(sequence):
   other = sequence[position]
   used.add(other['slug'])
   neighbors.append(f'<a rel="{direction}" href="/news/{other["slug"]}/"><small>{label}</small>{e(other["title"])}</a>')
 related = []
 for slug in a['related']:
  if slug in used or slug not in catalog:
   raise ValueError(f'{a["slug"]}: invalid related link {slug}')
  used.add(slug)
  related.append(f'<li><a href="/news/{slug}/">{e(catalog[slug]["title"])}</a></li>')
 return '<nav class="story-nav" aria-label="文章翻页">'+''.join(neighbors)+'</nav><section class="related"><h2>相关阅读</h2><ul>'+''.join(related)+'</ul></section><a href="/news/">查看全部蓝天资讯</a></article>'

def cover_alt(a):
 return a.get('cover_alt') or credits[a['original']]['caption']

for a in articles:
 c=credits[a['image']]
 src=''.join(f'<li><a href="{e(u)}" target="_blank" rel="noopener">{e(t)}</a></li>' for t,u in a['sources'])
 body=f'<article class="article"><nav aria-label="面包屑"><a href="/">首页</a> / <a href="/news/">蓝天资讯</a></nav><h1>{a["title"]}</h1><p class="meta">{a["category"]} · 发布于 {a["date"]} · China BSR 编辑整理</p><p class="lead">{a["description"]}</p><figure><picture class="archive-photo"><img src="/{a["image"]}" alt="{e(c["caption"])}"></picture><figcaption>{e(c["caption"])}。摄影／来源：<a href="{e(c["source"])}">{e(c["author"])}</a> · {e(c["license"])}</figcaption></figure>'
 body+=''.join(f'<section><h2>{h}</h2><p>{paragraph(a,p)}</p></section>' for h,p in a['sections'])
 body+=f'<section class="sources"><h2>参考资料</h2><ul>{src}</ul><p>中国蓝天视界（China BSR · chinabsr.org）是独立的公益科普信息平台。本频道为非官方账号，仅用于公益介绍与信息分享。</p></section>' + article_footer(a, articles)
 path='/news/'+a['slug']+'/'
 ld={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['description'],'datePublished':a['date'],'dateModified':a['date'],'image':['https://chinabsr.org/'+a['image']],'author':{'@type':'Organization','name':'China BSR 编辑整理'},'publisher':{'@type':'Organization','name':'中国蓝天视界','url':'https://chinabsr.org/'},'mainEntityOfPage':'https://chinabsr.org'+path}
 write('news/'+a['slug']+'/index.html',page(a['title'],a['description'],path,body,ld))


def news_cards(items):
 out = []
 for a in items:
  photo = f'<img loading="lazy" src="/{a["cover"]}" alt="{e(cover_alt(a))}">' if a.get('cover') else ''
  out.append(f'<a class="card" href="/news/{a["slug"]}/">{photo}<div><span>新闻动态</span> · <time>{a["when"]}</time><h2>{e(a["title"])}</h2><p>{e(a["description"])}</p></div></a>')
 return '<div class="cards news-list">' + ''.join(out) + '</div>'

def photo_feature(a):
 return f'<a class="card photo-feature" href="/news/{a["slug"]}/"><img src="/{a["cover"]}" alt="{e(cover_alt(a))}"><div><span>新闻动态</span> · 新闻回顾 · <time>{a["when"]}</time><h2>{e(a["title"])}</h2></div></a>'

featured = next((a for a in news if a.get('original')), None)
feature = photo_feature(featured) if featured else ''
for a in news:
 path = '/news/'+a['slug']+'/'
 url = 'https://chinabsr.org'+path
 label = '新闻回顾' if a['when'][:4] < a['date'][:4] else '新闻动态'
 body = f'<article class="article"><nav aria-label="面包屑"><a href="/">首页</a> / <a href="/news/">蓝天资讯</a></nav><h1>{e(a["title"])}</h1><p class="meta">{label} · 中国蓝天视界整理于 {a["date"]}</p><p class="lead">{paragraph(a,a["description"])}</p>'
 ld = {'@context':'https://schema.org','@type':'NewsArticle','headline':a['title'],'description':a['description'],'datePublished':a['date'],'mainEntityOfPage':url,'publisher':{'@type':'Organization','name':'中国蓝天视界','url':'https://chinabsr.org/'},'citation':[u for _,u in a['sources']]}
 if a.get('cover_alt'):
  ld['image'] = 'https://chinabsr.org/'+a['cover']
  body += f'<figure><img src="/{a["cover"]}" alt="{e(cover_alt(a))}"><figcaption>资讯封面 · 中国蓝天视界制图</figcaption></figure>'
 elif a.get('cover'):
  c = credits[a['original']]
  ld['image'] = 'https://chinabsr.org/'+a['cover']
  body += f'<figure><img src="/{a["cover"]}" alt="阿德亚曼震区的中国蓝天和伊朗搜救人员"><figcaption>阿德亚曼震区的中国蓝天和伊朗搜救人员。摄影／<a href="{e(c["source"])}">{e(c["author"])}</a> · <a href="{c["license_url"]}">{c["license"]}</a>，本站添加左上角标识。</figcaption></figure>'
 body += ''.join(f'<p>{paragraph(a,p)}</p>' for p in a['paragraphs'])
 body += '<section class="sources"><h2>报道来源</h2><ul>'+''.join(f'<li>{e(t)}</li>' for t,_ in a['sources'])+'</ul></section>'+article_footer(a, news)
 result = page(a['title'],a['description'],path,body,ld)
 if 'image' in ld:
  result = result.replace('</head>',f'<meta property="og:image" content="{ld["image"]}"></head>')
 write('news/'+a['slug']+'/index.html',result)

filters='<div class="filters" hidden>'+''.join(f'<button aria-pressed="{str(i==0).lower()}" data-category="{t}">{t}</button>' for i,t in enumerate(['全部','新闻动态','认识蓝天','救援纪实','训练与装备','公益与公众']))+'</div>'
body='<h1>蓝天资讯</h1><p class="lead">认识中国蓝天救援，了解救援故事、专业训练与公益精神。</p>'+filters+feature+news_cards([a for a in news if a is not featured])+cards(articles)
body+='''<script>const filters=document.querySelector('.filters');filters.hidden=false;filters.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;filters.querySelectorAll('button').forEach(x=>x.setAttribute('aria-pressed',String(x===b)));document.querySelectorAll('.card').forEach(x=>x.hidden=b.dataset.category!=='全部'&&x.querySelector('span').textContent!==b.dataset.category)});</script>'''
write('news/index.html',page('蓝天资讯','中国蓝天救援发展、故事、训练与公益科普文章。','/news/',body))
write('about/index.html',page('关于本站','认识China BSR独立公益科普信息平台。','/about/','''<article class="article"><h1>关于中国蓝天视界</h1><p>中国蓝天视界（China BSR · chinabsr.org）是一个独立的公益科普信息平台，致力于向公众介绍蓝天救援队（Blue Sky Rescue）的发展、故事与救援精神，让更多人了解民间救援力量的重要价值。</p><p>本频道为非官方账号，仅用于公益介绍与信息分享。</p><h2>资料与图片</h2><p>文章根据公开资料编辑整理，文末提供参考链接，配图注明资料背景和来源。地方队伍的资料与数据以对应来源和时间为准。</p><h2>反馈与纠错</h2><p>如发现内容或图片署名有误，可以通过 <a target="_blank" rel="noopener" href="https://www.youtube.com/@Chinabsr">YouTube 频道</a>反馈，或在 <a href="https://github.com/alititi-jackie/chinabsr-site/issues">GitHub Issues</a>提供页面网址、问题说明和依据。</p></article>'''))
home=(R/'templates/home.html').read_text()
home=re.sub(r'<header.*?</header>',header_for('/'),home,count=1,flags=re.S)
home=re.sub(r"const share = document.getElementById\('share'\);.*?const slides =", "const slides =", home, count=1, flags=re.S)
home=home.replace('</head>', '<link rel="stylesheet" href="/assets/navigation.css"><script src="/assets/navigation.js" defer></script></head>')
home=home.replace('</head>' ,'<link rel="stylesheet" href="/assets/site.css"></head>')
# Prevent the home stylesheet from changing the slideshow layout.
latest = '<ul class="latest-news">'+''.join(f'<li><time>{a["when"]}</time><a href="/news/{a["slug"]}/">{e(a["title"])}</a></li>' for a in news[:3])+'</ul>'
home=home.replace('<footer>','<section class="wrap home-news"><h2>新闻动态</h2>'+feature+latest+'<h2>蓝天资讯</h2>'+cards(articles[:6])+'<p><a href="/news/">查看全部资讯 →</a></p></section><footer>')
write('index.html',home)
paths=['/','/news/','/about/']+['/news/'+a['slug']+'/' for a in news+articles]
write('sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+escape('https://chinabsr.org'+p)+'</loc><lastmod>2026-11-19</lastmod></url>' for p in paths)+'</urlset>')
write('robots.txt','User-agent: *\nAllow: /\nSitemap: https://chinabsr.org/sitemap.xml\n')
print('Generated',len(articles),'articles and shared pages')
