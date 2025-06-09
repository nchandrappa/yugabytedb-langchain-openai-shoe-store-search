from llm_db import query_database;

if __name__ == '__main__':
    
    query_str = input("What is your question? \n\n")
    while query_str != "":
        augmented_query_string = f"Answer this question specifically: {query_str}. Ignore null values."
        response = query_database(augmented_query_string)
        print(response)
        query_str = input("What is your question? \n\n")