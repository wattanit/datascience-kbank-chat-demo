import os
from dotenv import load_dotenv
from openai import OpenAI
import tiktoken

# Load environment variables
load_dotenv()

class OpenAIEmbedder:
    def __init__(self):
        self.OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        self.OPENAI_EMBEDDING_MODEL = os.environ.get('OPENAI_EMBEDDING_MODEL')
        self.OPENAI_EMBEDDING_ENCODING = os.environ.get('OPENAI_EMBEDDING_ENCODING')
        self.OPENAI_MAX_TOKENS_ENCODING = int(os.environ.get('OPENAI_MAX_TOKENS_ENCODING'))
        self.openai_client = OpenAI(api_key=self.OPENAI_API_KEY)

    def get_embedding(self, text, model=None):
        """Get the embedding for the given text using the specified model."""
        model = model or self.OPENAI_EMBEDDING_MODEL
        text = text.replace("\n", " ")
        return self.openai_client.embeddings.create(input=[text], model=model).data[0].embedding

    def count_tokens(self, text, model=None):
        """Count the number of tokens in the given text using the specified encoding."""
        model = model or self.OPENAI_EMBEDDING_ENCODING
        encoding = tiktoken.get_encoding(model)
        return len(encoding.encode(text))

    def check_token_length(self, text):
        """Check if the number of tokens in the text is within the maximum limit."""
        return self.count_tokens(text) <= self.OPENAI_MAX_TOKENS_ENCODING

# Example usage:
# embedder = OpenAIEmbedder()
# print(embedder.get_embedding("example text"))
# print(embedder.count_tokens("example text"))
# print(embedder.check_token_length("example text"))
