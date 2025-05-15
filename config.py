import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables"""
    # Make sure environment variables are loaded
    load_dotenv()
    
    # MongoDB Configuration
    mongodb_username = os.getenv('MONGODB_USERNAME')
    mongodb_password = os.getenv('MONGODB_PASSWORD')
    mongodb_uri = os.getenv('MONGODB_URI') or f"mongodb+srv://{mongodb_username}:{mongodb_password}@ircw.371s5.mongodb.net/?retryWrites=true&w=majority&appName=IRCW"
    
    # Default MongoDB Collections Configuration
    default_mongodb_collections = [
        {"db": "newsfirst_data", "collection": "articles"},
        {"db": "newswire_data", "collection": "articles"},
        {"db": "adaderana_data", "collection": "articles"}
    ]
    
    # Pinecone Configuration
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    pinecone_index_name = os.getenv('PINECONE_INDEX_NAME', 'news-articles-index')
    pinecone_cloud = os.getenv('PINECONE_CLOUD', 'aws')
    pinecone_region = os.getenv('PINECONE_REGION', 'us-east-1')
    
    # OpenAI Configuration
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    # Return configuration as a dictionary
    return {
        "MONGODB_USERNAME": mongodb_username,
        "MONGODB_PASSWORD": mongodb_password,
        "MONGODB_URI": mongodb_uri,
        "DEFAULT_MONGODB_COLLECTIONS": default_mongodb_collections,
        "PINECONE_API_KEY": pinecone_api_key,
        "PINECONE_INDEX_NAME": pinecone_index_name,
        "PINECONE_CLOUD": pinecone_cloud,
        "PINECONE_REGION": pinecone_region,
        "OPENAI_API_KEY": openai_api_key
    }
