// Threads 자체 예약 스크립트 (2026-11-19 검증)
// 사용법: 내장 브라우저에서 https://www.threads.com/@shufuro_acos 를 새로 열고(글마다 페이지 새로 고침 권장),
// 아래 전체를 javascript_tool 로 실행한다. 맨 아래 __S(...) 호출의 인자만 바꾼다.
//   TEXT: 본문(줄바꿈 \n, 마지막 줄에 #28卒 또는 #就活 토픽 1개)
//   DAY : 달력의 aria-label 형식 "2026년 11월 25일" (한국어 UI 기준)
//   HH, MM: "12","15" / "21","00"
// 반환값이 "OK ...게시 예정 | dialogs 0" 이면 성공. 그 외(DIALOG OPEN / TEXT MISMATCH / NO PICKER)는 페이지를 새로 고치고 다시 시도.
// 주의: 작성창이 열린 채로 다음 글을 쓰면 이미 예약된 글의 편집 창에 붙어 들어갈 수 있다 → 그때는 저장하지 말고 force 새로 고침.
// 확인: 새로운 스레드 → 「임시 저장본」 목록에 "…에 게시 예정"으로 보이면 예약 완료.
window.__S=async(TEXT,DAY,HH,MM)=>{const sl=ms=>new Promise(r=>setTimeout(r,ms));
const waitFor=async(fn,t=8000)=>{const s=Date.now(); while(Date.now()-s<t){const v=fn(); if(v) return v; await sl(250);} return null;};
if(document.querySelectorAll('[role="dialog"]').length) return 'DIALOG OPEN, STOP';
const b=[...document.querySelectorAll('[role="button"]')].find(e=>(e.getAttribute('aria-label')||e.innerText||'').includes('새로운 스레드'));
(b.closest('[role="button"]')||b).click();
const d=await waitFor(()=>[...document.querySelectorAll('[role="dialog"]')].find(d=>d.innerText.includes('새로운 스레드') && d.querySelector('[contenteditable="true"]')));
const ed=d.querySelector('[contenteditable="true"]');
if(ed.innerText.trim().length>0) return 'EDITOR NOT EMPTY';
ed.focus(); const dt=new DataTransfer(); dt.setData('text/plain', TEXT);
ed.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true})); await sl(900);
if(ed.innerText.replace(/\s/g,'')!==TEXT.replace(/\s/g,'')) return 'TEXT MISMATCH';
[...d.querySelectorAll('[role="button"],button')].find(x=>(x.getAttribute('aria-label')||'')==='더 보기').click();
const item=await waitFor(()=>[...document.querySelectorAll('[role="menu"] [role="menuitem"]')].find(i=>i.innerText.includes('예약')));
item.click();
const m=await waitFor(()=>{const mm=document.querySelector('[role="menu"]'); return mm && mm.querySelector('input[placeholder="hh"]') ? mm : null;});
if(!m) return 'NO PICKER';
await sl(500);
const days=[...m.querySelectorAll('*')].filter(e=>(e.getAttribute('aria-label')||'').includes(DAY));
const dEl=days.length? days[days.length-1] : [...m.querySelectorAll('*')].reverse().find(e=>e.innerText&&e.innerText.startsWith(DAY));
(dEl.closest('[role="button"],[role="gridcell"],button')||dEl).click(); await sl(500);
const setv=(el,v)=>{const s=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set; el.focus(); s.call(el,v); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); el.blur();};
for(const i of m.querySelectorAll('input')){ setv(i, i.placeholder==='hh'?HH:MM); await sl(150);}
const dones=[...m.querySelectorAll('[role="button"],button')].filter(x=>x.innerText.trim()==='완료'); dones[dones.length-1].click(); await sl(1500);
const head=d.innerText.split('\n')[2];
const btn=[...d.querySelectorAll('[role="button"],button')].find(x=>x.innerText.trim()==='예약');
if(!btn) return 'NO BTN '+head;
btn.click(); await sl(3000); return 'OK '+head+' | dialogs '+document.querySelectorAll('[role="dialog"]').length;};
// 예: await __S("本文\n#28卒","2026년 11월 25일","12","15")
