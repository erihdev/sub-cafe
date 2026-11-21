# «الأذن الأقوى»: تعرّف على الكلام بنموذج ويسبر مع توقيت كل كلمة.
# الاستعمال: python3 hear.py audio [model=large-v3-turbo] [lang=ar]  → يكتب audio.hear.json
import sys,json,time,subprocess
import numpy as np
def load16k(path):
    # يفكّ أي ملف صوت أو فيديو إلى صوت أحادي 16 كيلوهرتز عبر ffmpeg
    raw=subprocess.run(['ffmpeg','-v','error','-i',path,'-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True).stdout
    return np.frombuffer(raw,dtype=np.float32)
from faster_whisper import WhisperModel
def hear(path,model='large-v3-turbo',lang='ar',prompt=None):
    m=WhisperModel(model,device='cpu',compute_type='int8',cpu_threads=2)
    t0=time.time(); segs,info=m.transcribe(load16k(path),language=lang,word_timestamps=True,beam_size=5,vad_filter=False,initial_prompt=prompt,condition_on_previous_text=True)
    out=[]; words=[]
    for s in segs:
        out.append({'t':round(s.start,2),'e':round(s.end,2),'text':s.text.strip()})
        for w in (s.words or []): words.append({'t':round(w.start,2),'e':round(w.end,2),'w':w.word.strip(),'p':round(w.probability,2)})
    return {'model':model,'secs':round(time.time()-t0,1),'dur':round(info.duration,2),'text':' '.join(x['text'] for x in out),'segs':out,'words':words}
if __name__=='__main__':
    p=sys.argv[1]; model=sys.argv[2] if len(sys.argv)>2 else 'large-v3-turbo'; lang=sys.argv[3] if len(sys.argv)>3 else 'ar'
    r=hear(p,model,lang); json.dump(r,open(p+'.hear.'+model.replace('/','_')+'.json','w',encoding='utf-8'),ensure_ascii=False)
    print(r['secs'],'s for',r['dur'],'s audio'); print(r['text'])
