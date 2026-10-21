// يحفظ واجهة التطبيق على الجوال، ويعرض الإشعارات حتى والتطبيق مغلق
const C='sub-v21';
const API='https://script.google.com/macros/s/AKfycbyLF3MAe7sq1LGwAxI1lY5V63UiTcRdT2fR9Y8SJiLPDJ-jz7c8Yyw8yud5NZxa8H00/exec';
const FILES=['./','index.html','brand.js','manifest.webmanifest','icon-192.png','icon-512.png','icon-180.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting();});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C&&x!=='sub-pin').map(x=>caches.delete(x)))));self.clients.claim();});
self.addEventListener('fetch',e=>{
  const u=new URL(e.request.url);
  if(e.request.method!=='GET'||u.origin!==location.origin)return;
  e.respondWith(fetch(e.request,{cache:'no-cache'}).then(r=>{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp));return r;}).catch(()=>caches.match(e.request).then(r=>r||caches.match('index.html'))));
});
async function noticeText(){
  try{
    const c=await caches.open('sub-pin');const r=await c.match('./__pin');if(!r)return {text:'',url:''};
    const pin=await r.text();
    const j=await (await fetch(API,{method:'POST',body:JSON.stringify({op:'inbox',pin})})).json();
    return {text:(j&&j.ok&&j.text)||'',url:(j&&j.url)||''};
  }catch(e){return {text:'',url:''};}
}
self.addEventListener('push',e=>{
  e.waitUntil(noticeText().then(t=>self.registration.showNotification('صُب',{
    body:t.text||'فيه تحديث جديد من شركائك',icon:'icon-192.png',badge:'icon-192.png',tag:'sub',renotify:true,lang:'ar',dir:'rtl',data:{url:t.url||''}})));
});
self.addEventListener('notificationclick',e=>{
  e.notification.close();const u=new URL('./'+((e.notification.data&&e.notification.data.url)||''),self.registration.scope).href;
  e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(ws=>{
    for(const w of ws){if('focus' in w){if('navigate' in w&&u.includes('#'))w.navigate(u);return w.focus();}}
    return self.clients.openWindow(u);
  }));
});
