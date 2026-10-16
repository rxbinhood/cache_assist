FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml server.py ./
RUN pip install --no-cache-dir mcp>=1.9,<2
USER nobody
CMD ["python", "server.py"]
