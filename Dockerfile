# 使用官方 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 配置 pip 使用阿里源并安装 uv
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ uv==0.8.13

# 复制项目文件
COPY pyproject.toml uv.lock ./

# 配置 uv 使用阿里源并安装生产依赖
RUN uv sync --frozen --no-dev --no-install-project --index-url https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY main.py ./

# 暴露端口
EXPOSE 9050

# 检查容器内部服务是否正常
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=6 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:9050/health', timeout=2)" || exit 1

# 运行应用
CMD [".venv/bin/uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9050"]
