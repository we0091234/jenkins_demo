# 使用官方 Python 基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 配置 pip 使用阿里源并安装 uv
RUN pip install -i https://mirrors.aliyun.com/pypi/simple/ uv

# 复制项目文件
COPY pyproject.toml uv.lock ./

# 配置 uv 使用阿里源并安装依赖
RUN uv sync --frozen --index-url https://mirrors.aliyun.com/pypi/simple/

# 复制应用代码
COPY main.py ./

# 暴露端口
EXPOSE 9050

# 运行应用
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9050"]
