// Reviewer cases from the exact-head review of 2daffc6 (two FAIL findings and five guards).
import { expect, mock, test } from 'claude-code/testing'
const pane = (placement = 'dock') => ({plugin:'binnacle-hud', component:'Pane',requestId:'binnacle-hud',surface:'terminal',viewport:{columns:160,rows:40,isFullscreen:true},props:{title:'Binnacle',isFocused:true,bodyColumns:46,placement,scroll:{offset:0,bodyRows:32},view:{}}}) as const
async function start($:any,on:any, initial:any = {}) {
 const clock=mock.clock(on)
 const cells: any = Object.fromEntries(Object.entries(initial).map(([k,value])=>[k,{value,version:1}]))
 const cell=(k:string)=>cells[k]??{value:undefined,version:0}
 let box=''
 on('command.register',()=>({value:undefined})); on('ui.open',()=>({value:{isPlaced:true}})); on('ui.focus',()=>({value:{}}))
 on('session.start',(_:any,e:any)=>({cwd:e.cwd}))
 on('state.get',(_:any,e:any)=>({value:{...cell(e.key)}}))
 on('state.set',(_:any,e:any)=>{const old=cell(e.key); if(e.ifVersion!==undefined&&e.ifVersion!==old.version)return {value:{isSet:false,version:old.version}}; cells[e.key]={value:e.value,version:old.version+1};return {value:{isSet:true,version:old.version+1}}})
 on('prompt.edit',(_:any,e:any)=>{box=e.text.slice(0,e.start)+e.inputText+e.text.slice(e.end);return {text:box,cursor:box.length}})
 on('prompt.change',(_:any,e:any)=>({text:e.text})); on('prompt.submit',(_:any,e:any)=>({text:e.text}))
 on('ui.copy',()=>({value:{isCopied:true}}))
 await $.session.start({cwd:'/',surface:'terminal',isInteractive:true})
 const type=(text:string)=>$.prompt.edit({origin:{kind:'composer'},text:box,cursor:box.length,start:0,end:box.length,inputText:text})
 const clear=()=>{box='';return $.prompt.change({text:'',cursor:0,origin:{kind:'clear'}})}
 const submit=()=>$.prompt.submit({text:box,wait:false,origin:{kind:'composer'}})
 const press=async(key:string)=>{const ui=await $.ui.mount(pane());await ui.press({key:`k-${key}`});await clock.settle();await ui.unmount()}
 const shown=async(placement='dock')=>{const ui=await $.ui.mount(pane(placement));const text=JSON.stringify(await ui.drawn());await ui.unmount();return text}
 return {cells,cell,type,clear,submit,press,shown}
}
test('acceptance: reload-shaped stored draft then edit submit preserves it',async($,on)=>{
 const s=await start($,on,{lost:{text:'saved before reload',at:1,moves:10}})
 await s.type('new prompt');await s.submit();expect(s.cell('lost').value?.text).toBe('saved before reload')
})
test('acceptance: a stored number colliding with next edit loses unrelated saved draft',async($,on)=>{
 const s=await start($,on);await s.type('calibration');await s.clear()
 // Observe the counter without changing production code, then supply a persisted record at its next number.
 const next=s.cell('lost').value.moves+1
 s.cells.lost={value:{text:'unrelated pre-reload draft',at:1,moves:next},version:s.cell('lost').version+1}
 await s.type('new prompt');await s.submit()
 expect(s.cell('lost').value?.text).toBe('unrelated pre-reload draft')
})
test('acceptance: copy then fresh different clear then paste old preserves fresh clear',async($,on)=>{
 const s=await start($,on);await s.type('old copied');await s.clear();await s.press('c');await s.type('fresh draft');await s.clear();await s.type('old copied');expect(s.cell('lost').value?.text).toBe('fresh draft')
})
test('acceptance: x invalidates copy marker for subsequently retyped equal draft',async($,on)=>{
 const s=await start($,on);await s.type('same words');await s.clear()
 // Hand typing without a preceding copy deliberately preserves the old row.
 await s.type('same words');await s.press('c');await s.press('x')
 // The existing prompt is now a fresh clear, unrelated to the forgotten copy.
 await s.clear();await s.type('same words');expect(s.cell('lost').value?.text).toBe('same words')
})
test('acceptance: submit invalidates copy marker before new equal-text clear',async($,on)=>{
 const s=await start($,on);await s.type('same words');await s.clear();await s.press('c');await s.type('different submitted');await s.submit();await s.clear()
 await s.type('same words');await s.clear();await s.type('same words');expect(s.cell('lost').value?.text).toBe('same words')
})
for(const placement of ['dock','inline']) test(`acceptance: ${placement} refusal without unrecorded Send says Not sent`,{options:{narrow:'strip'}},async($,on)=>{
 const s=await start($,on,{memory:['not sent'],view:{ring:2,expand:1,failed:'injected refusal'}})
 const text=await s.shown(placement);expect(text).toContain('Not sent.');expect(text).not.toContain('The later Send was refused');expect(text).not.toContain('Claude has the lines sent at')
})
