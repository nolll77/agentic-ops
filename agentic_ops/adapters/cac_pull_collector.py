"""
CacPullCollector — Adaptateur de lecture seule vers la plateforme distante CAC MLOps.

Ce module implémente un collecteur en mode "pull" (lecture seule, GET uniquement)
qui interroge les services distants de la plateforme cac_mlops via le tunnel
Tailscale (proxy SOCKS5 local sur 127.0.0.1:1055).

Architecture :
    - CacRemoteConfig     : Configuration des endpoints et du proxy.
    - RemoteServiceStatus : Enum décrivant l'état de disponibilité du serveur.
    - CacCollectedSnapshot: Pydantic model agrégant les données récupérées.
    - CacPullCollector    : Client HTTP principal avec les 5 méthodes de collecte.

Règle d'or (Contrat d'interfaçage Read-Only) :
    Lecture seule UNIQUEMENT. Aucun appel POST/PUT/DELETE vers l'infrastructure cible.
    Ne jamais appeler : /predict, /loki/api/v1/push,
    POST registered-models/alias, POST /api/deployments/.../create_flow_run.

Résilience :
    Si le VPS scw-jovial-dubinsky (100.117.99.62) est hors-ligne, le collecteur
    renvoie un CacCollectedSnapshot avec status=REMOTE_TARGET_OFFLINE sans lever
    d'exception, ce qui permet à l'orchestrateur de continuer à fonctionner.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger("agentic_ops.cac_pull_collector")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CAC_VPS_IP = "100.117.99.62"

# Adresses par service (plateforme cible CAC MLOps)
CAC_LOKI_BASE        = f"http://{CAC_VPS_IP}:3100"
CAC_PROMETHEUS_BASE  = f"http://{CAC_VPS_IP}:9090"
CAC_MLFLOW_BASE      = f"http://{CAC_VPS_IP}:5001"
CAC_PREFECT_BASE     = f"http://{CAC_VPS_IP}:4200"
CAC_DRIFT_REPORT_URL = "https://mlops.jakat-inc.fr/reports/drift/latest_summary.json"

# Proxy SOCKS5 du démon tailscaled en mode userspace-networking
TAILSCALE_SOCKS5_PROXY = "socks5://127.0.0.1:1055"

# Timeout global par appel (15-30s)
DEFAULT_TIMEOUT_S = 20.0


# ---------------------------------------------------------------------------
# Types de données
# ---------------------------------------------------------------------------

class RemoteServiceStatus(str, Enum):
    """Statut de connectivité vers le VPS cible CAC MLOps."""
    ONLINE             = "ONLINE"
    REMOTE_TARGET_OFFLINE = "REMOTE_TARGET_OFFLINE"
    PARTIAL            = "PARTIAL"
    ERROR              = "ERROR"


class LokiAlert(BaseModel):
    """Représentation d'une alerte Grafana lue depuis Loki."""
    timestamp: datetime
    labels: Dict[str, str] = Field(default_factory=dict)
    line: str


class PrometheusSnapshot(BaseModel):
    """Métriques-clés extraites de Prometheus."""
    drift_share:            Optional[float] = None   # cac_mlops_drift_share
    model_in_production:    Optional[str]   = None   # mlops_model_info{alias="Production"}
    api_request_total:      Optional[float] = None   # http_requests_total
    collected_at:           datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MlflowModelInfo(BaseModel):
    """Informations du modèle actif récupéré depuis MLflow."""
    name:           Optional[str] = None
    alias:          Optional[str] = None
    version:        Optional[str] = None
    run_id:         Optional[str] = None
    metrics:        Dict[str, Any] = Field(default_factory=dict)
    tags:           Dict[str, str] = Field(default_factory=dict)
    collected_at:   datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrefectFlowRunSummary(BaseModel):
    """Résumé des derniers flow runs lus depuis Prefect."""
    id:             str
    name:           Optional[str] = None
    state_name:     Optional[str] = None
    state_type:     Optional[str] = None
    start_time:     Optional[datetime] = None
    end_time:       Optional[datetime] = None


