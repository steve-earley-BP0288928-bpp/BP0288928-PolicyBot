# Contributing to _PolicyBot_

## Table of contents
- [Contributing to _PolicyBot_](#contributing-to-policybot)
  - [Table of contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Architecture and structure](#architecture-and-structure)
  - [Requirements](#requirements)
  - [1. Setup PostgreSQL locally](#1-setup-postgresql-locally)
  - [3. Setup environment](#3-setup-environment)
    - [3.1 Install Python dependencies](#31-install-python-dependencies)
    - [Set up the Azure OPenAI service HERE](#set-up-the-azure-openai-service-here)
    - [3.2 Config environment variables](#32-config-environment-variables)
      - [Set Postgres Host](#set-postgres-host)
      - [Set Huggingface Access Token](#set-huggingface-access-token)
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

You will need an [Azure subscription](https://azure.microsoft.com/en-gb/pricing/purchase-options/azure-account) with access to the Azure OpenAI service. A private endpoint and firewall rules should be confifured to allow secure connections from your development machine. All of this will need to be set up using the [Azure Portal](https://portal.azure.com/). Detailed instructions are outside the scope of this document.

The following instructions assume MacOS is being used.

## 1. Setup PostgreSQL locally

Run PostrgeSQL using docker container:

```bash
$ docker run -itd --name policybot-postgres --restart unless-stopped -p 5432:5432 -e POSTGRES_PASSWORD=policybot -e POSTGRES_USER=policybot -e POSTGRES_DB=policybot -d pgvector/pgvector:0.7.1-pg16
```

To verify the container is up and running:

```bash
$ docker ps -a

CONTAINER ID   IMAGE                          COMMAND                  CREATED         STATUS         PORTS                                       NAMES
45d7301f5ef8   pgvector/pgvector:0.7.1-pg16   "docker-entrypoint.s…"   2 seconds ago   Up 2 seconds   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   chatlse-postgres
```

The STATUS of the container shoule be something like "Up 2 seconds".


## 3. Setup environment

### 3.1 Install Python dependencies

Open the terminal in VSCode by clicking on 'Terminal' -> 'New Terminal' and create a virtual environment. 

```bash
# Use conda as an example. Can also use other virtual environments like venv

conda create -n policybot python=3.11 ipython
conda activate policybot # or the equivalent for your OS
```

(Important) Ensure that `pip` refers to the pip inside the conda environment we just created:

```bash
which pip
```

This should output something like `/home/your-username/miniconda3/envs/chat-lse/bin/pip`

Install dependencies 

```bash
pip install -r requirements.txt
```

### Set up the Azure OPenAI service HERE


### 3.2 Config environment variables

Copy **.env.sample** into **.env**.

#### Set Postgres Host

```
# For local setup
POSTGRES_HOST=localhost
```

```
# Remote setup, for testing and deployment only
POSTGRES_HOST=<Host IP address>
```


#### Set Huggingface Access Token

```
# Required for access to thenlper/gte-large
HF_TOKEN=<obtain access token from Huggingface>
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
