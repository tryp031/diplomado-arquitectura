# Panel de control: plano de CONTROL, no de datos. Trae k6 para lanzar cargas desde la página.
FROM grafana/k6:latest AS k6

FROM python:3.13-slim
COPY --from=k6 /usr/bin/k6 /usr/bin/k6
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY panel/requirements.txt panel-requirements.txt
RUN pip install --no-cache-dir -r panel-requirements.txt
COPY panel ./panel
