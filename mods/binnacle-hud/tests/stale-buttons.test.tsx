import { expect, mock, test } from 'claude-code/testing'
const deferred=()=>{let resolve!:()=>void;const promise=new Promise<void>(r=>resolve=r);return {promise,resolve}}
const pane={plugin:'binnacle-hud',component:'Pane',requestId:'binnacle-hud',surface:'terminal',viewport:{columns:160,rows:40,isFullscreen:true},props:{title:'Binnacle',isFocused:true,bodyColumns:46,placement:'dock',scroll:{offset:0,bodyRows:32},view:{}}} as const
async function start($:any,on:any,initial:any={}) {
 const clock=mock.clock(on)
 const cells:any=Object.fromEntries(Object.entries(initial).map(([k,value])=>[k,{value,version:1}]))
 const cell=(k:string)=>cells[k]??{value:undefined,version:0}
 let gate:any=null, changeGate:any=null, box=''; let denied=false; let copy:any={isCopied:true}
 const writes:any[]=[]
 on('command.register',()=>({value:undefined}));on('ui.open',()=>({value:{isPlaced:true}}));on('ui.focus',()=>({value:{}}))
 on('session.start',(_:any,e:any)=>({cwd:e.cwd}))
 on('state.get',(_:any,e:any)=>({value:{...cell(e.key)}}))
 on('state.set',async(_:any,e:any)=>{
  if(denied&&e.key==='log')return {deny:'injected keep failure'}
  if(gate&&gate.match(e)){const g=gate;gate=null;g.entered.resolve();await g.release.promise}
  const old=cell(e.key)
  const ok=e.ifVersion===undefined||e.ifVersion===old.version
  writes.push({key:e.key,value:e.value,ok})
  if(!ok)return {value:{isSet:false,version:old.version}}
  cells[e.key]={value:e.value,version:old.version+1};return {value:{isSet:true,version:old.version+1}}
 })
 on('prompt.edit',(_:any,e:any)=>{box=e.text.slice(0,e.start)+e.inputText+e.text.slice(e.end);return {text:box,cursor:box.length}})
 on('prompt.change',async(_:any,e:any)=>{if(changeGate&&changeGate.match(e)){const g=changeGate;changeGate=null;g.entered.resolve();await g.release.promise}return {text:e.text}});on('prompt.submit',(_:any,e:any)=>({text:e.text}));on('ui.copy',()=>({value:copy}))
 await $.session.start({cwd:'/',surface:'terminal',isInteractive:true})
 return {clock,cells,cell,writes,deny:()=>denied=true,refuseCopy:()=>copy={isCopied:false,reason:'no clipboard'},
 hold:(match:any)=>{const g={match,entered:deferred(),release:deferred()};gate=g;return g},
 holdChange:(match:any)=>{const g={match,entered:deferred(),release:deferred()};changeGate=g;return g},
 type:(text:string)=>$.prompt.edit({origin:{kind:'composer'},text:box,cursor:box.length,start:0,end:box.length,inputText:text}),
 change:(kind:string,text='')=>{box=text;return $.prompt.change({text,cursor:text.length,origin:{kind}})},
 submit:()=>$.prompt.submit({text:box,wait:false,origin:{kind:'composer'}}),
 press:async(key:string)=>{const ui=await $.ui.mount(pane);await ui.press({key:`k-${key}`});await clock.settle();await ui.unmount()}}
}
test('round2: dismissal drawn while failure append pending must preserve unseen equal-text failure',async($,on)=>{
 const s=await start($,on,{failed:['same thought']});s.deny()
 const first=await $.ui.mount(pane)
 const g=s.hold((e:any)=>e.key==='failed'&&e.value.length===2)
 const input=$.ui.input({plugin:'binnacle-hud',key:'thought',text:'same thought'})
 await g.entered.promise
 await first.unmount()
 const ui=await $.ui.mount(pane)
 await ui.press({key:'k-d'});await s.clock.settle()
 expect(s.cell('failed').value).toEqual([])
 g.release.resolve();await input;await s.clock.settle()
 expect(s.cell('failed').value.map((e: any) => e.text)).toEqual(['same thought'])
 await ui.press({key:'k-d'});await s.clock.settle();await ui.unmount()
 expect(s.cell('failed').value.map((e: any) => e.text)).toEqual(['same thought'])
})
test('round2: stale Memory remove button must not remove shifted unseen line',async($,on)=>{
 const s=await start($,on,{memory:['first line','second line','third line'],view:{ring:2,expand:1,failed:''}})
 const ui=await $.ui.mount(pane)
 await ui.press({key:'k-1'});await s.clock.settle()
 expect(s.cell('memory').value.map((e: any) => e.text)).toEqual(['second line','third line'])
 // This drawn key still names the original second line, not the current index 1.
 await ui.press({key:'k-2'});await s.clock.settle();await ui.unmount()
 expect(s.cell('memory').value.map((e: any) => e.text)).toEqual(['third line'])
})
const texts=(v:any[])=>v.map(e=>e.text)
const seed=(t:string[],saved:boolean)=>saved?t.map((text,i)=>({id:`r${i}`,text})):t
for(const saved of [false,true]){
test(`round3: [A,A,B,A], k-1 then the stale k-2 removes the second A (saved=${saved})`,async($,on)=>{
 const s=await start($,on,{memory:seed(['A','A','B','A'],saved)});const ui=await $.ui.mount(pane)
 await ui.press({key:'k-1'});await s.clock.settle();await ui.press({key:'k-2'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['B','A'])
})
test(`round3: [A,B,A], k-1 twice on one draw removes only the first A (saved=${saved})`,async($,on)=>{
 const s=await start($,on,{memory:seed(['A','B','A'],saved)});const ui=await $.ui.mount(pane)
 await ui.press({key:'k-1'});await s.clock.settle();await ui.press({key:'k-1'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['B','A'])
})
}
test('round3: a line added twice with the same text is two entries',async($,on)=>{
 const s=await start($,on,{typed:'A'})
 for(let n=0;n<2;n++){const ui=await $.ui.mount(pane);await ui.press({key:'k-a'});await s.clock.settle();await ui.unmount();s.cells.typed={value:'A',version:s.cell('typed').version+1}}
 const ids=s.cell('memory').value.map((e:any)=>e.id)
 expect(ids).toHaveLength(2);expect(new Set(ids).size).toBe(2)
})
test('round3: a stale dismissal cannot drop a later failure with the same text (both from real keeps)',async($,on)=>{
 const s=await start($,on);s.deny()
 const first=await $.ui.mount(pane)
 await $.ui.input({plugin:'binnacle-hud',key:'thought',text:'same thought'});await s.clock.settle()
 await first.unmount()
 const ui=await $.ui.mount(pane)
 await ui.press({key:'k-d'});await s.clock.settle()
 expect(s.cell('failed').value).toEqual([])
 await $.ui.input({plugin:'binnacle-hud',key:'thought',text:'same thought'});await s.clock.settle()
 await ui.press({key:'k-d'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('failed').value)).toEqual(['same thought'])
})
test('round3: a 4.1.0 session loads with every line and failed keep drawn, and session start mints their ids',async($,on)=>{
 const s=await start($,on,{memory:['a line','b line'],failed:['a failed keep'],view:{ring:2,expand:1,failed:''}})
 for(const key of ['memory','failed'])expect(s.cell(key).value.every((e:any)=>typeof e==='object'&&typeof e.id==='string')).toBe(true)
 const ui=await $.ui.mount(pane);const drawn=JSON.stringify(await ui.drawn())
 expect(drawn).toContain('a line');expect(drawn).toContain('b line');expect(drawn).toContain('a failed keep');expect(drawn).not.toContain('undefined')
 await ui.press({key:'k-1'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['b line'])
})
test('round3: a 4.1.0 string appended after a saved entry cannot share its id',async($,on)=>{
 const s=await start($,on,{memory:[{id:'v1-1-B',text:'B'},{id:'v1-2-C',text:'C'},'X'],view:{ring:2,expand:1,failed:''}})
 const ui=await $.ui.mount(pane);await ui.press({key:'k-2'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['B','X'])
})
const bare=(k:string)=>(s:any,t:string)=>{const old=s.cell(k);s.cells[k]={value:[...old.value,t],version:old.version+1}}
test('round4: a 4.1.0 string written after start is drawn, and no key acts on it',async($,on)=>{
 const s=await start($,on,{memory:['A'],view:{ring:2,expand:1,failed:''}});bare('memory')(s,'late')
 const ui=await $.ui.mount(pane);const drawn=JSON.stringify(await ui.drawn())
 expect(drawn).toContain('late');expect(drawn).toContain('k-1');expect(drawn).not.toContain('k-2')
 await ui.unmount()
})
test('round4: d is not offered when the only failed keeps are 4.1.0 strings written after start',async($,on)=>{
 const s=await start($,on,{failed:[]});bare('failed')(s,'late failure')
 const ui=await $.ui.mount(pane);const drawn=JSON.stringify(await ui.drawn());await ui.unmount()
 expect(drawn).toContain('late failure');expect(drawn).not.toContain('k-d')
})
test('round3: a stale p copies the thought on screen, not one kept after the draw',async($,on)=>{
 const s=await start($,on,{log:[{text:'seen thought',at:'2026-11-09T00:00:00.000Z',from:'terminal'}]})
 const ui=await $.ui.mount(pane)
 s.cells.log={value:[...s.cell('log').value,{text:'unseen thought',at:'2026-11-09T00:01:00.000Z',from:'terminal'}],version:s.cell('log').version+1}
 await ui.press({key:'k-p'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['seen thought'])
})
