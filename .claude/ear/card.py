# «بطاقة الصوت»: وصف مقروء لأي ملف صوت أو فيديو — الكلام، السرعة، الوقفات، علوّ الصوت، طبقة الصوت، الإيقاع.
# الاستعمال: python3 card.py audio [--no-speech]  → يطبع البطاقة ويكتب audio.card.json
import sys,json,subprocess,numpy as np
def load(path,sr=22050):
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','1','-ar',str(sr),'-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,dtype=np.float32).copy(),sr
def card(path,speech=True,model='large-v3-turbo'):
    import librosa,parselmouth
    x,sr=load(path); dur=len(x)/sr; c={'الملف':path.split('/')[-1],'المدة_ث':round(dur,2)}
    hop=int(sr*0.05); rms=np.array([np.sqrt(np.mean(x[i:i+hop]**2)+1e-12) for i in range(0,len(x)-hop,hop)]); db=20*np.log10(rms+1e-9); t=np.arange(len(db))*0.05
    loud=db>(np.percentile(db,95)-30); c['متوسط_العلو_ديسيبل']=round(float(np.mean(db[loud])),1); c['المدى_الديناميكي_ديسيبل']=round(float(np.percentile(db[loud],95)-np.percentile(db[loud],10)),1)
    # الوقفات: مقاطع هادئة 0.35 ثانية فأكثر
    q=~loud; gaps=[]; i=0
    while i<len(q):
        if q[i]:
            j=i
            while j<len(q) and q[j]: j+=1
            if (j-i)*0.05>=0.35 and t[i]>0.2 and t[min(j,len(t)-1)]<dur-0.2: gaps.append([round(float(t[i]),2),round((j-i)*0.05,2)])
            i=j
        else: i+=1
    c['الوقفات']=gaps; c['عدد_الوقفات']=len(gaps)
    # أعلى خمس لحظات (ضربات)
    sm=np.convolve(db,np.ones(4)/4,'same'); pk=[]
    for k in np.argsort(-sm):
        if all(abs(t[k]-p)>2.0 for p in pk): pk.append(float(t[k]))
        if len(pk)==5: break
    c['أعلى_اللحظات_ث']=sorted(round(p,1) for p in pk)
    # طبقة الصوت
    f0=parselmouth.Sound(x.astype(np.float64),sr).to_pitch(time_step=0.02,pitch_floor=70,pitch_ceiling=400).selected_array['frequency']; f0=f0[f0>0]
    if len(f0)>20: c['طبقة_الصوت_هرتز']={'الوسيط':round(float(np.median(f0))),'من':round(float(np.percentile(f0,5))),'إلى':round(float(np.percentile(f0,95)))}
    # الإيقاع الموسيقي
    try:
        tempo,beats=librosa.beat.beat_track(y=x,sr=sr); c['الإيقاع_نبضة_بالدقيقة']=round(float(np.atleast_1d(tempo)[0])); c['عدد_النبضات']=int(len(beats))
    except Exception as e: c['الإيقاع_نبضة_بالدقيقة']=None
    if speech:
        from hear import hear
        h=hear(path,model); w=h['words']; c['النص']=h['text']; c['عدد_الكلمات']=len(w)
        if w:
            span=w[-1]['e']-w[0]['t']; c['سرعة_الكلام_كلمة_بالدقيقة']=round(60*len(w)/max(span,1)); c['أول_كلمة_عند_ث']=w[0]['t']
            c['كلمات_غير_واضحة']=[[x_['w'],x_['t'],x_['p']] for x_ in w if x_['p']<0.5][:25]
        c['_كلمات']=w
    return c
if __name__=='__main__':
    p=sys.argv[1]; c=card(p,speech='--no-speech' not in sys.argv)
    json.dump(c,open(p+'.card.json','w',encoding='utf-8'),ensure_ascii=False)
    for k,v in c.items():
        if k not in('_كلمات','النص','الوقفات'): print(k,':',v)
