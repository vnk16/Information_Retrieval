import streamlit as st
import re
from collections import defaultdict

# Function to tokenize the input text into lowercase words
def tokenize(text):
    return set(re.findall(r'\b\w+\b', text.lower()))

# Function to build an inverted index from a collection of documents
def build_inverted_index(docs):
    index = defaultdict(set)
    for doc_id, text in docs.items():
        words = tokenize(text)
        for word in words:
            index[word].add(doc_id)
    return index

# Function to perform Boolean retrieval based on the inverted index
def boolean_retrieval(index, query):
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    
    # Initialize result_docs as a set of all document IDs
    result_docs = set(index.keys())
    
    # Process AND operations
    if 'and' in tokens:
        terms = query.split(' and ')
        result_docs = set(index.get(terms[0].strip(), set()))
        for term in terms[1:]:
            term = term.strip()
            result_docs = result_docs.intersection(index.get(term, set()))
    
    # Process OR operations
    elif 'or' in tokens:
        terms = query.split(' or ')
        result_docs = set()
        for term in terms:
            term = term.strip()
            result_docs = result_docs.union(index.get(term, set()))
    
    # Process NOT operations
    elif 'not' in tokens:
        terms = query.split(' not ')
        if len(terms) == 2:
            term_to_exclude = terms[1].strip()
            result_docs = result_docs.difference(index.get(term_to_exclude, set()))
    
    # Handle queries without Boolean operators
    else:
        result_docs = set()
        for token in tokens:
            result_docs = result_docs.union(index.get(token, set()))
    
    return result_docs

# Streamlit App Interface
st.title("Boolean Retrieval System")

# File Uploader for Documents
uploaded_files = st.file_uploader("Upload documents (text files)", accept_multiple_files=True, type=["txt"])

# Check if files were uploaded
if uploaded_files:
    documents = {}
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        documents[file.name] = content

    st.success("Documents successfully uploaded and processed!")
    
    # Build the inverted index from the uploaded documents
    inverted_index = build_inverted_index(documents)
    
    # Boolean Query Input
    query = st.text_input("Enter your Boolean query (supports AND, OR, NOT)")
    
    # Run the Boolean retrieval when the user submits the query
    if st.button("Run Query"):
        if query:
            results = boolean_retrieval(inverted_index, query)
            if results:
                st.write("Matching documents:")
                for doc_id in results:
                    st.write(f"{doc_id}: {documents[doc_id]}")
            else:
                st.write("No documents matched the query.")
        else:
            st.error("Please enter a Boolean query.")

