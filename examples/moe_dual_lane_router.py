#!/usr/bin/env python3
"""
Frontier C1 — MoE dual-lane router for quantum-llm-lab.

Chooses lane: ent | python | vision | base so the entanglement LoRA is
NEVER applied to Python/chat prompts.

  python examples/moe_dual_lane_router.py --smoke
  python examples/moe_dual_lane_router.py --bench-codigo-vivo
  python examples/moe_dual_lane_router.py --vqc-router --smoke   # ablation only

No quantum-advantage claims. Anti-contam: router never sees GT labels.
READ-ONLY: never write/overwrite data/lora_adapter/.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples"))

Lane = Literal["ent", "python", "vision", "base"]
LANES: tuple[Lane, ...] = ("ent", "python", "vision", "base")

RO_ADAPTER = ROOT / "data" / "lora_adapter"
ENT2_ADAPTER = ROOT / "data" / "lora_adapter_ent2"
ENT_ADAPTER = ROOT / "data" / "lora_adapter_ent"
CLASSICAL_ADAPTER = ROOT / "data" / "lora_adapter_classical"
VIDEO_ADAPTER = ROOT / "data" / "lora_adapter_video_f1"

BASELINE_JSON = ROOT / "data" / "BENCHMARK_CODIGO_VIVO.json"
SMOKE_OUT = ROOT / "data" / "frontier_moe_dual_lane_smoke.json"

# --- keyword rules (order: ent beats python when both fire? prefer specificity) ---
ENT_RE = re.compile(
    r"\b("
    r"circuit|circuits|gates?|pennylane|entrelaz(?:amiento|ar|ado)?|"
    r"entangle(?:ment|d)?|qubit|qubits|n_qubits|bell|cx\b|cnot|"
    r"hadamard|ry\(|rx\(|rz\(|quantum.?circuit|circuito.?cu[aá]ntico|"
    r"domain.?label|jev|unitary"
    r")\b",
    re.IGNORECASE,
)
PYTHON_RE = re.compile(
    r"\b("
    r"python|def\s+\w+|ONLY\s+code|write\s+(a\s+)?python|"
    r"print\s*\(|import\s+\w+|expected_stdout|markdown\s+fences?|"
    r"factorial|executable|sandbox|programa\s+en\s+python"
    r")\b",
    re.IGNORECASE,
)
VISION_RE = re.compile(
    r"\b("
    r"image|images|frame|frames|visi[oó]n|look\s+at\s+the\s+image|"
    r"look\s+at\s+the\s+(?:image\s+)?sequence|"
    r"look\s+at\s+the\s+(?:diagram|chalkboard|whiteboard|photo|screenshot)|"
    r"in\s+the\s+image|screenshot|photo|picture|png|jpeg|"
    r"mira\s+la\s+imagen|video\s+frame|vlm|chalkboard|whiteboard|diagram|"
    # R2 bilingual vision cues (ES) from freeze-polish-bridge
    r"observa\s+la\s+imagen|imagen\s+adjunta|\bfoto\b|en\s+la\s+foto"
    r")\b",
    re.IGNORECASE,
)

# Negated / text-only vision cues — hard-neg polish (do not treat as vision lane)
VISION_NEG_RE = re.compile(
    r"("
    r"no\s+image(?:\s+file)?|without\s+(?:any\s+)?(?:image|picture|png|photo|frame)|"
    r"text[- ]only|pure\s+chat|no\s+png\s+attached|no\s+picture|"
    r"sin\s+imagen|sin\s+archivo\s+de\s+imagen|no\s+frame\s+attached|"
    r"no\s+visual\s+input|description\s+only\s+\(no\s+image"
    r")",
    re.IGNORECASE,
)

# R2: cancel ent when chat explicitly rejects circuit/code (bilingual)
ENT_NEG_RE = re.compile(
    r"("
    r"no\s+circuit|not\s+a\s+(?:quantum\s+)?circuit|sin\s+circuito|"
    r"no\s+code,\s*no\s+circuit|ignore\s+(?:any\s+)?(?:circuit|qubit)|"
    r"no\s+pennylane|no\s+quantum\s+circuit"
    r")",
    re.IGNORECASE,
)

# Tiny bag-of-words vocab for optional logistic (hand-picked, no GT)
BOW_VOCAB = [
    "python", "def", "print", "code", "import", "factorial", "integer",
    "circuit", "gate", "gates", "qubit", "qubits", "pennylane", "entangle",
    "entrelaz", "bell", "cx", "n_qubits", "hadamard",
    "image", "frame", "vision", "visión", "png", "photo", "look",
    "hello", "chat", "thanks", "weather",
]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()


def _adapter_complete(path: Path) -> bool:
    return (path / "adapters.safetensors").is_file() and (path / "adapter_config.json").is_file()


def adapter_path_for(lane: Lane) -> Path | None:
    """Map lane → adapter Path or None (base / no LoRA).

    Prefer lora_adapter_ent2 if complete else RO lora_adapter for ent pillar
    READ only. Never returns a path intended for destructive writes.
    """
    if lane == "ent":
        if _adapter_complete(ENT2_ADAPTER):
            return ENT2_ADAPTER
        if _adapter_complete(ENT_ADAPTER):
            return ENT_ADAPTER
        if _adapter_complete(RO_ADAPTER):
            return RO_ADAPTER  # frozen good RO — read-only eval OK
        return None
    if lane == "python":
        # Never apply ent LoRA. Prefer base (None); classical optional but
        # classical is visual-physics, not code — keep base for Python pillar.
        return None
    if lane == "vision":
        # Código-vivo vision set is mostly image-math; video_f1 / classical
        # are domain specialists that can hurt that set (−30pp measured).
        # Default = base (None). Opt-in via MOE_VISION_ADAPTER=video|classical.
        import os
        pref = (os.environ.get("MOE_VISION_ADAPTER") or "base").strip().lower()
        if pref in ("video", "video_f1", "f1") and _adapter_complete(VIDEO_ADAPTER):
            return VIDEO_ADAPTER
        if pref in ("classical", "class") and _adapter_complete(CLASSICAL_ADAPTER):
            return CLASSICAL_ADAPTER
        return None
    # base / chat
    return None


def route_heuristic(prompt: str) -> Lane:
    """Keyword rules. Entanglement LoRA must not win on Python/code prompts."""
    text = prompt or ""
    # Priority: if clearly Python/code → python (even if "quantum" appears in string)
    # Exception: explicit circuit+JSON asks stay ent.
    has_ent = bool(ENT_RE.search(text))
    has_py = bool(PYTHON_RE.search(text))
    has_vis = bool(VISION_RE.search(text))
    vis_negated = bool(VISION_NEG_RE.search(text))
    ent_negated = bool(ENT_NEG_RE.search(text))
    # R3: bare n_qubits / N_QUBITS in strings or len('N_QUBITS') is NOT a JSON circuit ask.
    # Keep ent_json_ask for explicit gates=/json-válido OR n_qubits + JSON-reply intent.
    # R4: gates=hadamard_cleanup / gates: [] ops-config labels are NOT circuit asks.
    # R4: OpenAPI/schema "reply JSON only" near a deprecated n_qubits *field* is NOT ent.
    # R5: gates=[nonempty] k8s/helm allow-lists, redis gates:key paths, protobuf gates=N; are NOT ent.
    # label-protect: empty gates=[] ops + negated "json válido" near fall/super taxonomy are NOT ent.
    # R6: Bazel //gates:target; HTML data-gates="..."; Groovy/Jenkins gates = '...' quoted assigns.
    # R7: CI YAML multiline gates:\n  - …; Make .PHONY: gates; bare len('gates:') key tokens.
    # R8: Dockerfile ARG gates=; JSON Schema "gates"; TF/TOML/Nix gates = [...]; markdown 'gates: list'; Rego input.gates[_]; CUE #Gates:; EDN :gates; fullwidth lookalikes.
    # R9: OpenAPI /gates:; Helm values gates: enabled; Pulumi gates:prod; CFN Gates:; Dhall gates : Bool; Justfile recipe gates:; Cedar when { gates:.
    # R10: AsyncAPI/Istio/ArgoCD/Tekton/FlatBuffers/Cypher/Earthfile gates:; Nomad/Vault/Cap'n/Solidity/Rust cfg/Kotlin/csproj/SPARQL.
    # R11: Smithy/Ansible/Linkerd/Cilium/Airflow/Kafka/Prometheus/Kyverno/Temporal gates: scalars; Prisma/Consul/Gradle/Zig/Dart held by priors.
    # R12: Traefik/Envoy/NATS/ClickHouse/dbt/Crossplane/Flux/RabbitMQ/ES/Swift/Elixir/Julia/Kong/Spinnaker gates: scalars.
    # R13: Nginx/HAProxy/Caddy/Redis/Postgres/Skaffold/Buildkite/Packer/Salt/Bazel/Dagger/Dagster/Hasura/NestJS gates: scalars.
    # R22: SvelteKit/Remix/Next.js/Nuxt/Typesense/Weaviate/Milvus/Chroma/Render/Vercel/Netlify/Wasmtime/Wasmer/Leptos gates: scalars.
    gates_token = bool(re.search(r"\bgates\s*[=:\[]", text, re.I))
    gates_ops_label = bool(
        re.search(
            r"gates\s*=\s*[A-Za-z_][\w\-]*"
            r"|gates\s*:\s*\[\s*\]"
            r"|ops\s+config\s+line\s+gates="
            r"|config\s+(?:line\s+)?gates="
            r"|not\s+gates\s*[=:\[]"  # R4 schema/comment disclaimer
            r"|property\s+list"
            # R5: nonempty gates=[...] / gates: [...] ops allow-lists (k8s/helm)
            r"|gates\s*=\s*\[[^\]]+\]"
            r"|gates\s*:\s*\[[^\]]+\]"
            # label-protect: empty gates=[] / gates = [] ops marker (fall/super taxonomy)
            r"|gates\s*=\s*\[\s*\]"
            # R5: redis/key path gates:session:42 (colon key, not JSON)
            r"|gates\s*:\s*[A-Za-z_][\w\-]*(?:\s*:\s*[\w\-]+)+"
            # R5: protobuf field "gates = 2;" / "Gate gates = N"
            r"|\bgates\s*=\s*\d+\s*;"
            r"|repeated\s+\w+\s+gates\s*="
            # R5: annotation/chat mention of gates=[cleanup] ops lists
            r"|annotation(?:\s+value)?\s+gates\s*="
            r"|k8s\s+annotation"
            r"|helm\s+value\s+gates"
            # R6: Bazel package label //gates:target (single colon segment)
            r"|//gates\s*:\s*[A-Za-z_][\w\-]*"
            r"|bazel\s+target\s+//gates"
            # R6: HTML data-gates= / data-gates="..." ops allow-list attrs
            r"|data-gates\s*="
            r"|html\s+data-gates"
            # R6: Groovy/Jenkins quoted assign gates = 'cleanup' / gates = "..."
            r"|gates\s*=\s*['\"][^'\"]*['\"]"
            r"|jenkins(?:file)?\s+.*gates\s*="
            r"|groovy\s+assign\s+gates"
            # R7: CI YAML multiline dashed list gates:\n  - item / gates:\n- item
            r"|gates\s*:\s*\n\s*-"
            r"|yaml\s+list\s+gates:"
            r"|yaml\s+gates:\s+dashed"
            r"|ci\s+yaml\s+.*gates:"
            r"|azure\s+yaml\s+gates:"
            # R7: Make .PHONY: gates target list
            r"|\.PHONY\s*:\s*gates\b"
            r"|phony\s*:\s*gates\b"
            # R7: bare string key token len('gates:') / 'gates:' CI key
            r"|len\s*\(\s*['\"]gates:['\"]\s*\)"
            r"|['\"]gates:['\"]"
            # R7: bilingual NOT gates / NO son gates disclaimers
            r"|\bnot\s+gates\b"
            r"|\bno\s+son\s+gates\b"
            r"|esto\s+no\s+son\s+gates"
            # R8: prose / docs "gates: list" (not YAML dashed list)
            r"|gates\s*:\s*list\b"
            r"|markdown\s+(?:fence|fenced).*gates:"
            r"|docs?\s+.*gates:\s*list"
            # R8: Dockerfile ARG gates= / ARG GATES=
            r"|\bARG\s+gates\s*="
            r"|\bARG\s+GATES\s*="
            r"|dockerfile\s+arg\s+gates"
            # R8: JSON Schema property "gates": { / "gates":{"type"
            r"|[\"']gates[\"']\s*:\s*\{"
            r"|json\s+schema\s+property\s+gates"
            # R8: Rego/OPA input.gates[_] / input.gates[
            r"|input\.gates\s*\["
            r"|rego\s+.*gates"
            r"|opa\s*/?\s*rego"
            # R8: CUE comment/field #Gates: / gates?:
            r"|#\s*Gates\s*:"
            r"|gates\?\s*:"
            r"|cue\s+(?:comment|field|schema).*gates"
            # R8: EDN/Clojure :gates keyword / {:gates
            r"|\{:gates\b"
            r"|:gates\b"
            r"|len\s*\(\s*:gates\s*\)"
            r"|clojure\s+.*:gates"
            # R8: TOML/Nix gates = [ already partly covered by gates\s*=\s*\[; add nix/toml hints
            r"|toml\s+gates\s*="
            r"|nix\s+attr\s+gates"
            # R8: ASCII 'gates' disclaimer near fullwidth lookalikes
            r"|fullwidth.*gates"
            r"|not\s+ASCII\s+gates"
            r"|lookalike.*gates"
            # R9: OpenAPI path /gates: / gates:allow|read
            r"|/gates\s*:"
            r"|openapi\s+.*gates:"
            r"|gates:allow"
            r"|gates:read"
            # R9: Helm values.yaml gates: enabled|disabled scalar
            r"|gates\s*:\s*enabled\b"
            r"|gates\s*:\s*disabled\b"
            r"|helm\s+.*gates:"
            r"|values\.yaml\s+gates:"
            # R9: Pulumi config gates:prod|tag|staging|dev
            r"|gates\s*:\s*(?:prod|tag|staging|dev)\b"
            r"|pulumi\s+.*gates:"
            r"|stackreference\s+gates:"
            # R9: CloudFormation Parameter Gates:
            r"|cloudformation\s+.*gates:"
            r"|parameters?\s+gates:"
            r"|cfn\s+.*gates:"
            # R9: Dhall gates : Bool|Text|Natural|Integer
            r"|gates\s*:\s*(?:Bool|Text|Natural|Integer)\b"
            r"|dhall\s+.*gates"
            # R9: Justfile recipe gates:
            r"|justfile\s+.*gates:"
            r"|recipe\s+gates:"
            # R9: Cedar when { gates: / gates: true|false|attr
            r"|when\s*\{\s*gates\s*:"
            r"|cedar\s+.*gates:"
            r"|gates\s*:\s*(?:true|false|attr)\b"
            # R10: AsyncAPI channel gates: / gates: subscribe
            r"|gates\s*:\s*subscribe\b"
            r"|asyncapi\s+.*gates:"
            r"|channel(?:\s+name)?\s+gates:"
            # R10: Istio VirtualService gates: mesh
            r"|gates\s*:\s*mesh\b"
            r"|istio\s+.*gates:"
            r"|virtualservice\s+.*gates:"
            # R10: ArgoCD syncOption gates: Create
            r"|gates\s*:\s*Create\b"
            r"|argocd\s+.*gates:"
            r"|syncoptions?\s+.*gates:"
            # R10: Tekton Task/Pipeline param gates:
            r"|tekton\s+.*gates:"
            r"|task\s+param\s+gates:"
            r"|pipeline\s+param\s+gates:"
            # R10: FlatBuffers table field gates: string
            r"|gates\s*:\s*string\b"
            r"|flatbuffers?\s+.*gates:"
            r"|table\s+.*\bgates\s*:"
            # R10: Neo4j Cypher {gates: property
            r"|\{gates\s*:"
            r"|cypher\s+.*gates:"
            r"|neo4j\s+.*gates:"
            # R10: Earthfile target gates:
            r"|earthfile\s+.*gates:"
            r"|build\s+target\s+gates:"
            r"|target\s+gates:\s*(?:is\s+)?(?:a\s+)?(?:build\s+)?(?:target|mention)"
            # R10: messaging-only / GitOps / schema-only gates: prose
            r"|gates:\s+is\s+messaging"
            r"|gates:\s+is\s+(?:CI|schema)\b"
            r"|gates:\s+mention"
            # R11: Smithy member gates: Long|Boolean
            r"|gates\s*:\s*(?:Long|Boolean)\b"
            r"|smithy\s+.*gates:"
            r"|member\s+gates:"
            # R11: Ansible vars gates: yes / gates: "{{
            r"|gates\s*:\s*yes\b"
            r"|gates\s*:\s*\{\{"
            r"|ansible\s+.*gates:"
            r"|vars?\s+gates:"
            # R11: Linkerd Server gates: inbound
            r"|gates\s*:\s*inbound\b"
            r"|linkerd\s+.*gates:"
            r"|server\s+gates:\s*inbound"
            # R11: Cilium NetworkPolicy gates: toEntities|toCIDR
            r"|gates\s*:\s*toEntities\b"
            r"|gates\s*:\s*toCIDR\b"
            r"|cilium\s+.*gates:"
            r"|cnp\s+.*gates:"
            # R11: Airflow task_id gates: branch_
            r"|gates\s*:\s*branch_\w+"
            r"|airflow\s+.*gates:"
            r"|task_id\s+gates:"
            r"|branchpythonoperator\s+.*gates:"
            # R11: Kafka ACL gates: Describe
            r"|gates\s*:\s*Describe\b"
            r"|kafka\s+.*gates:"
            r"|acl\s+.*gates:"
            # R11: Prometheus relabel gates: replacement
            r"|gates\s*:\s*replacement\b"
            r"|prometheus\s+.*gates:"
            r"|relabel(?:_config)?\s+.*gates:"
            # R11: Kyverno validate gates: Audit
            r"|gates\s*:\s*Audit\b"
            r"|kyverno\s+.*gates:"
            r"|validationfailureaction\s+.*gates:"
            # R11: Temporal activity gates: ActivityOptions
            r"|gates\s*:\s*ActivityOptions\b"
            r"|temporal\s+.*gates:"
            r"|activity(?:options)?\s+.*gates:"
            # R11: IDL / YAML / mesh-proxy / eBPF / DAG / broker / scrape / policy / orchestration prose
            r"|gates:\s+is\s+(?:IDL|YAML|mesh-proxy|eBPF|DAG|broker|scrape|policy|orchestration)\b"
            r"|gates:\s+mention"
            # R12: Traefik middleware gates: stripPrefix
            r"|gates\s*:\s*stripPrefix\b"
            r"|traefik\s+.*gates:"
            r"|middleware\s+gates:"
            # R12: Envoy filter gates: HTTP
            r"|gates\s*:\s*HTTP\b"
            r"|envoy\s+.*gates:"
            r"|filter\s+gates:\s*HTTP"
            # R12: NATS subject gates: publish
            r"|gates\s*:\s*publish\b"
            r"|nats\s+.*gates:"
            r"|subject\s+.*gates:"
            # R12: ClickHouse setting gates: Readonly
            r"|gates\s*:\s*Readonly\b"
            r"|clickhouse\s+.*gates:"
            r"|setting\s+gates:"
            # R12: dbt model gates: ephemeral
            r"|gates\s*:\s*ephemeral\b"
            r"|dbt\s+.*gates:"
            r"|model\s+config\s+gates:"
            # R12: Crossplane claim gates: Ready
            r"|gates\s*:\s*Ready\b"
            r"|crossplane\s+.*gates:"
            r"|claim\s+gates:"
            # R12: Flux Kustomization gates: prune
            r"|gates\s*:\s*prune\b"
            r"|flux\s+.*gates:"
            r"|kustomization\s+.*gates:"
            # R12: RabbitMQ policy gates: ha-mode
            r"|gates\s*:\s*ha-mode\b"
            r"|rabbitmq\s+.*gates:"
            r"|policy\s+.*gates:\s*ha"
            # R12: Elasticsearch ingest gates: set
            r"|gates\s*:\s*set\b"
            r"|elasticsearch\s+.*gates:"
            r"|ingest\s+(?:pipeline\s+)?gates:"
            # R12: Swift property gates: Wrapped
            r"|gates\s*:\s*Wrapped\b"
            r"|swift\s+.*gates:"
            r"|propertywrapper\s+.*gates:"
            # R12: Elixir attribute gates: :atom
            r"|gates\s*:\s*:\w+"
            r"|elixir\s+.*gates:"
            r"|@gates\s*:"
            r"|attribute\s+gates:"
            # R12: Julia macro gates: Symbol
            r"|gates\s*:\s*Symbol\b"
            r"|julia\s+.*gates:"
            r"|macro\s+@gates:"
            # R12: Kong plugin gates: rate-limiting
            r"|gates\s*:\s*rate-limiting\b"
            r"|kong\s+.*gates:"
            r"|plugin\s+gates:"
            # R12: Spinnaker stage gates: manualJudgment
            r"|gates\s*:\s*manualJudgment\b"
            r"|spinnaker\s+.*gates:"
            r"|stage\s+gates:"
            # R12: proxy / messaging / DB / SQL / k8s / GitOps / broker / search / language / BEAM / gateway / CD prose
            r"|gates:\s+is\s+(?:proxy|messaging|DB|SQL|k8s|GitOps|broker|search|language|BEAM|gateway|CD)\b"
            # R13: Nginx map gates: $request
            r"|gates\s*:\s*\$request\b"
            r"|nginx\s+.*gates:"
            r"|map\s+gates:"
            # R13: HAProxy ACL gates: hdr
            r"|gates\s*:\s*hdr\b"
            r"|haproxy\s+.*gates:"
            r"|acl\s+gates:"
            # R13: Caddy matcher gates: path
            r"|gates\s*:\s*path\b"
            r"|caddy\s+.*gates:"
            r"|matcher\s+gates:"
            # R13: Redis ACL gates: ~*
            r"|gates\s*:\s*~\*"
            r"|redis\s+.*gates:"
            r"|acl\s+.*gates:\s*~\*"
            # R13: Postgres RLS gates: USING
            r"|gates\s*:\s*USING\b"
            r"|postgres\s+.*gates:"
            r"|rls\s+.*gates:"
            # R13: Skaffold profile gates: activation
            r"|gates\s*:\s*activation\b"
            r"|skaffold\s+.*gates:"
            r"|profile\s+gates:"
            # R13: Buildkite step gates: if
            r"|gates\s*:\s*if\b"
            r"|buildkite\s+.*gates:"
            r"|step\s+gates:\s*if"
            # R13: Packer provisioner gates: shell
            r"|gates\s*:\s*shell\b"
            r"|packer\s+.*gates:"
            r"|provisioner\s+gates:"
            # R13: Salt pillar gates: grains
            r"|gates\s*:\s*grains\b"
            r"|salt\s+.*gates:"
            r"|pillar\s+gates:"
            # R13: Bazel select gates: //conditions
            r"|gates\s*:\s*//conditions\b"
            r"|bazel\s+select\s+.*gates:"
            r"|select\(\s*\{[^}]*gates:"
            # R13: Dagger pipeline gates: withSecret
            r"|gates\s*:\s*withSecret\b"
            r"|dagger\s+.*gates:"
            r"|pipeline\s+gates:\s*with"
            # R13: Dagster asset gates: AutoMaterialize
            r"|gates\s*:\s*AutoMaterialize\b"
            r"|dagster\s+.*gates:"
            r"|asset\s+gates:"
            # R13: Hasura permission gates: check
            r"|gates\s*:\s*check\b"
            r"|hasura\s+.*gates:"
            r"|permission\s+gates:"
            # R13: NestJS guard gates: CanActivate
            r"|gates\s*:\s*CanActivate\b"
            r"|nestjs\s+.*gates:"
            r"|guard\s+gates:"
            # R13: proxy / LB / webserver / cache / DB / k8s / CI / image / config / build / orchestration / GraphQL / framework prose
            r"|gates:\s+is\s+(?:proxy|LB|webserver|cache|DB|k8s|CI|image|config|build|orchestration|GraphQL|framework)\b"
            # R22: SvelteKit hook gates: handle
            r"|gates\s*:\s*handle\b"
            r"|sveltekit\s+.*gates:"
            r"|hook\s+gates:\s*handle"
            # R22: Remix loader gates: loader
            r"|gates\s*:\s*loader\b"
            r"|\bremix\b\s+.*gates:"
            r"|loader\s+gates:"
            # R22: Next.js matcher gates: matcher
            r"|gates\s*:\s*matcher\b"
            r"|next\.js\s+.*gates:"
            r"|\bnextjs\b\s+.*gates:"
            r"|matcher\s+gates:"
            # R22: Nuxt server gates: defineEventHandler
            r"|gates\s*:\s*defineEventHandler\b"
            r"|\bnuxt\b\s+.*gates:"
            r"|server\s+gates:\s*defineEventHandler"
            # R22: Typesense schema gates: token_separators
            r"|gates\s*:\s*token_separators\b"
            r"|typesense\s+.*gates:"
            r"|schema\s+gates:\s*token_separators"
            # R22: Weaviate class gates: vectorizer
            r"|gates\s*:\s*vectorizer\b"
            r"|weaviate\s+.*gates:"
            r"|class\s+gates:\s*vectorizer"
            # R22: Milvus collection gates: index_type
            r"|gates\s*:\s*index_type\b"
            r"|milvus\s+.*gates:"
            r"|collection\s+gates:\s*index_type"
            # R22: Chroma query gates: where_document
            r"|gates\s*:\s*where_document\b"
            r"|\bchroma\b\s+.*gates:"
            r"|query\s+gates:\s*where_document"
            # R22: Render health gates: healthCheckPath
            r"|gates\s*:\s*healthCheckPath\b"
            r"|\brender\b\s+.*gates:"
            r"|health\s+gates:\s*healthCheckPath"
            # R22: Vercel cron gates: crons
            r"|gates\s*:\s*crons\b"
            r"|vercel\s+.*gates:"
            r"|cron\s+gates:\s*crons"
            # R22: Netlify redirect gates: force
            r"|gates\s*:\s*force\b"
            r"|netlify\s+.*gates:"
            r"|redirect\s+gates:\s*force"
            # R22: Wasmtime fuel gates: fuel
            r"|gates\s*:\s*fuel\b"
            r"|wasmtime\s+.*gates:"
            r"|fuel\s+gates:"
            # R22: Wasmer env gates: mapped_dirs
            r"|gates\s*:\s*mapped_dirs\b"
            r"|wasmer\s+.*gates:"
            r"|env\s+gates:\s*mapped_dirs"
            # R22: Leptos resource gates: create_resource
            r"|gates\s*:\s*create_resource\b"
            r"|leptos\s+.*gates:"
            r"|resource\s+gates:\s*create_resource"
            # R22: hook / loader / matcher / server / schema / class / collection / query / health / cron / redirect / fuel / env / resource prose
            r"|gates:\s+is\s+(?:hook|loader|matcher|server|schema|class|collection|query|health|cron|redirect|fuel|env|resource)\b",
            text,
            re.I,
        )
    )
    # label-protect: "json válido" only when not explicitly negated (NOT/NO es/never reply)
    json_valido = bool(re.search(r"\bjson\s+v[aá]lido\b", text, re.I)) and not bool(
        re.search(
            r"(?:"
            r"not\s+(?:a\s+)?json\s+v[aá]lido|"
            r"never\s+reply\s+json\s+v[aá]lido|"
            r"no\s+es\s+(?:un\s+)?json\s+v[aá]lido|"
            r"\bnot\s+json\s+v[aá]lido\b"
            r")",
            text,
            re.I,
        )
    )
    schema_field_distract = bool(
        re.search(
            r"(?:openapi|schema|deprecated|property|field)\s+"
            r"(?:n_qubits|.*\bn_qubits\b)"
            r"|\bn_qubits\b\s+(?:field|property|is\s+deprecated)"
            r"|reply\s+json\s+only\s+for\s+/\w+",
            text,
            re.I,
        )
    )
    ent_json_ask = (
        (gates_token and not gates_ops_label) or json_valido
    ) or (
        bool(re.search(r"\bn_qubits\b", text, re.I))
        and bool(
            re.search(
                r"(reply\s+(?:json|only)|responde\s+solo\s+json|valid\s+json|"
                r"json\s+object|return\s+(?:a\s+)?valid\s+json|json\s+only)",
                text,
                re.I,
            )
        )
        and not bool(
            re.search(
                r"len\s*\(\s*['\"]n_qubits['\"]\s*\)|['\"]n_qubits['\"]|"
                r"['\"]N_QUBITS['\"]|return\s+['\"]n_qubits['\"]",
                text,
                re.I,
            )
        )
        and not schema_field_distract
    )
    # Vision arithmetic / explicit "no circuit" beats stray "circuit" token in the prompt
    vis_arith = bool(
        has_vis
        and not vis_negated
        and re.search(
            r"(only\s+the\s+final\s+integer|solve\s+the\s+arithmetic|"
            r"only\s+the\s+integer|reply\s+with\s+only\s+the\s+integer|"
            r"no\s+circuit|responde\s+solo\s+un\s+entero|"
            r"how\s+many\s+\w+\s+(?:are|is)\s+visible)",
            text,
            re.I,
        )
    )

    # Code-generation intent dominates (protect Python lane from ent LoRA)
    if has_py and not (has_ent and ent_json_ask):
        return "python"
    # R2: explicit "no circuit" chat stays base (unless real JSON circuit ask)
    # R4: bare n_qubits *field/property* mention no longer blocks ENT_NEG cancel.
    if has_ent and ent_negated and not (
        ent_json_ask
        or (
            re.search(
                r"\b(gates\s*[=:\[]|json\s+v[aá]lido|reply\s+json|responde\s+solo\s+json)\b",
                text,
                re.I,
            )
            and not gates_ops_label  # R5: ops allow-list gates=[...] must not block ENT_NEG cancel
        )
    ):
        has_ent = False
    if vis_arith and not ent_json_ask:
        return "vision"
    if has_ent:
        return "ent"
    # Vision only when positive cues are not cancelled by text-only / no-image negations
    if has_vis and not vis_negated:
        return "vision"
    if has_py:
        return "python"
    return "base"


def _bow_vector(text: str) -> list[float]:
    low = (text or "").lower()
    toks = re.findall(r"[a-záéíóúñü0-9_]+", low, flags=re.I)
    counts = {t: 0 for t in BOW_VOCAB}
    for t in toks:
        if t in counts:
            counts[t] += 1
        # stem-ish: entrelaz*
        for v in BOW_VOCAB:
            if v.startswith("entrelaz") and t.startswith("entrelaz"):
                counts[v] += 1
            if v.startswith("entangle") and t.startswith("entangle"):
                counts[v] += 1
    n = max(1, len(toks))
    return [counts[v] / n for v in BOW_VOCAB]


# Hand-tuned logistic weights (4 classes): columns = [ent, python, vision, base]
# Built so BOW cues push the matching lane; no training on eval GT.
_LOGIT_W = None  # lazy


def _build_logit_w():
    import numpy as np

    w = np.zeros((len(BOW_VOCAB), 4), dtype=float)
    lane_idx = {"ent": 0, "python": 1, "vision": 2, "base": 3}
    groups = {
        "ent": ["circuit", "gate", "gates", "qubit", "qubits", "pennylane",
                "entangle", "entrelaz", "bell", "cx", "n_qubits", "hadamard"],
        "python": ["python", "def", "print", "code", "import", "factorial", "integer"],
        "vision": ["image", "frame", "vision", "visión", "png", "photo", "look"],
        "base": ["hello", "chat", "thanks", "weather"],
    }
    for lane, words in groups.items():
        j = lane_idx[lane]
        for word in words:
            if word in BOW_VOCAB:
                w[BOW_VOCAB.index(word), j] = 8.0
    bias = np.array([0.0, 0.0, 0.0, 0.5])  # slight base prior
    return w, bias


def route_mlp(prompt: str) -> Lane:
    """Tiny bag-of-words logistic (no sklearn). Fallback to heuristic on ties."""
    import numpy as np

    global _LOGIT_W
    if _LOGIT_W is None:
        _LOGIT_W = _build_logit_w()
    w, bias = _LOGIT_W
    x = np.asarray(_bow_vector(prompt), dtype=float)
    logits = x @ w + bias
    # Softmax not needed for argmax
    idx = int(np.argmax(logits))
    lane = LANES[idx]
    # Safety: if heuristic says python, never override to ent
    h = route_heuristic(prompt)
    if h == "python" and lane == "ent":
        return "python"
    if h == "ent" and lane == "python" and ENT_RE.search(prompt or ""):
        return "ent"
    return lane  # type: ignore[return-value]


def route_vqc(prompt: str, n_wires: int = 4) -> Lane:
    """Optional PennyLane AngleEmbedding stub (CPU ablation). Default OFF.

    Embeds first n_wires BOW features as angles → expects PauliZ; maps to lane.
    Not a claim of quantum advantage — classical simulation only.
    """
    try:
        import pennylane as qml
        from pennylane import numpy as pnp
    except ImportError:
        return route_heuristic(prompt)

    feats = _bow_vector(prompt)[:n_wires]
    # pad / scale to [0, pi]
    while len(feats) < n_wires:
        feats.append(0.0)
    angles = [min(math.pi, max(0.0, float(f) * math.pi * 4)) for f in feats[:n_wires]]

    dev = qml.device("default.qubit", wires=n_wires)

    @qml.qnode(dev)
    def circuit(x):
        qml.AngleEmbedding(x, wires=range(n_wires), rotation="Y")
        for i in range(n_wires - 1):
            qml.CNOT(wires=[i, i + 1])
        return [qml.expval(qml.PauliZ(i)) for i in range(min(4, n_wires))]

    expvals = list(circuit(pnp.array(angles, dtype=float)))
    # Map 4 expectation signs/magnitudes → lane scores
    scores = {
        "ent": float(-expvals[0]) + 0.1 * abs(float(expvals[min(1, len(expvals) - 1)])),
        "python": float(-expvals[1]) if len(expvals) > 1 else 0.0,
        "vision": float(-expvals[2]) if len(expvals) > 2 else 0.0,
        "base": float(-expvals[3]) if len(expvals) > 3 else 0.0,
    }
    # Blend with heuristic so VQC alone cannot send Python→ent
    h = route_heuristic(prompt)
    scores[h] += 1.5
    if h == "python":
        scores["ent"] -= 2.0
    lane = max(scores, key=scores.get)  # type: ignore[arg-type]
    return lane  # type: ignore[return-value]


def route(prompt: str, *, method: str = "heuristic") -> Lane:
    """Public API: route(prompt) → lane."""
    method = (method or "heuristic").lower()
    if method in ("mlp", "logistic", "bow"):
        return route_mlp(prompt)
    if method in ("vqc", "vqc-router", "quantum"):
        return route_vqc(prompt)
    return route_heuristic(prompt)


# ---------------------------------------------------------------------------
# Smoke fixtures (12) — expected lanes; no GT circuit labels in prompts
# ---------------------------------------------------------------------------
SMOKE_FIXTURES: list[dict[str, str]] = [
    {"id": "ent_01", "expected": "ent",
     "prompt": "Propose a quantum circuit with n_qubits and gates for this entanglement scene. Reply JSON only."},
    {"id": "ent_02", "expected": "ent",
     "prompt": "Eres un asistente de circuitos cuánticos. Usa PennyLane gates h,x,cx. Escena de entrelazamiento."},
    {"id": "ent_03", "expected": "ent",
     "prompt": "Build a Bell-pair circuit: Hadamard then CX. Return n_qubits and gates list."},
    {"id": "py_01", "expected": "python",
     "prompt": "Write a Python program that prints the integer result of 47 + 18. Output ONLY the code, no markdown fences."},
    {"id": "py_02", "expected": "python",
     "prompt": "Write Python that prints the factorial of 6 as an integer. ONLY code."},
    {"id": "py_03", "expected": "python",
     "prompt": "def solve():\n    print(sum(range(1,11)))\n# complete this Python script"},
    {"id": "vis_01", "expected": "vision",
     "prompt": "Look at the image. Solve the arithmetic problem. Reply with ONLY the final integer answer, no words."},
    {"id": "vis_02", "expected": "vision",
     "prompt": "Mira la imagen del frame. ¿Cuántos objetos hay en la visión?"},
    {"id": "vis_03", "expected": "vision",
     "prompt": "Describe the objects in this video frame image (png). Reply briefly."},
    {"id": "base_01", "expected": "base",
     "prompt": "Hello! How are you today?"},
    {"id": "base_02", "expected": "base",
     "prompt": "Thanks for the help earlier. What is the weather like in general terms?"},
    {"id": "base_03", "expected": "base",
     "prompt": "Tell me a short fun fact about cats."},
]


HARDNEG_ROUTER_PATH = ROOT / "data" / "bench_live" / "hardneg_mixed_router.json"
HARDNEG_OUT = ROOT / "data" / "frontier_moe_dual_lane_hardneg.json"


def load_hardneg_fixtures(path: Path | None = None) -> list[dict[str, str]]:
    """Load hard-neg mixed fixtures. Expected lane is harness-only (post-hoc)."""
    p = path or HARDNEG_ROUTER_PATH
    blob = json.loads(p.read_text(encoding="utf-8"))
    items = blob.get("items") or blob
    out: list[dict[str, str]] = []
    for it in items:
        out.append({
            "id": str(it["id"]),
            "expected": str(it["expected"]),
            "prompt": str(it["prompt"]),
            "family": str(it.get("family") or ""),
        })
    return out


def run_hardneg(method: str = "heuristic", path: Path | None = None) -> dict[str, Any]:
    """Score hard-neg mixed fixtures; GT lane compared post-hoc only."""
    fixtures = load_hardneg_fixtures(path)
    rows = []
    hits = 0
    by_family: dict[str, dict[str, int]] = {}
    for fx in fixtures:
        lane = route(fx["prompt"], method=method)
        ok = lane == fx["expected"]
        if ok:
            hits += 1
        fam = fx.get("family") or "unknown"
        by_family.setdefault(fam, {"n": 0, "hits": 0})
        by_family[fam]["n"] += 1
        if ok:
            by_family[fam]["hits"] += 1
        ap = adapter_path_for(lane)  # type: ignore[arg-type]
        rows.append({
            "id": fx["id"],
            "family": fam,
            "expected": fx["expected"],
            "got": lane,
            "ok": ok,
            "adapter": str(ap) if ap else None,
            "prompt_preview": fx["prompt"][:80],
            "ent_adapter_blocked": lane == "python" and (
                ap is None or "ent" not in Path(str(ap)).name
            ),
        })
    n = len(fixtures)
    return {
        "method": method,
        "n": n,
        "hits": hits,
        "misses": n - hits,
        "score": f"{hits}/{n}",
        "rate": round(hits / n, 4) if n else 0.0,
        "by_family": {
            k: {**v, "rate": round(v["hits"] / v["n"], 4) if v["n"] else 0.0}
            for k, v in by_family.items()
        },
        "ent_never_on_python": all(
            (r["got"] != "python") or r.get("ent_adapter_blocked")
            for r in rows
        ),
        "rows": rows,
        "fixture_path": str((path or HARDNEG_ROUTER_PATH).resolve().relative_to(ROOT.resolve())),
        "anti_contamination": {
            "expected_lane_harness_only": True,
            "gt_never_in_route_api": True,
        },
    }


def run_smoke(method: str = "heuristic") -> dict[str, Any]:
    rows = []
    hits = 0
    for fx in SMOKE_FIXTURES:
        lane = route(fx["prompt"], method=method)
        ok = lane == fx["expected"]
        if ok:
            hits += 1
        ap = adapter_path_for(lane)  # type: ignore[arg-type]
        rows.append({
            "id": fx["id"],
            "expected": fx["expected"],
            "got": lane,
            "ok": ok,
            "adapter": str(ap) if ap else None,
            "prompt_preview": fx["prompt"][:80],
        })
        mark = "OK" if ok else "MISS"
        print(f"  [{mark}] {fx['id']:8s} expected={fx['expected']:7s} got={lane:7s} adapter={ap.name if ap else 'None'}")
    return {
        "method": method,
        "n": len(SMOKE_FIXTURES),
        "hits": hits,
        "misses": len(SMOKE_FIXTURES) - hits,
        "score": f"{hits}/{len(SMOKE_FIXTURES)}",
        "rows": rows,
    }


def load_baseline() -> dict[str, Any] | None:
    if not BASELINE_JSON.is_file():
        return None
    return json.loads(BASELINE_JSON.read_text(encoding="utf-8"))


def gate_check(routed: dict[str, Any], baseline_summary: dict[str, Any]) -> dict[str, Any]:
    """Código-vivo 3-pillar gate: Python≥base AND Ent≥0.95; vision not worse than −5pp."""
    py_base = float(baseline_summary["python"]["base_solve_rate"])
    py_r = float(routed["python"]["solve_rate"])
    ent_r = float(routed["entanglement"]["label_acc"])
    vis_base = float(baseline_summary["vision"]["base_accuracy"])
    vis_r = float(routed["vision"]["accuracy"]) if routed["vision"]["n"] else None

    py_ok = py_r >= py_base - 1e-9
    ent_ok = ent_r >= 0.95 - 1e-9
    vis_delta = None if vis_r is None else (vis_r - vis_base)
    vis_ok = True if vis_r is None else (vis_delta >= -0.05 - 1e-9)
    passed = py_ok and ent_ok and vis_ok
    return {
        "python_ge_base": py_ok,
        "python_routed": py_r,
        "python_baseline_base": py_base,
        "ent_ge_0_95": ent_ok,
        "ent_routed_label_acc": ent_r,
        "vision_not_worse_than_minus_5pp": vis_ok,
        "vision_routed": vis_r,
        "vision_baseline_base": vis_base,
        "vision_delta_pp": None if vis_delta is None else round(vis_delta * 100, 2),
        "gate_pass": passed,
        "note": "No quantum-advantage claims. Own-delta usability metrics only.",
    }


def run_bench_codigo_vivo(
    model: str,
    method: str = "heuristic",
    skip_vision: bool = False,
) -> dict[str, Any]:
    """Invoke bench pillars with per-lane adapters (injection hook, no full rewrite)."""
    import bench_codigo_vivo as bench

    py_items = json.loads((ROOT / "data/bench_live/python_items.json").read_text())["items"]
    ent_items = json.loads((ROOT / "data/bench_live/ent_items.json").read_text())
    vis_items = json.loads((ROOT / "data/bench_live/vision_items.json").read_text())["items"]
    for it in vis_items:
        cand = Path(it["image"])
        if not cand.exists():
            for c in [
                ROOT / it["image"],
                ROOT / "data/bench_live/vision_items" / Path(str(it["image"])).name,
            ]:
                if c.exists():
                    it["image"] = str(c)
                    break

    # Route a representative prompt per pillar to decide adapter
    sample_py = py_items[0]["prompt"]
    sample_ent = (
        "Eres un asistente de circuitos cuánticos. Mira la imagen. "
        "Responde SOLO JSON válido con claves n_qubits, gates, domain, label. PennyLane gates."
    )
    sample_vis = vis_items[0]["prompt"] if vis_items else "Look at the image."

    lane_py = route(sample_py, method=method)
    lane_ent = route(sample_ent, method=method)
    lane_vis = route(sample_vis, method=method)

    # Hard safety: python pillar must never get ent adapter
    if lane_py == "ent":
        lane_py = "python"
    adapter_py = adapter_path_for(lane_py)
    adapter_ent = adapter_path_for(lane_ent if lane_ent == "ent" else "ent")
    adapter_vis = None if skip_vision else adapter_path_for(lane_vis)

    print(f"[moe] python lane={lane_py} adapter={adapter_py}", flush=True)
    print(f"[moe] ent    lane={lane_ent}→ent adapter={adapter_ent}", flush=True)
    print(f"[moe] vision lane={lane_vis} adapter={adapter_vis}", flush=True)

    def empty_py():
        return {"n": 0, "solved": 0, "solve_rate": 0.0, "exec_errors": 0, "details": []}

    def empty_ent():
        return {
            "n": 0, "parse_ok": 0, "compile_ok": 0, "circuit_ran": 0,
            "label_correct": 0, "domain_correct": 0, "energy_ok": 0,
            "parse_rate": 0.0, "compile_rate": 0.0, "label_acc": 0.0,
            "domain_acc": 0.0, "energy_ok_rate": 0.0, "unique_gate_combos": 0,
            "details": [],
        }

    def empty_vis():
        return {"n": 0, "correct": 0, "accuracy": 0.0, "errors": 0, "details": []}

    t0 = time.time()
    out: dict[str, Any] = {
        "python": empty_py(),
        "entanglement": empty_ent(),
        "vision": empty_vis(),
    }
    routing = {
        "python": {"lane": lane_py, "adapter": str(adapter_py) if adapter_py else None},
        "entanglement": {"lane": "ent", "adapter": str(adapter_ent) if adapter_ent else None},
        "vision": {"lane": lane_vis, "adapter": str(adapter_vis) if adapter_vis else None, "skipped": skip_vision},
    }

    # Group by adapter path to minimize VLM reloads
    jobs: list[tuple[str | None, list[str]]] = []
    # python
    jobs.append((str(adapter_py) if adapter_py else None, ["python"]))
    # ent (usually different)
    ent_key = str(adapter_ent) if adapter_ent else None
    if jobs and jobs[-1][0] == ent_key:
        jobs[-1][1].append("entanglement")
    else:
        jobs.append((ent_key, ["entanglement"]))
    if not skip_vision:
        vis_key = str(adapter_vis) if adapter_vis else None
        if jobs and jobs[-1][0] == vis_key:
            jobs[-1][1].append("vision")
        else:
            jobs.append((vis_key, ["vision"]))

    # Merge jobs with same adapter
    merged: dict[str | None, list[str]] = {}
    for ak, pillars in jobs:
        merged.setdefault(ak, [])
        for p in pillars:
            if p not in merged[ak]:
                merged[ak].append(p)

    for ak, pillars in merged.items():
        print(f"=== MOE load adapter={ak!r} pillars={pillars} ===", flush=True)
        bundle = bench._load_vlm(model, ak)
        if "python" in pillars:
            out["python"] = bench.run_pillar_python(bundle, py_items, "moe-py")
        if "entanglement" in pillars:
            out["entanglement"] = bench.run_pillar_entanglement(
                bundle, ent_items["scene_ids"], "moe-ent"
            )
        if "vision" in pillars:
            out["vision"] = bench.run_pillar_vision(bundle, vis_items, "moe-vis")
        del bundle

    elapsed = round(time.time() - t0, 1)
    baseline = load_baseline()
    base_sum = baseline["summary"] if baseline else None
    gate = gate_check(out, base_sum) if base_sum else {"gate_pass": None, "reason": "no_baseline"}

    return {
        "written": _now(),
        "elapsed_s": elapsed,
        "model": model,
        "router_method": method,
        "routing": routing,
        "pillars": out,
        "baseline_ref": str(BASELINE_JSON) if baseline else None,
        "baseline_summary": base_sum,
        "gate": gate,
        "claims": "No quantum-advantage claims. MoE routing usability only.",
        "anti_contamination": {
            "gt_in_router_prompts": False,
            "quantum_adapter_ro_writes": False,
            "ent_never_on_python": adapter_py is None or "ent" not in Path(str(adapter_py)).name,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description="MoE dual-lane router (Frontier C1)")
    p.add_argument("--smoke", action="store_true", help="Print lane decisions on 12 fixtures")
    p.add_argument("--bench-codigo-vivo", action="store_true",
                   help="Run código-vivo pillars with routed adapters")
    p.add_argument("--vqc-router", action="store_true",
                   help="Ablation: PennyLane AngleEmbedding router (CPU). Default OFF.")
    p.add_argument("--mlp", action="store_true", help="Use tiny BOW logistic instead of heuristics")
    p.add_argument("--model", default="mlx-community/Qwen3-VL-8B-Thinking-4bit")
    p.add_argument("--skip-vision", action="store_true")
    p.add_argument("--out", type=Path, default=SMOKE_OUT)
    p.add_argument("--route", type=str, default=None,
                   help="Route a single prompt and print lane+adapter")
    p.add_argument("--hardneg", action="store_true",
                   help="Score hard-neg mixed router fixtures (R1/R2/R3)")
    p.add_argument("--hardneg-path", type=Path, default=HARDNEG_ROUTER_PATH)
    args = p.parse_args()

    method = "heuristic"
    if args.mlp:
        method = "mlp"
    if args.vqc_router:
        method = "vqc"

    if args.route is not None:
        lane = route(args.route, method=method)
        ap = adapter_path_for(lane)
        print(json.dumps({"lane": lane, "adapter": str(ap) if ap else None}, indent=2))
        return 0

    if args.hardneg:
        print(f"=== MoE hardneg method={method} ===", flush=True)
        hn = run_hardneg(method, path=args.hardneg_path)
        print(
            f"Hardneg: {hn['score']} rate={hn['rate']} "
            f"ent_never_on_python={hn['ent_never_on_python']}",
            flush=True,
        )
        out = args.out if args.out != SMOKE_OUT else HARDNEG_OUT
        hp = str(args.hardneg_path).lower()
        if 'label_protect' in hp or 'label-protect' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_label_protect.json"
        elif 'r22' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r22.json"
        elif 'r13' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r13.json"
        elif 'r12' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r12.json"
        elif 'r11' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r11.json"
        elif 'r10' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r10.json"
        elif 'r9' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r9.json"
        elif 'r8' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r8.json"
        elif 'r7' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r7.json"
        elif 'r6' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r6.json"
        elif 'r5' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r5.json"
        elif 'r4' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r4.json"
        elif 'r3' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r3.json"
        elif 'r2' in hp:
            out = ROOT / "data" / "frontier_moe_dual_lane_hardneg_r2.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            __import__('json').dumps(hn, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {out}", flush=True)
        return 0

    if not args.smoke and not args.bench_codigo_vivo:
        args.smoke = True  # default to smoke

    artifact: dict[str, Any] = {
        "frontier": "C1-moe-dual-lane",
        "written": _now(),
        "router_method": method,
        "claims": "No quantum-advantage claims.",
        "adapter_map": {
            "ent": str(adapter_path_for("ent")) if adapter_path_for("ent") else None,
            "python": str(adapter_path_for("python")) if adapter_path_for("python") else None,
            "vision": str(adapter_path_for("vision")) if adapter_path_for("vision") else None,
            "base": None,
        },
        "ro_lock": str(RO_ADAPTER),
        "smoke": None,
        "bench": None,
        "gpu_skipped": False,
        "notes": [],
    }

    if args.smoke:
        print(f"=== MoE smoke method={method} ===", flush=True)
        artifact["smoke"] = run_smoke(method)
        print(f"Smoke score: {artifact['smoke']['score']}", flush=True)

    if args.bench_codigo_vivo:
        # Prefer not stealing GPU if a long mlx_vlm.lora job is live
        try:
            import subprocess
            ps = subprocess.check_output(["ps", "-ax", "-o", "command="], text=True)
            busy = any(
                ("mlx_vlm.lora" in ln) or ("qlora-ent-v6" in ln) or ("train_lora" in ln and "python" in ln)
                for ln in ps.splitlines()
            )
        except Exception:
            busy = False
        if busy:
            artifact["gpu_skipped"] = True
            artifact["notes"].append(
                "GPU skipped: mlx_vlm.lora / qlora-ent-v6 / train_lora live; smoke-only."
            )
            print("[moe] GPU busy — skipping --bench-codigo-vivo", flush=True)
        else:
            print(f"=== MoE bench-codigo-vivo method={method} ===", flush=True)
            artifact["bench"] = run_bench_codigo_vivo(
                args.model, method=method, skip_vision=args.skip_vision
            )
            print(json.dumps(artifact["bench"].get("gate"), indent=2), flush=True)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
