import numpy as np, wave
SR=44100; DUR=101.5; N=int(SR*DUR)
rng=np.random.default_rng(7)
mix=np.zeros(N); sfx=np.zeros(N)
def mf(m): return 440*2**((m-69)/12)
def add(buf,t,sig):
    i=int(t*SR); j=min(N,i+len(sig))
    if i<N: buf[i:j]+=sig[:j-i]
def env(n,a,tau):
    t=np.arange(n)/SR; e=np.exp(-t/tau); ai=int(a*SR)
    if ai>0: e[:ai]*=np.linspace(0,1,ai)
    return e
BPM=104; B=60/BPM; BAR=4*B
# F  C  Dm  Bb  (midi roots oct 3)
prog=[(53,[0,4,7]),(48,[0,4,7]),(50,[0,3,7]),(46,[0,4,7])]
bounds=[6.4,15.6,21.6,40.2,48.0,57.6,67.6,75.6,82.4,93.2]
DRUM_ON=(6.35,93.2); BREAK=(15.6,21.5)
nbars=int(DUR/BAR)+1
for b in range(nbars):
    t0=b*BAR; root,iv=prog[b%4]
    # pad
    n=int(BAR*1.25*SR); tt=np.arange(n)/SR
    e=np.minimum(1,tt/0.35)*np.clip((BAR*1.25-tt)/0.5,0,1)
    for k in iv+[12]:
        f=mf(root+12+k)
        s=sum(np.sin(2*np.pi*f*d*tt+ph) for d,ph in [(1,0),(1.003,1.3),(0.997,2.1)])/3
        s+=0.18*np.sin(2*np.pi*2*f*tt)
        add(mix,t0,0.035*e*s)
    # pluck arpeggio 8ths
    pat=[0,7,12,16,12,7,16,19] if iv[1]==4 else [0,7,12,15,12,7,15,19]
    for k,st in enumerate(pat):
        f=mf(root+24+st); n=int(0.6*SR); tt=np.arange(n)/SR
        s=(np.sin(2*np.pi*f*tt)+0.35*np.sin(4*np.pi*f*tt)+0.12*np.sin(6*np.pi*f*tt))*env(n,0.004,0.22)
        vel=0.085 if k%2==0 else 0.06
        add(mix,t0+k*B/2,vel*s)
    # bass
    for off,ln in [(0,0.9),(1.5*B,0.5),(2*B,0.9),(3.5*B,0.4)]:
        t=t0+off
        if not(DRUM_ON[0]<=t<DRUM_ON[1]): continue
        f=mf(root-12+12); n=int(ln*SR); tt=np.arange(n)/SR
        s=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt))*env(n,0.006,0.3)
        add(mix,t,0.20*s)
# drums
nb=int(DUR/B)+1
for i in range(nb):
    t=i*B
    if not(DRUM_ON[0]<=t<DRUM_ON[1]): continue
    brk=BREAK[0]<=t<BREAK[1]
    if not brk or i%4==0:
        n=int(0.35*SR); tt=np.arange(n)/SR
        ph=2*np.pi*np.cumsum(45+80*np.exp(-tt/0.04))/SR
        add(mix,t,0.55*np.sin(ph)*env(n,0.001,0.12))
    if i%4 in(1,3) and not brk:
        n=int(0.25*SR); nz=rng.standard_normal(n); nz=np.diff(nz,prepend=0)
        tt=np.arange(n)/SR
        add(mix,t,0.10*nz*env(n,0.001,0.07)+0.08*np.sin(2*np.pi*190*tt)*env(n,0.001,0.05))
    for h in (0.5,):
        n=int(0.08*SR); nz=np.diff(rng.standard_normal(n),prepend=0)
        add(mix,t+h*B,(0.035 if not brk else 0.025)*nz*env(n,0.001,0.018))
# whooshes
def whoosh(tc,length=0.95,vol=0.22):
    n=int(length*SR); nz=rng.standard_normal(n+400); C=np.cumsum(nz)
    tt=np.arange(n)/length/SR
    k=(60-50*tt).astype(int)+2  # brighter as it goes
    idx=np.arange(n)+400
    y=(C[idx]-C[idx-k])/k
    e=np.sin(np.pi*np.clip(tt,0,1))**2
    e*= np.where(tt<0.65, tt/0.65, np.exp(-(tt-0.65)*9))
    add(sfx,tc-0.62*length,vol*y*e/np.max(np.abs(y)+1e-9))
for t in bounds: whoosh(t)
# taps / ui
def tick(t,f=1800,vol=0.10):
    n=int(0.05*SR); tt=np.arange(n)/SR
    add(sfx,t,vol*np.sin(2*np.pi*f*tt)*env(n,0.0005,0.01))
S4=21.6+0.15
for o in [3.6,5.4,6.1,6.8,8.9,12.3]: tick(S4+o)
for o in [8.9]: tick(S4+o+0.05,2400,0.06)
# typing
for k in range(25): tick(S4+9.6+k*0.06,3000+rng.integers(-300,300),0.035)
for k in range(5): tick(S4+11.3+k*0.1,3000,0.035)
# confirm ding
for f,d in [(mf(84),0),(mf(88),0.09),(mf(91),0.18)]:
    n=int(0.9*SR); tt=np.arange(n)/SR
    add(sfx,S4+13.2+d,0.07*(np.sin(2*np.pi*f*tt)+0.2*np.sin(4*np.pi*f*tt))*env(n,0.003,0.3))
# order pops in panel
S6=48.0+0.15
for o in [1.9,2.7]: tick(S6+o+0.25,1200,0.08)
# printer
S7=57.6+0.15
n=int(3.2*SR); tt=np.arange(n)/SR
buzz=np.sign(np.sin(2*np.pi*26/3.2*tt*8))*0.5+np.diff(rng.standard_normal(n),prepend=0)*0.6
am=0.5+0.5*np.sign(np.sin(2*np.pi*(26/3.2)*tt))
add(sfx,S7+1.0,0.05*buzz*am*np.minimum(1,tt/0.05)*np.clip((3.2-tt)/0.1,0,1))
# stamp thud
n=int(0.4*SR); tt=np.arange(n)/SR
add(sfx,S7+6.72,0.4*np.sin(2*np.pi*np.cumsum(60+60*np.exp(-tt/0.02))/SR)*env(n,0.001,0.08)+0.08*np.diff(rng.standard_normal(n),prepend=0)*env(n,0.001,0.02))
# price counter ticks
S10=82.4+0.15
for k in range(14): tick(S10+0.4+1.6*(1-(1-k/14)**0.5)*0.9,2200,0.04)
out=mix+sfx
# global fades
fi=int(0.8*SR); out[:fi]*=np.linspace(0,1,fi)
fo=int(3.0*SR); out[-fo:]*=np.linspace(1,0,fo)**1.5
out/=np.max(np.abs(out))/0.89
pcm=(out*32767).astype(np.int16)
st=np.repeat(pcm[:,None],2,axis=1)
with wave.open('music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('ok')
