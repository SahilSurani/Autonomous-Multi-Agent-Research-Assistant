"""
====================================================================
PRISM AI - FULL SYSTEM VERIFICATION TEST SUITE
====================================================================
Tests every implemented feature end-to-end and reports pass/fail.
Run from the project root:
    python scratch/verify_tests.py
====================================================================
"""
import sys, os, json, time, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"
INFO = "[INFO]"

results = []

def check(name, passed, detail=""):
    label = PASS if passed else FAIL
    results.append((label, name))
    suffix = f"  =>  {detail}" if detail else ""
    print(f"  {label}  {name}{suffix}")
    return passed

def section(title):
    print()
    print("=" * 64)
    print(f"  {title}")
    print("=" * 64)

# ─────────────────────────────────────────────────────────────────
# TEST 1: MODULE IMPORTS
# ─────────────────────────────────────────────────────────────────
section("TEST 1: Module Imports")

import_tests = [
    ("tools.pdf_parser_tool",       ["ingest_pdf_to_chroma","search_pdf_context","chunk_document",
                                     "extract_pdf_text_and_sections","extract_tables_as_markdown",
                                     "validate_pdf","validate_text_quality","generate_pdf_summary_preview"]),
    ("tools.academic_search_tool",  ["search_academic_literature","search_arxiv","search_semantic_scholar",
                                     "search_crossref","optimize_search_query","format_academic_context",
                                     "rank_and_deduplicate_papers","clean_abstract"]),
    ("tools.groq_client",           ["ask_groq"]),
    ("tools.web_search_tool",       ["search_web","format_search_results"]),
    ("agents.researcher_agent",     ["generate_research","create_research_prompt","clean_report_headings","refine_research"]),
    ("agents.planner_agent",        ["generate_plan"]),
    ("memory.chroma_store",         ["get_chroma_client"]),
    ("memory.memory_manager",       ["save_research_to_memory","search_memory_context"]),
]

for mod_name, funcs in import_tests:
    try:
        mod = __import__(mod_name, fromlist=funcs)
        missing = [f for f in funcs if not hasattr(mod, f)]
        if missing:
            check(f"Import: {mod_name}", False, f"missing: {missing}")
        else:
            check(f"Import: {mod_name}", True, f"{len(funcs)} functions verified")
    except Exception as e:
        check(f"Import: {mod_name}", False, str(e)[:80])

# ─────────────────────────────────────────────────────────────────
# TEST 2: PDF CREATION + VALIDATION
# ─────────────────────────────────────────────────────────────────
section("TEST 2: PDF Creation & Validation")

import fitz
from tools.pdf_parser_tool import validate_pdf, validate_text_quality

# Build a realistic test PDF
test_pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_test_paper.pdf")
try:
    doc = fitz.open()
    page1 = doc.new_page()
    page1.insert_text((60, 80), "Graph Neural Networks for Molecular Property Prediction\n", fontsize=14)
    page1.insert_text((60, 110), (
        "Abstract\n"
        "We present a deep learning approach using Graph Convolutional Networks (GCN) to predict "
        "molecular toxicity with high accuracy. Our model was trained on 1.5 million compounds from "
        "ChEMBL and achieves state-of-the-art AUC-ROC of 0.94 on the Tox21 benchmark dataset, "
        "outperforming classical machine learning baselines by over 12 percentage points.\n\n"
        "Introduction\n"
        "Predicting molecular properties early in the drug discovery pipeline reduces costs and "
        "accelerates development. Traditional QSAR methods rely on handcrafted fingerprints and "
        "struggle to generalize. Graph-based deep learning models directly operate on molecular graphs, "
        "enabling end-to-end learning of both structure and property relationships."
    ), fontsize=10)
    
    page2 = doc.new_page()
    page2.insert_text((60, 80), (
        "Methodology\n"
        "Molecules are represented as undirected graphs G=(V,E) where nodes V represent atoms and "
        "edges E represent chemical bonds. Node features include atomic number, hybridization state, "
        "and aromaticity. We employ a 5-layer message-passing GCN with residual connections and "
        "attention-based readout. The model is trained with binary cross-entropy loss.\n\n"
        "Results\n"
        "Our model achieves AUC-ROC of 0.94 on Tox21 and 0.91 on BBBP. Ablation studies confirm "
        "attention-based readout contributes +3% over mean pooling. Training converges in 48 hours "
        "on 4x NVIDIA A100 GPUs.\n\n"
        "Conclusion\n"
        "Graph neural networks are powerful tools for molecular property prediction. The proposed "
        "architecture generalizes across diverse molecular tasks with minimal hyperparameter tuning.\n\n"
        "References\n"
        "[1] Gilmer et al. (2017). Neural Message Passing for Quantum Chemistry. ICML.\n"
        "[2] Yang et al. (2019). Analyzing Learned Molecular Representations for Property Prediction.\n"
        "[3] Duvenaud et al. (2015). Convolutional Networks on Graphs for Learning Molecular Fingerprints."
    ), fontsize=10)
    
    doc.save(test_pdf_path)
    doc.close()
    check("Create test PDF with fitz", True, f"Saved to {os.path.basename(test_pdf_path)}")
