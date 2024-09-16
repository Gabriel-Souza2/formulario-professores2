# Usar uma imagem base oficial do Python
FROM python:3.10-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instalar as dependências do projeto
RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt


# Copiar o restante do código da aplicação
COPY . .

# Expor a porta em que o Django vai rodar
EXPOSE 8000


# Comando para iniciar o servidor do Django
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "setup.wsgi:application"]
