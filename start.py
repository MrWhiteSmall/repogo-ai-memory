#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Original RepoGo launcher. Official ai-memory provides all storage and search."""
import argparse,hashlib,json,os,platform,subprocess,tarfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
VERSION='3.3.1'
SHA256='0289d5b6ed3d371216bf086addc65e5f1beedff76cf6e640ad9fe4ddba70a18a'
ASSET='ai-memory-macos-aarch64.tar.gz'
URL='https://github.com/akitaonrails/ai-memory/releases/download/v'+VERSION+'/'+ASSET

def binary(explicit=None):
    if explicit:
        p=Path(explicit).expanduser().resolve()
        if not p.is_file():raise RuntimeError('指定的官方binary不存在')
        return p
    runtime=ROOT/'.runtime';exe=runtime/'ai-memory'
    if exe.is_file():
        # This binary is extracted only from the checksum-pinned official archive.
        manifest=runtime/'binary-sha256.txt'
        if not manifest.is_file() or hashlib.sha256(exe.read_bytes()).hexdigest()!=manifest.read_text().strip():
            raise RuntimeError('已下载binary指纹变化；先核对文件，不自动覆盖')
        return exe
    if platform.system()!='Darwin' or platform.machine() not in {'arm64','aarch64'}:
        raise RuntimeError('自动下载入口本轮仅验收macOS Apple Silicon。其他系统按RUN.md取得官方3.3.1 binary，再加 --binary 路径；未宣称Linux/Windows通过。')
    runtime.mkdir(exist_ok=True)
    archive=runtime/ASSET
    with urllib.request.urlopen(URL,timeout=30) as r,archive.open('wb') as f:
        while True:
            chunk=r.read(1024*1024)
            if not chunk:break
            f.write(chunk)
    actual=hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual!=SHA256:raise RuntimeError('官方归档SHA256不匹配，停止执行')
    with tarfile.open(archive) as t:
        member=t.getmember('./ai-memory')
        if not member.isfile():raise RuntimeError('官方归档不是预期的单文件binary')
        exe.write_bytes(t.extractfile(member).read())
    exe.chmod(0o755)
    (runtime/'binary-sha256.txt').write_text(hashlib.sha256(exe.read_bytes()).hexdigest()+'\n')
    return exe

def env(port):
    # Preserve OS paths, not provider/agent credentials. Never rewrite HOME or shell config.
    result={k:os.environ[k] for k in ['PATH','HOME','TMPDIR','LANG','SYSTEMROOT','WINDIR'] if k in os.environ}
    result['AI_MEMORY_SERVER_URL']='http://127.0.0.1:'+str(port)
    return result

def command(exe,data,port):
    data=Path(data).resolve();data.mkdir(parents=True,exist_ok=True)
    config=data/'repogo-demo.toml'
    wanted='bind = "127.0.0.1:%s"\nembedding_provider = "none"\n'%port
    if config.exists() and config.read_text()!=wanted:raise RuntimeError('现有demo配置不同，请使用新的 --data 目录')
    config.write_text(wanted)
    return [str(exe),'--data-dir',str(data),'--config',str(config),'serve','--transport','http','--bind','127.0.0.1:'+str(port),'--enable-web','--workspace','repogo-demo','--project','library']

def main():
    ap=argparse.ArgumentParser(description='原创样例独立记忆服务，不安装hooks或接入你的聊天')
    ap.add_argument('--binary',help='已取得的官方3.3.1 binary（非Mac系统需自行核验）')
    ap.add_argument('--data',default=str(ROOT/'.runtime/demo-data'))
    ap.add_argument('--port',type=int,default=18683)
    args=ap.parse_args();exe=binary(args.binary)
    version=subprocess.check_output([str(exe),'--version'],text=True,timeout=10).strip()
    if version!='ai-memory '+VERSION:raise RuntimeError('需要固定版本 '+VERSION+'，实际 '+version)
    print('启动原创样例服务：http://127.0.0.1:%d/web\n保持本窗口，另开窗口运行 python3 exercise.py。按Ctrl+C停止。'%args.port,flush=True)
    print('这是只监听本机、无账号鉴权的练习服务。只放原创虚构样例；实际私人记忆请按官方init/auth文档另建实例。',flush=True)
    p=subprocess.Popen(command(exe,args.data,args.port),env=env(args.port))
    try:return p.wait()
    except KeyboardInterrupt:
        p.terminate()
        try:return p.wait(timeout=10)
        except subprocess.TimeoutExpired:p.kill();return p.wait(timeout=5)
if __name__=='__main__':raise SystemExit(main())
