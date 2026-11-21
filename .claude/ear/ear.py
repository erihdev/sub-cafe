# «أذن» آلية: تحويل الصوت إلى رموز صوتية (IPA) للتحقق من النطق لأني لا أسمع. نموذج wav2vec2 متعدد اللغات، محلي بلا تكلفة.
import sys,json,os,subprocess,numpy as np,torch
from transformers import Wav2Vec2ForCTC
from huggingface_hub import hf_hub_download
M='facebook/wav2vec2-xlsr-53-espeak-cv-ft'
_m=None
def model():
    global _m
    if _m is None:
        net=Wav2Vec2ForCTC.from_pretrained(M).eval(); v=json.load(open(hf_hub_download(M,'vocab.json'),encoding='utf-8')); _m=(net,{i:t for t,i in v.items()})
    return _m
def wav16(p,a=None,b=None):
    c=['ffmpeg','-v','error','-i',p]+(['-ss',str(a),'-to',str(b)] if a is not None else [])+['-ac','1','-ar','16000','-f','f32le','-']
    x=np.frombuffer(subprocess.run(c,capture_output=True,check=True).stdout,dtype=np.float32).copy(); return (x-x.mean())/(x.std()+1e-7)
def ipa(p,a=None,b=None):
    net,id2=model(); x=wav16(p,a,b)
    with torch.no_grad(): ids=net(torch.tensor(x)[None]).logits[0].argmax(-1).tolist()
    out=[];prev=None
    for i in ids:
        if i!=prev and id2[i] not in('<pad>','<s>','</s>','<unk>'): out.append(id2[i])
        prev=i
    return ' '.join(out)
if __name__=='__main__':
    for p in sys.argv[1:]: print(os.path.basename(p),'→',ipa(p))
