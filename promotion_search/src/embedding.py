import pandas as pd
from tqdm import tqdm
from utils.embedder import OpenAIEmbedder

def embed_data(file_name):
    # Create an instance of the OpenAIEmbedder class
    openai_embedder = OpenAIEmbedder()

    # Read the CSV file into a DataFrame
    df = pd.read_csv(f"data/raw/{file_name}")

    # # Combine 'promotion_title' and 'promotion_description' into 'promotion' column
    # df['promotion'] = (
    #     "promotion title: " + df.promotion_title.str.strip() + 
    #     "; promotion description: " + df.promotion_description.str.strip()
    # )

    # Define columns to embed 
    columns_to_embed = [
        'promotion_title',
        'promotion_description',
        'shop',
        'credit_card',
        'special_day'
    ]

    # Apply embedding to specified columns
    for column in tqdm(columns_to_embed):
        df['vector_'+column] = df[column].apply(lambda x: openai_embedder.get_embedding(x))

    # Save the processed DataFrame to a new CSV file
    df.to_csv(f"data/processed/{file_name}", index=False)
    print(f"file saved in data/processed/{file_name}")

if __name__ == "__main__":
    # var = input("Please enter the file name to embed (it should include '.csv' in the name): ")
    var = "promotion_special_day.csv"
    embed_data(var)
