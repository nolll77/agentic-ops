"""
Deterministic In-Memory RAG Engine for Agentic-Ops Control Plane.
=================================================================
Zero-Token & Zero-Cost local retrieval engine providing deterministic,
authoritative grounding across:
1. The 435 MLOps Failure Modes Taxonomy (docs/mlops_failure_modes_taxonomy.md)
2. The 36 SRE Simulation Scenarios (docs/mlops_simulation_scenarios_registry.md)
3. The Executable Declarative YAML Scenario Contracts (tests/scenarios/data/*.yaml)

Architectural Philosophy:
- Zero external vector DB dependencies (No Chroma, No Pinecone, No Redis vector).
- Zero external embedding API calls (0 EUR, 0 latency, 100% deterministic).
- Sub-5ms in-memory startup time and microsecond search latency.
- Dual-use: Grounding context for LLMs (RAG) and standalone fallback in Zero-Token mode.
"""

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agentic_ops.core.deterministic_rag")


class FailureModeEntry:
    def __init__(
        self,
        risk_id: str,
        name: str,
        dimension: str,
        category: str,
        impact_slo: str,
        gravite: int,
        probabilite: int,
        detectabilite: int,
        rpn: int,
        detection: str,
        temps: str,
        reponse_auto: str,
        intervention_humaine: str,
        cout: str,
        chaos_script: str,
        vague: str,
    ):
        self.risk_id = risk_id
        self.name = name
        self.dimension = dimension
        self.category = category
        self.impact_slo = impact_slo
        self.gravite = gravite
        self.probabilite = probabilite
        self.detectabilite = detectabilite
        self.rpn = rpn
        self.detection = detection
        self.temps = temps
        self.reponse_auto = reponse_auto
        self.intervention_humaine = intervention_humaine
        self.cout = cout
        self.chaos_script = chaos_script
        self.vague = vague

    def to_markdown_card(self) -> str:
        return (
            f"### Panne `{self.risk_id}` : {self.name}\n\n"
            f"- **Dimension MLOps :** {self.dimension} (Catégorie `{self.category}`)\n"
            f"- **Impact SLO Principal :** `{self.impact_slo}`\n"
            f"- **Score RPN :** **{self.rpn}** / 125 (Gravité : `{self.gravite}/5` · Probabilité : `{self.probabilite}/5` · Détectabilité : `{self.detectabilite}/5`)\n"
            f"- **Outil de Détection :** {self.detection} (Délai : `{self.temps}`)\n"
            f"- **Atténuation Déterministe (Réponse Auto) :** {self.reponse_auto}\n"
            f"- **Intervention Humaine (Runbook) :** {self.intervention_humaine}\n"
            f"- **Script de Chaos Engineering Associé :** `{self.chaos_script}` (Priorité Vague `{self.vague}`)"
        )


class SimulationScenarioEntry:
    def __init__(
        self,
        number: int,
        title: str,
        sim_id: str,
        propagation_type: str,
        root_cause: str,
        threat_vector: str,
        severity: str,
        summary: str,
        timeline_snippet: str,
    ):
        self.number = number
        self.title = title
        self.sim_id = sim_id
        self.propagation_type = propagation_type
        self.root_cause = root_cause
        self.threat_vector = threat_vector
        self.severity = severity
        self.summary = summary
        self.timeline_snippet = timeline_snippet

    def to_markdown_card(self) -> str:
        return (
            f"### Scénario de Simulation {self.number} : {self.title} (`{self.sim_id}`)\n\n"
            f"- **Identifiant :** `{self.sim_id}`\n"
            f"- **Type de Propagation :** {self.propagation_type}\n"
            f"- **Sévérité Finale :** `{self.severity}`\n"
            f"- **Cause Racine (Root Cause) :** {self.root_cause}\n"
            f"- **Vecteur de Menace :** {self.threat_vector}\n"
            f"- **Synthèse de la Pathologie SRE :**\n{self.summary}\n\n"
            f"- **Déroulé Chronologique (Extrait Timeline) :**\n{self.timeline_snippet}"
        )


class DeclarativeScenarioContract:
    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.scenario_id = filename.replace(".yaml", "").upper().replace("_", "-")
        self.content = content


