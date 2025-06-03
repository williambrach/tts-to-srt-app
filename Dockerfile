# FROM python:3.12

# WORKDIR /workspace
# ADD requirements.txt app.py .env /workspace/
# RUN pip install -r /workspace/requirements.txt
# EXPOSE 8888
# CMD ["python", "/workspace/app.py"]

FROM python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV PATH="/app/.venv/bin:$PATH"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH=/usr/local/bin:$PATH


# Copy dependency files
COPY requirements.txt /
COPY pyproject.toml /

# Install dependencies using uv
RUN uv sync

# Copy application files
COPY app.py .env /

EXPOSE 8888
CMD ["python", "/app.py"]