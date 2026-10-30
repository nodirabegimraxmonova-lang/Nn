import numpy as np, json, subprocess, wave
SR=48000; rng=np.random.default_rng(7)
TL=json.load(open("timeline.json")); S=TL["S"]; E=TL["E"]; T=TL["T"]
N=int((T+0.5)*SR)
def z(n): return np.zeros(n)
def env_exp(n,tau): return np.exp(-np.arange(n)/(tau*SR))
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); y=np.empty_like(x); s=0.
    for i in range(len(x)): s=(1-a)*x[i]+a*s; y[i]=s
    return y
def lpv(x,fcs): # time-varying one-pole
    y=np.empty_like(x); s=0.
    a=np.exp(-2*np.pi*np.asarray(fcs)/SR)
    for i in range(len(x)): s=(1-a[i])*x[i]+a[i]*s; y[i]=s
    return y
def hp(x,fc): return x-lp(x,fc)
def bp(x,lo,hi): return lp(hp(x,lo),hi)
def norm(x,peak=1.0): m=np.max(np.abs(x))+1e-9; return x/m*peak
def db(d): return 10**(d/20)
def place(buf,sig,t,gain=1.0,pan=0.0):
    i=int(t*SR); 
    if i>=buf.shape[1] or i+len(sig)<=0: return
    s=sig if sig.ndim==2 else np.vstack([sig*np.sqrt(.5*(1-pan)), sig*np.sqrt(.5*(1+pan))])*np.sqrt(2)
    a=max(0,i); b=min(buf.shape[1],i+s.shape[1]); buf[:,a:b]+=gain*s[:,a-i:b-i]
def reverb(x,dur=1.2,mix=.25):
    n=int(dur*SR); ir=rng.standard_normal(n)*env_exp(n,dur/5); ir=lp(ir,4000); ir/=np.sqrt(np.sum(ir**2))
    y=np.concatenate([x,z(n)]); w=np.convolve(x,ir)[:len(y)]; w=np.pad(w,(0,len(y)-len(w)))
    return y*(1-mix)+w*mix*0.6
# ---------- SFX ----------
def whoosh(d=.6,lo=300,hi=4000,peak=.5):
    n=int(d*SR); x=rng.standard_normal(n); u=np.linspace(0,1,n)
    e=np.sin(np.pi*u**0.8)**2
    fc=lo+(hi-lo)*np.sin(np.pi*u)**1.5
    y=lpv(hp(x,lo*.6),fc)*e
    y=norm(y,peak); pan=np.linspace(-.7,.7,n)
    return np.vstack([y*np.sqrt(.5*(1-pan)),y*np.sqrt(.5*(1+pan))])*np.sqrt(2)
def riser(d=1.6):
    n=int(d*SR); u=np.linspace(0,1,n); x=rng.standard_normal(n)
    noise=lpv(hp(x,400),300+7000*u**2)*u**2.2
    f=200+1000*u**2; ph=2*np.pi*np.cumsum(f)/SR
    tone=(np.sin(ph)+.4*np.sin(2.01*ph))*u**2.5*.35
    return norm(noise+tone,.6)
def impact(peak=.9,tail=1.6):
    n=int(tail*SR); t=np.arange(n)/SR
    f=60*np.exp(-t*3)+38; body=np.sin(2*np.pi*np.cumsum(f)/SR)*env_exp(n,.45)
    nz=lp(rng.standard_normal(n),900)*env_exp(n,.08)*.8
    click=hp(rng.standard_normal(n),3000)*env_exp(n,.006)*.5
    y=np.tanh(1.6*(body+nz+click))
    return norm(reverb(y,1.4,.3),peak)
def thump(peak=.6):
    n=int(.5*SR); t=np.arange(n)/SR
    f=110*np.exp(-t*18)+48; y=np.sin(2*np.pi*np.cumsum(f)/SR)*env_exp(n,.12)
    y+=lp(rng.standard_normal(n),1500)*env_exp(n,.02)*.4
    return norm(np.tanh(1.5*y),peak)
def bassdrop(d=2.2):
    n=int(d*SR); t=np.arange(n)/SR
    f=34+90*np.exp(-t*2.2); ph=2*np.pi*np.cumsum(f)/SR
    y=np.sin(ph)+.25*np.sin(2*ph)
    y=np.tanh(2.2*y)*env_exp(n,.9)*np.minimum(1,t/0.004)
    return norm(lp(y,500),1.0)
