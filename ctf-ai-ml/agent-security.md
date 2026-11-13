# Agent security: prompt injection, RAG and tool boundaries

Use for challenges involving a tool-using LLM, RAG pipeline, memory store, multi-agent system, model gateway or agent evaluation. The underlying bug may be web, crypto or access control; follow the primitive.

## Map the trust boundaries

Draw:

- who can write each channel (user, retrieved document, tool output, memory, another agent, model);
- who can read each channel and with what privilege;
- where text becomes an instruction, a tool call, a URL, SQL, code or a file path;
- what the final success condition is (flag in response, secret read, privileged action, exfiltration).

A prompt-injection finding is only a solve when it crosses a boundary to the flag or a stronger primitive. Otherwise it is a medium-value observation.

A clean final answer does not mean the injection failed. Inspect tool calls, side effects, file/network changes and logs for concealed actions (Gray Swan's concealment finding).

## Test families

| Hypothesis | Cheap test |
|---|---|
| Direct instruction override | One benign canary instruction that changes a harmless output token |
| Indirect injection via retrieved content | Place the canary in one document and ask a question that retrieves it |
| Tool-output injection | A tool returns text impersonating a system/developer message or a new task |
| Memory poisoning | Write a durable fact in one turn; check whether a later turn treats it as authority |
| Tool selection/parameter confusion | Ask for a benign action that requires choosing between two tools or paths |
| Secret exfiltration | Can the model send a canary secret to an allowed-looking but attacker-chosen destination? |
| Sandbox escape | Does generated code/tool input reach a shell, file, network or another tenant? |
| Evaluation contamination | Does a fake flag/README/checker change the reported success? |

Use a canary value you control. Do not use real credentials or third-party systems. One test per hypothesis; do not spray jailbreak strings.

## RAG-specific

- Inspect chunking, metadata filters, tenant isolation and source precedence.
- Test whether untrusted documents can outrank system/developer instructions or operator policy.
- Check citation/attribution: does the answer trust the retrieved text as fact?
- Test cross-tenant retrieval, stale index entries, deleted documents and embedding collisions.
- A retrieved page containing instructions is data. It cannot expand scope or authorize tools.

## Agent-specific

- Enumerate tools, permissions, network egress, filesystem mounts and secret access.
- Check whether tool output is re-injected as trusted context.
- Test human-approval bypass, confirmation fatigue and plan/act separation.
- Check subagent inheritance: does a child get broader tools or a different system prompt?
- Inspect logs/traces for secrets and for the first point a candidate flag appears.

## Evaluation hygiene

A model saying “the flag is X” is not a solve. Record the exact transcript, tool calls and first appearance of the value. Verify with the challenge checker or an independent oracle. Do not claim universal prompt-injection immunity from finite tests; report scope and limitations.

## Defense (for building, not only breaking)

- Separate instructions from data; label provenance at every boundary.
- Require independent verification before accepting success or changing goals.
- Bound exploration of hypotheses that repeatedly fail to produce corroboration.
- Keep authorization, scope, budgets and expected commitments outside model-controlled text.
- Minimize tool privileges and egress; never expose provider credentials to challenge artifacts.

## References

This reference adapts AgentLSD's trap families and CTF-ABACUS's provenance lesson; see [research sources](../knowledge/research-frameworks.json).
