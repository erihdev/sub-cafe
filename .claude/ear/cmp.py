# مقارنة تفريغ بنص مرجعي: نسبة الكلمات المختلفة وقائمة الاختلافات
import re,difflib,sys
def nd(s):
    s=re.sub('[ً-ْٰـ]','',s); s=re.sub('[إأآا]','ا',s); s=s.replace('ى','ي').replace('ة','ه').replace('ؤ','و').replace('ئ','ي')
    s=re.sub(r'\[[^\]]*\]',' ',s); s=re.sub('[^ء-ي ]',' ',s); return s.split()
def diff(ref,hyp):
    a,b=nd(ref),nd(hyp); sm=difflib.SequenceMatcher(None,a,b,autojunk=False); err=0; out=[]
    for tag,i1,i2,j1,j2 in sm.get_opcodes():
        if tag!='equal': err+=max(i2-i1,j2-j1); out.append((' '.join(a[i1:i2]) or '∅',' '.join(b[j1:j2]) or '∅'))
    return err,len(a),out
