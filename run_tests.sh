#!/bin/bash
set -e

echo "=== ANALYZE TESTS ==="
prof analyze test.docx
prof analyze test.txt @parser
prof analyze test.txt @research
prof analyze test.txt @analysis
prof analyze test.txt @recommendation

echo "=== SUMMARIZE TESTS ==="
prof summarize test.txt
prof summarize test.pdf
prof summarize test.docx

echo "=== SUPPORT COMMAND TESTS ==="
prof doctor
prof history
prof agents

echo "ALL TESTS COMPLETED SUCCESSFULLY"
