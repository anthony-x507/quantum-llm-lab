# Plan maestro — 5 métodos (quantum ↔ LLM fusion)

**Repo:** `anthony-x507/quantum-llm-lab` · **Hardware:** Mac M4 128 GB  
**Claims:** **NO quantum advantage.** Pedagogical / experimental fusion only.  
**Standing rule:** No Cloud Agents. `data/lora_adapter/` is **read-only** (do not fuse/overwrite).  
**Updated:** 2026-09-24 ~04:30 ET

| # | Method | Status now |
|---|--------|------------|
| 1 | Amplitude embedding | **BUILT** — `examples/amplitude_embed_prototype.py` |
| 2 | MPS tensor networks | PLAN ONLY |
| 3 | Real QEC (Steane / surface) self-correction | PLAN ONLY (toy QEC already in repo) |
| 4 | Hybrid model→quantum oracle→model loop | PLAN ONLY (bridge exists; not closed-loop) |
| 5 | Distillation teacher→Qwen8B in quantum format | PLAN ONLY |

---

## 1) Amplitude embedding *(Piece 1 — built)*

**What it is.** Take a small PennyLane circuit (Bell / product), read the **statevector / amplitude vector**, map complex amplitudes to real features (`Re/Im` or `|amp|+phase`), project with a seeded Linear probe into the transformer **embedding dim** (Qwen3-VL-8B text = **4096**), and **inject** that vector as a soft-prompt residual on the first token embedding (or prepend a virtual soft token). Not via text/JSON serialization of the amplitudes.

**Novelty.** Direct numeric channel from simulator Hilbert space into `inputs_embeds`, instead of asking the LLM to read gate lists as text. Side MLP proves the amplitude features alone carry entangled/separable signal.

**Risk.** MLX-VLM generate path does not expose a first-class `inputs_embeds` API; hooks are fragile. OOM if a LoRA train already holds unified memory. Soft-prompt residual can be ignored by a frozen base model (no training of the probe jointly with the LM). Easy to over-claim “quantum” when it is classical simulation + linear algebra.

**Effort.** S (prototype done) → M if joint-training the probe with LoRA.

**Success metric.** On fixed ENT_SET (12 scenes): report `label_acc` and `energy_proxy_acc` for **base vs amp-embed vs LoRA-RO**. Honest win if amp-embed beats base on label; **valid negative** if it does **not** beat LoRA text path.

**How to run.**
```bash
python examples/amplitude_embed_prototype.py --self-test
python examples/amplitude_embed_prototype.py --cpu-eval \
  --ent-set data/bench_live/ent_items.json
# only when TRAIN_LOCK absent / GPU free:
python examples/amplitude_embed_prototype.py --mlx-eval \
  --adapter-ro data/lora_adapter
```

---

## 2) MPS / tensor-network compression of activations *(Piece 2 — plan only)*

**What it is.** Represent intermediate transformer activations (or KV cache slices) as a **Matrix Product State** / tensor train; bond dimension χ controls fidelity vs RAM. Optionally map amplitude tensors of multi-qubit states into the same TN language for a shared “compressed quantum+LM” substrate.

**Novelty.** Classical TN techniques (DMRG-style) as a memory/compute knob for long multimodal contexts on Apple Silicon; shared language with many-qubit simulation.

**Risk.** High engineering cost in MLX; bond-dimension tuning can destroy reasoning quality; little evidence TN helps *entanglement reasoning* vs plain LoRA.

**Effort.** L (weeks).

**Success metric.** Same ENT_SET label/energy vs LoRA baseline at ≤χ_max RAM; perplexity / Jev not worse than −5 pp for ≥30% activation RAM cut.

---

## 3) Real QEC (Steane / surface) for self-correction *(Piece 2 — plan only)*

**What it is.** Move beyond the lab’s **toy syndrome analogy** (`qec_robustness.py`) to an actual **Steane [[7,1,3]]** or small **surface-code** patch: encode a logical qubit, inject Pauli noise, decode (MWPM / lookup), and use the correction event as a **guardrail signal** that resets / rewrites the LLM system prompt when adversarial prompt “errors” are detected.

**Novelty.** Grounding the existing QEC metaphor in a real code distance + decoder, with measurable logical error rate vs physical p.

**Risk.** Still an analogy when wired to text; decoder CPU cost; false positives resetting good generations; over-claiming fault tolerance.

**Effort.** M (Steane lookup) → L (surface + MWPM).

**Success metric.** Decoder recovers ≥99% of single-qubit Pauli errors at code capacity; live wire: adversarial prompt set shows ≥+15 pp Jev recover vs no-QEC guard (same LoRA adapter RO).

---

## 4) Hybrid model → quantum oracle → model loop *(Piece 2 — plan only)*

**What it is.** Close the loop already sketched in `llm_quantum_bridge.py` + Jev: LLM proposes circuit JSON → PennyLane oracle returns probs / amplitudes / energy-proxy → **structured feedback** re-enters the model for a second pass (self-consistency / repair). Optional Studio 2B/4B ranker in the middle (`cluster.yaml`).

**Novelty.** Tool-use with a **physics simulator** as verifier, not a web search tool; amplitudes can feed method (1) on the repair pass.

**Risk.** Infinite repair loops; Thinking models emit non-JSON; latency on M4 when 8B + oracle + second pass stack; base model may ignore oracle numbers.

**Effort.** M (wire existing pieces) → L (multi-turn policy).

**Success metric.** On ENT_SET + fall set: `parse→compile→Jev` after ≤2 oracle rounds ≥ LoRA single-pass; track oracle-reject→repair success rate.

---

## 5) Distillation: teacher → Qwen8B in quantum format *(Piece 2 — plan only)*

**What it is.** A stronger teacher (larger local model, or ensemble of oracle-checked traces) produces **quantum-format** targets: circuit JSON + amplitude feature summaries + Jev rationale. Distill into Qwen3-VL-8B via LoRA/QLoRA **without** overwriting the frozen baseline adapter — train a **new** adapter dir (e.g. `data/lora_adapter_distill/`).

**Novelty.** Distillation target includes **numeric amplitude channels** (method 1 features) alongside text, so the student learns the fusion format end-to-end.

**Risk.** Teacher collapse to template copying; label leak (PASO1 must hold); disk/RAM for another 3-epoch train; still no quantum advantage.

**Effort.** M–L.

**Success metric.** Distill adapter vs frozen `data/lora_adapter/` RO on balanced N≥30: label_acc ≥ baseline, ent gate-combo diversity ≥ baseline, PASO1 leak=0.

---

## Sequencing recommendation

1. **Now:** finish amp-embed CPU metrics; run `--mlx-eval` only when `qlora-ent` / TRAIN_LOCK clear.  
2. **Next piece:** (4) hybrid oracle loop — highest leverage with existing bridge+Jev.  
3. Then (3) Steane wire on top of oracle rejects.  
4. (5) distill once oracle traces exist.  
5. (2) MPS last (highest effort / uncertain LLM gain).

## Non-goals

- Claiming quantum speedup or supremacy.  
- Overwriting `data/lora_adapter/`.  
- Cloud Agents / paid remote GPU for this lane.
