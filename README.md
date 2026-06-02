# Jenkins Demo

使用 `uv` 管理依赖的最小 FastAPI 项目。

## 安装依赖

```bash
uv sync
```

## 启动服务

```bash
uv run uvicorn main:app --reload
```

服务启动后可访问：

- API: <http://127.0.0.1:8000/>
- 健康检查: <http://127.0.0.1:8000/health>
- Swagger 文档: <http://127.0.0.1:8000/docs>

## 自动化测试

安装包含测试工具在内的依赖：

```bash
uv sync --dev
```

执行测试：

```bash
uv run pytest
```

测试脚本位于 `tests/test_main.py`，覆盖首页展示内容和健康检查接口。
