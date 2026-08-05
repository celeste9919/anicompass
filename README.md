# AniCompass

AniCompass 是一款面向动漫爱好者的桌面软件，提供真实目录搜索、AI 推荐、追番片单、推荐历史和本地备份恢复功能。

当前提供 Windows 发行版；macOS `.app` 计划在后续版本提供。

## 下载与运行

前往 GitHub 的 **Releases** 页面下载：

- `AniCompass-windows-x64-v0.1.0.zip`
- `AniCompass-windows-x64-v0.1.0.sha256`

解压 ZIP 后，双击 `AniCompass\AniCompass.exe` 即可启动。首次启动时 Windows 可能显示 SmartScreen 提示，因为当前版本尚未进行代码签名；请核对 SHA256 后再按实际情况选择运行。

## 主要功能

- **动漫搜索**：通过 Jikan / MyAnimeList 目录搜索真实动漫信息。
- **我的片单**：管理想看、在看、已完成；记录进度、10 分制评分与备注。
- **AI 推荐**：配置 OpenAI、DeepSeek、通义千问或兼容 OpenAI 接口的服务后，按偏好生成推荐。
- **目录校验**：AI 只提出候选作品，展示前会通过目录服务校验，避免把 AI 编造的信息当作真实条目。
- **推荐历史**：本地保存最近 10 次已确认的推荐会话。
- **本地备份**：导出或恢复片单与推荐历史的版本化 JSON 备份。
- **界面个性化**：支持中文/英文切换和 RGB 主题色调节。

## 隐私与安全

- API Key 只存储在操作系统的 `keyring` 凭据存储中。
- API Key 不会写入 SQLite、设置文件、日志、测试数据、截图或备份文件。
- 本地备份只包含片单和推荐历史，不包含 API Key。
- 搜索和 AI 推荐需要网络；本地片单、历史和备份功能使用本机 SQLite 数据库。

## 使用 AI 推荐

1. 打开“设置”。
2. 选择 AI 提供商，填写并保存 API Key。
3. 点击“测试连接”，确认连接成功。
4. 回到“推荐”，输入喜欢的题材、节奏、氛围或已喜欢的作品。
5. 选择推荐数量并生成结果；结果会经过目录校验后显示。

## 从源码运行

环境要求：Python 3.12+，Windows 为当前已验证的平台。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:PYTHONPATH='src'
.\.venv\Scripts\python -m anicompass.main
```

## 开发检查

```powershell
.\.venv\Scripts\python -m ruff check . --no-cache
.\.venv\Scripts\python -m pytest -q -p no:cacheprovider -p no:anyio
.\.venv\Scripts\pyside6-qmllint src\anicompass\ui\Main.qml
```

当前验证状态：72 个 pytest 检查通过；Windows 打包的 `AniCompass.exe --smoke-test` 通过。

## 项目资料

- 开发需求、架构、设计、安全、测试和阶段记录：`docs/`
- 每日开发日志：`dev-logs/`
- 许可证：MIT License，详见 `LICENSE`

## 发行包校验

`v0.1.0` 的 SHA256 校验文件随 Release 一同发布。建议下载后使用：

```powershell
Get-FileHash -Algorithm SHA256 .\AniCompass-windows-x64-v0.1.0.zip
```