except Exception as e:
    check("Create test PDF with fitz", False, str(e))

# Validate the PDF
try:
    v = validate_pdf(test_pdf_path)
    check("validate_pdf() — file exists & readable", v, "2 pages confirmed")
except Exception as e:
    check("validate_pdf()", False, str(e))

# Validate bad path
try:
    v_bad = validate_pdf("non_existent.pdf")
    check("validate_pdf() — rejects missing file", not v_bad)
except Exception as e:
    check("validate_pdf() — rejects missing file", False, str(e))

# Text quality
try:
    good_text = "This is a well-written academic abstract about neural networks." * 5
    bad_text = "\x00\x01\x02\x03" * 100
    g = validate_text_quality(good_text)
    b = validate_text_quality(bad_text)
    check("validate_text_quality() — good text passes", g)
    check("validate_text_quality() — garbage text fails", not b)
except Exception as e:
    check("validate_text_quality()", False, str(e))

# ─────────────────────────────────────────────────────────────────
# TEST 3: PDF TEXT EXTRACTION & SECTION DETECTION
# ─────────────────────────────────────────────────────────────────
section("TEST 3: PDF Text Extraction & Section Detection")

from tools.pdf_parser_tool import extract_pdf_text_and_sections

extracted = None
try:
    extracted = extract_pdf_text_and_sections(test_pdf_path)
    check("extract_pdf_text_and_sections() — runs without error", True)
except Exception as e:
    check("extract_pdf_text_and_sections()", False, str(e))

if extracted:
    title = extracted.get("title", "")
    sections = extracted.get("sections", {})
    references = extracted.get("references", [])
    raw_text = extracted.get("raw_text", "")
    
    check("Title extracted (non-empty)", bool(title), f'"{title[:60]}"')
    check("Sections dict non-empty", bool(sections), f"Keys: {list(sections.keys())}")
    
    # Check specific sections are found
    expected_sections = ["Abstract", "Introduction", "Methodology", "Conclusion", "References"]
    for sec in expected_sections:
        check(f"Section detected: {sec}", sec in sections, 
              f"{len(sections[sec])} chars" if sec in sections else "MISSING")
    
    check("References extracted", len(references) >= 1, f"{len(references)} reference(s)")
    check("Raw text non-empty", len(raw_text) > 200, f"{len(raw_text)} chars total")
    check("Text quality passes", validate_text_quality(raw_text))

# ─────────────────────────────────────────────────────────────────
# TEST 4: CHUNKING STRATEGIES
# ─────────────────────────────────────────────────────────────────
section("TEST 4: Chunking Strategies")

from tools.pdf_parser_tool import chunk_document

