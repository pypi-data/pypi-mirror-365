# docker build -t rpa:v1.0.0 .

# ------------------------------

# 安装 Python
FROM python:3.8-slim-bullseye

# ------------------------------

# 安装依赖
RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list && \
    sed -i 's|http://security.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list && \
	apt-get update && \
	apt-get install -y gcc && \
	apt-get install -y wget && \
	wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
	apt install -y ./google-chrome-stable_current_amd64.deb && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/* && \
	rm -f google-chrome-stable_current_amd64.deb

# ------------------------------

# 进入应用目录
WORKDIR /app

# 复制代码
COPY . .

# 安装依赖包
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

# 设置启动命令
CMD ["python", "main.py"]

# docker run -it --name rpa rpa:v1.0.0

# docker run -dit --name rpa rpa:v1.0.0

# docker stop rpa

# docker logs -f rpa

# docker rm rpa