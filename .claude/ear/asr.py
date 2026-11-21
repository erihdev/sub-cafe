# «أذن» ثانية: تفريغ الصوت إلى حروف عربية بنموذج عربي (غير نموذج الرموز الصوتية) للمقارنة
import sys,json,subprocess,numpy as np,torch
from transformers import Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M='jonatasgrosman/wav2vec2-large-xlsr-53-arabic'; net=Wav2Vec2ForCTC.from_pretrained(M).eval(); V=json.load(open(hf_hub_download(M,'vocab.json'),encoding='utf-8')); I={i:c for c,i in V.items()}
def txt(p,a=None,b=None):
    c=['ffmpeg','-v','error','-i',p]+(['-ss',str(a),'-to',str(b)] if a is not None else [])+['-ac','1','-ar','16000','-f','f32le','-']
    x=np.frombuffer(subprocess.run(c,capture_output=True,check=True).stdout,dtype=np.float32).copy(); x=(x-x.mean())/(x.std()+1e-7)
    with torch.no_grad(): ids=net(torch.tensor(x)[None]).logits[0].argmax(-1).tolist()
    o=[];pv=None
    for i in ids:
        if i!=pv and I[i] not in('<pad>','<s>','</s>','<unk>'): o.append(' ' if I[i]=='|' else I[i])
        pv=i
    return ''.join(o)
if __name__=='__main__':
    for a in sys.argv[1:]: print(a.split('/')[-1],'→',txt(a))