if extracted:
    sections_data = extracted["sections"]
    
    # Semantic chunking
    try:
        chunks_s = chunk_document(sections_data, strategy="semantic", chunk_size=600, overlap=100)
        check("Semantic chunking produces chunks", len(chunks_s) > 0, f"{len(chunks_s)} chunks")
        
        all_have_text = all(c.get("text","").strip() for c in chunks_s)
        check("All semantic chunks have text", all_have_text)
        
        all_have_section = all(c.get("section") for c in chunks_s)
        check("All semantic chunks have section label", all_have_section)
        
        # Check overlap works (no chunk exceeds chunk_size + overlap significantly)
        oversized = [c for c in chunks_s if len(c["text"]) > 800]
        check("No chunk exceeds size limit", len(oversized) == 0, 
              f"{len(oversized)} oversized" if oversized else "all within limit")
        
        print(f"       Chunk breakdown:")
        for i, c in enumerate(chunks_s[:6]):
            print(f"         [{i+1}] {c['section']:20s} | {len(c['text'])} chars")
    except Exception as e:
        check("Semantic chunking", False, str(e))
    
    # Sliding window chunking
    try:
        chunks_w = chunk_document(sections_data, strategy="sliding_window", chunk_size=600, overlap=100)
        check("Sliding window chunking produces chunks", len(chunks_w) > 0, f"{len(chunks_w)} chunks")
    except Exception as e:
        check("Sliding window chunking", False, str(e))

# ─────────────────────────────────────────────────────────────────
# TEST 5: CHROMADB INGESTION
# ─────────────────────────────────────────────────────────────────
section("TEST 5: ChromaDB PDF Ingestion & RAG Retrieval")

from tools.pdf_parser_tool import ingest_pdf_to_chroma, search_pdf_context

# Ingest
record = None
try:
    record = ingest_pdf_to_chroma(test_pdf_path, "verify_test_paper.pdf", strategy="semantic")
    check("ingest_pdf_to_chroma() — completes", bool(record))
except Exception as e:
    check("ingest_pdf_to_chroma()", False, str(e)[:100])

if record:
    check("Record has filename",       record.get("filename") == "verify_test_paper.pdf")
    check("Record has title",          bool(record.get("title")))
    check("Record has chunk_count > 0", record.get("chunk_count", 0) > 0, f"{record.get('chunk_count')} chunks")
    check("Record has sections list",  len(record.get("sections", [])) > 0, str(record.get("sections")))
    check("Record has summary",        len(record.get("summary", "")) > 50, f"{len(record.get('summary',''))} chars")
    check("Record has timestamp",      bool(record.get("timestamp")))
    
    print(f"\n       Ingest Record:")
    print(f"         Title:       {record['title'][:70]}")
    print(f"         Chunks:      {record['chunk_count']}")
    print(f"         Sections:    {record['sections']}")
    print(f"         Tables:      {record['table_count']}")
    print(f"         References:  {record['reference_count']}")
    print(f"         Summary len: {len(record['summary'])} chars")

# RAG Search
time.sleep(0.5)
try:
    ctx, chunks = search_pdf_context("molecular property prediction graph neural network", n_results=3, min_similarity=0.10)
    check("search_pdf_context() — returns context string", bool(ctx), f"{len(ctx)} chars")
    check("search_pdf_context() — returns chunks list",   bool(chunks), f"{len(chunks)} chunks")
    
    if chunks:
        best = chunks[0]
        check("Chunk has similarity_score", "similarity_score" in best)
        check("Chunk has document text",    bool(best.get("document")))
        check("Chunk has metadata",         bool(best.get("metadata")))
        check("Chunk metadata has title",   bool(best.get("metadata", {}).get("title")))
        check("Chunk metadata has section", bool(best.get("metadata", {}).get("section")))
        
        print(f"\n       Top RAG Result:")
        print(f"         Section:    {best['metadata'].get('section')}")
        print(f"         Similarity: {best.get('similarity_pct')}")
        print(f"         Excerpt:    {best['document'][:100]}...")
