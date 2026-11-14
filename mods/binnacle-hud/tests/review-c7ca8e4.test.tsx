import { expect, mock, test } from 'claude-code/testing'
const deferred=()=>{let resolve!:()=>void;const promise=new Promise<void>(r=>resolve=r);return {promise,resolve}}
const pane={plugin:'binnacle-hud',component:'Pane',requestId:'binnacle-hud',surface:'terminal',viewport:{columns:160,rows:40,isFullscreen:true},props:{title:'Binnacle',isFocused:true,bodyColumns:46,placement:'dock',scroll:{offset:0,bodyRows:32},view:{}}} as const
async function start($:any,on:any,initial:any={}) {
 const clock=mock.clock(on)
 const cells:any=Object.fromEntries(Object.entries(initial).map(([k,value])=>[k,{value,version:1}]))
 const cell=(k:string)=>cells[k]??{value:undefined,version:0}
 let readGate:any=null, box='',engine:any
 on('command.register',()=>({value:undefined}));on('ui.open',()=>({value:{isPlaced:true}}));on('ui.focus',()=>({value:{}}))
 on('session.start',($:any,e:any)=>{engine=$;return {cwd:e.cwd}})
 on('state.get',async(_:any,e:any)=>{
  if(readGate&&e.key==='lost'){const g=readGate;readGate=null;g.entered.resolve();await g.release.promise}
  return {value:{...cell(e.key)}}
 })
 on('state.set',(_:any,e:any)=>{
  const old=cell(e.key)
  if(e.ifVersion!==undefined&&e.ifVersion!==old.version)return {value:{isSet:false,version:old.version}}
  cells[e.key]={value:e.value,version:old.version+1};return {value:{isSet:true,version:old.version+1}}
 })
 on('prompt.edit',(_:any,e:any)=>{box=e.text.slice(0,e.start)+e.inputText+e.text.slice(e.end);return {text:box,cursor:box.length}})
 on('prompt.change',(_:any,e:any)=>({text:e.text}));on('prompt.submit',(_:any,e:any)=>({text:e.text}));on('ui.copy',()=>({value:{isCopied:true}}))
 await $.session.start({cwd:'/',surface:'terminal',isInteractive:true})
 return {clock,cells,cell,legacyAppend:(text:string)=>{const old=cell('memory');cells.memory={value:[...old.value,text],version:old.version+1}},
 holdRead:()=>{const g={entered:deferred(),release:deferred()};readGate=g;return g},
 type:(text:string)=>$.prompt.edit({origin:{kind:'composer'},text:box,cursor:box.length,start:0,end:box.length,inputText:text}),
 change:(kind:string,text='')=>{box=text;return $.prompt.change({text,cursor:text.length,origin:{kind}})}}
}
for(const key of ['2'])test(`adversarial: equal legacy append after shift must not collide on k-${key}`,async($,on)=>{
 const padding=key==='0'?['C','D','E','F','G','H','I','J']:[]
 const s=await start($,on,{memory:['A','B',...padding,'A'],view:{ring:2,expand:1,failed:''}})
 const before=await $.ui.mount(pane);await before.press({key:'k-1'});await s.clock.settle();await before.unmount()
 // Model a completed 4.1.0 append at the fixture state boundary, not a native reload.
 await s.legacyAppend('A')
 const ui=await $.ui.mount(pane);await ui.press({key:`k-${key}`});await s.clock.settle();await ui.unmount()
 expect(s.cell('memory').value.map((e:any)=>e.text??e)).toEqual(['B',...padding,'A'])
})
for(const key of ['2'])test(`adversarial: stale k-${key} must not match equal-text legacy replacement`,async($,on)=>{
 const padding=key==='0'?['C','D','E','F','G','H','I','J']:[]
 const s=await start($,on,{memory:['B',...padding,'A'],view:{ring:2,expand:1,failed:''}})
 const ui=await $.ui.mount(pane);await ui.press({key:`k-${key}`});await s.clock.settle()
 await s.legacyAppend('A')
 await ui.press({key:`k-${key}`});await s.clock.settle();await ui.unmount()
 expect(s.cell('memory').value.map((e:any)=>e.text??e)).toEqual(['B',...padding,'A'])
})
