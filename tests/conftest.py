import pytest, yaml
from pathlib import Path

# Load gaps
try:
    GAPS = yaml.safe_load((Path(__file__).parent / "known_gaps.yaml").read_text()) or {}
except FileNotFoundError:
    GAPS = {}
_used: set[str] = set()

def pytest_configure(config):
    config.addinivalue_line("markers", "gap(id): test attendu en échec tant que l'entrée existe dans known_gaps.yaml")

def pytest_collection_modifyitems(config, items):
    for it in items:
        m = it.get_closest_marker("gap")
        if not m:
            continue
        gid = m.args[0]
        _used.add(gid)
        if gid in GAPS:
            it.add_marker(pytest.mark.xfail(strict=True, reason=f"{GAPS[gid]['p0']}: {GAPS[gid]['why']}"))

def pytest_collection_finish(session):
    stale = set(GAPS) - _used
    if stale and not session.config.option.keyword:
        import warnings
        warnings.warn(f"known_gaps.yaml: entrées sans test: {sorted(stale)}")


TEST_PEDAGOGICAL_DESCRIPTIONS: dict[str, list[str]] = {
    # Phase C — Adversarial & WORM Ledger
    "test_ledger_append_and_verify_chain": [
        "[GUIDE:ROLE] TEST WORM 1/3 : Chaînage cryptographique SHA-256 (Merkle-like) de EvidenceStore.",
        "[GUIDE:PROD] IMPACT PROD : Écriture locale append-only dans ledger.jsonl (0 appel externe).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : 3 décisions d'audit sont ajoutées ; chaque entrée scelle le hash prev_hash de la précédente et verify_chain() retourne True.",
    ],
    "test_ledger_tamper_payload_detected": [
        "[GUIDE:ROLE] TEST WORM 2/3 : Détection d'altération malveillante du payload JSON dans ledger.jsonl.",
        "[GUIDE:PROD] IMPACT PROD : Simulation Red-Team d'un attaquant modifiant un octet d'une preuve passée.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : La recalculation du digest SHA-256 diverge immédiatement du champ entry_hash enregistré -> verify_chain() lève une erreur d'intégrité.",
    ],
    "test_ledger_tamper_chain_detected": [
        "[GUIDE:ROLE] TEST WORM 3/3 : Détection de suppression/réordonnancement de ligne dans la chaîne SHA-256.",
        "[GUIDE:PROD] IMPACT PROD : Protection anti-effacement de traces d'audit (WORM Compliance).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : La rupture du lien prev_hash entre l'entrée N-1 et l'entrée N est détectée instantanément.",
    ],
    "test_production_fails_without_redis": [
        "[GUIDE:ROLE] TEST REDIS 1/2 : Politique Fail-Closed de DistributedLock en environnement de production.",
        "[GUIDE:PROD] IMPACT PROD : Empêche deux workers concurrents d'exécuter deux fois la même remédiation sur la prod.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Si Redis (:6379) est injoignable en mode prod, le système refuse de démarrer au lieu de retomber silencieusement en mémoire.",
    ],
    "test_lock_acquire_and_release": [
        "[GUIDE:ROLE] TEST REDIS 2/2 : Acquisition atomique SETNX + TTL et libération du verrou distribué.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le premier worker acquiert le verrou, un second worker concurrent est bloqué jusqu'au release().",
    ],
    "test_untrusted_text_is_fenced_in_prompts": [
        "[GUIDE:ROLE] TEST PROMPT HYGIENE 1/3 : Encapsulation XML stricte (<untrusted_telemetry>) des logs externes.",
        "[GUIDE:AGENT] AGENT CONCERNÉ : Protège les agents LLM (data_specialist_llm / infra_specialist_llm) contre l'injection de prompt via les logs Loki.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Tout texte externe est isolé dans des balises de quarantaine explicites avant d'être envoyé au LLM.",
    ],
    "test_wrapper_cannot_be_closed_by_payload": [
        "[GUIDE:ROLE] TEST PROMPT HYGIENE 2/3 : Neutralisation d'évasion de balise (</untrusted_telemetry> injecté dans un log).",
        "[GUIDE:AGENT] AGENT CONCERNÉ : Empêche un attaquant de fermer la balise de quarantaine pour injecter de fausses instructions système au LLM.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les séquences de fermeture XML malveillantes sont échappées/neutralisées avant construction du prompt.",
    ],
    "test_arbitrary_target_never_allowed_unless_well_formed": [
        "[GUIDE:ROLE] TEST PROMPT HYGIENE 3/3 : Validation stricte par liste blanche/regex des cibles d'exécution (target).",
        "[GUIDE:PROD] IMPACT PROD : Interdit toute injection shell (; rm -rf, ../, caractères spéciaux) dans le nom du service cible.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les cibles malformées ou contenant des métacaractères shell sont rejetées par le validateur.",
    ],
    "test_create_issue_is_explicitly_simulated": [
        "[GUIDE:ROLE] TEST EXECUTOR 1/2 : Cloisonnement dry-run de l'Executor en mode test/simulation.",
        "[GUIDE:PROD] IMPACT PROD : Garantit que l'action 'create_issue' génère une référence traçable sans polluer le vrai GitHub/Jira de prod.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : L'Executor retourne un statut 'simulated' explicite et horodaté.",
    ],
    "test_simulated_issue_references_are_unique_under_threads": [
        "[GUIDE:ROLE] TEST EXECUTOR 2/2 : Thread-safety et unicité des identifiants d'actions sous charge multi-thread.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : 50 exécutions parallèles produisent 50 références uniques sans collision.",
    ],
    # Phase E — FSM, Grafana & Tool Sandboxing
    "test_state_machine_valid_transitions": [
        "[GUIDE:ROLE] TEST FSM 1/2 : Parcours nominal complet de l'automate à états finis (IDLE -> INVESTIGATING -> DIAGNOSING -> PLANNING -> POLICY_CHECK -> EXECUTING -> RESOLVED).",
        "[GUIDE:AGENT] AGENT CONCERNÉ : Orchestre le passage de relais entre l'Agent Spécialiste, le PolicyEngine et l'Executor.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Chaque transition autorisée met à jour l'état et journalise l'événement sans erreur.",
    ],
    "test_state_machine_invalid_transition": [
        "[GUIDE:ROLE] TEST FSM 2/2 : Impossibilité mathématique de sauter POLICY_CHECK (ex: IDLE -> EXECUTING ou PLANNING -> EXECUTING).",
        "[GUIDE:PROD] IMPACT PROD : Verrou architectural majeur — aucun agent ne peut toucher la prod sans passer par PolicyEngine.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Toute transition illégale lève immédiatement InvalidTransitionError.",
    ],
    "test_parse_grafana_alerts": [
        "[GUIDE:ROLE] TEST GRAFANA 1/5 : Normalisation d'un webhook Grafana Alerting valide en AnomalySignal Pydantic.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les labels (risk_id, service, severity) sont extraits et typés sans perte.",
    ],
    "test_reject_invalid_grafana_payloads": [
        "[GUIDE:ROLE] TEST GRAFANA : Rejet Fail-Closed d'un payload webhook Grafana corrompu ou malformé.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le parseur rejette l'entrée invalide avec un message d'erreur explicite avant toute invocation d'agent.",
    ],
    "test_readonly_tool_executes_without_approval": [
        "[GUIDE:ROLE] TEST SANDBOX TOOLS 1/3 : Outil en lecture seule (L1 Read-Only) exécuté en autonomie.",
        "[GUIDE:SLACK] SLACK HITL : Aucune approbation Slack requise pour les outils purement déclaratifs/lecture.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : L'outil read-only s'exécute directement et retourne ses métriques.",
    ],
    "test_dangerous_tool_blocked_without_approval": [
        "[GUIDE:ROLE] TEST SANDBOX TOOLS 2/3 : Blocage physique d'un outil destructif/mutation appelé sans jeton d'approbation humaine.",
        "[GUIDE:SLACK] SLACK HITL : Exige un jeton d'approbation signé via Slack Block Kit ([APPROVE]).",
        "[GUIDE:PROD] IMPACT PROD : ZÉRO MUTATION — l'appel non approuvé est stoppé net.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : L'invocation directe sans approval_token lève PermissionError.",
    ],
    "test_dangerous_tool_allowed_with_approval": [
        "[GUIDE:ROLE] TEST SANDBOX TOOLS 3/3 : Déblocage contrôlé d'un outil critique après validation humaine (HITL).",
        "[GUIDE:SLACK] SLACK HITL : Jeton d'approbation Slack valide fourni à l'exécuteur.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Avec l'approbation humaine vérifiée, l'outil est autorisé à s'exécuter et est tracé dans le WORM Ledger.",
    ],
    # Phase F — CAC Tailscale Pull Collector (13 Tests)
    "test_parse_alerts_correctement": [
        "[GUIDE:ROLE] TEST CAC LOKI 1/2 : Extraction des alertes [DRIFT_ALERT] et [LATENCY_WARN] depuis les flux LogQL Loki (:3100).",
        "[GUIDE:PROD] IMPACT PROD : Requête HTTP GET pure sur /loki/api/v1/query_range via proxy SOCKS5 Tailscale.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les timestamps nanosecondes et lignes de log JSON sont convertis en objets structurés.",
    ],
    "test_retourne_liste_vide_si_no_result": [
        "[GUIDE:ROLE] TEST CAC LOKI 2/2 : Résilience face à une réponse Loki vide (aucun log d'erreur sur la fenêtre).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Retourne proprement [] sans lever de KeyError.",
    ],
    "test_parse_drift_share": [
        "[GUIDE:ROLE] TEST CAC PROMETHEUS : Lecture de la jauge 'evidently:dataset_drift:share' et 'http_request_duration_seconds' (:9090).",
        "[GUIDE:PROD] IMPACT PROD : Lecture GET PromQL non-intrusive de la dérive de données du modèle BAAC.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le ratio de drift Evidently et la latence P95 sont extraits en float.",
    ],
    "test_parse_modele_production": [
        "[GUIDE:ROLE] TEST CAC MLFLOW : Inspection du modèle 'gravite-lightgbm-model' (@Production) sur MLflow (:5000).",
        "[GUIDE:PROD] IMPACT PROD : Lecture GET des métadonnées de version et run_id sans toucher aux poids ni aux alias.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : La version active en production et son statut READY sont correctement identifiés.",
    ],
    "test_parse_flow_runs": [
        "[GUIDE:ROLE] TEST CAC PREFECT 1/2 : Récupération de l'historique des derniers pipelines ETL/training sur Prefect (:4200).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les états COMPLETED/FAILED des flow_runs sont extraits et triés.",
    ],
    "test_n_appelle_que_get": [
        "[GUIDE:ROLE] TEST CAC PREFECT 2/2 : Vérification de sécurité Read-Only sur le client Prefect.",
        "[GUIDE:PROD] IMPACT PROD : Garantit qu'aucun endpoint de mutation Prefect n'est déclenché.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Seules des requêtes de lecture d'état sont émises.",
    ],
    "test_parse_rapport_public": [
        "[GUIDE:ROLE] TEST CAC EVIDENTLY : Lecture du rapport public de dérive de données (Data Drift JSON/HTML).",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les colonnes en dérive (ex: hrmn, lum, atm) et le score global sont extraits.",
    ],
    "test_status_online_si_tout_repond": [
        "[GUIDE:ROLE] TEST CAC SNAPSHOT 1/4 : Agrégation complète quand les 4 services du VPS répondent (status='online').",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le CacObservabilitySnapshot consolide Loki + Prometheus + MLflow + Prefect avec status='online'.",
    ],
    "test_status_offline_si_vps_eteint": [
        "[GUIDE:ROLE] TEST CAC SNAPSHOT 2/4 : Mode dégradé gracieux quand le VPS distant est éteint (status='offline').",
        "[GUIDE:PROD] IMPACT PROD : Prouve que la console Web fonctionne à 100% même lorsque ton collègue a éteint son VPS !",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Aucune exception non gérée ; retourne un snapshot propre avec status='offline' et la liste des erreurs de connexion.",
    ],
    "test_status_partial_si_une_source_echoue": [
        "[GUIDE:ROLE] TEST CAC SNAPSHOT 3/4 : Résilience partielle si 1 seul service (ex: MLflow) tombe sur le VPS (status='partial').",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Les 3 autres sources sont conservées et status='partial' indique la dégradation partielle.",
    ],
    "test_snapshot_est_serialisable": [
        "[GUIDE:ROLE] TEST CAC SNAPSHOT 4/4 : Sérialisation JSON complète du snapshot pour l'API /api/cac/snapshot et le LLM.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : json.dumps(snapshot.to_dict()) réussit sans erreur de typage.",
    ],
    "test_aucun_post_dans_fetch_mlflow": [
        "[GUIDE:ROLE] TEST CONTRAT READ-ONLY 1/2 : Preuve formelle par inspection qu'aucun POST/PUT/DELETE/PATCH n'est émis vers MLflow.",
        "[GUIDE:PROD] IMPACT PROD : Garantie mathématique de ZÉRO MUTATION sur le Model Registry de production.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le mock HTTP vérifie que 100% des appels utilisent la méthode GET.",
    ],
    "test_aucun_post_dans_fetch_loki": [
        "[GUIDE:ROLE] TEST CONTRAT READ-ONLY 2/2 : Preuve formelle qu'aucun POST/PUT/DELETE n'est émis vers Loki.",
        "[GUIDE:PROD] IMPACT PROD : Garantie mathématique de lecture seule sur l'agrégateur de logs du VPS.",
        "[GUIDE:HOW_IT_PASSES] POURQUOI ÇA PASSE : Le mock HTTP confirme que seul client.get() est invoqué.",
    ],
}


def pytest_runtest_call(item):
    base_name = item.name.split("[")[0]
    lines = TEST_PEDAGOGICAL_DESCRIPTIONS.get(base_name)
    if lines:
        print("")
        for line in lines:
            print(line)

