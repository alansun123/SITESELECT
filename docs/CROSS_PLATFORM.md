# CROSS_PLATFORM (Windows + macOS)

本项目目标：同一套代码在 **macOS** 与 **Windows** 都能运行（GUI-first，CLI辅助）。

## 1) 统一前提

- Python 3.10+
- 使用项目虚拟环境（不要装到系统 Python）
- 进入仓库根目录执行命令

---

## 2) macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install streamlit
python3 src/siteselect/cli.py analyze --input examples/candidates.example.csv --weights examples/weights.example.json --out output/report.html
streamlit run app/gui_app.py
```

---

## 3) Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install streamlit
python src\siteselect\cli.py analyze --input examples\candidates.example.csv --weights examples\weights.example.json --out output\report.html
streamlit run app\gui_app.py
```

> 如果 PowerShell 禁止脚本执行，可先：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 4) 最小兼容检查清单

- [ ] CLI 在两端都能生成 `output/report.html`
- [ ] GUI 能正常启动并完成 4 步流程
- [ ] 路径分隔符兼容（代码统一使用 `pathlib`）
- [ ] 文本编码统一 UTF-8
- [ ] 换行差异不影响 CSV 读取

---

## 5) 已知建议

- 依赖安装优先虚拟环境，避免系统环境冲突
- 发布前至少做一次 Windows 实机验证（或 CI Windows runner）
- 后续可补 `requirements.txt` / `pyproject.toml` 做版本锁定
