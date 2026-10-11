import fitz
import time
import os

test_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_test_paper.pdf")

doc = fitz.open(test_pdf)
t0 = time.time()
table_count = 0
for page in doc:
    try:
        tables = page.find_tables()
        table_count += len(tables.tables)
    except AttributeError as e:
        print("find_tables is not supported in this version of PyMuPDF:", e)
        break
t1 = time.time()
print(f"PyMuPDF find_tables: found {table_count} tables in {t1 - t0:.4f}s")
doc.close()
