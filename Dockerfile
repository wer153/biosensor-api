FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY . .
RUN uv sync
ENV PORT=8000
CMD ["/bin/uv", "run", "server"]
