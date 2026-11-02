#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real upstream binary: fresh standalone service, two samples, stop/restart/persist."""
from pathlib import Path
import argparse,json,socket,subprocess,tempfile,time,urllib.request
import start,exercise
ROOT=Path(__file__).resolve().parent

def wait_ready(port,p):
    for _ in range(100):
        if p.poll() is not None:raise RuntimeError('服务提前退出，请读output/verify.log')
        try:
            req=urllib.request.Request('http://127.0.0.1:%d/mcp'%port,json.dumps({'jsonrpc':'2.0','id':1,'method':'tools/list','params':{}}).encode(),{'Content-Type':'application/json','Accept':'application/json, text/event-stream'})
            with urllib.request.urlopen(req,timeout=.5) as r:json.load(r)
            return
        except Exception:time.sleep(.1)
    raise RuntimeError('启动超出预算')
def stop(p):
    p.terminate()
    try:p.wait(timeout=10)
    except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--binary');args=ap.parse_args()
    port=18684;s=socket.socket();s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1);s.bind(('127.0.0.1',port));s.close()
    exe=start.binary(args.binary);version=start.checked_version(exe);out=ROOT/'output';out.mkdir(exist_ok=True)
    dest=out/('verify-'+str(time.time_ns()))
    with tempfile.TemporaryDirectory(prefix='repogo-ai-memory-') as tmp,(out/'verify.log').open('wb') as log:
        cmd=start.command(exe,tmp,port);p=subprocess.Popen(cmd,env=start.env(port),stdout=log,stderr=subprocess.STDOUT)
        try:
            wait_ready(port,p);r=exercise.exercise(port,'library-verify',dest)
        finally:stop(p)
        p=subprocess.Popen(cmd,env=start.env(port),stdout=log,stderr=subprocess.STDOUT)
        try:
            wait_ready(port,p)
            c=exercise.Client(port,'library-verify',dest)
            page=c.call('memory_read_page',{'path':'decisions/reservation.md'},'10-after-restart')
            assert 'cancelled' in page['body'] and page['page_id']==r['decision_page_id']
            pending=c.call('memory_handoff_list',{},'11-after-restart')
            assert not pending['handoffs']
        finally:stop(p)
        r.update(restart_persisted=True,service_stopped=True,binary_version=version)
        (dest/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2));(out/'latest-verify.json').write_text(json.dumps({'result_path':str(dest/'result.json'),**r},ensure_ascii=False,indent=2))
        print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
