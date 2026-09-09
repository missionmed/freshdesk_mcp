FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir .

# Railway injects PORT; the server binds it and serves MCP over streamable HTTP.
ENV TRANSPORT=http HOST=0.0.0.0 PORT=8080
EXPOSE 8080

CMD ["freshdesk-mcp"]
