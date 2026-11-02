# 运行、停止与接续

## 官方来源与本包增量

上游：https://github.com/akitaonrails/ai-memory 。固定tag v3.3.1，对应源码commit `1c506228b701f4496d3d9af6f00180749e0563d1`。官方负责存储、索引、版本与handoff；RepoGo仅增加中文说明、隔离启动和两份原创练习，没有重写记忆引擎。

本轮读过固定版本README和programmatic-memory/use-cases/macOS资料，使用官方语言无关MCP配方。MCP在这里是程序互相调用功能的接口，不是另一个模型。

## 环境与启动

macOS Apple Silicon：Python3，首次联网，约20MB官方归档。`sh start.sh`或`python3 start.py`，前台运行，Ctrl+C停止。官方归档SHA256：

`0289d5b6ed3d371216bf086addc65e5f1beedff76cf6e640ad9fe4ddba70a18a`

脚本仅从已校验归档提取binary，不运行安装脚本，不写全局PATH，不安装LaunchAgent或助手hook。已有binary会再核对本地指纹。下载失败或SHA变化即停止，不跳过校验。

独立数据：当前目录`.runtime/demo-data`；演示输出：`output/`；页面：`http://127.0.0.1:18683/web`。改端口用`python3 start.py --port 18685`，练习相应使用`python3 exercise.py --port 18685`。已有数据目录的配置与端口不符会停止，不自动覆盖，改端口时同时传新的`--data .runtime/demo-18685`。

本包显式设置`embedding_provider = "none"`。只做全文关键词检索，不下载嵌入模型；没有配置LLM。官方3.3.1默认可能自动下载本地嵌入模型，不能把“没API key”理解为所有默认模式都无下载。

## 两个独立用途

`python3 exercise.py`每次建立新的`library-时间编号`项目。

第一部分把原创预约决定写成知识页，用“预约”找回完整正文，再条件更新“cancelled不占用”。新版本编号应变化。它是长期知识，日后仍可以读取。

第二部分把尚未实现的接口和三条边界测试保存为handoff，先列举，再按编号领取。成功状态是`claimed`；再次领取同一编号为`none_pending`。这只是协议测试，没有启动两个真实助手，不代表全自动捕获或跨机器集成已验收。

示例不会执行预约业务，也不会从笔记里的句子自动运行命令。

## 完整验收与数据

`python3 verify.py`：下载固定binary、启动独立临时实例18684、完成两用途、停止再重启、读回同一个决策版本与已领状态，最后停止。报告在`output/latest-verify.json`，临时数据由Python临时目录正常清理；不会触及你的练习实例或其他业务。

普通服务停止时不删除数据。备份练习数据应先Ctrl+C停止，再复制`.runtime/demo-data`整个目录；不要只备份SQLite单个文件。本轮验证了停启持久化，未验证备份导入、版本升级或真实多用户部署。

## 三系统边界

| 系统 | 本包入口 | 本轮结果 |
| --- | --- | --- |
| macOS Apple Silicon arm64 | `sh start.sh`，自动下载官方arm64归档 | 官方binary核心、原创两用途、完整入口与停启已实测 |
| macOS Intel x86_64 | 官方macOS x86_64发布包后`python3 start.py --binary /path/ai-memory` | 未实测；不能用arm64归档代替 |
| Linux | 官方Linux对应架构发布包后`python3 start.py --binary /path/ai-memory` | 官方支持，未实测；`sh start.sh --binary ...`是同一转交入口 |
| Windows | 官方原生Windows包解压后`py -3 start.py --binary C:\path\ai-memory.exe`；也可`start.cmd --binary ...` | 上游原生Windows标实验；本轮未测ARM64/x64/WSL2，不能互相代替 |

非Mac自动下载路径会明确停止并提示人工取得官方binary，不猜架构或改执行策略。其他系统的发布文件名、前置要求与支持说明以固定版本官方资料为准：https://github.com/akitaonrails/ai-memory/tree/v3.3.1/docs 。

## 真的用于私人项目时

当前实例是没有账户鉴权的loopback原创样例。官方原生私人部署从`ai-memory init`开始，会生成本地令牌；接入服务与客户端按官方`docs/users.md`、`docs/install.md`和`docs/programmatic-memory.md`。本包不替你读取或分发令牌，也不会主动安装捕获当前助手聊天的hook/MCP。实际部署与数据范围由你决定，配置好后另行验证。官方界面大部分仍为英文，本包不宣称界面汉化。
