import { expect, mock, test } from 'claude-code/testing'
const deferred=()=>{let resolve!:()=>void;const promise=new Promise<void>(r=>resolve=r);return {promise,resolve}}
const pane={plugin:'binnacle-hud',component:'Pane',requestId:'binnacle-hud',surface:'terminal',viewport:{columns:160,rows:40,isFullscreen:true},props:{title:'Binnacle',isFocused:true,bodyColumns:46,placement:'dock',scroll:{offset:0,bodyRows:32},view:{}}} as const
async function start($:any,on:any,initial:any={}) {
 const clock=mock.clock(on)
 const cells:any=Object.fromEntries(Object.entries(initial).map(([k,value])=>[k,{value,version:1}]))
 const cell=(k:string)=>cells[k]??{value:undefined,version:0}
 let gate:any=null, box=''; let denied=false; let copy:any={isCopied:true}
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
 on('prompt.change',(_:any,e:any)=>({text:e.text}));on('prompt.submit',(_:any,e:any)=>({text:e.text}));on('ui.copy',()=>({value:copy}))
 await $.session.start({cwd:'/',surface:'terminal',isInteractive:true})
 return {clock,cells,cell,writes,deny:()=>denied=true,refuseCopy:()=>copy={isCopied:false,reason:'no clipboard'},
 hold:(match:any)=>{const g={match,entered:deferred(),release:deferred()};gate=g;return g},
 type:(text:string)=>$.prompt.edit({origin:{kind:'composer'},text:box,cursor:box.length,start:0,end:box.length,inputText:text}),
 change:(kind:string,text='')=>{box=text;return $.prompt.change({text,cursor:text.length,origin:{kind}})},
 submit:()=>$.prompt.submit({text:box,wait:false,origin:{kind:'composer'}}),
 press:async(key:string)=>{const ui=await $.ui.mount(pane);await ui.press({key:`k-${key}`});await clock.settle();await ui.unmount()}}
}
for(const kind of ['history','plugin','undo'])test(`round2: delayed ${kind} restore must not delete a newer equal-text clear`,async($,on)=>{
 const s=await start($,on);await s.type('same draft');await s.change('clear');const old=s.cell('lost').value
 const g=s.hold((e:any)=>e.key==='lost'&&e.value===null)
 const restoring=s.change(kind,'same draft');await g.entered.promise
 await s.change('clear');const fresh=s.cell('lost').value
 expect(fresh.moves).not.toBe(old.moves)
 g.release.resolve();await restoring
 expect(s.writes.some(w=>w.key==='lost'&&!w.ok)).toBe(true)
 expect(s.cell('lost').value).toEqual(fresh)
})
test('round2: stale x must distinguish equal timestamp and counter across load identities (modeled boundary)',async($,on)=>{
 const s=await start($,on,{lost:{text:'old',at:5,moves:2,load:'old-load'}})
 const ui=await $.ui.mount(pane)
 const fresh={text:'new load draft',at:5,moves:2,load:'new-load'}
 s.cells.lost={value:fresh,version:s.cell('lost').version+1}
 await ui.press({key:'k-x'});await s.clock.settle();await ui.unmount()
 expect(s.cell('lost').value).toEqual(fresh)
})
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
 await ui.press({key:'k-2'});await s.clock.settle();await ui.unmount()
 expect(s.cell('memory').value.map((e: any) => e.text)).toEqual(['third line'])
})
test('round2: modeled old-load pending clear arriving after new-load edit survives submit',async($,on)=>{
 const s=await start($,on)
 await s.type('new load prompt')
 const pending={text:'old pending clear',at:0,moves:1,load:'old-load'}
 s.cells.lost={value:pending,version:1}
 await s.submit();expect(s.cell('lost').value).toEqual(pending)
})
test('round2: stale copy after actual clear-submit cannot consume a fresh equal record',async($,on)=>{
 const s=await start($,on);await s.type('same');await s.change('clear');await s.press('c');await s.submit()
 expect(s.cell('lost').value).toBe(null)
 await s.type('same');await s.change('clear');const fresh=s.cell('lost').value
 await s.type('same');expect(s.cell('lost').value).toEqual(fresh)
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
test(`round3: k-0 twice on one draw removes only the drawn last line (saved=${saved})`,async($,on)=>{
 const ten=Array.from({length:10},(_,i)=>`line ${i+1}`)
 const s=await start($,on,{memory:seed(ten,saved)});const ui=await $.ui.mount(pane)
 await ui.press({key:'k-0'});await s.clock.settle();await ui.press({key:'k-0'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(ten.slice(0,9))
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
test('round3: a 4.1.0 session loads with every line and failed keep drawn, and the first write saves the new shape',async($,on)=>{
 const s=await start($,on,{memory:['a line','b line'],failed:['a failed keep'],view:{ring:2,expand:1,failed:''}})
 const ui=await $.ui.mount(pane);const drawn=JSON.stringify(await ui.drawn())
 expect(drawn).toContain('a line');expect(drawn).toContain('b line');expect(drawn).toContain('a failed keep');expect(drawn).not.toContain('undefined')
 await ui.press({key:'k-1'});await s.clock.settle();await ui.unmount()
 expect(s.cell('memory').value).toEqual([{id:'v1-1-b line',text:'b line'}])
})
test('round3: a 4.1.0 string appended after a saved entry cannot share its id',async($,on)=>{
 const s=await start($,on,{memory:[{id:'v1-1-B',text:'B'},{id:'v1-2-C',text:'C'},'X'],view:{ring:2,expand:1,failed:''}})
 const ui=await $.ui.mount(pane);await ui.press({key:'k-2'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['B','X'])
})
test('round3: a stale p copies the thought on screen, not one kept after the draw',async($,on)=>{
 const s=await start($,on,{log:[{text:'seen thought',at:'2026-11-09T00:00:00.000Z',from:'terminal'}]})
 const ui=await $.ui.mount(pane)
 s.cells.log={value:[...s.cell('log').value,{text:'unseen thought',at:'2026-11-09T00:01:00.000Z',from:'terminal'}],version:s.cell('log').version+1}
 await ui.press({key:'k-p'});await s.clock.settle();await ui.unmount()
 expect(texts(s.cell('memory').value)).toEqual(['seen thought'])
})
test('round3: a refused copy leaves no marker, so typing the same text keeps the row',async($,on)=>{
 const s=await start($,on);s.refuseCopy();await s.type('same');await s.change('clear');const rec=s.cell('lost').value
 await s.press('c');await s.type('same')
 expect(s.cell('lost').value).toEqual(rec)
})
test('round3: a submit from outside the composer does not drop a cleared draft',async($,on)=>{
 const s=await start($,on);await s.type('draft');await s.change('clear');const rec=s.cell('lost').value
 await $.prompt.submit({text:'from a plugin',wait:false,origin:{kind:'plugin'}})
 expect(s.cell('lost').value).toEqual(rec)
})
