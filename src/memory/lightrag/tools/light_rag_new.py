from .ingestion_new import initialize_rag, index_file
# from .retrieval_new import run_async_query
from dotenv import load_dotenv
import asyncio
from datasets import Dataset
from ragas.metrics import faithfulness, answer_relevancy, context_recall, answer_similarity, answer_correctness
from ragas import evaluate
from ragas.dataset_schema import SingleTurnSample
# from ragas.metrics._bleu_score import BleuScore
# from langchain_openai import AzureChatOpenAI
# from langchain_ollama import OllamaEmbeddings
import os
# from .validate import validateResponse
from configparser import ConfigParser
from server import mcp
import traceback
from lightrag import QueryParam

config = ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), r'..\..\config.ini')
config_path = os.path.abspath(config_path)
print("Loading config from:", config_path)
read_files = config.read(config_path)
if not read_files:
    raise FileNotFoundError(f"Could not find config.ini at {config_path}")

azure_api_key = config.get('Azure_OpenAI_Model', 'api_key')
azure_api_base = config.get('Azure_OpenAI_Model', 'api_base')
azure_api_version = config.get('Azure_OpenAI_Model', 'api_version')
azure_deployement_name = config.get('Azure_OpenAI_Model', 'llm_model')

embedding_dim = config.getint("Ollama_Model", "embedding_model_dims", fallback="1024")
max_token_size = config.getint("Ollama_Model", "embedding_model_max_tokens", fallback="8192")
base_url = config.get("Ollama_Model", "base_url")
embedding_model = config.get("Ollama_Model", "embedding_model")

@mcp.tool()
async def lightrag_new_tool(directory_selection:str=None, question:str=None, history:list=[]) -> dict:
    """
    1. Initialize RAG
    2. Index file (open file, read file, chunking, stream each chunk to both vector store and knowldege graph) all being done by rag.ainsert().
    3. Run async queries
    """
    try:

        domain = 'Project Management'

        if domain == 'Project Management':
            data_path = '../data/Project'
            working_dir = '../data/Aadarsh_Project'
        elif domain == 'HR':
            data_path = '../data/HR'
            working_dir = '../data/Aadarsh_HR'
        else:
            data_path = '../data/Insurance'
            working_dir = '../data/Aadarsh_Insurance'

        rag = await initialize_rag(working_dir=working_dir)
        # await index_file(rag=rag, proj_dir=data_path) # this function wait here until all files be
        source_dir = data_path
        input_list = []
        path_list = []
        for file in os.listdir(source_dir):
            with open(os.path.join(source_dir,file), "r", encoding='utf-8') as text:
                content = text.read()
                input_list.append(content)
                path_list.append(os.path.join(source_dir,file))

        # stream chunks into vector store and graph

        for i in range(len(input_list)):
            rag.insert(input=input_list[i], file_paths=[path_list[i]])
        # conversation_history_naive = chat_history_naiverag

        # eval
        # with open("./data/questions_new.txt", "r") as file:
        #     lines = file.readlines()

        # questions = [line.strip() for line in lines]

        # with open("./data/answers_new.txt", "r") as file:
        #     lines = file.readlines()

        # answers = [line.strip() for line in lines]




        # run query
        # llm = AzureChatOpenAI(
        #     deployment_name = azure_deployement_name,
        #     api_key = azure_api_key,
        #     azure_endpoint = azure_api_base,
        #     api_version = azure_api_version,
        # )

        # embeddings = OllamaEmbeddings(
        #     model = embedding_model,
        #     base_url = base_url,
        # )

        response = {}

        mode="mix"
        # resp_async, context_mix = await run_async_query(rag, question, mode, conversation_history_mix)
        resp_async = rag.query(
                    question,
                    param=QueryParam(mode=mode, top_k=5, conversation_history=history)
                )
        # eval_result_mix = validateResponse(question=question, answer=resp_async, context=context_mix, reference_questions=questions, reference_answers=answers, llm=llm, embeddings=embeddings)
        response["LightRAG"] = resp_async
        # eval_result_mix : JSON(
        # metric_name: score
        # )
        
        # user_mix = {}
        # user_mix["role"] = "user"
        # user_mix["content"] = question
        # assistant_mix = {}
        # assistant_mix["role"] = "assistant"
        # assistant_mix["content"] = resp_async
        # conversation_history_mix.append(user_mix)
        # conversation_history_mix.append(assistant_mix)
        # mode="naive"
        # # resp_async, context_naive = await run_async_query(rag, question, mode, conversation_history_naive)
        # resp_async,context_naive = rag.query(
        #             question,
        #             param=QueryParam(mode=mode, top_k=5, conversation_history=conversation_history_naive)
        #         )
        # eval_result_naive = validateResponse(question=question, answer=resp_async, context=context_naive, reference_questions=questions, reference_answers=answers, llm=llm, embeddings=embeddings)
        # response["Naive"] = {"response":resp_async,"score":eval_result_naive.scores}
        # user_naive = {}
        # user_naive["role"] = "user"
        # user_naive["content"] = question
        # assistant_naive = {}
        # assistant_naive["role"] = "assistant"
        # assistant_naive["content"] = resp_async
        # conversation_history_naive.append(user_naive)
        # conversation_history_naive.append(assistant_naive)
    except Exception as e:
        response = {"error":str(traceback.format_exc())}
    return response

