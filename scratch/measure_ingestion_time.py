import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.pdf_parser_tool import extract_pdf_text_and_sections, chunk_document, generate_pdf_summary_preview
from memory.chroma_store import get_chroma_client, get_collection_name_for_workspace

test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_test_paper.pdf")

if not os.path.exists(test_pdf):
    print("Test PDF does not exist, creating it...")
    # Run verify_tests.py once to generate the test PDF
    import subprocess
    subprocess.run(["python", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_tests.py")], stdout=subprocess.DEVNULL)

print("Starting measurement for PDF:", test_pdf)

# 1. Measure text & section parsing (which calls table extraction)
t0 = time.time()
parsed_data = extract_pdf_text_and_sections(test_pdf)
t1 = time.time()
print(f"Time for text and section extraction (including tables): {t1 - t0:.4f}s")

# Measure table extraction specifically
from tools.pdf_parser_tool import extract_tables_as_markdown
t_tab_0 = time.time()
tables = extract_tables_as_markdown(test_pdf)
t_tab_1 = time.time()
print(f"Time for table extraction only (using pdfplumber): {t_tab_1 - t_tab_0:.4f}s")

# 2. Measure chunking
t2 = time.time()
chunks = chunk_document(parsed_data["sections"], strategy="semantic")
t3 = time.time()
print(f"Time for chunking: {t3 - t2:.4f}s")

# 3. Measure ChromaDB database storage (one-by-one)
client = get_chroma_client()
from chromadb.utils import embedding_functions
fast_ef = embedding_functions.DefaultEmbeddingFunction()
pdf_collection = client.get_or_create_collection("test_speed_pdfs", embedding_function=fast_ef)

# Clean up first
try:
    client.delete_collection("test_speed_pdfs")
except Exception:
    pass
pdf_collection = client.get_or_create_collection("test_speed_pdfs", embedding_function=fast_ef)

t4 = time.time()
for idx, chunk in enumerate(chunks):
    chunk_id = f"test_chunk_{idx}"
    pdf_collection.add(
        documents=[chunk["text"]],
        metadatas=[{"section": chunk["section"]}],
        ids=[chunk_id]
    )
t5 = time.time()
print(f"Time for ChromaDB one-by-one storage: {t5 - t4:.4f}s")

# 4. Measure ChromaDB database storage (batched)
try:
    client.delete_collection("test_speed_pdfs")
except Exception:
    pass
pdf_collection = client.get_or_create_collection("test_speed_pdfs", embedding_function=fast_ef)

t6 = time.time()
docs = [c["text"] for c in chunks]
metas = [{"section": c["section"]} for c in chunks]
ids = [f"test_chunk_{idx}" for idx in range(len(chunks))]
pdf_collection.add(
    documents=docs,
    metadatas=metas,
    ids=ids
)
t7 = time.time()
print(f"Time for ChromaDB batched storage: {t7 - t6:.4f}s")

# Clean up
try:
    client.delete_collection("test_speed_pdfs")
except Exception:
    pass
