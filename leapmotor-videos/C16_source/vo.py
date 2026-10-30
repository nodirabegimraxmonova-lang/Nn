import certifi, json, asyncio, sys, subprocess
certifi.where=lambda: "/root/.ccr/ca-bundle.crt"
import edge_tts
VOICE="uz-UZ-SardorNeural"
LINES=[
 ("hook","Hali ham hamma qatori oq-qora mashinada yuribsizmi?"),
 ("reveal","Tanishing: Lipmotor Si o'n olti. Yangi ikki ming yigirma oltinchi yil — olti o'rinli VIP krossover."),
 ("silver","Kumushrang: chang ham, chiziq ham bilinmaydi. Quyoshda esa hashamat bilan tovlanadi."),
 ("green","Yashil va mokriy asfalt ranglari ham bor."),
 ("range","Faqat tokda — ikki yuz sakson kilometr."),
 ("tech","Tomda laydar. Salonda haqiqiy muzlatgich, massaj, ambient podsvetka va orqa yo'lovchilar uchun monitor."),
 ("price","Narxi — to'rt yuz besh million so'm."),
 ("credit","Yigirma besh foiz to'lov bilan — oyiga atigi sakkiz million. Ellik foiz bilan — besh yarim million."),
 ("cta","Har kuni o'ndan yigirmagacha kutamiz. Test-drayvga hoziroq yoziling!"),
]
async def one(key,text):
    c=edge_tts.Communicate(text,VOICE,rate="+6%",boundary="WordBoundary")
    words=[]
    with open(f"{key}.mp3","wb") as f:
        async for ch in c.stream():
            if ch["type"]=="audio": f.write(ch["data"])
            elif ch["type"]=="WordBoundary":
                words.append([ch["text"],ch["offset"]/1e7,ch["duration"]/1e7])
    d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{key}.mp3"]))
    return {"key":key,"text":text,"dur":d,"words":words}
async def main():
    out=[await one(k,t) for k,t in LINES]
    json.dump(out,open("vo.json","w"),ensure_ascii=False,indent=1)
    for o in out: print(o["key"],round(o["dur"],2),len(o["words"]),o["words"][:3])
asyncio.run(main())
