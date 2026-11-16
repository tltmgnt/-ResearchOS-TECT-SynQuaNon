const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('web/app.js','utf8');
const code=source.slice(source.indexOf('function valid('),source.indexOf('function persist('))+source.slice(source.indexOf('function gap('),source.indexOf('function download('));
const ctx=vm.createContext({});vm.runInContext(code,ctx);
const record={schema_version:1,id:'test-001',title:'Test',owner:'Tester',hypothesis:'Test',data_kind:'synthetic',application:'qubits',model:{name:'bcs-gap-toy-v1',critical_temperature_K:2,baseline_critical_temperature_K:1.2,temperatures_K:[0,.1,.5,1,1.2,1.5,2,3]},evidence:[]};
assert.equal(ctx.valid(record),record);
assert.equal(ctx.gap(2,2),0);assert.equal(ctx.gap(3,2),0);assert.ok(Math.abs(ctx.gap(0,2)-.30401951748336)<1e-12);
assert.ok(ctx.gap(.1,2)>ctx.gap(1,2));
for(const mutate of [r=>r.id='../bad',r=>r.model.temperatures_K=[-1],r=>r.model.temperatures_K=[true],r=>r.model.critical_temperature_K=Infinity,r=>r.data_kind='experimental']){let r=structuredClone(record);mutate(r);assert.throws(()=>ctx.valid(r))}
assert.equal(ctx.results(record).length,8);
console.log('Model boundaries, record validation and result generation passed.');
