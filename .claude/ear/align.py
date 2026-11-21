# مطابقة قسرية: ملف صوت جاهز (من موقع خارجي) + نصّه → توقيت كل كلمة. يكتب <out>.wav و<out>.wav.json بنفس صيغة tts2.py
# الاستعمال: align.py صوت.mp3 "النص" out.wav
import sys,json,re,subprocess,numpy as np,torch
from transformers import Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M='jonatasgrosman/wav2vec2-large-xlsr-53-arabic'
src,text,out=sys.argv[1:4]
net=Wav2Vec2ForCTC.from_pretrained(M).eval(); V=json.load(open(hf_hub_download(M,'vocab.json'),encoding='utf-8'))
x=np.frombuffer(subprocess.run(['ffmpeg','-v','error','-i',src,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout,dtype=np.float32).copy(); x=(x-x.mean())/(x.std()+1e-7)
with torch.no_grad(): lp=torch.log_softmax(net(torch.tensor(x)[None]).logits[0],-1).numpy()
T=lp.shape[0]; sec=len(x)/16000/T; blank=V.get('<pad>',0); bar=V.get('|')
words=[w for w in re.split(r'\s+',text.strip()) if re.sub(r'[^ء-ي]','',w)]
norm=lambda w: [c for c in re.sub(r'[ً-ْـ]','',w) if c in V]
toks=[];owner=[]
for i,w in enumerate(words):
    if i and bar is not None: toks.append(bar); owner.append(-1)
    for c in norm(w): toks.append(V[c]); owner.append(i)
# فيتربي على مسار CTC (فراغ بين كل رمزين)
ext=[blank]; eo=[-1]
for t,o in zip(toks,owner): ext+= [t,blank]; eo+=[o,-1]
N=len(ext); NEG=-1e9; D=np.full((T,N),NEG,dtype=np.float32); B=np.zeros((T,N),dtype=np.int8)
D[0,0]=lp[0,ext[0]]; D[0,1]=lp[0,ext[1]]
skip=np.array([i>1 and ext[i]!=blank and ext[i]!=ext[i-2] for i in range(N)]); E=np.array(ext)
for t in range(1,T):
    a=D[t-1]; b=np.concatenate(([NEG],a[:-1])); c=np.where(skip,np.concatenate(([NEG,NEG],a[:-2])),NEG)
    st3=np.stack([a,b,c]); k=st3.argmax(0); D[t]=st3[k,np.arange(N)]+lp[t,E]; B[t]=k
s=N-1 if D[T-1,N-1]>=D[T-1,N-2] else N-2; path=[0]*T
for t in range(T-1,-1,-1): path[t]=s; s-=int(B[t,s])
st={};en={}
for t,s in enumerate(path):
    o=eo[s]
    if o>=0: st.setdefault(o,t); en[o]=t
W=[{'t':round(st[i]*sec,3),'d':round((en[i]-st[i]+1)*sec,3),'w':w} for i,w in enumerate(words)]
lead=max(0,W[0]['t']-0.05); end=min(len(x)/16000,W[-1]['t']+W[-1]['d']+0.25)
subprocess.run(['ffmpeg','-v','error','-y','-ss','%.3f'%lead,'-t','%.3f'%(end-lead),'-i',src,'-ar','44100','-ac','1','-c:a','pcm_s16le',out],check=True)
for w in W: w['t']=round(w['t']-lead,3)
json.dump({'dur':round(end-lead,3),'words':W,'text':text},open(out+'.json','w',encoding='utf-8'),ensure_ascii=False)
print('dur',round(end-lead,3),'score/frame',round(float(D[T-1,path[-1]])/T,3)); print(' | '.join('%s@%.2f+%.2f'%(w['w'],w['t'],w['d']) for w in W))