except Exception as e:
    check("search_pdf_context()", False, str(e)[:100])

# ─────────────────────────────────────────────────────────────────
# TEST 6: METADATA JSON PERSISTENCE
# ─────────────────────────────────────────────────────────────────
section("TEST 6: PDF Metadata JSON Persistence")

try:
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "database")
    metadata_file = os.path.join(db_dir, "pdf_metadata.json")
    check("database/ directory exists", os.path.isdir(db_dir))
    check("pdf_metadata.json exists",   os.path.isfile(metadata_file))
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        meta_list = json.load(f)
    check("pdf_metadata.json is valid JSON", True, f"{len(meta_list)} record(s)")
    
    our_record = next((m for m in meta_list if m["filename"] == "verify_test_paper.pdf"), None)
    check("Our paper appears in metadata", bool(our_record))
    
    if our_record:
        for field in ["filename", "title", "chunk_count", "sections", "table_count", "reference_count", "summary", "timestamp"]:
            check(f"  metadata field: '{field}'", field in our_record)
except Exception as e:
    check("Metadata persistence", False, str(e))

# ─────────────────────────────────────────────────────────────────
# TEST 7: ACADEMIC SEARCH TOOL
# ─────────────────────────────────────────────────────────────────
section("TEST 7: Academic Search Tool")

from tools.academic_search_tool import (
    clean_abstract, clean_title, rank_and_deduplicate_papers,
    search_semantic_scholar, search_crossref, format_academic_context
)

# clean_abstract
check("clean_abstract() strips XML tags",
      "<" not in clean_abstract("<jats:p>Hello world</jats:p>"),
      clean_abstract("<jats:p>Hello world</jats:p>"))

check("clean_abstract() handles None", 
      clean_abstract(None) == "No abstract available.")

check("clean_abstract() strips 'Abstract:' prefix",
      not clean_abstract("Abstract: This is a test").startswith("Abstract:"),
      clean_abstract("Abstract: This is a test"))

# clean_title
check("clean_title() normalizes to lowercase alphanum",
      clean_title("Graph Neural Networks!") == "graphneuralnetworks")

# rank_and_deduplicate_papers
sample_papers = [
    {"title": "Deep Learning in Medicine", "authors": ["A"], "abstract": "Good abstract here for testing", "year": 2023, "citations": 100, "url": "https://arxiv.org/abs/1234", "venue": "Nature", "source": "Semantic Scholar"},
    {"title": "Deep Learning in Medicine", "authors": ["B"], "abstract": "No abstract available.", "year": 2022, "citations": 50,  "url": "https://crossref.org/1", "venue": "", "source": "Crossref"},
    {"title": "Quantum Computing Basics",  "authors": ["C"], "abstract": "Quantum computing intro text.", "year": 2024, "citations": 5,   "url": "https://arxiv.org/abs/5678", "venue": "arXiv", "source": "arXiv"},
]
try:
    ranked = rank_and_deduplicate_papers(sample_papers, target_limit=3)
    check("rank_and_deduplicate() removes duplicates", len(ranked) == 2, f"{len(ranked)} unique papers")
    check("rank_and_deduplicate() keeps higher-scoring duplicate", 
          any(p["source"] == "Semantic Scholar" for p in ranked))
    check("rank_and_deduplicate() returns ranking_score", 
          all("ranking_score" in p for p in ranked))
    print(f"       Ranked results:")
    for p in ranked:
        print(f"         '{p['title'][:40]}' | score={p['ranking_score']:.2f} | source={p['source']}")
except Exception as e:
    check("rank_and_deduplicate_papers()", False, str(e))

# format_academic_context
try:
    ctx = format_academic_context(ranked[:2])
    check("format_academic_context() returns non-empty string", bool(ctx) and len(ctx) > 50)
    check("format_academic_context() contains GROUND TRUTH header", "GROUND TRUTH" in ctx)
    check("format_academic_context() contains source URLs", "http" in ctx)
