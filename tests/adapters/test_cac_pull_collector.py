"""
Tests unitaires du CacPullCollector.

Stratégie : tous les appels HTTP sont mockés avec pytest-mock + httpx.MockTransport.
Le VPS cible (100.117.99.62) n'a pas besoin d'être allumé pour que ces tests
passent. Ils valident le parsing des réponses JSON, la gestion du mode offline
et le respect strict du principe lecture-seule (aucun POST/PUT/DELETE appelé).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import httpx
import pytest

from agentic_ops.adapters.cac_pull_collector import (
    CAC_DRIFT_REPORT_URL,
    CAC_LOKI_BASE,
    CAC_MLFLOW_BASE,
    CAC_PREFECT_BASE,
    CAC_PROMETHEUS_BASE,
    CacCollectedSnapshot,
    CacPullCollector,
    DriftReportSnapshot,
    LokiAlert,
    MlflowModelInfo,
    PrefectFlowRunSummary,
    PrometheusSnapshot,
    RemoteServiceStatus,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def collector_no_proxy() -> CacPullCollector:
    """Collecteur sans proxy Tailscale (pour les tests mockés)."""
    return CacPullCollector(use_proxy_for_vps=False)


# ---------------------------------------------------------------------------
# Données de réponse simulées (copie fidèle des schémas de l'API distante)
# ---------------------------------------------------------------------------

LOKI_RESPONSE: Dict[str, Any] = {
    "data": {
        "resultType": "streams",
        "result": [
            {
                "stream": {"service": "prefect-worker", "level": "warning"},
                "values": [
                    ["1728768000000000000", '{"event":"alert","risk_id":"DATA-042","message":"drift detected"}'],
                    ["1728771600000000000", '{"event":"alert","risk_id":"INFRA-001","message":"cpu spike"}'],
                ]
            }
        ]
    }
}

PROMETHEUS_DRIFT_RESPONSE: Dict[str, Any] = {
    "data": {"result": [{"metric": {}, "value": [1728771600, "0.34"]}]}
}

PROMETHEUS_MODEL_RESPONSE: Dict[str, Any] = {
    "data": {"result": [{"metric": {"alias": "Production"}, "value": [1728771600, "lgbm_v3"]}]}
}

PROMETHEUS_EMPTY_RESPONSE: Dict[str, Any] = {
    "data": {"result": []}
}

MLFLOW_ALIAS_RESPONSE: Dict[str, Any] = {
    "model_version": {
        "name": "lgbm_accidents",
        "version": "7",
        "run_id": "abc123def456",
        "tags": [{"key": "stage", "value": "production"}],
    }
}

MLFLOW_RUN_RESPONSE: Dict[str, Any] = {
    "run": {
        "data": {
            "metrics": [
                {"key": "f1_score", "value": 0.883},
                {"key": "accuracy", "value": 0.891},
            ]
        }
    }
}

PREFECT_FLOW_RUNS_RESPONSE = [
    {
        "id": "run-001",
        "name": "lgbm-training-2026-10-10",
        "state_name": "Completed",
        "state_type": "COMPLETED",
        "start_time": "2026-10-10T08:00:00Z",
        "end_time":   "2026-10-10T08:47:12Z",
    },
    {
        "id": "run-002",
        "name": "data-validation-2026-10-11",
        "state_name": "Failed",
        "state_type": "FAILED",
        "start_time": "2026-10-11T09:00:00Z",
        "end_time":   "2026-10-11T09:03:22Z",
    }
]

DRIFT_REPORT_RESPONSE: Dict[str, Any] = {
    "report_date": "2026-10-12",
    "drift_share": 0.34,
    "drifted_columns": ["age_conducteur", "hrmn", "surf"],
    "total_columns": 18,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_response(status_code: int, body: Any) -> httpx.Response:
    """Construit une httpx.Response mockée avec le body JSON fourni."""
    return httpx.Response(
        status_code=status_code,
        content=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        request=httpx.Request("GET", "http://mock"),
    )


def _connect_error() -> httpx.ConnectError:
    return httpx.ConnectError("Connection refused")


# ---------------------------------------------------------------------------
# Tests — fetch individuel
# ---------------------------------------------------------------------------

class TestFetchLokiAlerts:
    def test_parse_alerts_correctement(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie que les streams Loki sont bien parsés en LokiAlert."""
        with patch.object(
            collector_no_proxy, "_vps_client"
        ) as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = _make_response(200, LOKI_RESPONSE)

            alerts = collector_no_proxy._fetch_loki_alerts()

        assert len(alerts) == 2
        assert all(isinstance(a, LokiAlert) for a in alerts)
        assert alerts[0].labels["service"] == "prefect-worker"
        assert '"event":"alert"' in alerts[0].line
        assert "risk_id" in alerts[0].line

    def test_retourne_liste_vide_si_no_result(self, collector_no_proxy: CacPullCollector) -> None:
        """Retourne une liste vide si Loki ne trouve aucun log."""
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = _make_response(200, {"data": {"result": []}})

            alerts = collector_no_proxy._fetch_loki_alerts()

        assert alerts == []


