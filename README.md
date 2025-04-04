
# 🚀 Como rodar este projeto localmente

Siga os passos abaixo para subir o ambiente Airflow + FastAPI com Astronomer:

---

## 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

---

## 2. Inicie o fast_api

```bash 
docker compose -f docker-compose.override.yml build fastapi
```

## 2. Inicialize o projeto Astronomer

Este comando cria os arquivos de configuração necessários:

```bash
astro dev init
```

---

## 3. Descubra o nome da rede usada pelo Astronomer

Rode o comando abaixo para listar as redes Docker:

```bash
docker network ls --filter name=_airflow
```

Você verá algo como:

```
NETWORK ID     NAME                            DRIVER    SCOPE
7d4e3cb1fd00   nome-do-projeto_xxxxx_airflow   bridge    local
```

---

## 4. Atualize o arquivo `.env`

Abra o arquivo `.env` na raiz do projeto e **substitua o valor da variável `ASTRO_NETWORK`** com o nome da rede que você acabou de encontrar.

Exemplo:

```env
# Substitua este valor
ASTRO_NETWORK=nome-do-projeto_xxxxx_airflow
```

---

## 5. Suba o ambiente

Agora que tudo está configurado, execute:

```bash
astro dev start
```

Isso irá:

- Construir e iniciar todos os containers (Airflow, Postgres, FastAPI)
- Colocar todos os serviços na mesma rede
- Permitir que o FastAPI se conecte ao Postgres corretamente

---

## 6. Acesse as interfaces

- Airflow: http://localhost:8080
- FastAPI: http://localhost:8001
- Teste de conexão com o banco: http://localhost:8001/ping-db
