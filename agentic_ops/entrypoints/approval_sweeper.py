def run(orch):
    for eid in orch.repo.sweep_expired():
        orch.close_episode(eid, "EXPIRED")
        orch.notifier.notify_expired(eid)
    for eid in orch.repo.stuck_claims(older_than_s=300):
        orch.notifier.alert(f"{eid}: CLAIMED depuis >5 min sans issue. Vérifier l'état réel, NE PAS rejouer.")
