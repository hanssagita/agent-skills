#!/usr/bin/env bash
set -euo pipefail

# Closed Loop Execution Harness
# Usage:
#   ./scripts/run_loop.sh                (Interactive step mode: prompts between iterations)
#   ./scripts/run_loop.sh "<command>"    (Automated worker mode: runs <command> each iteration before verifying)

MAX_ITER={max_iterations}
STEP_CMD="${{1:-}}"
VERIFIER_CMD={verifier_sh_cmd}

echo "=================================================="
echo " Starting Closed Loop: {title}"
echo " Max Iterations: $MAX_ITER"
if [ -n "$STEP_CMD" ]; then
    echo " Step Command: $STEP_CMD"
else
    echo " Mode: Interactive (make changes between iterations)"
fi
echo "=================================================="

ITER=1
while [ "$ITER" -le "$MAX_ITER" ]; do
    echo ""
    echo ">>> Iteration $ITER of $MAX_ITER..."

    # If an automated step command was supplied, run it first
    if [ -n "$STEP_CMD" ]; then
        echo "[STEP] Executing: $STEP_CMD"
        eval "$STEP_CMD" || echo "[WARN] Step command exited non-zero; continuing to verification."
    fi

    # Run the verification check
    if eval "$VERIFIER_CMD"; then
        echo ""
        echo "[SUCCESS] Verifier passed on iteration $ITER! Exiting loop."
        exit 0
    fi

    echo "[INFO] Verifier failed on iteration $ITER."
    if [ "$ITER" -eq "$MAX_ITER" ]; then
        echo "[STOP] Reached maximum iterations ($MAX_ITER) without passing verifier."
        echo "[ACTION] Escalate to human operator. Do not continue blind looping."
        exit 1
    fi

    # In interactive mode, wait for user/agent edit
    if [ -z "$STEP_CMD" ]; then
        if [ -t 0 ]; then
            echo ""
            read -r -p "Apply surgical edit, then press [Enter] to run iteration $((ITER + 1)) (or Ctrl+C to abort)..."
        else
            echo "[INFO] Non-interactive execution without step command; stopping after single verification check."
            exit 1
        fi
    fi

    ITER=$((ITER + 1))
done