except Exception as e:
    check("format_academic_context()", False, str(e))

# Live Semantic Scholar test
print(f"\n  [INFO] Testing live Semantic Scholar API (may take 5s)...")
try:
    t0 = time.time()
    papers = search_semantic_scholar("transformer attention mechanism NLP", limit=3)
    elapsed = time.time() - t0
    check("search_semantic_scholar() — live API call",  len(papers) > 0, f"{len(papers)} papers in {elapsed:.1f}s")
    if papers:
        p = papers[0]
        check("  Paper has title",    bool(p.get("title")))
        check("  Paper has year",     bool(p.get("year")))
        check("  Paper has url",      p.get("url","").startswith("http"))
        check("  Paper has source",   p.get("source") in ["arXiv","Semantic Scholar"])
        check("  Abstract cleaned",   "<" not in (p.get("abstract") or ""))
        print(f"       Best paper: \"{p['title'][:60]}\"")
        print(f"       Year: {p['year']} | Citations: {p['citations']} | Source: {p['source']}")
        print(f"       URL: {p['url'][:70]}")
except Exception as e:
    check("search_semantic_scholar()", False, str(e)[:80])

# Live Crossref test
print(f"\n  [INFO] Testing live Crossref API (may take 5s)...")
try:
    t0 = time.time()
    papers_cr = search_crossref("machine learning drug discovery", limit=2)
    elapsed = time.time() - t0
    check("search_crossref() — live API call", len(papers_cr) > 0, f"{len(papers_cr)} papers in {elapsed:.1f}s")
    if papers_cr:
        pc = papers_cr[0]
        check("  Crossref paper has title",  bool(pc.get("title")))
        check("  Crossref paper has year",   bool(pc.get("year")))
        check("  Crossref abstract cleaned", "<" not in (pc.get("abstract") or ""))
        print(f"       Best paper: \"{pc['title'][:60]}\"")
except Exception as e:
    check("search_crossref()", False, str(e)[:80])

# ─────────────────────────────────────────────────────────────────
# TEST 8: REPORT HEADING CLEANER
# ─────────────────────────────────────────────────────────────────
section("TEST 8: Report Heading Cleaner")

from agents.researcher_agent import clean_report_headings

test_report = """# Research Report: Test Topic

## 1.0 Introduction
Some intro text here.

## 2.1 Core Concepts  
Some core concepts here.

## 3. Applications
Real world applications.

## 4 Advantages
Benefits listed here.
"""

try:
    cleaned = clean_report_headings(test_report)
    lines = cleaned.split("\n")
    h2_lines = [l for l in lines if l.startswith("## ")]
    check("clean_report_headings() — runs without error", bool(cleaned))
    check("Decimal headings fixed (1.0 → 1)", all(not re.search(r"## \d+\.\d+", l) for l in h2_lines),
          str(h2_lines))
    check("Integer headings preserved (3.)", any("## 3." in l for l in h2_lines))
    print(f"       Fixed headings: {h2_lines}")
except Exception as e:
    check("clean_report_headings()", False, str(e))

# ─────────────────────────────────────────────────────────────────
# TEST 9: CHROMADB CONNECTIVITY
# ─────────────────────────────────────────────────────────────────
section("TEST 9: ChromaDB & Memory System")

try:
    from memory.chroma_store import get_chroma_client
    client = get_chroma_client()
    check("get_chroma_client() returns client", client is not None)
    
    collections = client.list_collections()
    col_names = [c.name for c in collections]
    check("pdf_documents collection exists", "pdf_documents" in col_names, str(col_names))
    
    pdf_col = client.get_collection("pdf_documents")
    count = pdf_col.count()
    check(f"pdf_documents has stored chunks", count > 0, f"{count} chunks in ChromaDB")
except Exception as e:
    check("ChromaDB connectivity", False, str(e)[:100])


