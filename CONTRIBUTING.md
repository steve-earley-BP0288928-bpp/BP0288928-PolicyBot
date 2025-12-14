# Contributing to _PolicyBot_

## Table of contents
- [Contributing to _PolicyBot_](#contributing-to-policybot)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Architecture and structure](#architecture-and-structure)
  - [Requirements](#requirements)
  - [Clone the project](#clone-the-project)
  - [Set up PostgreSQL database in Docker](#set-up-postgresql-database-in-docker)
  - [Set up Python virtual environment and dependencies](#set-up-python-virtual-environment-and-dependencies)
  - [Add a model deployment in Azure OpenAI service](#add-a-model-deployment-in-azure-openai-service)
  - [Configure environment variables](#configure-environment-variables)
    - [PostgreSQL](#postgresql)
    - [Azure OpenAI](#azure-openai)
    - [Hugging Face](#hugging-face)
  - [4. Initialise the database](#4-initialise-the-database)
    - [4.1 Run crawler to populate database](#41-run-crawler-to-populate-database)
    - [4.2 Run the embedding script](#42-run-the-embedding-script)
  - [5. Start the FastAPI APP](#5-start-the-fastapi-app)
  - [6. Setup and run Frontend APP](#6-setup-and-run-frontend-app)
    - [6.1 Install npm dependencies](#61-install-npm-dependencies)
    - [6.2 Start the frontend APP](#62-start-the-frontend-app)
  - [6.3 Use the APP](#63-use-the-app)

## Introduction

The _PolicyBot_ project is based on a fork of the [ChatLSE](https://github.com/LSE-DSI/chat-lse) project developed by the [LSE Data Science Institute](https://www.lse.ac.uk/dsi), which itself was based on the [Rag on Postgres](https://github.com/pamelafox/rag-on-postgres) project.

Major modifications made:

- Altered to use Azure OpenAI service.
- Altered LLM prompts to focus on providing policy assistance to LSE staff.
- Added process for ingesting additional PDF documents.

Minor modifications made:

- Altered user interface to reflect the specific purpose of _PolicyBot_.
- Altered logging approach to create date-based logs with additional information logged.
- Resolved a TypeError issue in the main chat function.

The code has been fully tested on MacOS (Intel and M2) and partially tested on Ubuntu 22.04 LTS.

## Architecture and structure

The high-level architecture of the _PolicyBot_ application is shown here:

![High-level architecture of the PolicyBot application](/img/PolicyBot_simple_architecture.png "High-level architecture of the PolicyBot application")

There are four main components:

- The Frontend of the _PolicyBot_ web app, built using [ReactJS](https://react.dev/) and [FluentUI](https://github.com/microsoft/fluentui).
- The Backend of the web app, built using [FastAPI](https://fastapi.tiangolo.com/) and Python.
- A [PostgreSQL](https://www.postgresql.org/) database, deployed locally using [Docker](https://www.docker.com/).
- A chat model, deployed remotely using [Azure OpenAI](https://ai.azure.com/) service.

The application also uses a [local embedding model](https://developers.llamaindex.ai/python/examples/embeddings/huggingface/) in Python.

A scripted process uses [Crawley](https://github.com/elixir-crawly/crawly) to populate the database with documents scraped from the [LSE website](https://www.lse.ac.uk/). An additional process is used to ingest locally-stored PDF documents.

To run the application all four components must be installed and configured correctly. For development purposes both components of the web app - the Frontend and Backend - should be colocated. The database can optionally be installed on a remote service e.g. in [Azure Database for PostgreSQL](https://azure.microsoft.com/en-us/products/postgresql).

## Requirements

The following software needs to be installed on your development machine before proceeding: 

- [Conda](https://anaconda.org/) (or equivalent package manager - Conda is assumed here)
- [Docker](https://docs.docker.com/desktop/)
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [VSCode](https://code.visualstudio.com/) (or your preferred IDE)

These instructions assume MacOS is being used.

You will need an [Azure subscription](https://azure.microsoft.com/en-gb/pricing/purchase-options/azure-account) with access to the Azure OpenAI service. A private endpoint and firewall rules should be confifured to allow secure connections from your development machine. All of this will need to be set up using the [Azure Portal](https://portal.azure.com/). Detailed instructions are outside the scope of this document.

## Clone the project

Clone the _PolicyBot_ project repository from GitHub:

```bash
$ git clone https://github.com/steve-earley-BP0288928-bpp/BP0288928-PolicyBot.git
```

Not essential but for convenience create a symbolic link to the repository from your home directory, for example:

```bash
cd ~
ln -s Documents/GitHub/BP0288928-PolicyBot/ policybot
```

The rest of the set up should be performed from the root of the project:

```bash
cd policybot
```

## Set up PostgreSQL database in Docker

Run PostgreSQL in a Docker container:

```bash
$ docker container run -itd --name policybot-postgres --restart unless-stopped -p 5432:5432 -e POSTGRES_DB=policybot -e POSTGRES_USER=policybot -e POSTGRES_PASSWORD=policybot -d pgvector/pgvector:0.7.1-pg16
```

Note that this uses a Docker image of PostgreSQL database with the [pgvector](https://github.com/pgvector/pgvector) extension.

The database name and credentials for the database account can be changed as required.

To verify the container is running:

```bash
$ docker ps -a

CONTAINER ID   IMAGE                          COMMAND                  CREATED          STATUS          PORTS                                         NAMES
6fb5ba57cdf9   pgvector/pgvector:0.7.1-pg16   "docker-entrypoint.s…"   43 seconds ago   Up 42 seconds   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   policybot-postgres
```

The STATUS of the container should be something like "Up 42 seconds".

## Set up Python virtual environment and dependencies

Create and activate a virtual environment for PolicyBot (this uses conda but other virtual environments like venv could be used):

```bash
conda create -n policybot python=3.11 ipython
conda activate policybot
```

**Important** - ensure that `pip` refers to the pip inside the conda environment just created:

```bash
which pip
/opt/anaconda3/envs/policybot/bin/pip
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## Add a model deployment in Azure OpenAI service

Go to [Azure OpenAI](https://ai.azure.com/) service.

Navigate to `Shared resources > Deployments` and deploy a model suitable for chat completions and responses, for example `gpt-4.1`.

You will need details from the model deployment later.

## Configure environment variables

Copy the file `.env.sample` into `.env`.

### PostgreSQL

The environment variables relating to the PostgeSQL database can be left with their default values:

```bash
POSTGRES_HOST=localhost
POSTGRES_USERNAME=policybot
POSTGRES_PASSWORD=policybot
POSTGRES_DATABASE=policybot
POSTGRES_SSL=disable
POSTGRES_PORT=5432
```

If the database name, username or password were changed when the database was deployed in Docker then the environment variables should be set as required.

If the PostgreSQL database is installed on a remote host then `POSTGRES_HOST` should be changed to reflect the IP address or URL as appropriate.

### Azure OpenAI

The environment variables relating to Azure OpenAI and the chat model deployment need to be set:

```bash
AZURE_OPENAI_ENDPOINT=https://<resourcename>.openai.azure.com
AZURE_OPENAI_API_KEY=<your API key>
AZURE_OPENAI_CHAT_MODEL=gpt-4.1 # for example
AZURE_OPENAI_CHAT_MODEL_VERSION=2025-04-14 # for example
```

### Hugging Face

An access token is needed to access the `thenlper/gte-large` embedding model.

Go to [Hugging Face](https://huggingface.co/) (create an account as needed) and generate an access token named e.g. `policybot`.

Set the `HF_TOKEN` environment variable:

```bash
HF_TOKEN=<your Hugging Face access token>
```

## 4. Initialise the database

### 4.1 Run crawler to populate database 

The following script will take a while for the first time you run it as it crawls through all the files and webpages with lse.ac.uk domain name. Subsequent runs of the crawler should be quicker as it only updates the files and webpages that has changed. 

Run the following code to start the crawler :

```bash
sh scripts/start_crawlers.sh 
```

### 4.2 Run the embedding script

Set up embedding type in the **.env** file: 

```
# Select embedding type from ["simple_embeddings", "title_embeddings", "context_embeddings"]
EMBEDDING_TYPE=title_embeddings
```

The default setting is `title_embeddings` as our experiments show that it provides the best results. 

The following script will take a while for the first time you run it as it generates embeddings for all the documents in the database. Subsequent runs of the embedding script should be quicker as it only updates the embeddings for the documents that has changed.

Run the following code to start the embedding script:

```bash
sh scripts/embed_db.sh
```

## 5. Start the FastAPI APP

We need our API to be running in the background, to handle requests from the website to LLAMA and Postgres:

```bash 
sh ./scripts/start_fastapi_app.sh
```

You should see something like:

```bash
INFO:     Will watch for changes in these directories: ['<your-path-to>/chat-lse']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [7609] using WatchFiles
WARNING:  ASGI app factory detected. Using it, but please consider setting the --factory flag explicitly.
INFO:     Started server process [7611]
INFO:     Waiting for application startup.
INFO:ragapp:Authenticating to PostgreSQL using password...
INFO:ragapp:Authenticating to OpenAI using Ollama...
INFO:ragapp:Authenticating to OpenAI using Ollama...
INFO:     Application startup complete.
```

## 6. Setup and run Frontend APP

### 6.1 Install npm dependencies

```bash
# Go to chat-lse/frontend
cd frontend 
npm install
```

You might see the following warning. We can ignore it for now.

```bash
1 moderate severity vulnerability

To address all issues, run:
  npm audit fix

Run `npm audit` for details.
```

### 6.2 Start the frontend APP

Open a new terminal and run:

```bash
# Go to chat-lse/frontend
$ cd frontend 
$ npm run dev
```

You should see something like:

```bash
> frontend@0.0.0 dev
> vite


  VITE v4.5.2  ready in 309 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

## 6.3 Use the APP

Open http://localhost:5173/ in the web browser to try the app.
