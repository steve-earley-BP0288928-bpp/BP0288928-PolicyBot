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
      - [Data acquistion](#data-acquistion)
      - [Embeddings](#embeddings)
      - [Data storage](#data-storage)
    - [Example use](#example-use)

## Introduction

PolicyBot is a prototype LLM-RAG chatbot that is grounded on information and documents sourced from the website of the [London School of Economics](https://www.lse.ac.uk) (LSE).

The implementation of PolicyBot was part of an MSc research project exploring the potential benefits of using a chat interface to improve the experience of LSE administrative staff when they are searching for and accessing university polices, procedures, and other information.

The research project and PolicyBot implementation was undertaken by [Steve Earley](https://github.com/steve-earley-BP0288928-bpp) with the support of LSE.
 
### MSc research project

The research project was delivered as part of an MSc programme in Applied Data Analytics under a Digital and Technology Solutions Specialist Integrated Degree Apprenticeship run by [BPP University](https://www.bpp.com/).

The project sought to understand the current experience of LSE administratitve staff in accessing and understanding published university information, particularly official policies and procedures. There were two research hypotheses:

- That it is hard for administrative staff to find and use policy information.
- That an LLM-RAG chatbot grounded on LSE policy information would be beneficial to staff.

Quantitative research proved the first hypothesis. A second phase of qualitative research, involving a sample of volunteers, suggested the second hypothesis was also true.

The qualitative research gave participants access to PolicyBot through supervised interactive evaluation sessions.

### Original *ChatLSE* project

PolicyBot is based on a fork of the [ChatLSE](https://github.com/LSE-DSI/chat-lse) project developed by the [LSE Data Science Institute](https://www.lse.ac.uk/dsi) and coordinated and managed by [Jonathan Cardoso-Silva](https://github.com/jonjoncardoso). 

Details of the ChatLSE project are provided in [ChatLSE README](/docs/ChatLSE_README.md) and [ChatLSE CONTRIBUTING](ChatLSE_CONTRIBUTING.md) including information about the original project team and contributers.

My thanks to Jon and his team for enabling me to adapt their work for my own project.

### Modifications from ChatLSE

This section provides details of the modifications I made to the original ChatLSE application to implement PolicyBot for use in my MSc research project.

Instructions on deploying and configuring PolicyBot are available [here](CONTRIBUTING.md).

#### Hybrid architecture 

ChatLSE was designed and implemented to use only open-source components and to "serve as a blueprint for a fully open-source RAG solution".

ChatLSE was itself based on the [Rag on Postgres](https://github.com/pamelafox/rag-on-postgres) project. Modifications made included removing the requirement to use any Azure services and to remove dependencies on close-sourced OpenAI chat and embedding models. In ChatLSE the LLM component runs locally using [Ollama](https://ollama.com/).

For PolicyBot I decided to alter the architecture to reinstate the use of an OpenAI model (gpt-4.1) running in the Azure OpenAI service. This decision was made due to poor model performance under Ollama caused by resource limitations on my development computer, and to gain a better understanding of implementing an application making use of cloud services.

This change was mainly made in `src/python/chatlse/clients.py`.

PolicyBot is implemented in a hybrid architecture with the main web application (and embedding model) running locally in Python, the database component running locally in a Docker container, and the chat model running remotely in Azure.

An abstracted view of the overall system is shown in this C4 container diagram:

![PolicyBot system container diagram](/img/PolicyBot_Container_AsIs.png "PolicyBot system container diagram")

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

This imagee shows the ChatLSE and PolicyBot UIs side-by-side for comparison:

![Comparison view of ChatLSE and PolicyBot UI](/img/ui_comparison.png "Comparison view of ChatLSE and PolicyBot UI")

#### Ingesting local PDF documents 

ChatLSE was implemented to populate its document database by scraping publicly available HTML files and PDF documents from the LSE website. Some policy and procedure documents on the website are not publicly available and require authentication using an LSE account. This category of documents were relevant to my research hypothesis so for PolicyBot I added the ability to populate the document database with local copies of PDF documents.

This is a scripted process (`scripts/ingest_pdfs.sh` and `scripts/ingest_pdfs.py`) that reads PDF documents from a specified local directory and processes them using the same Python functions as the main web scraping process.

Note that the process does not itself access the documents that require authentication - this is a manual process to preserve security. The PolicyBot implementation for my research stored these local PDFs in a folder on OneDrive.

#### Logging

ChatLSE wrote logging information to a single logfile located at the project root.

For PolicyBot I added a `logs` directory and altered `fastapi_app/logger.py` to generate a separate logfile each day. This was to make the logs easier to review and to facilitate analysis of the logs recorded during the interactive evaluation sessions as part of the research project.

I also extend the information included in the logs, and added a scripted process (`scripts/ingest_pdfs.sh` and `scripts/log_parser.py`) that parses the logs and produces a csv file in the `analysis` directory that can be further analysed in e.g. Excel or Tableau etc.

## Overview of PolicyBot

### Components and workflow

Diagram based on original from [ChatLSE README](/docs/ChatLSE_README.md) document.

main view of how the app works
![a](/img/policybot_app_schematic.png "A")

explain each part in sequence
details of the models used

#### Chat Interface
User question
LLM response

#### Query Rewriter
conversation history
build a prompt
generate rewritten question

#### Query Classifier
classify how

#### Embedding
what
embedded question

#### Retrieval
hybrid search
postgresql

#### LLM
rewritten question and retrieved docs
prompts
call to chat model
return to the interface

### Data ingestion and embeddings

view of the ingest process
![d](/img/policybot_ingest_schematic.png "D")

explain each part in sequence

#### Data acquistion
scrape from web
download docs
clean and prep

#### Embeddings
simple embeddings
title embeddings
context embeddings and chatmodel

#### Data storage
include the database diagram?

![e](/img/policybot_database.png "E")

### Example use

![e](/img/policybot_example_chat.png "Chat")
![e](/img/policybot_example_thought.png "Thought")
![e](/img/policybot_example_support.png "Support")