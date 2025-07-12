import os
import openai
from openai import AzureOpenAI  # 11-JUL-2025
from openai import AsyncAzureOpenAI  # 11-JUL-2025
import logging
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

logger = logging.getLogger("ragapp")

DEFAULT_EMBED_MODEL = "thenlper/gte-large"
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_MODEL = os.getenv("AZURE_OPENAI_CHAT_MODEL")
AZURE_OPENAI_CHAT_MODEL_VERSION = os.getenv("AZURE_OPENAI_CHAT_MODEL_VERSION")

logger.info("LOADED clients.py")


async def create_chat_client():
    # logger.info("Creating Ollama Chat Client")
    # chat_client = openai.AsyncOpenAI(
    #     base_url=os.getenv("OLLAMA_ENDPOINT"),
    #     api_key="nokeyneeded",
    # )

    # 11-JUL-2025
    logger.info("Creating AsyncAzureOpenAI Chat Client in clients")
    chat_client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_CHAT_MODEL_VERSION
    )
    chat_model = AZURE_OPENAI_CHAT_MODEL

    return chat_client, chat_model


async def create_embed_client():
    logger.info("Initialising Embedding model")
    embed_model = HuggingFaceEmbedding(model_name=os.getenv(
        "OLLAMA_EMBED_MODEL", DEFAULT_EMBED_MODEL))
    return embed_model
