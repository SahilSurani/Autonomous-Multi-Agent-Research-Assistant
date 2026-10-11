import os
import sys
import fitz

# Resolve paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_sample_pdf(pdf_path):
    print(f"[*] Creating sample PDF at '{pdf_path}'...")
    doc = fitz.open()
    page = doc.new_page()
    
    content = """Abstract
This is a sample research abstract discussing the application of Neural Networks to General Organic Chemistry (GOC). We explore how deep learning models can classify molecules and predict reaction pathways.

Introduction
In this paper, we investigate machine learning approaches for General Organic Chemistry (GOC). Organic chemistry relies on structural rules that can be learned by graph neural networks.

Methodology
Our proposed method represents molecules as molecular graphs. We train a GCN model to predict stability metrics.

Conclusion
We demonstrated that deep neural networks can learn fundamental GOC concepts. Future work will expand to larger reaction datasets.

References
[1] Smith, J. et al. Deep learning in organic synthesis. Journal of Chemistry, 2024.
[2] Johnson, R. Graph neural networks for molecules. arXiv, 2025.
"""
    # Insert text lines
    page.insert_textbox((50, 50, 550, 750), content, fontsize=11, fontname="helv")
    doc.save(pdf_path)
    doc.close()
    print("[*] Sample PDF created successfully.")

def test_pipeline():
    # Load dotenv to load GROQ API keys if summary is generated
    from dotenv import load_dotenv
    load_dotenv()
    
    pdf_path = "scratch/test_paper.pdf"
    create_sample_pdf(pdf_path)
    
    from tools.pdf_parser_tool import ingest_pdf_to_chroma, search_pdf_context
    
    print("\n[*] Ingesting PDF paper...")
    record = ingest_pdf_to_chroma(pdf_path, "test_paper.pdf")
    print(f"Ingested record: {record}")
    
    print("\n[*] Querying PDF RAG context...")
    context, chunks = search_pdf_context("GOC chemistry neural networks")
    
    print("\n=== RAG Context Output ===")
    print(context)
    print("==========================")
    
    print(f"\nRetrieved {len(chunks)} chunks.")
    for c in chunks:
        print(f" - Chunk section: {c['metadata']['section']}, score: {c['similarity_score']}")

if __name__ == "__main__":
    test_pipeline()
