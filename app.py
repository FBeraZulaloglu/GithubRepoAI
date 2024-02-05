from openai import OpenAI
import streamlit as st
from dotenv import load_dotenv
import os
import shelve
# Load environment variables before llama imports that is improtant!!!
load_dotenv()
from llama_index import download_loader
from llama_hub.github_repo import GithubRepositoryReader, GithubClient
from llama_index import VectorStoreIndex
from llama_index.vector_stores import DeepLakeVectorStore
from llama_index.storage.storage_context import StorageContext
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import (SimilarityPostprocessor)
from llama_index import get_response_synthesizer
import re
import time

st.title("Repository Chatbot ☕")
st.subheader("You can talk with your repository right now!")

USER_AVATAR = "💻"
BOT_AVATAR = "🐙"
# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Load chat history from shelve file
def load_chat_history():
    with shelve.open("chat_history") as db:
        return db.get("messages", [])


# Save chat history to shelve file
def save_chat_history(messages):
    with shelve.open("chat_history") as db:
        db["messages"] = messages

def save_api_key(key):
    with shelve.open("chat_history") as db:
        db["github_key"] = key

# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "engine" not in st.session_state:
    st.session_state.engine = None

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        save_chat_history([])

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.empty():
        if message["role"] == "user":
            st.markdown(f"{USER_AVATAR} **User:** {message['content']}")
        else:
            st.markdown(f"{BOT_AVATAR} **Assistant:** {message['content']}")
    time.sleep(0.1)  # Adjust the delay time as needed

# Define the list of programming languages
language_extensions = {
    ".py": "Python",
    ".js": "JavaScript",
    ".md": "Markdown",
    ".cpp": "C++",
    ".cs": "C#",
    ".rb": "Ruby",
    ".go": "Go",
    ".swift": "Swift",
    ".html": "HTML",
    ".css": "CSS",
    ".php": "PHP",
    ".sql": "SQL",
    ".java":"Java",
    ".ipynb":"Jupyter Notebook"
    # Add more extensions and their corresponding languages as needed
}

# Create a list to store the selected languages
selected_languages = []

# Github API Token
with st.sidebar:
    st.title('💬 Github Repository Chatbot')
    
    if 'GITHUB_TOKEN' in st.secrets:
        st.success('GITHUB API key already provided!', icon='✅')
        github_api = st.secrets['GITHUB_TOKEN']
    else:
        github_api = st.text_input('Enter Github API Token:', type='password')
        if not (github_api.startswith('ghp_')):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            openai_api_key = ""
            if 'OPENAI_API_KEY' in st.secrets:
                st.success('GPT API key already provided!', icon='✅')
                openai_api_key = st.secrets['OPENAI_API_KEY']
            else:
                openai_api_key = st.text_input('Enter GPT API Token:', type='password')
                if not (openai_api_key.startswith('sk-')):
                    st.warning('Please enter your credentials!', icon='⚠️')
                else:
                    st.success('Proceed to entering your github repository!', icon='👉')
            os.environ["OPENAI_API_KEY"] = openai_api_key

# Add checkboxes to the sidebar for each language
st.sidebar.title("Select Programming Languages")
for language in language_extensions.values():
    selected = st.sidebar.checkbox(language)
    if selected:
        selected_languages.append([extension for extension, lang in language_extensions.items() if lang == language][0])
        print(selected_languages)
        

# Github Repository
        
def parse_github_url(url):
    pattern = r"https://github\.com/([^/]+)/([^/]+)"
    match = re.match(pattern, url)
    return match.groups() if match else (None, None)

def validate_owner_repo(owner, repo):
    return bool(owner) and bool(repo)

def get_all_repos():
    from github import Github

    # Create a Github instance
    g = Github("your_access_token")

    # Get a user by username
    user = g.get_user("username")

    # Iterate over the user's repositories
    for repo in user.get_repos():
        print(repo.name)



def read_github_repo(github_client,owner,repo): 

    owner, repo = parse_github_url(github_url)
    if validate_owner_repo(owner, repo):
        loader = GithubRepositoryReader(
            github_client,
            owner=owner,
            repo=repo,
            filter_file_extensions=(
                selected_languages, # file extensions can be by check boxes
                GithubRepositoryReader.FilterType.INCLUDE,
            ),
            verbose=False,
            concurrent_requests=5,
        )
        print(f"Loading {repo} repository by {owner}")
        docs = loader.load_data(branch="main")
        print("Documents uploaded:")
        for doc in docs:
            print(doc.metadata)
        return docs

with st.sidebar:
    st.title('Repository')
    
    github_url = st.text_input('Enter Github Repository URL:', type='default')
    
    try:
        if st.button("Load repository"):
            with st.spinner("Loading Repository..."):
                github_client = GithubClient(github_api)
                download_loader("GithubRepositoryReader") # LlamaIndex feature
                owner,repo = parse_github_url(github_url)
                docs = read_github_repo(github_client,owner,repo)
                print("docs are ready!")
                try:
                    vector_store = DeepLakeVectorStore(
                        token = os.getenv("ACTIVELOOP_TOKEN"),
                        dataset_path=os.getenv("DATASET_PATH"),
                        overwrite=True,
                        runtime={"tensor_db": True},
                    )
                    print("vector store created!")
                except Exception as e:
                    print(f"An unexpected error occurred while creating or fetching the vector store: {str(e)}")
                
                storage_context = StorageContext.from_defaults(vector_store=vector_store)
                index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)

                retriever = VectorIndexRetriever(index=index, similarity_top_k=2)

                response_synthesizer = get_response_synthesizer()
                query_engine = RetrieverQueryEngine.from_args(
                        retriever=retriever,
                        response_mode='default',
                        response_synthesizer=response_synthesizer,
                        node_postprocessors=[
                            SimilarityPostprocessor(similarity_cutoff=0.7)]
                    )

                st.session_state.engine  = query_engine
                
    except Exception as e:
        print(e)
        st.error('Could not load the repo !', icon='⚠️')

# Check if the user has been greeted
if "greeted" not in st.session_state:
    # Greet the user
    greeting_message = """
        👋  Hello 👋 Welcome to your Github Booster AI! Step into the vast realm of knowledge and exploration with repositories. 📚 
            Whether you forgot the code you wrote or you just want to study your code again, your repositories is here to inspire and guide you again.
            """
    st.session_state.messages.append({"role": "assistant", "content": greeting_message})
    st.write(greeting_message)
    # Set the 'greeted' flag to True
    st.session_state.greeted = True

if st.session_state.engine is not None:
    # Main chat interface
    if prompt := st.chat_input("Ask your repos..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar=BOT_AVATAR):
            message_placeholder = st.empty()
            full_response = st.session_state.engine.query(prompt)
            message_placeholder.markdown(full_response)
        
            
        st.session_state.messages.append({"role": "assistant", "content": st.session_state.engine .query(prompt)})

    # Save chat history after each interaction
    save_chat_history(st.session_state.messages)