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
    - [Example](#example)

## Introduction

### MSc research project

Research project background and context for the chatbot

how used in research

### Original *ChatLSE* project

refer to original [ChatLSE README](/docs/ChatLSE_README.md) document.

The project is coordinated and managed by [Jonathan Cardoso-Silva](https://github.com/jonjoncardoso). 

_This repository is always a work in progress and **everyone** is encouraged to help us build something that is useful to the many._

Everyone who joins the project should check out our [contributing guidelines](ChatLSE_CONTRIBUTING.md) for more information on how to get started.

Community members are provided with opportunities to learn new skills, share their ideas and collaborate with others.

### Modifications from ChatLSE

reference Contributing guide 

#### Hybrid architecture 

architecture changes - azure openai

how this diverges from the original aims of chatlse

#### LLM prompts

#### User interface

UI changes

#### Ingesting local PDF documents 

ingest of local pdf documetns

#### Logging
logging

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

### Example 

![e](/img/policybot_example_chat.png "Chat")
![e](/img/policybot_example_thought.png "Thought")
![e](/img/policybot_example_support.png "Support")