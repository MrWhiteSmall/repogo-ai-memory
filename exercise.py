#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Two original samples through the documented stateless MCP interface."""
import argparse,json,time,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DECISION='''# 预约冲突处理：为什么两段接壤的预约可以共存

## 已决定
预约采用半开区间 [开始,结束)。09:00–10:00与10:00–11:00允许；09:00–10:30与10:00–11:00拒绝，关键词 overlap。

## 为什么
结束与开始相同不重叠，避免把连续借阅误判为冲突。

这是原创虚构图书预约说明，未运行真实预约应用。'''
class Client:
    def __init__(self,port,project,out):self.url='http://127.0.0.1:%d/mcp'%port;self.project=project;self.out=out;self.n=0
    def call(self,name,args,label):
        self.n+=1
        payload={'jsonrpc':'2.0','id':self.n,'method':'tools/call','params':{'name':name,'arguments':{'workspace':'repogo-demo','project':self.project,**args}}}
        req=urllib.request.Request(self.url,json.dumps(payload,ensure_ascii=False).encode(),{'Content-Type':'application/json','Accept':'application/json, text/event-stream'})
        with urllib.request.urlopen(req,timeout=15) as r:raw=json.load(r)
        (self.out/(label+'.json')).write_text(json.dumps({'request':payload,'response':raw},ensure_ascii=False,indent=2))
        if raw.get('error') or raw.get('result',{}).get('isError'):raise RuntimeError(json.dumps(raw,ensure_ascii=False))
        texts=[x['text'] for x in raw['result'].get('content',[]) if x.get('type')=='text']
        return json.loads(texts[0]) if texts else raw['result']

def exercise(port=18683,project=None,out=None):
    project=project or 'library-'+str(time.time_ns())
    out=Path(out) if out else ROOT/'output'/project
    out.mkdir(parents=True,exist_ok=False)
    c=Client(port,project,out)
    c.call('memory_write_page',{'path':'decisions/reservation.md','body':DECISION,'kind':'decision','create_only':True},'01-save')
    q=c.call('memory_query',{'query':'预约','limit':5},'02-find')
    if not any(x['path']=='decisions/reservation.md' for x in q['hits']):raise RuntimeError('未找回预约决策')
    r=c.call('memory_read_page',{'path':'decisions/reservation.md'},'03-read')
    if r['body']!=DECISION:raise RuntimeError('完整正文与输入不一致')
    revised=DECISION+'\n\n## 新增边界\n已取消 cancelled 的预约不占用时间段。'
    c.call('memory_write_page',{'path':'decisions/reservation.md','body':revised,'kind':'decision','expected_page_id':r['page_id']},'04-revise')
    updated=c.call('memory_read_page',{'path':'decisions/reservation.md'},'05-reread')
    if updated['body']!=revised or updated['page_id']==r['page_id']:raise RuntimeError('新版未保存')
    c.call('memory_handoff_begin',{'summary':'预约冲突规则已保存；接口尚未实现。','next_steps':['实现半开区间判断。','补接壤允许、重叠拒绝和取消不占用三个测试。'],'files_touched':['decisions/reservation.md']},'06-next')
    rows=c.call('memory_handoff_list',{},'07-list')['handoffs']
    if len(rows)!=1:raise RuntimeError('待办条数异常')
    hid=rows[0].get('id') or rows[0].get('handoff_id')
    claimed=c.call('memory_handoff_accept',{'handoff_id':hid},'08-claim')
    twice=c.call('memory_handoff_accept',{'handoff_id':hid},'09-repeat')
    if claimed['status']!='claimed' or twice['status']!='none_pending':raise RuntimeError('没有观察到一次认领行为')
    result={'passed':True,'project':project,'url':'http://127.0.0.1:%d/web/w/repogo-demo/%s'%(port,project),'decision_page_id':updated['page_id'],'handoff_id':hid,'second_claim':twice['status'],'sample_only':True,'llm':False,'embedding':False}
    (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=18683);p.add_argument('--project');a=p.parse_args()
    print(json.dumps(exercise(a.port,a.project),ensure_ascii=False,indent=2))
