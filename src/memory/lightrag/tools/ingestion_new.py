import os
from sys import api_version
import nest_asyncio
from dotenv import load_dotenv
from lightrag.utils import EmbeddingFunc
from openai import AzureOpenAI
from lightrag import LightRAG
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.llm.azure_openai import azure_openai_complete
from lightrag.kg.shared_storage import initialize_share_data, initialize_pipeline_status
import aiohttp
from configparser import ConfigParser

nest_asyncio.apply()

config = ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), '..\..\config.ini')
config_path = os.path.abspath(config_path)
print("Loading config from:", config_path)
read_files = config.read(config_path)
if not read_files:
    raise FileNotFoundError(f"Could not find config.ini at {config_path}")

azure_api_key = config.get('Azure_OpenAI_Model', 'api_key')
azure_api_base = config.get('Azure_OpenAI_Model', 'api_base')
azure_api_version = config.get('Azure_OpenAI_Model', 'api_version')
azure_deployement_name = config.get('Azure_OpenAI_Model', 'llm_model')

os.environ["NEO4J_URI"] = config.get("Neo4j_Database", "neo4j_bolt_uri", fallback="bolt://localhost:7687")
os.environ["NEO4J_USERNAME"] = config.get("Neo4j_Database", "neo4j_user")
os.environ["NEO4J_PASSWORD"] = config.get("Neo4j_Database", "neo4j_password")

embedding_dim = config.getint("Ollama_Model", "embedding_model_dims", fallback="1024")
max_token_size = config.getint("Ollama_Model", "embedding_model_max_tokens", fallback="8192")
base_url = config.get("Ollama_Model", "base_url")
embedding_model = config.get("Ollama_Model", "embedding_model")

# AZURE_EMBEDDING_DEPLOYMENT = "gpt-4o"
# AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION")



async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], **kwargs
) -> str:
    headers = {
        "Content-Type": "application/json",
        "api-key": azure_api_key,
    }
    endpoint = f"{azure_api_base}openai/deployments/{azure_deployement_name}/chat/completions?api-version={azure_api_version}"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    payload = {
        "messages": messages,
        "temperature": kwargs.get("temperature", 0),
        "top_p": kwargs.get("top_p", 1),
        "n": kwargs.get("n", 1),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, headers=headers, json=payload) as response:
            if response.status != 200:
                raise ValueError(
                    f"Request failed with status {response.status}: {await response.text()}"
                )
            result = await response.json()
            return result["choices"][0]["message"]["content"]

# async def test_funcs():
#     while True:
#         question = input("Please ask the question. q for quit")
#         print("-----------------------------------")
#         if question == 'q':
#             return
#         result = await llm_model_func(question)
#         print("Response from llm_model_func: ", result)
#         print("=======================================")

    # result = await embedding_func(["How are you?"])
    # print("Resultado do embedding_func: ", result.shape)
    # print("Dimensão da embedding: ", result.shape[1])


# asyncio.run(test_funcs())

async def initialize_rag(working_dir: str = "./srivastava"):
    
    rag = LightRAG(
        working_dir=working_dir,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=embedding_dim,
            max_token_size=max_token_size,
            func=lambda texts: ollama_embed(
                texts,
                embed_model=embedding_model,
                host=base_url,
            ),
        ),
        # graph_storage="Neo4JStorage",
        vector_storage="FaissVectorDBStorage",
        chunk_token_size=1000,
        chunk_overlap_token_size=200,
    )

    await rag.initialize_storages()
    initialize_share_data()
    await initialize_pipeline_status()

    return rag


async def index_data(rag: LightRAG, proj_dir: str) -> None:
    """
    Index a text file into LightRAG, tagging chunks with its filename.
    """
    source_dir = proj_dir
    input_list = []
    path_list = []
    for file in os.listdir(source_dir):
        with open(os.path.join(source_dir,file), "r", encoding='utf-8') as text:
            content = text.read()
            input_list.append(content)
            path_list.append(os.path.join(source_dir,file))

    # stream chunks into vector store and graph
    print("files has been read")
    # print(text[:100])
    for i in range(len(input_list)):
        await rag.ainsert(input=input_list[i], file_paths=[path_list[i]])
        print(f"File {path_list[i]} has been inserted")

async def index_file(rag: LightRAG, proj_dir: str) -> None:
    """
    Alias for index_data to mirror sync naming.
    """
    await index_data(rag, proj_dir)