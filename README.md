# PolicyBot

**Table of contents**

- [PolicyBot](#policybot)
  - [Introduction](#introduction)
    - [MSc research project](#msc-research-project)
    - [Original *ChatLSE* project](#original-chatlse-project)
    - [Modifications from ChatLSE](#modifications-from-chatlse)
      - [Hybrid architecture](#hybrid-architecture)
      - [LLM prompts](#llm-prompts)
      - [User interface](#user-interface)
      - [Ingesting local PDF documents](#ingesting-local-pdf-documents)
      - [Logging](#logging)
  - [Overview of PolicyBot](#overview-of-policybot)
    - [Components and workflow](#components-and-workflow)
      - [Chat Interface](#chat-interface)
      - [Query Rewriter](#query-rewriter)
      - [Query Classifier](#query-classifier)
      - [Embedding](#embedding)
      - [Retrieval](#retrieval)
      - [LLM](#llm)
    - [Data ingestion and embeddings](#data-ingestion-and-embeddings)
      - [Data acquisition](#data-acquisition)
        - [Files and documents on LSE website](#files-and-documents-on-lse-website)
        - [Documents stored locally](#documents-stored-locally)
      - [Embeddings](#embeddings)
      - [Data storage](#data-storage)
    - [Example use](#example-use)

## Introduction

PolicyBot is a prototype LLM-RAG (Large Language Model with Retrieval Augmented Generation) chatbot that is grounded on information and documents sourced from the website of the [London School of Economics](https://www.lse.ac.uk) (LSE).

The implementation of PolicyBot was part of an MSc research project exploring the potential benefits of using a chat interface to improve the experience of LSE administrative staff when they are searching for and accessing university polices, procedures, and other information.

The research project and PolicyBot implementation was undertaken by [Steve Earley](https://github.com/steve-earley-BP0288928-bpp) with the support of LSE.
 
### MSc research project

The research project was delivered as part of an MSc programme in Applied Data Analytics under a Digital and Technology Solutions Specialist Integrated Degree Apprenticeship run by [BPP University](https://www.bpp.com/).

The project sought to understand the current experience of LSE administrative staff in accessing and understanding published university information, particularly official policies and procedures. There were two research hypotheses:

- That it is hard for administrative staff to find and use policy information.
- That an LLM-RAG chatbot grounded on LSE policy information would be beneficial to staff.

Quantitative research proved the first hypothesis. A second phase of qualitative research, involving a sample of volunteers, suggested the second hypothesis was also true.

The qualitative research gave participants access to PolicyBot through supervised interactive evaluation sessions.

### Original *ChatLSE* project

PolicyBot is based on a fork of the [ChatLSE](https://github.com/LSE-DSI/chat-lse) project developed by the [LSE Data Science Institute](https://www.lse.ac.uk/dsi) and coordinated and managed by [Jonathan Cardoso-Silva](https://github.com/jonjoncardoso). 

Details of the ChatLSE project are provided in [ChatLSE README](/docs/ChatLSE_README.md) and [ChatLSE CONTRIBUTING](ChatLSE_CONTRIBUTING.md) including information about the original project team and contributors.

My thanks to Jon and his team for enabling me to adapt their work for my own project.

### Modifications from ChatLSE

This section provides details of the modifications I made to the original ChatLSE application to implement PolicyBot for use in my MSc research project.

Instructions on deploying and configuring PolicyBot are available [here](CONTRIBUTING.md).

#### Hybrid architecture 

ChatLSE was designed and implemented to use only open-source components and to "serve as a blueprint for a fully open-source RAG solution" ([ChatLSE README](/docs/ChatLSE_README.md)).

ChatLSE was itself based on the [Rag on Postgres](https://github.com/pamelafox/rag-on-postgres) project. Modifications made included removing the requirement to use any Azure services and to remove dependencies on close-sourced OpenAI chat and embedding models. In ChatLSE the LLM component runs locally using [Ollama](https://ollama.com/).

For PolicyBot I decided to alter the architecture to reinstate the use of an OpenAI model (`gpt-4.1`) running in the Azure OpenAI service. This decision was made due to poor model performance under Ollama caused by resource limitations on my development computer, and to gain a better understanding of implementing an application making use of cloud services.

This change was mainly made in `src/python/chatlse/clients.py`.

PolicyBot is implemented in a hybrid architecture with the main web application (and embedding model) running locally in Python, the database component running locally in a Docker container, and the chat model running remotely in Azure.

An abstracted view of the overall system is shown in this C4 container diagram:

![PolicyBot system container diagram](/img/policybot_container_asis.png "PolicyBot system container diagram")

#### LLM prompts

ChatLSE was intended to be used by both LSE students and staff for general queries about university information, without any specific focus on administrative policy documents etc.

I altered the LLM prompts to reflect the narrower purpose of PolicyBot for my research. This involved mainly minor changes e.g. removing references to students but with some more specific rephrasing for example:

```diff
- An assistant at the London School of Economics (LSE) answer queries that staff and students may have. 
+ An assistant at the London School of Economics and Political Science (LSE) answer queries that staff may have. 
+ The assistant answers questions related to administrative aspect of LSE including policies and procedures. 
```

For reference, the prompts are found in `fastapi_app/prompts`.

#### User interface

It was important for my research project that the user interface (UI) of PolicyBot clearly reflected its purpose and differentiated it from the original ChatLSE UI.

I added the BPP University logo, altered the colour scheme through changes to the CSS files, and modified the text and labels used for the user input fields. These changes were made to multiple files in `frontend/src` in particular `frontend/src/pages/chat/Chat.tsx`.

This image shows the ChatLSE and PolicyBot UIs side-by-side for comparison:

![Comparison view of ChatLSE and PolicyBot UI](/img/ui_comparison.png "Comparison view of ChatLSE and PolicyBot UI")

#### Ingesting local PDF documents 

ChatLSE was implemented to populate its document database by scraping publicly available HTML files and PDF documents from the LSE website. Some policy and procedure documents on the website are not publicly available and require authentication using an LSE account. This category of documents were relevant to my research hypothesis so for PolicyBot I added the ability to populate the document database with local copies of PDF documents.

This is a scripted process (`scripts/ingest_pdfs.sh` and `scripts/ingest_pdfs.py`) that reads PDF documents from a specified local directory and processes them using the same Python functions as the main web scraping process.

Note that the process does not itself access the documents that require authentication - this is a manual process to preserve security. The PolicyBot implementation for my research stored these local PDFs in a folder on OneDrive.

#### Logging

ChatLSE wrote logging information to a single log file located at the project root.

For PolicyBot I added a `logs` directory and altered `fastapi_app/logger.py` to generate a separate log file each day. This was to make the logs easier to review and to facilitate analysis of the logs recorded during the interactive evaluation sessions as part of the research project.

I also extended the information included in the logs, and added a scripted process (`scripts/parse_logs.sh` and `scripts/log_parser.py`) that parses the logs and produces a csv file in the `analysis` directory that can be further analysed in e.g. Excel or Tableau etc.

## Overview of PolicyBot

An overview of the PolicyBot implementation describing:

- The main parts of the application and broadly how it works.
- The process for populating the document database.
- An example of PolicyBot in use.

### Components and workflow

This diagram is a schematic view of the various parts of the PolicyBot application and shows conceptually how they function to respond to questions asked by a user:

![Schematic view of the PolicyBot application](/img/policybot_app_schematic.png "Schematic view of the PolicyBot application")

The diagram is based on the original version shown in [ChatLSE README](/docs/ChatLSE_README.md).

#### Chat Interface

This part provides a user interface (UI) accessed through a web browser that allows a user to ask questions and receive responses.

Restrictions are imposed on the scope of questions that can be answered by PolicyBot. Users are able to engage in extended interactions with PolicyBot in a conversational style. The UI has features that enable the user to see the thought process applied by the application and to review the document chunks that were retrieved to support the answer. 

This is implemented in `frontend`.

#### Query Rewriter

This part determines if the user is asking a question for the first time or if there is an existing conversation history.

If there is a history then this is combined with the latest question and rewritten by the LLM chat model to create an extended question with additional context. Otherwise, the question is left as asked by the user.

This is implemented in `fastapi_app/rag_advanced.py` and `src/python/chatlse/llm_functions.py`.

#### Query Classifier

This part attempts to classify the question using various LLM prompts to determine the best method of generating a response to the user.

If a question appears to be a greeting (e.g. "Hello...", "Hi...") or a farewell (e.g. "Goodbye...", "Thanks that's all") then PolicyBot is able to respond in a appropriate way, according to its prompts, and without using RAG.

If a question appears to be out of scope (based on various rules defined in the prompts) then the user is informed of this.

Otherwise if the question is in scope then it is classified as 'relevant' and the application proceeds to attempt to use RAG to generate an answer.

This is implemented in `fastapi_app/rag_advanced.py` and the prompts are held in `fastapi_app/prompts`.

#### Embedding

This part takes questions that are relevant and uses the local embedding model (`thenlper/gte-large`) to generate embeddings for the question, to be used in a vector similarity search.

There are three [types of embeddings](#embeddings) that can be used by PolicyBot.

This is implemented in `fastapi_app/rag_advanced.py` and `src/python/chatlse/embeddings.py`.

#### Retrieval

This part takes the question and the embeddings for the question and uses them to perform a hybrid search against the PostgreSQL database that stores chunked versions of LSE documents and embeddings of those chunks, using the pgvector extension. The hybrid search is achieved using a prepared SQL statement that combines a vector similarity search and a full text query search.

The relevant retrieved document chunks are combined with the users question and passed to the LLM to generate a response.

This is implemented in `fastapi_app/rag_advanced.py` and `fastapi_app/postgres_searcher.py`.

#### LLM

This part makes API calls to a chat completions and response model (`gpt-4.1`) deployed in the Azure OpenAI service.

The response is returned to the user through the user interface.

This is implemented in `fastapi_app/rag_advanced.py` and `src/python/chatlse/clients.py`.

### Data ingestion and embeddings

This diagram is a schematic view of the process for populating the PostgreSQL database and generating embeddings to enable the RAG capability of the PolicyBot application:

![Schematic view of the data ingestion and embeddings process](/img/policybot_ingest_schematic.png "Schematic view of the data ingestion and embeddings process")

This processes for this are manually executed and can be adjusted and repeated as required to change the scope and range of information available through PolicyBot.

#### Data acquisition

This part populates the database used by PolicyBot with information (HTML files and PDF documents) scraped from the LSE website, or with copies of PDF documents stored locally, or a combination of the two.

##### Files and documents on LSE website

This process uses [Crawley](https://github.com/elixir-crawly/crawly) to scrape the LSE website for publicly available HTML files and documents (limited for practical purposes to PDFs) using conditions and URL starting points defined in `crawler/spiders`.

The scraped files and documents are converted to plain text, split into overlapping chunks, and stored in the PostgreSQL database.

The process is executed on demand by the script `scripts/start_crawlers.sh`.

##### Documents stored locally

This process reads PDF documents stored in a locally accessible folder. Documents are converted to plain text, split into overlapping chunks, and stored in the PostgreSQL database following the same approach used for data scraped from the LSE website.

The process is executed on demand by the script `scripts/ingest_pdfs.sh`. It uses `scripts/ingest_pdfs.py`.

#### Embeddings

This part uses the local embedding model (`thenlper/gte-large`) to generate embeddings for the stored document chunks and adds those embedding to the database.

There are three embedding types supported by the PolicyBot application:

- Simple embeddings
- Title embeddings
- Context embeddings

With the **Simple** type each document chunk is embedded without any additional context.

With the **Title** type each document chunk is combined with the title of the document and the resulting text is embedded, providing some additional context.

With the **Context** type each document chunk is combined with the title of the document and also combined with a summary of the whole document, and the resulting text is embedded, providing greater context. Note that to generate the summary of the document this embedding type uses the Azure OpenAI service.

Embeddings can be generated for one or more of the embedding types and the PolicyBot application can be directed to use a specific type of embedding by setting an environment variable.

The process is executed on demand by the script `scripts/embed_db.sh`. It uses `scripts/embed_db.py` and `src/python/chatlse/embeddings.py`.

#### Data storage

The document chunks and embeddings are written to the PostgreSQL database. This uses a simple data archiecture as shown in this diagram:

![PolicyBot database structure](/img/policybot_database.png "PolicyBot database structure")

The `lse_doc` table stores the documents split into one or more document chunks, where each chunk is identified by a sequential `chunk_id` related to a `doc_id` generated from a hash of the whole document. The text of the chunk is stored in the `content` column. Three columns are used to store the respective embeddings.

The `doc_summary` table is only populated if the Context embedding type is used. The table stores the text of the document in the `content` column and the LLM-generated summary of the document in the `summary` column. There is an implied relationship between the two tables.

### Example use

Simple examples of PolicyBot in use.

The first image shows a typical question and response interaction. The first question asked by the user has been answered by PolicyBot with reference to two LSE documents with the relevant sources indicated in the response.

![PolicyBot chat](/img/policybot_example_chat.png "PolicyBot Chat")

In the second image the lightbulb icon (💡) has been clicked to reveal the 'thought process' applied by PolicyBot. This shows that the application used the RAG functionality to answer the question and provides details of the database search results and the prompt passed to the OpenAI service.

![PolicyBot Thought](/img/policybot_example_thought.png "PolicyBot Thought")

In the third image the clipboard icon (📋) has been clicked to reveal the document chunks used as supporting content for the response.

![PolicyBot Support](/img/policybot_example_support.png "PolicyBot Support")