# Contributing to PolicyBot

Adapted and updated from the original [ChatLSE CONTRIBUTING](/docs/ChatLSE_CONTRIBUTING.md) document.

**Table of contents**
- [Contributing to PolicyBot](#contributing-to-policybot)
  - [Introduction](#introduction)
  - [Architecture and structure](#architecture-and-structure)
  - [Requirements](#requirements)
  - [Initial implementation](#initial-implementation)
    - [Clone the project](#clone-the-project)
    - [Set up PostgreSQL database in Docker](#set-up-postgresql-database-in-docker)
    - [Set up Python virtual environment and dependencies](#set-up-python-virtual-environment-and-dependencies)
    - [Add a model deployment in Azure OpenAI service](#add-a-model-deployment-in-azure-openai-service)
    - [Configure environment variables](#configure-environment-variables)
      - [PostgreSQL](#postgresql)
      - [Azure OpenAI](#azure-openai)
      - [Hugging Face](#hugging-face)
    - [Populate the database](#populate-the-database)
      - [Remote content](#remote-content)
      - [Local content](#local-content)
      - [Generate embeddings](#generate-embeddings)
    - [Start the backend of the web app](#start-the-backend-of-the-web-app)
    - [Set up and start the frontend of the web app](#set-up-and-start-the-frontend-of-the-web-app)
      - [Install npm dependencies](#install-npm-dependencies)
      - [Start the frontend](#start-the-frontend)
    - [Test the web app](#test-the-web-app)
  - [Running PolicyBot after implementation](#running-policybot-after-implementation)

## Introduction

The PolicyBot project is based on a fork of the [ChatLSE](https://github.com/LSE-DSI/chat-lse) project developed by the [LSE Data Science Institute](https://www.lse.ac.uk/dsi), which itself was based on the [Rag on Postgres](https://github.com/pamelafox/rag-on-postgres) project.

Major modifications made:

- Altered to use Azure OpenAI service.
- Altered LLM prompts to focus on providing policy assistance to LSE staff.
- Added process for ingesting additional PDF documents.

Minor modifications made:

- Altered user interface to reflect the specific purpose of PolicyBot.
- Altered logging approach to create date-based logs with additional information logged.
- Resolved a TypeError issue in the main chat function.

The code has been fully tested on MacOS (Intel and M2) and partially tested on Ubuntu 22.04 LTS.

## Architecture and structure

The high-level architecture of the PolicyBot application is shown here:

![High-level architecture of the PolicyBot application](/img/policybot_simple_architecture.png "High-level architecture of the PolicyBot application")

There are four main components:

- The frontend of the PolicyBot web app, built using [ReactJS](https://react.dev/) and [FluentUI](https://github.com/microsoft/fluentui).
- The backend of the web app, built using [FastAPI](https://fastapi.tiangolo.com/) and Python.
- A [PostgreSQL](https://www.postgresql.org/) database, deployed locally using [Docker](https://www.docker.com/).
- A chat model, deployed remotely using [Azure OpenAI](https://ai.azure.com/) service.

The application also uses a [local embedding model](https://developers.llamaindex.ai/python/examples/embeddings/huggingface/) in Python.

A scripted process uses [Crawley](https://github.com/elixir-crawly/crawly) to populate the database with documents scraped from the [LSE website](https://www.lse.ac.uk/). An additional process is used to ingest locally-stored PDF documents.

To run the application all four components must be installed and configured correctly. For development purposes both components of the web app - the Frontend and Backend - should be colocated. The database can optionally be installed on a remote service e.g. in [Azure Database for PostgreSQL](https://azure.microsoft.com/en-us/products/postgresql).

## Requirements

The following software needs to be installed on your development machine before proceeding: 

- [Conda](https://anaconda.org/) (or equivalent package manager - Conda is assumed here)
- [Docker](https://docs.docker.com/desktop/)
- [nvm](https://github.com/nvm-sh/nvm)
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
- [Node.js](https://nodejs.org/en/download/)
- [VSCode](https://code.visualstudio.com/) (or your preferred IDE)

These instructions assume MacOS is being used.

You will need an [Azure subscription](https://azure.microsoft.com/en-gb/pricing/purchase-options/azure-account) with access to the Azure OpenAI service. A private endpoint and firewall rules should be confifured to allow secure connections from your development machine. All of this will need to be set up using the [Azure Portal](https://portal.azure.com/). Detailed instructions are outside the scope of this document.

## Initial implementation

These are the steps required to get PolicyBot installed, configured, and working for the first time. With the exception of populating the database they are steps that only need to be performed once.

### Clone the project

Clone the PolicyBot project repository from GitHub:

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

### Set up PostgreSQL database in Docker

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

### Set up Python virtual environment and dependencies

Create and activate a virtual environment for PolicyBot (this uses Conda but other virtual environments like venv could be used):

```bash
conda create -n policybot python=3.11 ipython
conda activate policybot
```

**Important** - ensure that `pip` refers to the pip inside the Conda environment just created:

```bash
which pip
/opt/anaconda3/envs/policybot/bin/pip
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Add a model deployment in Azure OpenAI service

Go to [Azure OpenAI](https://ai.azure.com/) service.

Navigate to `Shared resources > Deployments` and deploy a model suitable for chat completions and responses, for example `gpt-4.1`.

You will need details from the model deployment later.

### Configure environment variables

Copy the file `.env.sample` into `.env`.

As the `.env` file will hold secrets such as API keys it is gitignored.

#### PostgreSQL

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

#### Azure OpenAI

The environment variables relating to Azure OpenAI and the chat model deployment need to be set:

```bash
AZURE_OPENAI_ENDPOINT=https://<resourcename>.openai.azure.com
AZURE_OPENAI_API_KEY=<your API key>
AZURE_OPENAI_CHAT_MODEL=gpt-4.1 # for example
AZURE_OPENAI_CHAT_MODEL_VERSION=2024-12-01-preview # for example
```

#### Hugging Face

An access token is needed to access the `thenlper/gte-large` embedding model.

Go to [Hugging Face](https://huggingface.co/) (create an account as needed) and generate an access token named e.g. `policybot`.

Set the `HF_TOKEN` environment variable:

```bash
HF_TOKEN=<your Hugging Face access token>
```

### Populate the database

The database needs to be populated with content for PolicyBot to use. This can be:

- Remote content - HTML files and PDF documents that are publicly available on the LSE website.
- Local content - PDF documents that are held in local storage.

It is not essential to populate the database with both types of content. Additional content can be added to the database at any point. As PolicyBot is a RAG-based chatbot how well it performs is related to the information it is able to reference for its responses.

#### Remote content

Run this script to scrape content from the LSE website:

```bash
sh scripts/start_crawlers.sh 
```

The script runs one or more crawlers defined in the `spiders` directory of the project.

The script will take a considerable amount of time to complete when it is first run. Subsequent runs will be quicker as it will only process files or documents that have changed compared to the versions in the database.

Note that it is safe to interrupt and restart the script.

#### Local content

Create or identify a local directory for storing PDF documents to ingest to the database. This can be any accessible directory including, for example, a locally synchronised folder from OneDrive.

Set the `OFFLINE_PDFS_DIR` environment variable with the path to the directory:

```bash
# Local directory holding copies of PDF documents to ingest
OFFLINE_PDFS_DIR='
```

Run this script to ingest the PDFs:

```bash
sh scripts/ingest_pdfs.sh 
```

The script can be run multiple times as it will only process documents that have changed compared to the versions in the database.

Note that it is safe to interrupt and restart the script.

#### Generate embeddings

Define the required embedding type environment variable in the `.env file: 

```bash
# Select embedding type from ["simple_embeddings", "title_embeddings", "context_embeddings"]
EMBEDDING_TYPE=title_embeddings
```

The default setting is `title_embeddings` as the original _ChatLSE_ project found through experimentation that this embedding type provides the best results.

Note that whilst the `simple_embeddings` and `title_embeddings` embedding types use the local embedding model, the `context_embeddings` embedding type additionally uses the remote chat model to summarise documents. This increases the time taken to generate embeddings and potentially incurs a considerable cost given the high token usage required.

Run this script to generate the embeddings:

```bash
sh scripts/embed_db.sh
```

You will see the script outputting something like this:
```
2025-12-14 17:22:23,870 INFO sqlalchemy.engine.Engine
                UPDATE lse_doc SET title_embeddings = %(title_embeddings)s WHERE id = %(id)s

INFO:sqlalchemy.engine.Engine:
                UPDATE lse_doc SET title_embeddings = %(title_embeddings)s WHERE id = %(id)s

2025-12-14 17:22:23,870 INFO sqlalchemy.engine.Engine [generated in 0.00034s] {'title_embeddings': [0.007386937737464905, -0.010910234414041042, -0.03177380934357643, -0.0029778603930026293, -0.011845835484564304, 0.011221017688512802, 0.00649735145 ... (22397 characters truncated) ... .06648965924978256, 0.0506301186978817, 0.05630011111497879, -0.011488036252558231, -0.02514929324388504, -0.015085604973137379, 0.016696428880095482], 'id': 'ea50b4c2c790dce7a78046ae639a310a_0'}
INFO:sqlalchemy.engine.Engine:[generated in 0.00034s] {'title_embeddings': [0.007386937737464905, -0.010910234414041042, -0.03177380934357643, -0.0029778603930026293, -0.011845835484564304, 0.011221017688512802, 0.00649735145 ... (22397 characters truncated) ... .06648965924978256, 0.0506301186978817, 0.05630011111497879, -0.011488036252558231, -0.02514929324388504, -0.015085604973137379, 0.016696428880095482], 'id': 'ea50b4c2c790dce7a78046ae639a310a_0'}
2025-12-14 17:22:23,885 INFO sqlalchemy.engine.Engine COMMIT
INFO:sqlalchemy.engine.Engine:COMMIT
INFO:ragapp:Embedding calculated and updated for id: ea50b4c2c790dce7a78046ae639a310a_0
INFO:ragapp:Embedding chunk 1/3057
INFO:ragapp:Embedding chunks...
```

The script will take a considerable amount of time to complete when it is first run. Subsequent runs will be quicker as it will only generate embeddings for files or documents that have changed compared to the versions in the database.

Note that it is safe to intersrupt and restart the script.

### Start the backend of the web app

The backend of the web app provides an API that handles requests from the frontend. It needs to be running before the frontend can be started.

Run this script to start the backend:

```bash 
sh scripts/start_backend.sh
```

You should see something like this:

```bash
INFO:     Will watch for changes in these directories: ['<your-path-to>/policybot']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [4665] using WatchFiles
[nltk_data] Downloading package punkt_tab to
[nltk_data]     /opt/anaconda3/envs/policybot/lib/python3.11/site-
[nltk_data]     packages/llama_index/core/_static/nltk_cache...
[nltk_data]   Package punkt_tab is already up-to-date!
INFO:ragapp:Start API ...
INFO:ragapp:ChatClass: QueryRewriterRAG
WARNING:  ASGI app factory detected. Using it, but please consider setting the --factory flag explicitly.
INFO:     Started server process [4672]
INFO:     Waiting for application startup.
INFO:ragapp:Creating AsyncAzureOpenAI Chat Client
INFO:ragapp:Chat Client: <openai.lib.azure.AsyncAzureOpenAI object at 0x175c6dfd0>
INFO:ragapp:Chat Model Selected: gpt-4.1
INFO:ragapp:Embedding Type: title_embeddings
INFO:ragapp:With User Context: True
INFO:sentence_transformers.SentenceTransformer:Load pretrained SentenceTransformer: thenlper/gte-large
INFO:ragapp:Embed Model Selected: model_name='thenlper/gte-large' embed_batch_size=10 callback_manager=<llama_index.core.callbacks.base.CallbackManager object at 0x1779f9cd0> num_workers=None max_length=512 normalize=True query_instruction=None text_instruction=None cache_folder=None
INFO:     Application startup complete.
```

### Set up and start the frontend of the web app

#### Install npm dependencies

Open a new Terminal/CLI session and run the following:

```bash
# go to ~policybot/frontend
cd frontend 
npm install
```

You might something like the following warning:

```bash
added 264 packages, and audited 265 packages in 16s

10 vulnerabilities (8 moderate, 2 high)

To address issues that do not require attention, run:
  npm audit fix

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
```

Depending on the number and nature of the vulnerabilities reported you can fix these now or later, using the commands indicated.

#### Start the frontend

Run the following:

```bash
# Go to chat-lse/frontend
$ cd frontend 
$ npm run dev
```

You should see something like:

```bash
> frontend@0.0.0 dev
> vite


  VITE v7.2.7  ready in 797 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Test the web app

Using a web browser open the following URL:

`http://localhost:5173/`

You should see the PolicyBot user interface:

![PolicyBot web app UI](/img/policybot_UI.png "PolicyBot web app UI")

Test PolicyBot by asking a question!

## Running PolicyBot after implementation

Assuming you will be starting and stopping PolicyBot on a regular basis this is the procedure to follow:

- Start the PostgreSQL database in Docker.
- Start the backend in one Terminal/CLI session: `cd ~policybot; sh scripts/start_backend.sh` (remember to activate the `policybot` Conda environment).
- Start the frontend in another Terminal/CLI session: `cd ~policybot; sh scripts/start_frontend.sh` (remember to activate the `policybot` Conda environment).
- Open `http://localhost:5173/` in a web browser.

The session where the backend is running will show a stream of information about what the application is doing. Additionally the application writes logfiles in `~/policybot/logs` with date-based filenames for example `app_log_2025-12-14.log`.

As multiple Terminal/CLI sessions are required a script is provided to make the process simpler. The script is specifically for use on MacOS and does require a symbolic link to the code directory to exist in your home directory.

This is the procedure to follow for running PolicyBot using the script:

- Start the PostgreSQL database in Docker.
- Open a Terminal/CLI session.
- Run `sh ~/policybot/scripts/run_app.sh`.

Separate Terminal windows will be opened, running the backend and frontend components of the web app, and tailing the log file. The URL will be opened in a Safari session. It will look something like this:

![PolicyBot running](/img/policybot_multi_windows.png "PolicyBot running")

The script dynamically sizes and positions the windows based on the size of the Mac display, so it will run equally well on for example a 24" iMac and a 13" MacBook 