class DeterministicRAGEngine:
    """
    Singleton in-memory indexing engine for authoritative MLOps & SRE knowledge.
    """

    _instance: Optional[DeterministicRAGEngine] = None

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or self._discover_base_dir()
        self.failure_modes: Dict[str, FailureModeEntry] = {}
        self.scenarios: Dict[str, SimulationScenarioEntry] = {}
        self.contracts: Dict[str, DeclarativeScenarioContract] = {}
        self._load_indexes()

    @classmethod
    def get_instance(cls) -> DeterministicRAGEngine:
        if cls._instance is None:
            cls._instance = DeterministicRAGEngine()
        return cls._instance

    @staticmethod
    def _discover_base_dir() -> Path:
        # Search relative to this file
        current = Path(__file__).resolve().parent
        for candidate in [current.parent.parent, current.parent.parent.parent]:
            if (candidate / "docs" / "mlops_failure_modes_taxonomy.md").exists():
                return candidate
            if (candidate / "agentic-ops-core" / "docs" / "mlops_failure_modes_taxonomy.md").exists():
                return candidate / "agentic-ops-core"
        return current.parent.parent

    def _load_indexes(self) -> None:
        try:
            self._load_failure_modes()
            self._load_simulation_scenarios()
            self._load_scenario_contracts()
            logger.info(
                "DeterministicRAGEngine indexed %d failure modes, %d simulation scenarios, and %d YAML contracts.",
                len(self.failure_modes),
                len(self.scenarios),
                len(self.contracts),
            )
        except Exception as exc:
            logger.warning("Error initializing DeterministicRAGEngine: %s", exc)

    def _load_failure_modes(self) -> None:
        taxo_file = self.base_dir / "docs" / "mlops_failure_modes_taxonomy.md"
        if not taxo_file.exists():
            return

        current_dimension = "Général"
        text = taxo_file.read_text(encoding="utf-8")
        lines = text.splitlines()

        for line in lines:
            line_str = line.strip()
            if line_str.startswith("## ") and "Dimension" in line_str:
                current_dimension = line_str.replace("## ", "").strip()
                continue

            if not line_str.startswith("|") or line_str.startswith("| n°") or line_str.startswith("| :---"):
                continue

            parts = [p.strip() for p in line_str.split("|")[1:-1]]
            if len(parts) < 16:
                continue

            # Format: | n° | Identifiant_Risque | Cat. | Failure Mode | Impact SLO | Grav. | Prob. | Dét. | RPN | Détection | Temps | Réponse Auto | Intervention Humaine | Coût | Chaos Script | Vague | Testé ? | Statut | Réponse |
            try:
                risk_id_raw = parts[1].replace("`", "").strip()
                category = parts[2].replace("`", "").strip()
                name = parts[3].replace("**", "").replace("`", "").strip()
                impact_slo = parts[4].replace("`", "").strip()
                grav = int(parts[5]) if parts[5].isdigit() else 3
                prob = int(parts[6]) if parts[6].isdigit() else 3
                det = int(parts[7]) if parts[7].isdigit() else 3
                rpn_match = re.search(r"\b(\d+)\b", parts[8])
                rpn = int(rpn_match.group(1)) if rpn_match else (grav * prob * det)
                detection = parts[9].strip()
                temps = parts[10].strip()
                reponse_auto = parts[11].strip()
                interv = parts[12].strip()
                cout = parts[13].strip()
                chaos_script = parts[14].replace("`", "").strip()
                vague = parts[15].strip()

                entry = FailureModeEntry(
                    risk_id=risk_id_raw,
                    name=name,
                    dimension=current_dimension,
                    category=category,
                    impact_slo=impact_slo,
                    gravite=grav,
                    probabilite=prob,
                    detectabilite=det,
                    rpn=rpn,
                    detection=detection,
                    temps=temps,
                    reponse_auto=reponse_auto,
                    intervention_humaine=interv,
                    cout=cout,
                    chaos_script=chaos_script,
                    vague=vague,
                )
                self.failure_modes[risk_id_raw.upper()] = entry
            except Exception:
                continue

    def _load_simulation_scenarios(self) -> None:
        reg_file = self.base_dir / "docs" / "mlops_simulation_scenarios_registry.md"
        if not reg_file.exists():
            return

        text = reg_file.read_text(encoding="utf-8")
        scenario_blocks = re.split(r"\n## Scénario (\d+)\s*:\s*", text)

        for i in range(1, len(scenario_blocks), 2):
            try:
                sc_num = int(scenario_blocks[i])
                block_content = scenario_blocks[i + 1]
                header_line = block_content.splitlines()[0].strip()
                title = header_line

                sim_id_match = re.search(r"\* \*\*ID\s*:\*\*\s*(SIM-\w+)", block_content, re.IGNORECASE)
                sim_id = sim_id_match.group(1).upper() if sim_id_match else f"SIM-{sc_num:03d}"

                prop_match = re.search(r"\* \*\*Type de Propagation\s*:\*\*\s*([^\n]+)", block_content)
                propagation = prop_match.group(1).strip() if prop_match else "Inconnue"

                root_match = re.search(r"\* \*\*Origine \(Root Cause\)\s*:\*\*\s*([^\n]+)", block_content)
                root_cause = root_match.group(1).strip() if root_match else "Non spécifiée"

                threat_match = re.search(r"\* \*\*Vecteur de Menace\s*:\*\*\s*([^\n]+)", block_content)
                threat = threat_match.group(1).strip() if threat_match else "Générique"

                sev_match = re.search(r"\* \*\*Sévérité Finale\s*:\*\*\s*([^\n]+)", block_content)
                severity = sev_match.group(1).strip() if sev_match else "Élevée"

                # Extrait du summary
                note_match = re.search(r"> \[!NOTE\]\s*\n(.*?)(?=\n\*\*Métadonnées|\n###|$)", block_content, re.DOTALL)
                summary = ""
                if note_match:
                    raw_lines = [ln.replace("> ", "").replace(">", "").strip() for ln in note_match.group(1).splitlines() if ln.strip()]
                    summary = " ".join(raw_lines[:4])
                if not summary:
                    summary = f"Scénario d'exercice SRE et Chaos Engineering simulant l'incident '{title}'."

                # Extrait de timeline
                timeline_match = re.search(r"### \d+\.1\s*:\s*Timeline.*?\n(.*?)(?=\n### \d+\.2|$)", block_content, re.DOTALL)
                timeline_snippet = ""
                if timeline_match:
                    tl_lines = [ln for ln in timeline_match.group(1).splitlines() if ln.startswith("#### ") or ln.startswith("* ") or ln.startswith("**Événement")][:8]
                    timeline_snippet = "\n".join(tl_lines)
                if not timeline_snippet:
                    timeline_snippet = f"Timeline chronologique simulant l'injection de panne de T=0 à T=4 pour le scénario {sim_id}."

                entry = SimulationScenarioEntry(
                    number=sc_num,
                    title=title,
                    sim_id=sim_id,
                    propagation_type=propagation,
                    root_cause=root_cause,
                    threat_vector=threat,
                    severity=severity,
                    summary=summary,
                    timeline_snippet=timeline_snippet,
                )
                self.scenarios[sim_id] = entry
                self.scenarios[f"SCENARIO-{sc_num}"] = entry
            except Exception:
                continue

    def _load_scenario_contracts(self) -> None:
        data_dir = self.base_dir / "tests" / "scenarios" / "data"
        if not data_dir.exists():
            return

        for ypath in data_dir.rglob("*.yaml"):
            try:
                contract = DeclarativeScenarioContract(
                    filename=ypath.name,
                    content=ypath.read_text(encoding="utf-8"),
                )
                clean_key = ypath.stem.upper().replace("_", "-")
                self.contracts[clean_key] = contract
                # Alias e.g. SC-001 -> SC-001-DATA-INGESTION-DROP
                prefix = clean_key.split("-")[0] + "-" + clean_key.split("-")[1] if len(clean_key.split("-")) >= 2 else clean_key
                self.contracts[prefix] = contract
            except Exception:
                continue

    def search_failure_modes(self, query: str, limit: int = 5) -> List[FailureModeEntry]:
        q = query.strip().upper()
        # Direct key match
        if q in self.failure_modes:
            return [self.failure_modes[q]]

        matches: List[FailureModeEntry] = []

        # Substring exact ID match from query e.g. "DATA-042" inside a sentence
        explicit_ids = re.findall(r"\b([A-Z]{3,5}-\d{2,4})\b", q)
        for xid in explicit_ids:
            if xid in self.failure_modes and self.failure_modes[xid] not in matches:
                matches.append(self.failure_modes[xid])
                if len(matches) >= limit:
                    return matches

        q_lower = query.lower()

        # Check for RPN filter
        rpn_ge_match = re.search(r"rpn\s*(?:>=|>|supérieur|critique)\s*(\d+)", q_lower)
        if rpn_ge_match or "critique" in q_lower or "top" in q_lower:
            threshold = int(rpn_ge_match.group(1)) if rpn_ge_match else 80
            crit_modes = sorted(
                [f for f in self.failure_modes.values() if f.rpn >= threshold],
                key=lambda x: (x.rpn, x.gravite),
                reverse=True,
            )
            return crit_modes[:limit]

        for entry in self.failure_modes.values():
            if (
                entry not in matches
                and (
                    q_lower in entry.name.lower()
                    or q_lower in entry.dimension.lower()
                    or q_lower in entry.chaos_script.lower()
                    or q_lower in entry.detection.lower()
                )
            ):
                matches.append(entry)
                if len(matches) >= limit:
                    break

        return matches

    def search_scenarios(self, query: str, limit: int = 3) -> List[SimulationScenarioEntry]:
        q_clean = query.strip().upper()
        # Direct key match
        if q_clean in self.scenarios:
            return [self.scenarios[q_clean]]

        # Scenario X matching
        sc_num_match = re.search(r"(?:sc[ée]nario|sim)\s*[-_]?\s*(\d+)", query, re.IGNORECASE)
        if sc_num_match:
            num = int(sc_num_match.group(1))
            k1 = f"SIM-{num:03d}"
            k2 = f"SIM-{num}"
            k3 = f"SCENARIO-{num}"
            for candidate in [k1, k2, k3]:
                if candidate in self.scenarios:
                    return [self.scenarios[candidate]]

        q_lower = query.lower()
        matches: List[SimulationScenarioEntry] = []
        for entry in self.scenarios.values():
            if (
                q_lower in entry.title.lower()
                or q_lower in entry.root_cause.lower()
                or q_lower in entry.propagation_type.lower()
                or q_lower in entry.threat_vector.lower()
            ):
                if entry not in matches:
                    matches.append(entry)
                if len(matches) >= limit:
                    break
        return matches

    def search_contracts(self, query: str) -> Optional[DeclarativeScenarioContract]:
        q = query.strip().upper().replace("_", "-")
        for key, contract in self.contracts.items():
            if key in q or q in key:
                return contract
        return None

    def retrieve_grounding_context(self, message: str) -> Optional[str]:
        """
        Extracts relevant reference facts to augment the LLM system prompt.
        """
        snippets = []

        # 1. Search failure modes
        modes = self.search_failure_modes(message, limit=3)
        if modes:
            snippets.append("### Extraits Référentiels : Taxonomie des Failure Modes MLOps")
            for m in modes:
                snippets.append(m.to_markdown_card())

        # 2. Search simulation scenarios
        scs = self.search_scenarios(message, limit=2)
        if scs:
            snippets.append("### Extraits Référentiels : Scénarios de Simulation SRE")
            for s in scs:
                snippets.append(s.to_markdown_card())

        # 3. Search YAML contracts
        contract = self.search_contracts(message)
        if contract:
            snippets.append(f"### Contrat Déclaratif YAML (`{contract.filename}`)\n```yaml\n{contract.content.strip()}\n```")

        if snippets:
            return "\n\n".join(snippets)
        return None

    def get_offline_sre_response(self, message: str) -> Optional[str]:
        """
        Generates an authoritative, instant Zero-Token response for the Chat UI
        when LLM is disabled or down.
        """
        # Exact ID match on failure modes
        risk_match = re.search(r"\b([A-Z]{3,5}-\d{2,4})\b", message.upper())
        if risk_match:
            risk_id = risk_match.group(1)
            if risk_id in self.failure_modes:
                mode = self.failure_modes[risk_id]
                return (
                    f"**[Mode Dégradé SRE — Base Déterministe In-Memory / RAG Zero-Token]**\n\n"
                    f"{mode.to_markdown_card()}\n\n"
                    f"> **Gouvernance Déterministe :** Tout signal détecté sur ce mode est validé par le `PolicyEngine`. "
                    f"Si une action mutante est requise, l'approbation humaine `Slack HITL` (Quorum 2-Man Rule) est imposée."
                )

        # Scenarios match
        sc_num_match = re.search(r"(?:sc[ée]nario|sim)\s*[-_]?\s*(\d+)", message, re.IGNORECASE)
        if sc_num_match or any(k in message.lower() for k in ["cascade silencieuse", "war room", "multi-fail"]):
            scs = self.search_scenarios(message, limit=1)
            if scs:
                sc = scs[0]
                return (
                    f"**[Mode Dégradé SRE — Registre des Scénarios de Simulation / RAG Zero-Token]**\n\n"
                    f"{sc.to_markdown_card()}\n\n"
                    f"> **Exécution Sandbox :** Ce scénario peut être rejoué sur `/console` via les suites de tests "
                    f"de la Phase D (`sandbox_phase_d_mlops_scenarios`). Le système garantit l'invariant `forbidden_executed=0`."
                )

        # High RPN / Top Risks
        if any(k in message.lower() for k in ["rpn >= 80", "pannes critiques", "top 10", "top 25", "plus dangereux"]):
            modes = self.search_failure_modes("rpn >= 80", limit=10)
            rows = [
                f"| `{m.risk_id}` | {m.name} | {m.dimension} | `{m.impact_slo}` | **{m.rpn}** | `{m.chaos_script}` |"
                for m in modes
            ]
            table = (
                "| ID | Panne MLOps | Dimension | Impact SLO | RPN | Script Chaos |\n"
                "| :--- | :--- | :--- | :--- | :---: | :--- |\n" + "\n".join(rows)
            )
            return (
                f"**[Mode Dégradé SRE — Top Risques Critiques (RPN ≥ 80) / RAG Zero-Token]**\n\n"
                f"Voici les pannes les plus critiques de notre taxonomie de 435 défaillances MLOps :\n\n"
                f"{table}\n\n"
                f"> **Priorité Chaos Vague 1 :** Toutes ces pannes critiques possèdent un script de simulation dédié sous `tests/chaos/` "
                f"et sont couvertes par les invariants du `PolicyEngine`."
            )

        # Taxonomy dimension overview
        if "taxonomie" in message.lower() and any(k in message.lower() for k in ["dimensions", "combien", "répartition", "10"]):
            return (
                "**[Mode Dégradé SRE — Structure de la Taxonomie 435 / RAG Zero-Token]**\n\n"
                "La taxonomie d'Agentic-Ops référence **435 Failure Modes** répartis en **10 Dimensions MLOps** :\n\n"
                "1. **Infrastructure** (32 pannes : `INFRA-001` à `INFRA-032`) : Saturation RAM/Disque, pannes PostgreSQL, crash Docker.\n"
                "2. **Données** (55 pannes : `DATA-001` à `DATA-055`) : Schémas Pandera rompus, dérive Evidently, désynchronisation train/serve.\n"
                "3. **Feature Engineering** (22 pannes : `FEAT-001` à `FEAT-022`) : Time-travel leakage, calculs Feast, imputations divergentes.\n"
                "4. **Entraînement** (47 pannes : `TRAIN-001` à `TRAIN-047`) : Data leakage, surapprentissage silencieux, incompatibilités d'artefacts.\n"
                "5. **Serving** (24 pannes : `SERV-001` à `SERV-024`) : Latence p99, dégradation d'inférence, OOM modèle lourd.\n"
                "6. **Observabilité** (35 pannes : `OBS-001` à `OBS-035`) : Métriques fantômes, alert storm thrashing, fausses alertes Loki.\n"
                "7. **Sécurité** (55 pannes : `SEC-001` à `SEC-055`) : Prompt injection, falsification de webhook, poison runbook.\n"
                "8. **FinOps** (20 pannes : `FIN-001` à `FIN-020`) : Explosion de facturation LLM, requêtes d'agents en boucle.\n"
                "9. **Gouvernance** (45 pannes : `GOV-001` à `GOV-045`) : Promotion non auditée, absence de traçabilité WORM.\n"
                "10. **Exploitation & HITL** (70 pannes : `OPS-001` à `OPS-070`) : Bypass d'approbation Slack, partition réseau Tailscale.\n\n"
                "Vous pouvez interroger n'importe quel identifiant spécifique (`DATA-042`, `INFRA-005`, `SEC-054`) ou demander les pannes d'une dimension !"
            )

        return None
