import os
from dotenv import load_dotenv

from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter

from langchain.vectorstores import pinecone, Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

# Load environmental variables
load_dotenv(".env")
APIKEY = os.getenv("OPENAI_KEY")
PINE_KEY = os.getenv("PINECONE_KEY")
PINE_ENV = os.getenv("PINECONE_ENV")

# Document loader
loader = DirectoryLoader('postural_stability_info')
documents = loader.load()
# Transformation
text_splitter = CharacterTextSplitter(
    chunk_size = 2000,
    chunk_overlap  = 20,
    length_function = len)
texts = text_splitter.split_documents(documents)

EMBEDDING_MODEL = "text-embedding-ada-002"
embeddings = OpenAIEmbeddings(openai_api_key=APIKEY)

pinecone.init(
    api_key=PINE_KEY,
    environment=PINE_ENV)

index_name = "post-stab-info"

index = pinecone.Index(index_name=index_name)
docstore = Pinecone.from_texts([d.page_content for d in texts], embeddings, index_name=index_name)

docs = docstore.similarity_search(query='What exercises should I avoid if I have plantar fasciitis?')