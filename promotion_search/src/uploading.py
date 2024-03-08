import os
import ast
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv
from qdrant_client import models, QdrantClient

# Load environment variables
load_dotenv()

# Get environment variables
qdrant_url = os.environ.get('QDRANT_URL')
qdrant_api_key = os.environ.get('QDRANT_API_KEY')
collection_name = os.environ.get('COLLECTION_NAME')
openai_embedding_dimension = os.environ.get('OPENAI_EMBEDDING_DIMENSION')

def upload_data_to_qdrant(file_name):
    
    # Read the CSV file into a DataFrame
    input_path = os.path.join(os.path.dirname(__file__), f"../data/processed/{file_name}")
    df = pd.read_csv(input_path, dtype=str)
    
    # Replacing NaN values by None values
    df = df.where(pd.notnull(df), None)

    # Define vector columns
    vector_columns = [col for col in df.columns if col.startswith('vector_')]

    # Split the main DataFrame into two parts
    df_vector = df[vector_columns]
    df_non_vector = df.drop(columns=vector_columns)
    del df # Delete the original DataFrame to free up memory

    # Convert string representations of lists to actual lists
    for col in vector_columns:
        df_vector[col] = df_vector[col].apply(ast.literal_eval)

    # Initialize QdrantClient with provided credentials
    qdrant = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
        prefer_grpc=True,
    )

    # Define vector configuration for each column
    vectors_config = {
        col: models.VectorParams(
            distance=models.Distance.COSINE,
            size=openai_embedding_dimension,
        )
        for col in vector_columns
    }

    # Recreate the collection in Qdrant
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=vectors_config
    )

    # Upload data to the collection
    qdrant.upload_points(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=idx, 
                vector={key: value for key, value in df_vector.loc[idx].items()},
                payload={key: value for key, value in df_non_vector.loc[idx].items()},
            )
            for idx in tqdm(df_non_vector.index)
        ],
    )

if __name__ == "__main__":
    # var = input("Please enter the file name to upload (it should include '.csv' in the name): ")
    var = "promotion_special_day.csv"
    upload_data_to_qdrant(var)