def snap():
    n=int(.25*SR); x=rng.standard_normal(n)
    y=bp(x,1800,5200)*env_exp(n,.012)*1.0+bp(x,600,1400)*env_exp(n,.03)*.4
    return norm(reverb(y,.5,.2),.8)
def tick(f=2400,peak=.25):
    n=int(.04*SR); t=np.arange(n)/SR; return norm(np.sin(2*np.pi*f*t)*env_exp(n,.008),peak)
def beep(f1=1320,f2=1760,peak=.28):
    out=[]
    for f in (f1,f2):
        n=int(.065*SR); t=np.arange(n)/SR
        sq=np.tanh(3*np.sin(2*np.pi*f*t))*np.minimum(1,t/.003)*np.minimum(1,(n/SR-t)/.01)
        out.append(lp(sq,6000))
    return norm(np.concatenate(out),peak)
def pop(peak=.35):
    n=int(.12*SR); t=np.arange(n)/SR; f=500+700*(1-np.exp(-t*60))
    return norm(np.sin(2*np.pi*np.cumsum(f)/SR)*env_exp(n,.04),peak)
def shimmer(d=1.0,peak=.18):
    n=int(d*SR); t=np.arange(n)/SR; y=z(n)
    for k in range(14):
        f=rng.uniform(3000,9000); st=rng.uniform(0,d*.5); i=int(st*SR)
        m=n-i; y[i:]+=np.sin(2*np.pi*f*t[:m])*env_exp(m,rng.uniform(.05,.25))*rng.uniform(.3,1)
    return norm(reverb(y,1.0,.4),peak)
def tap(): 
    n=int(.06*SR); return norm(bp(rng.standard_normal(n),800,3000)*env_exp(n,.006),.35)

sfx=np.zeros((2,N))
# hook
place(sfx,thump(.55),0.02)
place(sfx,whoosh(.45,500,5000,.30),E["hookL1"]-.15)
place(sfx,thump(.7),E["hookL2"])
place(sfx,whoosh(.4,600,6000,.32),E["hookL3"]-.12)
place(sfx,whoosh(.25,1500,9000,.35),E["slash"]-.05)
r=riser(1.7); place(sfx,r,S["reveal"]["a"]-1.7,.75)
place(sfx,impact(.95),S["reveal"]["a"])
place(sfx,shimmer(1.2,.22),E["sweep"])
place(sfx,whoosh(.5,200,2500,.35),E["c16"]-.2); place(sfx,thump(.55),E["c16"]+.15)
for k in ("chip1","chip2","chip3"): place(sfx,pop(.32),E[k])
# transitions
for sh in TL["SHOTS"][1:]:
    if sh["tin"] in ("whip","zoom"): place(sfx,whoosh(.55,250,4500,.42),sh["a"]-.3)
    if sh["tin"]=="light": place(sfx,shimmer(1.3,.25),sh["a"]-.2)
place(sfx,snap(),E["snap"]-.01)
place(sfx,beep(1568,2093,.22),E["ring1"]); place(sfx,beep(1568,2093,.22),E["lidar"])
for i in range(5): place(sfx,shimmer(.6,.10),E["silver2"]+.35+i*.42)
place(sfx,tick(1800,.3),E["mokriy"]+.1)
# range counter ticks: pc=eo3(p) crosses (i+.5)/10
d=E["count1"]-E["count0"]
for i in range(10):
    v=(i+.5)/10; p=1-(1-v)**(1/3); place(sfx,tick(2000+i*120,.22),E["count0"]+p*d)
place(sfx,beep(2093,2637,.25),E["count1"]+.05)
place(sfx,whoosh(.7,150,1500,.3),E["dim"]-.15)
for k in ("f1","f2","f3","f4"): place(sfx,beep(1320,1760,.24),E[k])
# price
place(sfx,bassdrop(),E["drop"],1.0); place(sfx,impact(.7),E["drop"])
place(sfx,pop(.3),E["drop"]+.55)
# credit
place(sfx,beep(1046,1318,.2),E["cr8"]-.2)
place(sfx,tap(),E["toggle"]-.1); place(sfx,beep(1568,2093,.24),E["toggle"])
for i in range(6): place(sfx,tick(2600,.12),E["toggle"]+.1+i*.12)
# cta
place(sfx,pop(.3),E["ctaHours"]); place(sfx,thump(.55),E["ctaBtn"]); place(sfx,shimmer(1.2,.2),E["ctaBtn"])

