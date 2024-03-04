import json
from openai import OpenAI
import pandas as pd
import os
from dotenv import load_dotenv
import numpy as np

GPT_MODEL = "text-embedding-3-large"


def calculate_similarity(vector1, vector2):
    return sum([a * b for a, b in zip(vector1, vector2)])


def get_max_key(dictionary):
    """
    Get the key with the maximum value from a dictionary.

    Args:
        dictionary (dict): The dictionary to search.

    Returns:
        dict: A dictionary containing the key with the maximum value and its corresponding value.
    """
    dictionary.pop("index", None)  # Remove the "index" key
    max_key = max(dictionary, key=dictionary.get)
    return {"related_key": max_key, "score": dictionary[max_key]}


def get_promotions_scores(embedded_word, promotions, embed_promotions, vector_columns):
    """
    Calculate similarity scores between an embedded word and a list of embedded promotions.

    Args:
        embedded_word (list): The embedded representation of a word.
        promotions (list[dict]): List of dictionaries representing promotions.
        embed_promotions (list[dict]): List of dictionaries representing embedded promotions.

    Returns:
        list[dict]: List of dictionaries representing promotions with similarity scores.

    """
    similarity_scores = []
    for promotion in embed_promotions:
        similarity = {}
        for embed_key in promotion:
            if embed_key in vector_columns:
                similarity[embed_key] = calculate_similarity(
                    embedded_word, promotion[embed_key]
                )
            elif embed_key == "index":
                similarity["index"] = promotion[embed_key]

        similarity_scores.append(get_max_key(similarity))

    promotions_with_scores = [
        dict(dict1, **dict2) or dict(dict1)
        for dict1, dict2 in zip(promotions, similarity_scores)
    ]

    return promotions_with_scores


def sort_promotions_by_scores(promotions_with_scores):
    """
    Sorts a list of promotions with scores in descending order based on the score.

    Args:
        promotions_with_scores (list[dict]) A list of dictionaries representing promotions with scores.

    Returns:
        list[dict]: A sorted list of promotions with scores in descending order based on the score.
    """
    sorted_promotions_with_scores = sorted(
        promotions_with_scores, key=lambda x: x["score"], reverse=True
    )
    return sorted_promotions_with_scores


def search_related_promotions(
    query_word, promotions, embed_promotions, vector_columns, client
):
    """
    Searches for related promotions based on a query word.

    Args:
        query_word (str): The query word to search for related promotions.
        promotions (list[dict]): List of promotions to search within.
        embed_promotions (list[dict]): List of embedded promotions.
        top_n (int, optional): Number of top related promotions to return. Defaults to 3.

    Returns:
        list[dict]: List of sorted promotions with scores, limited to top_n.
    """
    query_word_embedding = (
        client.embeddings.create(input=[query_word], model=GPT_MODEL).data[0].embedding
    )

    promotions_with_scores = get_promotions_scores(
        query_word_embedding, promotions, embed_promotions, vector_columns
    )

    for _promotion in promotions_with_scores:
        _promotion["query_word"] = query_word

    sorted_promotions_with_scores = sort_promotions_by_scores(promotions_with_scores)

    return sorted_promotions_with_scores


def get_unique_promotions(promotions_with_scores, top_n=3):
    """
    Get unique promotions based on scores.

    Args:
        promotions_with_scores (list[dict]): List of promotions with scores.
        top_n (int, optional): Number of unique promotions to return. Defaults to 3.

    Returns:
        list[dict]: List of unique promotions.
    """
    unique_promotions = []
    seen_ids = set()

    sorted_promotions = sorted(
        promotions_with_scores, key=lambda x: x["score"], reverse=True
    )

    # Find Top N unique promotions with the highest scores
    for promotion in sorted_promotions:
        if len(unique_promotions) == top_n:
            break
        if promotion["index"] not in seen_ids:
            unique_promotions.append(promotion)
            seen_ids.add(promotion["index"])

    return unique_promotions


if __name__ == "__main__":
    load_dotenv()

    client = OpenAI()

    promotions = json.load(
        open(
            "/Users/tarinnoovare/Downloads/embed_credit_card_promo/data/promotions.json"
        )
    )
    embed_promotions = json.load(
        open(
            "/Users/tarinnoovare/Downloads/embed_credit_card_promo/data/embed_promotions.json"
        )
    )

    query_words = ["วันวาเลนไทน์", "การซื้อช็อคโกแลตและขนมหวานเพื่อมอบให้คนพิเศษ"]
    top_n = 3

    related_promotions_1 = search_related_promotions(
        query_words[0], promotions, embed_promotions, client
    )

    related_promotions_2 = search_related_promotions(
        query_words[1], promotions, embed_promotions, client
    )

    related_promotions = get_unique_promotions(
        related_promotions_1 + related_promotions_2
    )

    print(related_promotions)
