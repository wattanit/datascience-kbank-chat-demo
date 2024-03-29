import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from utils.embedder import OpenAIEmbedder

# Load environment variables
load_dotenv()

class NeuralSearcher:
    """Class for performing searches using QdrantClient."""

    def __init__(self, collection_name: str):
        """
        Initialize the NeuralSearcher.

        Args:
        - collection_name (str): The name of the collection to search in.
        """

        self.collection_name = collection_name
        self.qdrant_url = os.environ.get('QDRANT_URL')
        self.qdrant_api_key = os.environ.get('QDRANT_API_KEY')
        self.qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key, prefer_grpc=True)
        self.openai_embedder = OpenAIEmbedder()
        
    def scored_points_to_list(self, scored_points):
        """
        Convert a list of ScoredPoint objects to a list of dictionaries.

        Args:
        - scored_points (list[ScoredPoint]): A list of ScoredPoint objects.

        Returns:
        - list: A list of dictionaries, each representing a ScoredPoint object.
        """
        return [{
            'id': point.id,
            'score': point.score,
            **point.payload  # Unpack all key-value pairs from the payload object
        } for point in scored_points]
    
    def search(self, text: str, vector_name: str, limit: int = 3):
        """
        Perform a search using the provided text query.

        Args:
        - text (str): The text query to search for.
        - vector_name (str): The name of the vector to use for the search.
        - limit (int): The maximum number of payload to return. Defaults to 3.

        Returns:
        - ScoredPoint: A list of ScoredPoint objects.
        """

        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=(vector_name, self.openai_embedder.get_embedding(text)),
            limit=limit,
            with_vectors=False,
            with_payload=True
        )

        return search_result
    
    def get_context(self, queries: list[str], embed_columns: list[str], limit_per_vec: int = 3):
        """
        Retrieve context information from a list of queries contained in each vector.

        Args:
        - queries (list[str]): A list of queries.
        - embed_columns (list[str]): A A list of embedding columns name.
        - limit_per_vec (int): The maximum number of payload to return each time retrieved from the vector. Defaults to 3.

        Returns:
        - list: A list of ScoredPoint objects.
        """

        # Define a nested function to perform the search operation
        def search_points(query, col):
            return self.search(text=query, vector_name=col, limit=limit_per_vec)

        # Initialize an empty list to store the scored points
        scored_points = []

        # Use ThreadPoolExecutor to parallelize the search operation
        with ThreadPoolExecutor() as executor:
            # Create a list to store the futures returned by executor.submit()
            futures = []
            # Submit tasks for each query and column combination
            for query in queries:
                for col in embed_columns:
                    futures.append(executor.submit(search_points, query, col))
            
            # Iterate over completed futures
            for future in as_completed(futures):
                # Retrieve and extend the scored_points list with the results
                scored_points.extend(future.result())

        # Return the aggregated scored_points list
        return scored_points

    def get_context_reranked(self,
                             queries: list[str],
                             embed_columns: list[str], 
                             limit: int = 3, 
                             threshold: float = 0.5, 
                             limit_per_vec: int = 3, 
                             columns: list[str] = ["id", 
                                                   "score",
                                                   "promotion_title",
                                                   "summary_text"]):
        """
        Rerank and select context embeddings based on the queries and embedding columns.

        Args:
        - queries (list[str]): A list of queries.
        - embed_columns (list[str]): A list of embedding columns name.
        - limit (int): The maximum number of payload to return. Defaults to 3.
        - threshold (float): The minimum score threshold for including a payload. Defaults to 0.5.
        - limit_per_vec (int): The maximum number of payload to return each time retrieved from the vector. Defaults to 3.

        Returns:
        - list: A list of reranked ScoredPoint objects as dictionaries.
        """
        scored_points = self.get_context(queries, embed_columns, limit)
        
        # Convert the list of ScoredPoint objects to a DataFrame
        df = pd.DataFrame(self.scored_points_to_list(scored_points))

        # Filter the DataFrame based on the threshold
        df = df[df['score'] >= threshold]

        # Sort the DataFrame by id and score, keep the last row for each id
        df = df.sort_values(['score', 'id'], ascending=False).drop_duplicates('id', keep='first')

        # Select the top rows based on the limit
        df = df.head(limit)

        # Convert the DataFrame to a list of dictionaries
        result = df[columns].to_dict(orient='records')
        return result

# # Example usage
# from utils.searcher import NeuralSearcher
    
# collection_name = "kbank_promotions"
# searcher = NeuralSearcher(collection_name)

# query = "เทคโนโลยี"
# embed_column = "vector_promotion_title"
# queries = ["s24 ultra", "สมาร์ทโฟน", "โทรศัพท์มือถือ", "อิเล็กทรอนิกส์", "กล้องถ่ายรูป", "เทคโนโลยี"]
# embed_columns = ['vector_promotion_title','vector_promotion_description','vector_shop','vector_special_day']


# search_result = searcher.search(query, embed_column, limit=3)
# print(search_result)

# results = searcher.get_context(queries, embed_columns, limit_per_vec=2)
# print(results)

# results= searcher.get_context_reranked(queries, embed_columns, limit=3, threshold=0.0, limit_per_vec=2)
# print(results)