class DriftReportSnapshot(BaseModel):
    """Rapport de dérive public Evidently."""
    report_date:    Optional[str] = None
    drift_share:    Optional[float] = None
    drifted_columns: List[str] = Field(default_factory=list)
    raw:            Dict[str, Any] = Field(default_factory=dict)
    collected_at:   datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CacCollectedSnapshot(BaseModel):
    """
    Agrégat complet d'une collecte vers la plateforme cible CAC MLOps.
    Chaque champ est optionnel : si le service est indisponible, le champ
    reste à None et status indique REMOTE_TARGET_OFFLINE ou PARTIAL.
    """
    status:         RemoteServiceStatus
    collected_at:   datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    errors:         Dict[str, str] = Field(default_factory=dict)

    loki_alerts:        Optional[List[LokiAlert]]         = None
    prometheus:         Optional[PrometheusSnapshot]      = None
    mlflow_model:       Optional[MlflowModelInfo]         = None
    prefect_flow_runs:  Optional[List[PrefectFlowRunSummary]] = None
    drift_report:       Optional[DriftReportSnapshot]     = None


# ---------------------------------------------------------------------------
# Collecteur principal
# ---------------------------------------------------------------------------

class CacPullCollector:
    """
    Collecteur en lecture seule vers la plateforme distante CAC MLOps.

    Utilise httpx avec un transport SOCKS5 pour que toutes les requêtes
    vers 100.117.99.62 transitent par le tunnel Tailscale chiffré.

    Usage minimal :
        collector = CacPullCollector()
        snapshot  = collector.collect_all()
        if snapshot.status == RemoteServiceStatus.ONLINE:
            print(snapshot.prometheus.drift_share)
    """

    def __init__(
        self,
        socks5_proxy: str = TAILSCALE_SOCKS5_PROXY,
        timeout: float = DEFAULT_TIMEOUT_S,
        use_proxy_for_vps: bool = True,
    ) -> None:
        self._timeout = timeout
        self._use_proxy = use_proxy_for_vps

        # Transport SOCKS5 pour les requêtes vers le VPS (via Tailscale)
        if use_proxy_for_vps:
            self._proxy_transport = httpx.HTTPTransport(
                proxy=httpx.Proxy(socks5_proxy)
            )
        else:
            self._proxy_transport = None

        # Transport direct pour les appels HTTPS publics (rapport de dérive)
        self._direct_transport = httpx.HTTPTransport()

    # -----------------------------------------------------------------------
    # API publique
    # -----------------------------------------------------------------------

    def collect_all(self) -> CacCollectedSnapshot:
        """
        Lance la collecte sur les 5 sources et retourne un snapshot agrégé.
        N'élève jamais d'exception : les erreurs sont loguées et consignées
        dans snapshot.errors.
        """
        errors: Dict[str, str] = {}
        collected: Dict[str, Any] = {}

        sources = {
            "loki_alerts":       self._fetch_loki_alerts,
            "prometheus":        self._fetch_prometheus,
            "mlflow_model":      self._fetch_mlflow_model,
            "prefect_flow_runs": self._fetch_prefect_flow_runs,
            "drift_report":      self._fetch_drift_report,
        }

        for key, fn in sources.items():
            try:
                collected[key] = fn()
            except httpx.ConnectError as exc:
                logger.warning("CacPullCollector | %s | ConnectError : %s", key, exc)
                errors[key] = f"ConnectError: {exc}"
            except httpx.TimeoutException as exc:
                logger.warning("CacPullCollector | %s | Timeout après %.0fs", key, self._timeout)
                errors[key] = f"Timeout: {exc}"
            except Exception as exc:
                logger.error("CacPullCollector | %s | Erreur inattendue : %s", key, exc)
                errors[key] = f"Error: {exc}"

        # Calcul du statut global
        if not errors:
            status = RemoteServiceStatus.ONLINE
        elif len(errors) == len(sources):
            status = RemoteServiceStatus.REMOTE_TARGET_OFFLINE
        else:
            status = RemoteServiceStatus.PARTIAL

        return CacCollectedSnapshot(
            status=status,
            errors=errors,
            loki_alerts=collected.get("loki_alerts"),
            prometheus=collected.get("prometheus"),
            mlflow_model=collected.get("mlflow_model"),
            prefect_flow_runs=collected.get("prefect_flow_runs"),
            drift_report=collected.get("drift_report"),
        )

    # -----------------------------------------------------------------------
    # Méthodes de collecte par service
    # -----------------------------------------------------------------------

    def _fetch_loki_alerts(self) -> List[LokiAlert]:
        """
        Interroge Loki en LogQL pour récupérer les alertes MLOps structurées.
        Requête : {service="prefect-worker"} |= "event=alert" sur les 6 dernières heures.
        """
        query = '{service="prefect-worker"} |= "event=alert"'
        end_ns   = int(datetime.now(timezone.utc).timestamp() * 1e9)
        start_ns = end_ns - int(6 * 3600 * 1e9)  # 6 heures

        params = {
            "query": query,
            "start": str(start_ns),
            "end":   str(end_ns),
            "limit": "100",
            "direction": "backward",
        }

        with self._vps_client() as client:
            resp = client.get(
                f"{CAC_LOKI_BASE}/loki/api/v1/query_range",
                params=params,
            )
            resp.raise_for_status()
            data = resp.json()

        alerts: List[LokiAlert] = []
        for stream in data.get("data", {}).get("result", []):
            labels = stream.get("stream", {})
            for ts_ns_str, line in stream.get("values", []):
                ts = datetime.fromtimestamp(int(ts_ns_str) / 1e9, tz=timezone.utc)
                alerts.append(LokiAlert(timestamp=ts, labels=labels, line=line))

        logger.info("CacPullCollector | Loki | %d alertes récupérées", len(alerts))
        return alerts

    def _fetch_prometheus(self) -> PrometheusSnapshot:
        """
        Interroge Prometheus pour les métriques-clés de la plateforme cible.
        Métriques ciblées (lecture seule, aucune modification) :
          - cac_mlops_drift_share          : taux de colonnes en dérive
          - mlops_model_info{alias="Production"} : modèle actuellement en prod
          - http_requests_total            : volume de trafic de l'API
        """
        def instant_query(metric_expr: str) -> Optional[Any]:
            with self._vps_client() as client:
                resp = client.get(
                    f"{CAC_PROMETHEUS_BASE}/api/v1/query",
                    params={"query": metric_expr},
                )
                resp.raise_for_status()
                result = resp.json().get("data", {}).get("result", [])
                if result:
                    return result[0].get("value", [None, None])[1]
            return None

        drift_share       = instant_query("cac_mlops_drift_share")
        model_in_prod_raw = instant_query('mlops_model_info{alias="Production"}')
        api_requests      = instant_query("http_requests_total")

        snap = PrometheusSnapshot(
            drift_share=float(drift_share) if drift_share is not None else None,
            model_in_production=str(model_in_prod_raw) if model_in_prod_raw else None,
            api_request_total=float(api_requests) if api_requests is not None else None,
        )
        logger.info("CacPullCollector | Prometheus | drift_share=%s", snap.drift_share)
        return snap

    def _fetch_mlflow_model(self) -> MlflowModelInfo:
        """
        Interroge MLflow pour récupérer les métadonnées du modèle actif.
        Endpoint : GET /api/2.0/mlflow/registered-models/alias
        Modèle ciblé : lgbm_accidents, alias : Production
        INTERDIT : ne jamais appeler POST/DELETE sur cet endpoint.
        """
        with self._vps_client() as client:
            # Récupération de l'alias Production
            resp = client.get(
                f"{CAC_MLFLOW_BASE}/api/2.0/mlflow/registered-models/alias",
                params={"name": "lgbm_accidents", "alias": "Production"},
            )
            resp.raise_for_status()
            mv = resp.json().get("model_version", {})

        # Récupération des métriques du run associé (GET uniquement)
        metrics: Dict[str, Any] = {}
        run_id = mv.get("run_id")
        if run_id:
            with self._vps_client() as client:
                run_resp = client.get(
                    f"{CAC_MLFLOW_BASE}/api/2.0/mlflow/runs/get",
                    params={"run_id": run_id},
                )
                if run_resp.status_code == 200:
                    run_data = run_resp.json().get("run", {})
                    for m in run_data.get("data", {}).get("metrics", []):
                        metrics[m["key"]] = m["value"]

        info = MlflowModelInfo(
            name=mv.get("name"),
            alias="Production",
            version=mv.get("version"),
            run_id=run_id,
            metrics=metrics,
            tags={t["key"]: t["value"] for t in mv.get("tags", [])},
        )
        logger.info(
            "CacPullCollector | MLflow | modèle=%s v%s run=%s",
            info.name, info.version, info.run_id
        )
        return info

    def _fetch_prefect_flow_runs(self) -> List[PrefectFlowRunSummary]:
        """
        Récupère les 10 derniers flow runs depuis Prefect (GET uniquement).
        INTERDIT : POST /api/deployments/{id}/create_flow_run et set_state.
        """
        with self._vps_client() as client:
            resp = client.get(
                f"{CAC_PREFECT_BASE}/api/flow_runs",
                params={"limit": 10, "sort": "START_TIME_DESC"},
            )
            resp.raise_for_status()
            raw_runs = resp.json()

        runs: List[PrefectFlowRunSummary] = []
        for r in raw_runs:
            runs.append(PrefectFlowRunSummary(
                id=r.get("id", ""),
                name=r.get("name"),
                state_name=r.get("state_name"),
                state_type=r.get("state_type"),
                start_time=_parse_dt(r.get("start_time")),
                end_time=_parse_dt(r.get("end_time")),
            ))

        logger.info("CacPullCollector | Prefect | %d flow runs récupérés", len(runs))
        return runs

    def _fetch_drift_report(self) -> DriftReportSnapshot:
        """
        Télécharge le rapport de dérive public Evidently (HTTPS, sans proxy Tailscale).
        URL : https://mlops.jakat-inc.fr/reports/drift/latest_summary.json
        Ce rapport est public et ne dépend pas du VPS Scaleway.
        """
        with httpx.Client(
            transport=self._direct_transport,
            timeout=self._timeout,
        ) as client:
            resp = client.get(CAC_DRIFT_REPORT_URL)
            resp.raise_for_status()
            raw = resp.json()

        snap = DriftReportSnapshot(
            report_date=raw.get("report_date") or raw.get("date"),
            drift_share=raw.get("drift_share") or raw.get("share_of_drifted_columns"),
            drifted_columns=raw.get("drifted_columns", []),
            raw=raw,
        )
        logger.info(
            "CacPullCollector | DriftReport | date=%s drift_share=%s",
            snap.report_date, snap.drift_share
        )
        return snap

    # -----------------------------------------------------------------------
    # Helpers internes
    # -----------------------------------------------------------------------

    def _vps_client(self) -> httpx.Client:
        """Retourne un client httpx configuré avec le proxy SOCKS5 Tailscale."""
        return httpx.Client(
            transport=self._proxy_transport,
            timeout=self._timeout,
        )


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def _parse_dt(value: Optional[str]) -> Optional[datetime]:
    """Parse une date ISO 8601 en datetime UTC. Retourne None si None ou invalide."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None
