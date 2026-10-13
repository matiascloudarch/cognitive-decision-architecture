#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

set -e

# Ensure Python locates the cda root package across environments
export PYTHONPATH=.

echo "=== 1. Auto-formatting Imports and Types (Ruff Fix) ==="
ruff check --fix cda/

echo -e "\n=== 2. Running Linter Check (Ruff) ==="
ruff check cda/

echo -e "\n=== 3. Running Static Type Checker (Mypy) ==="
mypy cda/

echo -e "\n=== 4. Running Pytest Suite with Coverage ==="
pytest --cov=cda cda/tests/ --cov-report=term-missing

echo -e "\n=== 5. Validating ITU-T Synthetic Vectors ==="
python3 cda/scripts/validate_vectors.py

echo -e "\n==========================================================="
echo " AUDIT SUCCESSFUL: All quality, type, test, and vector gates PASSED!"
echo "==========================================================="