# ---------- MUSIC ----------
BPM=100; B=60/BPM
mus=np.zeros((2,N)); tt=np.arange(N)/SR
CH=[(55.0,[220,261.63,329.63]),(43.65,[174.61,220,261.63]),(65.41,[196,261.63,329.63]),(49.0,[196,246.94,293.66])]
start=S["reveal"]["a"]; bar=4*B
def chord_at(t): return CH[int(max(0,t)//(2*bar))%4] if t>=0 else CH[0]
# pad (whole length)
pad=np.zeros(N)
for ci in range(int(N/SR/(2*bar))+2):
    a=int(ci*2*bar*SR); b=min(N,int((ci+1)*2*bar*SR)+int(.3*SR))
    if a>=N: break
    _,notes=CH[ci%4]; n=b-a; t=np.arange(n)/SR; seg=z(n)
    for f in notes:
        for dt in (-.12,.12):
            ph=f*(1+dt/100)*t; seg+=2*(ph%1)-1
    e=np.minimum(1,t/.6)*np.minimum(1,(n/SR-t)/.4)
    pad[a:b]+=seg*e
pad=lp(lp(pad,900),1400); pad=norm(pad,.22)
# sub bass pumping on beats after start
sub=z(N)
for bi in range(int((T-start)/B)+1):
    t0=start+bi*B; i=int(t0*SR); n=int(B*SR)
    if i+n>N: n=N-i
    if n<=0: break
    root,_=chord_at(t0-start); t=np.arange(n)/SR
    pump=np.minimum(1,t/.12)
    sub[i:i+n]+=np.sin(2*np.pi*root*2*t)*pump*.6+np.sin(2*np.pi*root*t)*pump*.4
sub=norm(lp(sub,300),.32)
# drums
drm=np.zeros((2,N))
k=thump(.55)
hh=lambda: norm(hp(rng.standard_normal(int(.05*SR)),7000)*env_exp(int(.05*SR),.012),.10)
cp=lambda: norm(reverb(bp(rng.standard_normal(int(.15*SR)),900,4000)*env_exp(int(.15*SR),.03),.4,.3),.16)
nb=int((T-start)/B)
for bi in range(nb):
    t0=start+bi*B
    place(drm,k,t0); place(drm,hh(),t0+B/2,1,.3)
    if bi%2==1: place(drm,cp(),t0,1,-.2)
    if bi%4==3: place(drm,hh(),t0+B*.75,.7,.4)
# mix music, intro only pad, price dropout, outro fade
musm=np.vstack([pad,pad])+np.vstack([sub,sub])+drm
gate=np.ones(N)
gate[tt<start]=0  # drums/sub start at reveal
introPad=np.vstack([pad,pad])*(tt<start)
musm=musm*gate+introPad
dip=np.ones(N); d0,d1=E["drop"]-.55,E["drop"]
dip[(tt>d0)&(tt<d1)]=0.05; dip[(tt>=d1)&(tt<d1+.08)]=np.linspace(.05,1,((tt>=d1)&(tt<d1+.08)).sum())
fo=np.clip((T-tt)/1.4,0,1); musm*=dip*fo

# ---------- VO ----------
vo=np.zeros(N)
for o in json.load(open("vo.json")):
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",f"{o['key']}.mp3","-f","f32le","-ac","1","-ar",str(SR),"-"])
    a=np.frombuffer(raw,np.float32).astype(float); i=int(S[o["key"]]["vo"]*SR); vo[i:i+len(a)]+=a[:N-i]
# light VO processing: highpass + gentle presence + compression-ish
vo=hp(vo,90); vo=np.tanh(vo*2.2)/np.tanh(2.2); vo=norm(vo,.9)
# ducking envelope
ve=np.abs(vo); ve=lp(ve,8); ve=ve/(ve.max()+1e-9)
duck=1-0.55*np.clip(ve*6,0,1); duck=lp(duck,4)
def wr(name,x):
    x=np.clip(x,-1,1); x=x if x.ndim==2 else np.vstack([x,x])
    with wave.open(name,"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x.T*32767).astype(np.int16).tobytes())
music=musm*duck*db(-3)
sfxo=sfx*db(-4)
wr("stem_vo.wav",vo); wr("stem_music.wav",norm(music,.7)*1); wr("stem_sfx.wav",norm(sfxo,.9))
full=np.vstack([vo,vo])*db(0)+music*db(-2)+sfxo*db(-3)
wr("mix_full.wav",norm(full,.95))
nomus=np.vstack([vo,vo])+sfxo*db(-3)
wr("mix_no_music.wav",norm(nomus,.95))
print("ok",T)
