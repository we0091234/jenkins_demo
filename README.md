# Jenkins Demo

使用 `uv` 管理依赖的最小 FastAPI 项目，当前已包含注册、登录和登录后欢迎页。

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

首页能力：

- 首页默认展示登录页，底部带注册跳转入口
- 注册页单独展示，注册成功后返回登录页
- 同一用户名密码连续输错 3 次后锁定 10 分钟
- 登录后支持使用当前密码修改新密码
- 登录成功后显示 `欢迎来到 jenkis 的大家庭`

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

继续测试
