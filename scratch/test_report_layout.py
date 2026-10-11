import sys
import os
import re

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.report_agent import generate_final_report

def main():
    print("Testing generate_final_report compilation layout...")
    
    # Setup test inputs
    validated_research = """
    ## Force Fields in Molecular Dynamics
    Force fields are mathematical functions used to calculate the potential energy of a system of atoms.
    
    ## Atomic Structures
    Atomic structures refer to the constitution of atoms, including protons, neutrons, and electrons.
    """
    
    summary = "This is a summary of the molecular dynamics research findings."
    
    critique_dict = {
        "score": 8.8,
        "research_grade": "Strong Pass (Grade A)",
        "coverage_analysis": {
            "Introduction": "9/10 - well structured",
            "Core Concepts": "8.5/10 - good coverage",
            "Detailed Analysis": "8.8/10 - analytical depth present"
        },
        "strengths": ["Clear structure", "Precise terminology"],
        "weaknesses": ["Needs more detail on quantum effects"],
        "missing_research_areas": ["Quantum calculations detail"],
        "improvement_priorities": {
            "High Priority": ["Expand quantum physics section"]
        },
        "confidence_level": "High",
        "final_verdict": "Publishable report with minor changes."
    }
    
    sources = [
        {"title": "Gilmer et al. (2017)", "url": "https://arxiv.org/abs/1704.01212", "type": "academic"},
        {"title": "Yang et al. (2019)", "url": "https://arxiv.org/abs/1910.03123", "type": "academic"},
        {"title": "Web MD Intro", "url": "https://example.com/md", "type": "web"},
    ]
    
    # Generate final report
    report = generate_final_report(validated_research, summary, critique_dict, sources)
    
    print("\n--- GENERATED REPORT START ---")
    print(report)
    print("--- GENERATED REPORT END ---\n")
    
    # Verify the structure
    lines = report.split("\n")
    headings = [line.strip() for line in lines if line.strip().startswith("## ")]
    
    print(f"Discovered {len(headings)} H2 headings:")
    for h in headings:
        print(f"  {h}")
        
    expected_headings = [
        "## 1. Executive Summary",
        "## 2. Introduction",
        "## 3. Research Methodology",
        "## 4. Core Concepts & Foundations",
        "## 5. Current State of the Field",
        "## 6. Detailed Technical Analysis",
        "## 7. Applications & Use Cases",
        "## 8. Advantages & Opportunities",
        "## 9. Challenges & Limitations",
        "## 10. Future Outlook",
        "## 11. Key Insights & Strategic Findings",
        "## 12. Expert Recommendations",
        "## 13. Conclusion",
        "## 14. References & Source Validation"
    ]
    
    success = True
    print("\nVerifying H2 headings:")
    for idx, expected in enumerate(expected_headings, start=1):
        matched = False
        for h in headings:
            pattern = rf"^##\s*{idx}\.\s*"
            if re.match(pattern, h):
                matched = True
                print(f"  [PASS] Section {idx} found: {h}")
                break
        if not matched:
            success = False
            print(f"  [FAIL] Section {idx} missing or malformed! Expected prefix: '{expected}'")
            
    # Check Section 14 content (References & Source Validation)
    print("\nChecking Section 14 content (References & Source Validation):")
    sec14_idx = report.lower().find("## 14.")
    if sec14_idx != -1:
        sec14_content = report[sec14_idx:]
        print(f"Academic Count '2' in Section 14: {'2' in sec14_content}")
        print(f"Web Count '1' in Section 14: {'1' in sec14_content}")
        print(f"Semantic Scholar database: {'Semantic Scholar' in sec14_content}")
        print(f"arXiv database: {'arXiv' in sec14_content}")
        print(f"CrossRef database: {'CrossRef' in sec14_content}")
        print(f"Source Reliability Analysis: {'reliability' in sec14_content.lower()}")
        
        required_words = ['2', '1', 'semantic scholar', 'arxiv', 'reliability']
        if not all(word in sec14_content.lower() for word in required_words):
            success = False
            print("  [FAIL] Section 14 content verification failed.")
        else:
            print("  [PASS] Section 14 content verification successful.")
    else:
        success = False
        print("  [FAIL] Heading 14 not found to check content.")

    if success:
        print("\nOVERALL VERDICT: SUCCESS (All 14 sections verified successfully)")
        sys.exit(0)
    else:
        print("\nOVERALL VERDICT: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
