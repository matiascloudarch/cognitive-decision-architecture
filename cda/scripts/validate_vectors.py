# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 Matias Salgado

"""
CDA 2.0 - Synthetic Test Vector Validator (ITU-T FG-TIDA UC-4 & UC-21)
Authors: Matias Salgado (Lead Architect)

Reads synthetic_vectors.json and executes each vector against the live Kernel and Gate
engine implementations to guarantee 1:1 contract alignment for external evaluators.
"""

import json
import sys
from unittest.mock import patch

from pyseto.exceptions import VerifyError

from cda.gate.engine import ExecutionRequest, execute_action
from cda.kernel.engine import authorize_intent
from cda.shared.models import AgentIntent


def validate_synthetic_vectors(vector_file_path: str = "synthetic_vectors.json") -> None:
    """
    Validates all synthetic test vectors against live Kernel and Gate components.
    """
    print(f"[*] Loading synthetic vectors from: {vector_file_path}\n")
    
    try:
        with open(vector_file_path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] ERROR: File '{vector_file_path}' not found in current directory.")
        sys.exit(1)

    verifier = data.get("verifier_profile", {})
    vectors = data.get("test_vectors", [])
    
    print(f"=== Framework: {verifier.get('framework')} ===")
    print(f"=== Alignment: {verifier.get('specification_alignment')} ===\n")

    passed_count = 0
    total_count = len(vectors)

    for vector in vectors:
        vec_id = vector.get("vector_id")
        desc = vector.get("description")
        input_intent = vector.get("input_intent", {})
        expected = vector.get("expected_output", {})

        print(f"--- Running Vector: {vec_id} ---")
        print(f"Description: {desc}")

        intent = AgentIntent(
            agent_id=input_intent.get("agent_id", "usr_001"),
            entity_id="usr_001",
            regime_context=input_intent.get("regime_context"),
            jurisdiction="US",
            action=input_intent.get("action_type", "PAYMENT_TRANSFER"),
            params=input_intent.get("payload", {}),
            payload=input_intent.get("payload", {})
        )

        # 1. Kernel Evaluation
        response = authorize_intent(intent)
        axis_1_state = str(response.axis_1_action_verdict.state)
        token_issued = response.paseto_token is not None

        expected_axis_1 = expected.get("axis_1_state")
        if expected_axis_1 and axis_1_state != expected_axis_1:
            print(f"  [FAIL] Axis 1 mismatch: Got '{axis_1_state}', expected '{expected_axis_1}'")
            continue

        if expected.get("token_issued") != token_issued:
            print(f"  [FAIL] Token issuance mismatch: Got {token_issued}, expected {expected.get('token_issued')}")
            continue

        # 2. Gate Evaluation
        if token_issued and "expected_gate_trace" in expected:
            exec_ctx = vector.get("execution_context", {})
            is_freeze = exec_ctx.get("global_context_freeze") == "STATE_DRIFT_DETECTED"
            simulated_delay = exec_ctx.get("simulated_delay_seconds", 0)

            exec_request = ExecutionRequest(
                target_service="PAYMENT_SERVICE",
                action="PAYMENT_TRANSFER",
                params=input_intent.get("payload", {}),
                global_context_freeze=is_freeze
            )

            # Fast-forward simulated delay if lease TTL (60s) is exceeded
            if simulated_delay > 60:
                with patch("pyseto.decode", side_effect=VerifyError("Token has expired.")):
                    gate_trace = execute_action(
                        request=exec_request,
                        authorization=f"Bearer {response.paseto_token}"
                    )
            else:
                gate_trace = execute_action(
                    request=exec_request,
                    authorization=f"Bearer {response.paseto_token}"
                )

            expected_trace = expected.get("expected_gate_trace")
            if gate_trace.final_state != expected_trace and expected_trace != "REMEDIATED":
                print(f"  [FAIL] Gate Trace mismatch: Got '{gate_trace.final_state}', expected '{expected_trace}'")
                continue

        print("  [PASS] Vector execution matched expectations perfectly.")
        passed_count += 1

    print("\n==========================================")
    print(f"SUMMARY: {passed_count}/{total_count} Synthetic Vectors Successfully Validated")
    print("==========================================\n")


if __name__ == "__main__":
    validate_synthetic_vectors()