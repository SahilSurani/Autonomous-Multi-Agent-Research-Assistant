"""
Unit Test for ChromaDB Multi-Workspace Isolation
================================================
Verifies dynamic collection switching, workspace routing, and context isolation.
"""

import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.chroma_store import list_workspaces, initialize_chroma, get_collection_name_for_workspace, get_chroma_client
from memory.memory_manager import save_research_to_memory, search_memory_context
from tools.pdf_parser_tool import search_pdf_context

def test_workspace_isolation():
    print("\n=== Running Workspace Isolation Unit Tests ===")
    
    # 1. Generate unique workspace names to ensure we start clean
    ws_alpha = f"test_alpha_{uuid.uuid4().hex[:6]}"
    ws_beta = f"test_beta_{uuid.uuid4().hex[:6]}"
    
    print(f"Creating workspaces: '{ws_alpha}' and '{ws_beta}'...")
    
    # Pre-warm collections
    col_alpha = initialize_chroma(workspace=ws_alpha)
    col_beta = initialize_chroma(workspace=ws_beta)
    
    # Verify they appear in workspace list
    workspaces = list_workspaces()
    print("Discovered workspaces:", workspaces)
    assert ws_alpha in workspaces
    assert ws_beta in workspaces
    
    # 2. Save a research session to ws_alpha
    topic = "Quantum Cryptography and Post-Quantum Security"
    report = "# Quantum Cryptography\nThis is a highly secure communication method based on quantum mechanics."
    summary = "Overview of quantum secure channels."
    critique = "Critique: Technical depth is excellent."
    
    print(f"Saving research memory to workspace: '{ws_alpha}'...")
    save_research_to_memory(
        topic=topic,
        full_research=report,
        summary=summary,
        critique=critique,
        workspace=ws_alpha
    )
    
    # 3. Retrieve memory context in ws_alpha (should return results)
    print(f"Querying memory context in workspace: '{ws_alpha}'...")
    context_alpha, memories_alpha = search_memory_context(
        query="Quantum Cryptography",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_alpha
    )
    assert len(memories_alpha) > 0, "Failed to retrieve saved memory in alpha workspace"
    assert "Quantum Cryptography" in context_alpha
    print(f"[PASS] Successfully retrieved memory context in '{ws_alpha}'")
    
    # 4. Retrieve memory context in ws_beta (should return NOTHING)
    print(f"Querying memory context in workspace: '{ws_beta}' (should be empty)...")
    context_beta, memories_beta = search_memory_context(
        query="Quantum Cryptography",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_beta
    )
    assert len(memories_beta) == 0, f"Contamination: Retrieved alpha memory from beta workspace! Memories found: {memories_beta}"
    assert context_beta == ""
    print(f"[PASS] Confirmed zero cross-workspace memory contamination in '{ws_beta}'")
    
    # 5. Test PDF RAG Ingestion Isolation
    print("\nTesting PDF RAG collection isolation...")
    client = get_chroma_client()
    pdf_col_name_alpha = get_collection_name_for_workspace(ws_alpha, suffix="_pdfs")
    pdf_col_name_beta = get_collection_name_for_workspace(ws_beta, suffix="_pdfs")
    
    pdf_col_alpha = client.get_or_create_collection(name=pdf_col_name_alpha)
    pdf_col_beta = client.get_or_create_collection(name=pdf_col_name_beta)
    
    # Add dummy chunk to ws_alpha pdf library
    pdf_col_alpha.add(
        documents=["Biological cell division and mitosis process details."],
        metadatas=[{"source_file": "mitosis.pdf", "title": "Mitosis Study", "section": "Biology", "workspace": ws_alpha}],
        ids=["pdf_alpha_chunk_1"]
    )
    
    # Retrieve PDF context in ws_alpha (should succeed)
    pdf_ctx_alpha, pdf_chunks_alpha = search_pdf_context(
        query="cell division",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_alpha
    )
    assert len(pdf_chunks_alpha) > 0, "Failed to retrieve PDF context in alpha workspace"
    print(f"[PASS] Successfully retrieved PDF context in '{ws_alpha}'")
    
    # Retrieve PDF context in ws_beta (should return NOTHING)
    pdf_ctx_beta, pdf_chunks_beta = search_pdf_context(
        query="cell division",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_beta
    )
    assert len(pdf_chunks_beta) == 0, "Contamination: Retrieved alpha PDF context from beta workspace!"
    assert pdf_ctx_beta == ""
    print(f"[PASS] Confirmed zero cross-workspace PDF library contamination in '{ws_beta}'")
    
    # 6. Clean up temporary test collections
    print("\nCleaning up test collections...")
    try:
        client.delete_collection(get_collection_name_for_workspace(ws_alpha))
        client.delete_collection(get_collection_name_for_workspace(ws_beta))
        client.delete_collection(pdf_col_name_alpha)
        client.delete_collection(pdf_col_name_beta)
        print("[PASS] Cleaned up temporary collections successfully.")
    except Exception as e:
        print(f"[WARN] Failed to delete collections: {e}")
        
    print("\n=== ALL WORKSPACE ISOLATION TESTS PASSED ===")

if __name__ == "__main__":
    test_workspace_isolation()