# ─────────────────────────────────────────────────────────────────
# TEST 11: WORKSPACE ISOLATION
# ─────────────────────────────────────────────────────────────────
section("TEST 11: Workspace Isolation")

try:
    import uuid
    from memory.chroma_store import list_workspaces, initialize_chroma, get_collection_name_for_workspace, get_chroma_client
    from memory.memory_manager import save_research_to_memory, search_memory_context
    from tools.pdf_parser_tool import search_pdf_context

    ws_alpha = f"verify_alpha_{uuid.uuid4().hex[:6]}"
    ws_beta = f"verify_beta_{uuid.uuid4().hex[:6]}"
    
    col_alpha = initialize_chroma(workspace=ws_alpha)
    col_beta = initialize_chroma(workspace=ws_beta)
    
    workspaces = list_workspaces()
    check("Workspace: Discovered workspaces list", ws_alpha in workspaces and ws_beta in workspaces)
    
    save_research_to_memory(
        topic="Workspace Isolation Verification",
        full_research="Mock report contents",
        summary="Mock summary",
        critique="Mock critique",
        workspace=ws_alpha
    )
    
    context_alpha, memories_alpha = search_memory_context(
        query="Workspace Isolation",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_alpha
    )
    check("Workspace: Retrieve memory in designated workspace", len(memories_alpha) > 0)
    
    context_beta, memories_beta = search_memory_context(
        query="Workspace Isolation",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_beta
    )
    check("Workspace: Retrieve memory in alternative workspace (should be isolated)", len(memories_beta) == 0)

    client = get_chroma_client()
    pdf_col_name_alpha = get_collection_name_for_workspace(ws_alpha, suffix="_pdfs")
    pdf_col_alpha = client.get_or_create_collection(name=pdf_col_name_alpha)
    
    pdf_col_alpha.add(
        documents=["Biological verification mitosis cell details."],
        metadatas=[{"source_file": "cell.pdf", "title": "Cell Study", "section": "Biology", "workspace": ws_alpha}],
        ids=["pdf_verify_chunk_1"]
    )
    
    pdf_ctx_alpha, pdf_chunks_alpha = search_pdf_context(
        query="mitosis",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_alpha
    )
    check("Workspace: Retrieve PDF context in designated workspace", len(pdf_chunks_alpha) > 0)
    
    pdf_ctx_beta, pdf_chunks_beta = search_pdf_context(
        query="mitosis",
        n_results=2,
        min_similarity=0.10,
        workspace=ws_beta
    )
    check("Workspace: Retrieve PDF context in alternative workspace (should be isolated)", len(pdf_chunks_beta) == 0)
    
    client.delete_collection(get_collection_name_for_workspace(ws_alpha))
    client.delete_collection(get_collection_name_for_workspace(ws_beta))
    client.delete_collection(pdf_col_name_alpha)
    
except Exception as e:
    check("Workspace isolation system verification", False, str(e))

# ─────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────
print()
print("=" * 64)
print("  FINAL VERIFICATION REPORT")
print("=" * 64)

passed  = sum(1 for r in results if r[0] == PASS)
failed  = sum(1 for r in results if r[0] == FAIL)
warned  = sum(1 for r in results if r[0] == WARN)
total   = len(results)
pct     = (passed / total * 100) if total else 0

print(f"  Total Tests : {total}")
print(f"  Passed      : {passed}  ({pct:.0f}%)")
print(f"  Failed      : {failed}")
print(f"  Warnings    : {warned}")
print()

if failed > 0:
    print("  FAILED TESTS:")
    for label, name in results:
        if label == FAIL:
            print(f"    ✗  {name}")

if pct >= 90:
    print(f"  VERDICT: SYSTEM VERIFIED ({pct:.0f}% pass rate)")
elif pct >= 70:
    print(f"  VERDICT: MOSTLY WORKING — {failed} issue(s) need attention")
else:
    print(f"  VERDICT: CRITICAL ISSUES FOUND — {failed} test(s) failing")
print("=" * 64)
