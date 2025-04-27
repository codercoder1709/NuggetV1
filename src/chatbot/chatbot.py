import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import google.generativeai as genai
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
# Go up two levels from src/chatbot to the project root to find .env
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(dotenv_path=os.path.join(project_root, '.env')) # Load .env from project root

# Define paths relative to the script's location and then navigate correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level from 'chatbot' to 'src', then into 'output'
output_dir = os.path.join(current_dir, '..', 'output')
# Normalize the path
output_dir = os.path.normpath(output_dir)

index_path = os.path.join(output_dir, 'faiss_index.bin')
metadata_path = os.path.join(output_dir, 'metadata.pkl')

# Ensure output directory exists (optional, good practice)
# os.makedirs(output_dir, exist_ok=True) # Uncomment if needed

# Load FAISS index
print(f"Attempting to load FAISS index from: {index_path}") # Added print statement
if os.path.exists(index_path):
    try:
        index = faiss.read_index(index_path)
        print("FAISS index loaded successfully.")
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        exit()
else:
    print(f"Error: FAISS index file not found at {index_path}")
    exit() # Or handle the error appropriately

# Load metadata
print(f"Attempting to load metadata from: {metadata_path}") # Added print statement
if os.path.exists(metadata_path):
    try:
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        print("Metadata loaded successfully.")
    except Exception as e:
        print(f"Error loading metadata: {e}")
        exit()
else:
    print(f"Error: Metadata file not found at {metadata_path}")
    exit()

# Load SentenceTransformer model
try:
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
except Exception as e:
    print(f"Error loading SentenceTransformer model: {e}")
    print("Please ensure you have internet connectivity and the 'sentence-transformers' library installed.")
    exit()

# Configure Gemini
try:
    # IMPORTANT: Store your API key securely, e.g., environment variable
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') # This will now read from the loaded .env file
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment or .env file.")
    genai.configure(api_key=GOOGLE_API_KEY)
    # Choose a Gemini model (e.g., 'gemini-1.5-flash' or 'gemini-pro')
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
    print("Gemini model loaded successfully.")
except Exception as e:
    print(f"Error configuring or loading Gemini model: {e}")
    print("Please ensure you have set the GOOGLE_API_KEY environment variable and installed 'google-generativeai'.")
    exit()

def retrieve_top_k(query, k=10):
    """Retrieve top-k most relevant documents"""
    try:
        query_embedding = embedder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        D, I = index.search(query_embedding, k)

        results = []
        for i, idx in enumerate(I[0]):
            if idx != -1 and idx < len(metadata): # FAISS returns -1 for no result
                result_item = metadata[idx].copy() # Make a copy to avoid modifying original metadata
                result_item['similarity_score'] = float(D[0][i]) # Add similarity score
                results.append(result_item)
            else:
                print(f"Warning: Index {idx} out of bounds or invalid in FAISS search results.")
        return results
    except Exception as e:
        print(f"Error during FAISS search: {e}")
        return []


