import warnings
import os
import getpass
import re

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

import bs4

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")


###############
### SOURCES ###
###############

# website-specific content strainers
apple_strainer = bs4.SoupStrainer(id='main')
google_strainer = bs4.SoupStrainer('main')
samsung_strainer = bs4.SoupStrainer(id='content')
url_config = [
  # Samsung
  # Galaxy S25|S25+
  {
    'url': 'https://www.samsung.com/ca/smartphones/galaxy-s25/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 Edge
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-edge/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 Ultra
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-ultra/',
    'strainer': samsung_strainer,
  },
  # Galaxy S25 FE
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-s25-fe/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Flip7 FE
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-flip7-fe/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Flip7
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-flip7/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z Fold7
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-fold7/',
    'strainer': samsung_strainer,
  },
  # Galaxy Z TriFold
  {
    'url': 'https://www.samsung.com/us/smartphones/galaxy-z-trifold/',
    'strainer': samsung_strainer,
  },
  
  # Apple
  # iPhone 17
  {
    'url': 'https://www.apple.com/iphone-17/',
    'strainer': apple_strainer
  },
  # iPhone 17 Pro
  {
    'url': 'https://www.apple.com/iphone-17-pro/',
    'strainer': apple_strainer
  },
  # iPhone Air
  {
    'url': 'https://www.apple.com/iphone-air/',
    'strainer': apple_strainer
  },
  # iPhone 16e
  {
    'url': 'https://www.apple.com/iphone-16e/',
    'strainer': apple_strainer
  },

  # Google
  # Google Pixel 10
  {
    'url': 'https://store.google.com/product/pixel_10?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 specs
  {
    'url': 'https://store.google.com/product/pixel_10_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 tech specs:\n'
  },
  # Google Pixel 10 Pro
  {
    'url': 'https://store.google.com/product/pixel_10_pro?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 Pro specs
  {
    'url': 'https://store.google.com/product/pixel_10_pro_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 Pro tech specs:\n'
  },
  # Google Pixel 10 Pro Fold
  {
    'url': 'https://store.google.com/product/pixel_10_pro_fold?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10 Pro Fold specs
  {
    'url': 'https://store.google.com/product/pixel_10_pro_fold_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10 Pro Fold tech specs:\n'
  },
  # Google Pixel 10a
  {
    'url': 'https://store.google.com/product/pixel_10a?hl=en-US',
    'strainer': google_strainer
  },
  # Google Pixel 10a specs
  {
    'url': 'https://store.google.com/product/pixel_10a_specs?hl=en-US',
    'strainer': google_strainer,
    'context': 'Google Pixel 10a tech specs:\n'
  },
]


########################
### DOCUMENT LOADING ###
########################

# Condense large amounts of whitespace
def clean_whitespace(text):
  text = re.sub(r'\n{3,}', '\n\n', text)
  text = re.sub(r'[ \t]{2,}', ' ', text)
  return text.strip()

def load_docs_from_urls(url_config):
  docs = []
  for config in url_config:
    loader = WebBaseLoader(
      web_paths=(config['url'],),
      bs_kwargs={'parse_only': config['strainer']},
      # bypass SSL verification errors during fetching
      requests_kwargs={'verify': False}
    )
    doc = loader.load()[0]
    
    # Give the doc a unique id
    doc.id = config['url']

    # add extra context (used for Google Pixel spec pages)
    if 'context' in config:
      doc.page_content = config['context'] + doc.page_content
    doc.page_content = clean_whitespace(doc.page_content)
    docs.append(doc)
  return docs

print('Loading docs from source URLs...')
docs = load_docs_from_urls(url_config)

for d in docs:
  print(len(d.page_content), '|', d.metadata['source'])

##########################
### DOCUMENT SPLITTING ###
##########################
print('Splitting docs...')
text_splitter = RecursiveCharacterTextSplitter(
  chunk_size=1000, chunk_overlap=200, add_start_index=True
)


all_splits = text_splitter.split_documents(docs)


##################
### EMBEDDINGS ###
##################
print('Loading embeddings...')
embeddings = OpenAIEmbeddings(model='text-embedding-3-large')

vector_store = Chroma(
  collection_name='collection',
  embedding_function=embeddings,
)

ids = vector_store.add_documents(documents=all_splits)


#################
### RAG Agent ###
#################

print('Creating agent...')

# context retrieval tool
@tool(response_format='content_and_artifact')
def retrieve_context(query: str):
  """Retrieve information to help answer a user's query"""
  retrieved_docs = vector_store.similarity_search(query, k=4)
  serialized = '\n\n'.join(
    (f'Source: {doc.metadata}\nContent: {doc.page_content}')
    for doc in retrieved_docs
  )
  return serialized, retrieved_docs

tools = [retrieve_context]

model = ChatOpenAI(
  model='gpt-4.1',
  temperature=0.1,
)

system_prompt = """
You are a helpful AI assistant who gives users information and recommendations regarding recent smartphone models.
You have access to a tool called retrieve_context that retrieves context from smartphone designer websites. Note that this data only applies to a few recent models from Apple, Samsung, and Google.
Use this tool to retrieve any information needed to answer user questions about these recent smartphone models.
If the user asks you something you don't know and can't find using the tool, tell the user that you don't know the specific answer to their question.
In these cases, you can still give related information that may be helpful to the user, as long as you give time context.
Start by greeting the user and letting them know what you are there to help them with.
"""

agent = create_agent(
  model=model,
  tools=tools,
  system_prompt=system_prompt,
  checkpointer=InMemorySaver(),
)

def get_response(query):
  return agent.invoke(
    {'messages': [{'role': 'user', 'content': query}]},
    {'configurable': {'thread_id': '1'}}
  )

response = get_response('')
print(f'\n{response["messages"][-1].content}\n')
while True:
  query = input('> ')
  response = get_response(query)
  print(f'\n{response["messages"][-1].content}\n')