class TestFetchPrometheus:
    def test_parse_drift_share(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie le parsing de la métrique cac_mlops_drift_share."""
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            # Réponse différente selon la métrique interrogée
            mock_client.get.side_effect = [
                _make_response(200, PROMETHEUS_DRIFT_RESPONSE),   # drift_share
                _make_response(200, PROMETHEUS_MODEL_RESPONSE),   # model_in_production
                _make_response(200, PROMETHEUS_EMPTY_RESPONSE),   # api_request_total vide
            ]

            snap = collector_no_proxy._fetch_prometheus()

        assert isinstance(snap, PrometheusSnapshot)
        assert snap.drift_share == pytest.approx(0.34)
        assert snap.model_in_production == "lgbm_v3"
        assert snap.api_request_total is None


class TestFetchMlflowModel:
    def test_parse_modele_production(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie la récupération du modèle lgbm_accidents alias Production."""
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.side_effect = [
                _make_response(200, MLFLOW_ALIAS_RESPONSE),  # alias
                _make_response(200, MLFLOW_RUN_RESPONSE),    # run metrics
            ]

            info = collector_no_proxy._fetch_mlflow_model()

        assert isinstance(info, MlflowModelInfo)
        assert info.name == "lgbm_accidents"
        assert info.version == "7"
        assert info.alias == "Production"
        assert info.run_id == "abc123def456"
        assert info.metrics["f1_score"] == pytest.approx(0.883)
        assert info.tags["stage"] == "production"


class TestFetchPrefect:
    def test_parse_flow_runs(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie le parsing des flow runs Prefect."""
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = _make_response(200, PREFECT_FLOW_RUNS_RESPONSE)

            runs = collector_no_proxy._fetch_prefect_flow_runs()

        assert len(runs) == 2
        assert isinstance(runs[0], PrefectFlowRunSummary)
        assert runs[0].id == "run-001"
        assert runs[0].state_type == "COMPLETED"
        assert runs[1].state_type == "FAILED"
        assert runs[0].start_time is not None

    def test_n_appelle_que_get(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie qu'aucun POST/PUT/DELETE n'est jamais émis vers Prefect."""
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = _make_response(200, PREFECT_FLOW_RUNS_RESPONSE)

            collector_no_proxy._fetch_prefect_flow_runs()

        # Seulement GET appelé
        mock_client.get.assert_called_once()
        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
        mock_client.delete.assert_not_called()


class TestFetchDriftReport:
    def test_parse_rapport_public(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie le parsing du rapport de dérive public Evidently."""
        with patch("httpx.Client") as MockClient:
            mock_resp = _make_response(200, DRIFT_REPORT_RESPONSE)
            MockClient.return_value.__enter__.return_value.get.return_value = mock_resp

            snap = collector_no_proxy._fetch_drift_report()

        assert isinstance(snap, DriftReportSnapshot)
        assert snap.drift_share == pytest.approx(0.34)
        assert snap.report_date == "2026-10-12"
        assert "age_conducteur" in snap.drifted_columns
        assert len(snap.drifted_columns) == 3


# ---------------------------------------------------------------------------
# Tests — collect_all() et résilience offline
# ---------------------------------------------------------------------------

class TestCollectAll:
    def test_status_online_si_tout_repond(self, collector_no_proxy: CacPullCollector) -> None:
        """Retourne ONLINE si les 5 sources répondent sans erreur."""
        with (
            patch.object(collector_no_proxy, "_fetch_loki_alerts",       return_value=[]),
            patch.object(collector_no_proxy, "_fetch_prometheus",         return_value=PrometheusSnapshot()),
            patch.object(collector_no_proxy, "_fetch_mlflow_model",       return_value=MlflowModelInfo()),
            patch.object(collector_no_proxy, "_fetch_prefect_flow_runs",  return_value=[]),
            patch.object(collector_no_proxy, "_fetch_drift_report",       return_value=DriftReportSnapshot()),
        ):
            snapshot = collector_no_proxy.collect_all()

        assert snapshot.status == RemoteServiceStatus.ONLINE
        assert not snapshot.errors

    def test_status_offline_si_vps_eteint(self, collector_no_proxy: CacPullCollector) -> None:
        """
        Retourne REMOTE_TARGET_OFFLINE si toutes les sources lèvent ConnectError.
        L'orchestrateur ne doit pas recevoir d'exception.
        """
        err = httpx.ConnectError("Connection refused")
        with (
            patch.object(collector_no_proxy, "_fetch_loki_alerts",       side_effect=err),
            patch.object(collector_no_proxy, "_fetch_prometheus",         side_effect=err),
            patch.object(collector_no_proxy, "_fetch_mlflow_model",       side_effect=err),
            patch.object(collector_no_proxy, "_fetch_prefect_flow_runs",  side_effect=err),
            patch.object(collector_no_proxy, "_fetch_drift_report",       side_effect=err),
        ):
            snapshot = collector_no_proxy.collect_all()  # ne doit pas lever

        assert snapshot.status == RemoteServiceStatus.REMOTE_TARGET_OFFLINE
        assert len(snapshot.errors) == 5
        assert snapshot.loki_alerts is None
        assert snapshot.prometheus is None

    def test_status_partial_si_une_source_echoue(self, collector_no_proxy: CacPullCollector) -> None:
        """Retourne PARTIAL si seulement une source est indisponible."""
        err = httpx.TimeoutException("timeout")
        with (
            patch.object(collector_no_proxy, "_fetch_loki_alerts",       side_effect=err),
            patch.object(collector_no_proxy, "_fetch_prometheus",         return_value=PrometheusSnapshot()),
            patch.object(collector_no_proxy, "_fetch_mlflow_model",       return_value=MlflowModelInfo()),
            patch.object(collector_no_proxy, "_fetch_prefect_flow_runs",  return_value=[]),
            patch.object(collector_no_proxy, "_fetch_drift_report",       return_value=DriftReportSnapshot()),
        ):
            snapshot = collector_no_proxy.collect_all()

        assert snapshot.status == RemoteServiceStatus.PARTIAL
        assert "loki_alerts" in snapshot.errors
        assert snapshot.loki_alerts is None
        assert snapshot.prometheus is not None

    def test_snapshot_est_serialisable(self, collector_no_proxy: CacPullCollector) -> None:
        """Vérifie que le snapshot peut être converti en dict JSON (pour Evidence Store)."""
        with (
            patch.object(collector_no_proxy, "_fetch_loki_alerts",       return_value=[]),
            patch.object(collector_no_proxy, "_fetch_prometheus",         return_value=PrometheusSnapshot(drift_share=0.34)),
            patch.object(collector_no_proxy, "_fetch_mlflow_model",       return_value=MlflowModelInfo(name="lgbm_accidents", version="7")),
            patch.object(collector_no_proxy, "_fetch_prefect_flow_runs",  return_value=[]),
            patch.object(collector_no_proxy, "_fetch_drift_report",       return_value=DriftReportSnapshot(drift_share=0.34)),
        ):
            snapshot = collector_no_proxy.collect_all()

        as_dict = snapshot.model_dump()
        assert as_dict["prometheus"]["drift_share"] == pytest.approx(0.34)
        assert as_dict["mlflow_model"]["name"] == "lgbm_accidents"
        assert as_dict["status"] == "ONLINE"


# ---------------------------------------------------------------------------
# Test de sécurité — vérification de la règle lecture seule
# ---------------------------------------------------------------------------

class TestReadOnlyEnforcement:
    """
    Garantit que le collecteur n'émet JAMAIS d'appels d'écriture.
    Ces tests vérifient que les méthodes .post / .put / .delete
    ne sont jamais appelées sur aucun des clients httpx.
    """

    def test_aucun_post_dans_fetch_mlflow(self, collector_no_proxy: CacPullCollector) -> None:
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.side_effect = [
                _make_response(200, MLFLOW_ALIAS_RESPONSE),
                _make_response(200, MLFLOW_RUN_RESPONSE),
            ]
            collector_no_proxy._fetch_mlflow_model()

        mock_client.post.assert_not_called()
        mock_client.put.assert_not_called()
        mock_client.delete.assert_not_called()

    def test_aucun_post_dans_fetch_loki(self, collector_no_proxy: CacPullCollector) -> None:
        with patch.object(collector_no_proxy, "_vps_client") as mock_ctx:
            mock_client = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_client
            mock_client.get.return_value = _make_response(200, LOKI_RESPONSE)
            collector_no_proxy._fetch_loki_alerts()

        mock_client.post.assert_not_called()