def generate_answer(context_texts, user_query):
    """Generate a natural answer based on retrieved context using Gemini"""
    if not context_texts:
        return "I couldn't find relevant information to answer your question based on the available data."

    # Improved context formatting
    context_parts = []
    # print("context_texts:", context_texts)  # Debugging line (keep commented out unless needed)
    for i, item in enumerate(context_texts):
        # print(item)
        # Ensure price is formatted reasonably, handle potential non-numeric data if necessary
        price_str = str(item.get('price', 'N/A'))
        context_parts.append(
            f"Result {i+1}:\n"
            f"  Restaurant: {item.get('restaurant_name', 'N/A')}\n"
            f"  Item: {item.get('item_name', 'N/A')}\n"
            f"  Price: {price_str}\n" 
            f"  Description: {item.get('short_description', '').strip()} {item.get('long_description', '').strip()}\n" # Use strip()
            f"  Location: {item.get('location', 'N/A')}\n"
            f"  Gluten Free: {item.get('gluten_free', 'N/A')}\n"
            f"  affordability: {item.get('affordability_tag', 'N/A')}\n"
            f"  Vegetarian: {item.get('tags', 'N/A')}\n"
            f"  Tags / Features : {item.get('dish_type', 'N/A')}\n"
            f"  popularity score / Famous / Rated: {item.get('popularity_score', 'N/A')}\n"
            f"  avaiable time : {item.get('available_time', 'N/A')}\n"
            f"  contact / phone number of restaurant: {item.get('contact', 'N/A')}\n"
            # Add similarity score to context if needed for debugging or advanced prompting
            # f"  Similarity Score: {item.get('similarity_score', 'N/A'):.4f}\n"
        )
    context = "\n".join(context_parts)
    # print(f"Formatted Context:\n{context}")  # Debugging line (keep commented out unless needed)

    # Refined prompt for Gemini to handle specific queries better
    prompt = f"""You are a helpful restaurant assistant. Based *only* on the following retrieved restaurant menu information, answer the user's question precisely.
- Do not make up information or prices not present in the context.
- If the context doesn't contain the answer (e.g., missing restaurant, missing item type like 'appetizers', insufficient details for comparison, no items matching criteria like 'gluten-free'), state that clearly. Do not apologize excessively.
- If asked for a price range (e.g., for desserts at restaurant XYZ), calculate the minimum and maximum price *only* from the relevant items (e.g., desserts from XYZ) found in the context. State the range or indicate if not enough data exists.
- If asked to compare (e.g., spice levels), use only the information (like descriptions or tags) present for the specific items/restaurants mentioned in the context.
- If asked for 'best' options (e.g., vegetarian), list the relevant options found in the context. Simply list the findings.
- If asked for dietary options (e.g., gluten-free), list the relevant options found in the context. if none are found, state that clearly.that it is is negative. i.e 'no gluten-free options found'.

Context:
---
{context}
---

User Question: {user_query}

Answer:"""

    try:
        # Generate content using the Gemini model
        response = gemini_model.generate_content(prompt)
        # Access the generated text
        if response.parts:
            answer = response.text
        elif hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
             answer = f"Blocked due to: {response.prompt_feedback.block_reason}"
             print(f"Warning: Gemini response blocked. Reason: {response.prompt_feedback.block_reason}")
        else:
            # Handle cases where response might be empty or lack 'parts' unexpectedly
            answer = "Sorry, I could not generate a valid answer from the model."
            print(f"Warning: Gemini returned an unexpected or empty response structure: {response}")


        return answer
    except Exception as e:
        # Log the full exception for debugging
        import traceback
        print(f"Error during Gemini text generation: {e}\n{traceback.format_exc()}")
        return "Sorry, I encountered an error while generating the answer with Gemini."

def chatbot_respond(user_query):
    """Main chatbot function"""
    print(f"\nUser Query: {user_query}")
    # Retrieve top 50 relevant documents to provide more context for specific/comparative queries
    retrieved_context = retrieve_top_k(user_query, k=50) # Increased k to 50

    if not retrieved_context:
        print("No relevant context found.")
        return "I couldn't find any relevant menu items for your query based on the available data."
    print(retrieved_context)
    print(f"\nRetrieved Context ({len(retrieved_context)} items):") # Show how many items were retrieved
    # Only print the top few retrieved items to avoid cluttering the console
    max_items_to_print = 10
    for i, item in enumerate(retrieved_context[:max_items_to_print]):
         print(f"  {i+1}. Restaurant: {item.get('restaurant_name', 'N/A')}, Item: {item.get('item_name', 'N/A')}, Score: {item.get('similarity_score', 'N/A'):.4f}")
    if len(retrieved_context) > max_items_to_print:
        print(f"  ... (and {len(retrieved_context) - max_items_to_print} more)")


    answer = generate_answer(retrieved_context, user_query)
    print(f"\nGenerated Answer: {answer}")
    return answer

# Example usage (optional, for testing)
if __name__ == "__main__":
    # Ensure the index and metadata files exist before running
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        print("Error: FAISS index or metadata file not found.")
        print("Please run the preprocessing and indexing script first (e.g., preprocess_and_index.py).")
    else:
        # --- Test Queries ---
        test_queries = [
            "Find spicy chicken dishes",
            "Are there any vegan options?",
            "Show me budget-friendly meals under 150", # Price filtering still relies on LLM interpretation of context
            "What desserts are available?",
            "Tell me about Italian food",
            "Any gluten-free pasta?",
            "Where can I get biryani?",
            # --- New Test Queries ---
            "Which restaurant has the most vegetarian options in their menu based on this data?", # Modified 'best'
            "Does 'Pizza Place' have any gluten-free appetizers?", # Replace 'Pizza Place' with an actual name from your data if possible
            "What's the price range for desserts at 'Curry House'?", # Replace 'Curry House' with an actual name
            "Compare the spice levels mentioned for dishes at 'Spice King' and 'Noodle Bar'", # Replace with actual names
            "List vegetarian main courses",

        ]

        for query in test_queries:
            chatbot_respond(query)
            print("-" * 50)

        # Interactive loop
        print("\nEnter your query (or type 'quit' to exit):")
        while True:
            user_input = input("> ")
            if user_input.lower() == 'quit':
                break
            chatbot_respond(user_input)
            print("-" * 50)