import streamlit as st
import re
from collections import defaultdict

# Function to tokenize text into a set of lowercase words
def tokenize(text):
    """Tokenize the input text into a set of lowercase words."""
    return set(re.findall(r'\b\w+\b', text.lower()))

# Function to build the inverted index
def build_inverted_index(docs):
    """
    Build an inverted index from a collection of documents.

    Args:
        docs (dict): A dictionary where keys are document IDs and values are the document texts.

    Returns:
        dict: An inverted index where keys are words and values are sets of document IDs containing the word.
    """
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

# Function to perform Boolean retrieval
def boolean_retrieval(index, query, all_doc_ids):
    """
    Perform Boolean retrieval based on the inverted index.

    Args:
        index (dict): The inverted index.
        query (str): The Boolean query (supports AND, OR, and NOT operations).
        all_doc_ids (set): A set of all document IDs.

    Returns:
        set: A set of document IDs that match the query.
    """
    # Precedence: NOT > AND > OR
    # Tokenize the query
    tokens = query.upper().split()
    output = []
    operators = []
    
    # Helper functions
    def precedence(op):
        if op == 'NOT':
            return 3
        elif op == 'AND':
            return 2
        elif op == 'OR':
            return 1
        return 0

    def apply_operator(op, operand1, operand2=None):
        if op == 'AND':
            return operand1 & operand2
        elif op == 'OR':
            return operand1 | operand2
        elif op == 'NOT':
            return operand1 - operand2
        return set()

    # Shunting Yard Algorithm to convert to Reverse Polish Notation (RPN)
    for token in tokens:
        if token in {'AND', 'OR', 'NOT'}:
            while (operators and precedence(operators[-1]) >= precedence(token)):
                output.append(operators.pop())
            operators.append(token)
        else:
            output.append(token)
    while operators:
        output.append(operators.pop())

    # Evaluate RPN
    stack = []
    for token in output:
        if token in {'AND', 'OR', 'NOT'}:
            if token == 'NOT':
                operand = stack.pop()
                stack.append(all_doc_ids - index.get(operand.lower(), set()))
            else:
                right = stack.pop()
                left = stack.pop()
                stack.append(apply_operator(token, left, right))
        else:
            stack.append(index.get(token.lower(), set()))
    
    return stack[0] if stack else set()

# Streamlit App
def main():
    st.title("Boolean Retrieval System")
    st.write("""
    ## Upload Documents and Perform Boolean Queries

    **Instructions:**
    - Enter your documents in the text area below.
    - Each document should be on a separate line starting with a unique document ID, followed by a colon, and then the document text.
    - Example:
      ```
      doc1: Information retrieval systems use Boolean queries to find documents.
      doc2: Boolean retrieval is fundamental to search engines.
      ```
    - Enter your Boolean query using `AND`, `OR`, and `NOT` operators.
    """)

    # Text area for document input
    docs_input = st.text_area("Enter Documents:", height=200, 
        value="""doc1: Information retrieval systems use Boolean queries to find documents.
doc2: Boolean retrieval is fundamental to search engines.
doc3: Modern search engines use advanced algorithms beyond simple Boolean queries.
doc4: Data mining techniques are used for more complex search tasks.""")

    # Text input for Boolean query
    query = st.text_input("Enter Boolean Query:", "Boolean AND retrieval")

    # Button to perform retrieval
    if st.button("Retrieve Documents"):
        # Parse the documents
        documents = {}
        for line in docs_input.strip().split('\n'):
            if ':' in line:
                doc_id, text = line.split(':', 1)
                documents[doc_id.strip()] = text.strip()
            else:
                st.error(f"Invalid document format: '{line}'. Expected 'docID: Document text.'")
                return

        if not documents:
            st.error("No valid documents found. Please enter documents in the correct format.")
            return

        # Build the inverted index
        inverted_index = build_inverted_index(documents)
        all_doc_ids = set(documents.keys())

        # Perform Boolean retrieval
        results = boolean_retrieval(inverted_index, query, all_doc_ids)

        # Display results
        st.subheader("Query Results")
        if results:
            st.write(f"**Documents matching the query '{query}':** {', '.join(sorted(results))}")
            st.write("### Document Details:")
            for doc_id in sorted(results):
                st.write(f"**{doc_id}**: {documents[doc_id]}")
        else:
            st.write("No documents matched the query.")

if __name__ == "__main__":
    main()
