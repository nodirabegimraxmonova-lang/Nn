import json
U="/root/.claude/uploads/a77ab4b0-dc61-5474-9c74-168948401e70/"
vo={o["key"]:o for o in json.load(open("vo.json"))}
# key, lead (VO offset in scene), tail
SC=[("hook",.15,.45),("reveal",.25,.35),("silver",.2,.3),("green",.2,.35),("range",.25,.55),
    ("tech",.2,.4),("price",.35,1.0),("credit",.3,.5),("cta",.25,1.6)]
t=0; scenes={}
for k,lead,tail in SC:
    d=lead+vo[k]["dur"]+tail
    scenes[k]={"a":round(t,3),"b":round(t+d,3),"vo":round(t+lead,3)}
    t+=d
T=round(t,3)
def w(k,word,n=1):
    c=0
    for x in vo[k]["words"]:
        if x[0]==word:
            c+=1
            if c==n: return round(scenes[k]["vo"]+x[1],3)
    raise KeyError((k,word))
def we(k,word,n=1):
    c=0
    for x in vo[k]["words"]:
        if x[0]==word:
            c+=1
            if c==n: return round(scenes[k]["vo"]+x[1]+x[2],3)
S=scenes
E={
 "hookL1":w("hook","Hali"),"hookL2":w("hook","oq-qora"),"hookL3":w("hook","mashinada"),
 "slash":w("hook","yuribsizmi")+.05,
 "sweep":S["reveal"]["a"]+.25,"c16":w("reveal","Si"),"brand":w("reveal","Lipmotor"),
 "chip1":w("reveal","ikki"),"chip2":w("reveal","olti",2),"chip3":w("reveal","VIP"),
 "ring1":S["silver"]["a"]+.3,"silver2":w("silver","Quyoshda")-.12,
 "snap":S["green"]["a"],"mokriy":w("green","mokriy"),
 "count0":w("range","ikki"),"count1":we("range","kilometr"),
 "lidar":w("tech","laydar"),"dim":w("tech","Salonda")-.15,
 "f1":w("tech","muzlatgich"),"f2":w("tech","massaj"),"f3":w("tech","ambient"),"f4":w("tech","monitor"),
 "drop":w("price","to'rt"),
 "cr25":w("credit","Yigirma"),"cr8":w("credit","sakkiz"),"toggle":w("credit","Ellik"),"cr55":w("credit","besh",2),
 "ctaHours":w("cta","Har"),"ctaBtn":w("cta","Test-drayvga"),
}
SHOTS=[
 dict(id="hook",img="f9ad5d38-image.jpg",a=S["hook"]["a"],b=S["reveal"]["a"],kb=[1.18,1.04],x=[0,30],y=[40,0],grade="neon",tin="none"),
 dict(id="reveal",img="fecd0164-image.jpg",a=S["reveal"]["a"],b=S["silver"]["a"],kb=[1.0,1.13],x=[0,0],y=[60,20],grade="cool",tin="zoom"),
 dict(id="silverA",img="8f4b8765-image.jpg",a=S["silver"]["a"],b=E["silver2"],kb=[1.08,1.18],x=[40,-30],y=[0,-40],grade="warm",tin="whip"),
 dict(id="silverB",img="f87813c9-image.jpg",a=E["silver2"],b=S["green"]["a"],kb=[1.14,1.02],x=[0,0],y=[30,0],grade="golden",tin="light"),
 dict(id="green",img="4c52a59a-image.jpg",a=S["green"]["a"],b=S["range"]["a"],kb=[1.15,1.05],x=[60,0],y=[0,0],grade="rich",tin="snap"),
 dict(id="range",img="d113ea9d-image.jpg",a=S["range"]["a"],b=S["tech"]["a"],kb=[1.0,1.07],x=[0,0],y=[0,0],grade="day",tin="whip",fit=True),
 dict(id="tech",img="fc309d08-image.jpg",a=S["tech"]["a"],b=S["price"]["a"],kb=[1.0,1.16],x=[0,0],y=[0,90],grade="night",tin="zoom"),
 dict(id="price",img="44f73d98-image.jpg",a=S["price"]["a"],b=S["credit"]["a"],kb=[1.02,1.12],x=[0,-20],y=[0,0],grade="golden",tin="whip"),
 dict(id="credit",img="f87813c9-image.jpg",a=S["credit"]["a"],b=S["cta"]["a"],kb=[1.25,1.32],x=[0,0],y=[0,0],grade="dark",tin="zoom"),
 dict(id="cta",img="706559b3-image.jpg",a=S["cta"]["a"],b=T+1,kb=[1.0,1.1],x=[0,0],y=[0,-30],grade="neon",tin="whip"),
]
for s in SHOTS: s["src"]="file://"+U+s["img"]
# subtitles: merge spoken tokens into display tokens
MERGE={
 "reveal":[(["Lipmotor"],"Leapmotor"),(["Si","o'n","olti"],"C16."),(["ikki","ming","yigirma","oltinchi","yil"],"2026-yil")],
 "range":[(["ikki","yuz","sakson"],"280"),(["kilometr"],"km")],
 "tech":[(["laydar"],"LiDAR.")],
 "price":[(["to'rt","yuz","besh","million"],"405 mln")],
 "credit":[(["Yigirma","besh","foiz"],"25%"),(["sakkiz","million"],"8 mln."),(["Ellik","foiz"],"50%"),(["besh","yarim","million"],"5,5 mln")],
 "cta":[(["o'ndan"],"10:00 dan"),(["yigirmagacha"],"20:00 gacha.")],
}
SUBS=[]
for k,_,_ in SC:
    ws=vo[k]["words"]; i=0; toks=[]
    rules=MERGE.get(k,[])
    while i<len(ws):
        for pat,rep in rules:
            if [x[0] for x in ws[i:i+len(pat)]]==pat:
                a=ws[i][1]; e=ws[i+len(pat)-1][1]+ws[i+len(pat)-1][2]
                toks.append([rep,a,e]); i+=len(pat); break
        else:
            toks.append([ws[i][0],ws[i][1],ws[i][1]+ws[i][2]]); i+=1
    base=S[k]["vo"]; chunk=[]
    for j,(tx,a,e) in enumerate(toks):
        if chunk and (len(chunk)>=3 or a-chunk[-1][2]>.3):
            SUBS.append(chunk); chunk=[]
        chunk.append([tx,round(base+a,3),round(base+e,3)])
    if chunk: SUBS.append(chunk)
HIDE_SUBS=[[S["hook"]["a"],S["hook"]["b"]],[S["price"]["a"],S["price"]["b"]],[S["range"]["a"],S["range"]["b"]],[S["cta"]["a"]+2.0,T+1]]
json.dump({"T":T,"S":S,"E":E,"SHOTS":SHOTS,"SUBS":SUBS,"HIDE":HIDE_SUBS},open("timeline.json","w"),ensure_ascii=False,indent=1)
print("total",T); print(json.dumps(S)); print(E)
