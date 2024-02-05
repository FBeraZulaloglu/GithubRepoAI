# Repository Chatbot ☕

This Streamlit application allows users to interact with their GitHub repositories using an AI-powered chatbot. The chatbot helps users explore, search, and analyze code repositories more efficiently.

## Usage
After you have create .env file then give the right API keys. You just need to give your repo to look up to
then you are able to chat with gpt model that knows your repo as you want.

### Prerequisites

Before running the application, make sure you have Python installed on your system.

### Setting Up a Virtual Environment

To create a virtual environment for this project, follow these steps:

1. Open a terminal window.
2. Navigate to the directory where you have stored the project files.
3. Run the following command to create a virtual environment named `venv`:

   ```bash
   python -m venv venv
   ```

4. Activate the virtual environment:

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```

   - On macOS and Linux:

     ```bash
     source venv/bin/activate
     ```

### Installing Required Libraries

Once the virtual environment is activated, you can install the required libraries using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### Running the Application

After installing the required libraries, you can run the application by executing the following command:

```bash
streamlit run your_script.py
```

Replace `your_script.py` with the filename of your Streamlit application script.

## API Keys

- You will need three API tokens to run this application these are the links for all of them. After you sign these platforms
you are able get your tokens then you are good to go for deploying your application.
- ACTIVE LOOP: https://www.activeloop.ai/
- GPT: https://openai.com/blog/openai-api
- GITHUB: https://github.com/settings/tokens


## .env file

- You need to create .env file. You can get the template from .env.example file
- ACTIVELOOP_TOKEN: You can get this after you create your account from the link above.
- DATASET_PATH: After you create your organization your dataset path should look like this:

```bash
hub://organization_name/your_path_name_you_want
```

## Features

- Users can interact with their GitHub repositories using natural language queries.
- The chatbot provides assistance in exploring and analyzing code repositories.
- Support for multiple programming languages for repository exploration.
- Integrated AI capabilities for enhanced user experience.

## Credits

- Inspired by https://learn.activeloop.ai/courses/take/rag/multimedia/51349127-chat-with-your-code-llamaindex-and-activeloop-deep-lake-for-github-repositories