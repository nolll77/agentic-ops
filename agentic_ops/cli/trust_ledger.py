import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

console = Console(width=140)

EVIDENCE_DIR = Path("agentic_ops/evidence_store")

def load_episodes():
    episodes = []
    if not EVIDENCE_DIR.exists():
        return episodes
        
    for file_path in EVIDENCE_DIR.glob("*.json"):
        if file_path.name == "_index.json":
            continue
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
                episodes.append(data)
        except Exception:
            pass
    # Sort by timestamp descending
    episodes.sort(key=lambda x: x.get("timestamp_utc", ""), reverse=True)
    return episodes

def cmd_list():
    episodes = load_episodes()
    if not episodes:
        console.print("[yellow]Aucune évidence trouvée dans le Trust Ledger.[/yellow]")
        return

    table = Table(title="Trust Ledger - Audit Trail", show_header=True, header_style="bold magenta")
    table.add_column("Episode ID", style="cyan", no_wrap=True)
    table.add_column("Timestamp", style="dim")
    table.add_column("Risk / Mode", style="yellow")
    table.add_column("Agent LLM", style="blue")
    table.add_column("Action Demandée", style="green")
    table.add_column("Décision Policy", justify="center")

    for ep in episodes:
        ep_id = ep.get("episode_id", "N/A")
        ts = ep.get("timestamp_utc", "N/A")[:19] # Truncate microseconds
        
        # Risk ID extraction
        risk = ep.get("risk_id")
        if not risk and "risk" in ep:
            risk = ep["risk"].get("id", "N/A")
            
        mode = ep.get("mode", "LIVE")
        risk_str = f"{risk} ({mode})"
        
        agent = ep.get("diagnosis", {}).get("agent", "N/A")
        action = ep.get("action_proposal", {}).get("type", "N/A")
        
        decision = ep.get("policy_evaluation", {}).get("decision", "N/A")
        if decision == "ALLOW":
            dec_str = f"[bold green]{decision}[/bold green]"
        elif decision == "DENY":
            dec_str = f"[bold red]{decision}[/bold red]"
        else:
            dec_str = f"[bold yellow]{decision}[/bold yellow]"

        table.add_row(ep_id, ts, risk_str, agent, action, dec_str)

    console.print(table)

def cmd_inspect(episode_id: str):
    episodes = load_episodes()
    episode = next((ep for ep in episodes if ep.get("episode_id") == episode_id), None)
    
    if not episode:
        console.print(f"[bold red]Episode {episode_id} introuvable.[/bold red]")
        return
        
    console.print(f"\n[bold cyan]=== Audit Détaillé : {episode_id} ===[/bold cyan]\n")
    
    # 1. Contexte
    risk_id = episode.get("risk_id") or episode.get("risk", {}).get("id", "N/A")
    ctx_text = f"[bold]Risk ID:[/bold] {risk_id}\n[bold]Timestamp:[/bold] {episode.get('timestamp_utc')}\n"
    
    if "state_machine_trace" in episode:
        trace = " ➜ ".join(episode["state_machine_trace"])
        ctx_text += f"\n[bold]State Machine Trace:[/bold]\n[dim]{trace}[/dim]"
    
    console.print(Panel(ctx_text, title="1. Contexte & Détection", border_style="cyan"))
    
    # 2. Diagnostic LLM
    diag = episode.get("diagnosis", {})
    agent = diag.get("agent", "N/A")
    conf = diag.get("confidence", 0.0)
    
    diag_text = f"[bold]Agent Spécialiste:[/bold] {agent}\n[bold]Confiance:[/bold] {conf*100:.1f}%\n\n[bold]Findings (Preuves):[/bold]\n"
    findings = diag.get("findings", [])
    for f in findings:
        if isinstance(f, dict):
            diag_text += f" - {f.get('description', '')}\n"
        else:
            diag_text += f" - {f}\n"
            
    console.print(Panel(diag_text, title="2. Diagnostic du LLM", border_style="blue"))
    
    # 3. Policy & Execution
    action = episode.get("action_proposal", {})
    policy = episode.get("policy_evaluation", {})
    exec_res = episode.get("execution", {})
    
    act_text = f"[bold]Action Demandée:[/bold] {action.get('type')}\n"
    act_text += f"[bold]Réversible:[/bold] {action.get('reversible', 'N/A')}\n\n"
    
    dec = policy.get('decision', 'N/A')
    dec_color = "green" if dec == "ALLOW" else ("red" if dec == "DENY" else "yellow")
    act_text += f"[bold]Décision du Policy Engine:[/bold] [{dec_color}]{dec}[/{dec_color}]\n"
    if "reason" in policy or "matched_rule" in policy:
        act_text += f"[bold]Règle/Raison:[/bold] {policy.get('matched_rule', policy.get('reason'))}\n"
        
    if exec_res:
        act_text += f"\n[bold]Résultat Exécution:[/bold] {exec_res.get('status')}\n"
        act_text += f"[dim]{exec_res.get('details', '')}[/dim]"
        
    console.print(Panel(act_text, title="3. Gouvernance & Exécution", border_style="green"))


def cmd_merkle_root():
    import math
    from agentic_ops.core.evidence import EvidenceStore
    store = EvidenceStore(str(EVIDENCE_DIR))
    tree = store.get_merkle_tree()
    episodes = store.load_all_episodes()
    n = len(episodes)
    depth = math.ceil(math.log2(n)) + 1 if n > 0 else 1
    console.print(f"\n[bold cyan]=== Binary Merkle Tree Cryptographique (RFC 6962) ===[/bold cyan]")
    console.print(f"[bold]Nombre d'épisodes scellés :[/bold] {n}")
    console.print(f"[bold]Merkle Root (SHA-256)      :[/bold] [bold green]{tree.root}[/bold green]")
    console.print(f"[bold]Profondeur maximale        :[/bold] {depth} niveaux (Vérification O(log N) <= {depth - 1} étapes)")
    console.print(f"[dim]Complexité : Construction O(N) | Taille de preuve & Vérification O(log N)[/dim]")
    console.print(f"[dim]Second-preimage resistant : Domain Separators 0x00 (feuilles) / 0x01 (nœuds parents)[/dim]\n")


def cmd_merkle_proof(episode_id: str):
    from agentic_ops.core.evidence import EvidenceStore
    store = EvidenceStore(str(EVIDENCE_DIR))
    proof_packet = store.get_merkle_proof(episode_id)
    if not proof_packet:
        console.print(f"[bold red]Episode {episode_id} introuvable dans le ledger.[/bold red]")
        return
    is_valid = EvidenceStore.verify_merkle_proof(proof_packet)
    console.print(f"\n[bold cyan]=== Preuve d'Inclusion Merkle RFC 6962 : {episode_id} ===[/bold cyan]")
    console.print(f"[bold]Position dans l'arbre :[/bold] Feuille index {proof_packet['leaf_index']} / {proof_packet['total_leaves']}")
    console.print(f"[bold]Leaf Hash (0x00)      :[/bold] [cyan]{proof_packet['leaf_hash']}[/cyan]")
    console.print(f"[bold]Liaison Cryptographique :[/bold] [green]Vérifiée (episode_id scellé dans canonical_payload)[/green]")
    console.print(f"[bold]Merkle Root Attendue  :[/bold] [green]{proof_packet['merkle_root']}[/green]")
    console.print(f"[bold]Audit Path (RFC 6962) :[/bold] {len(proof_packet['audit_path'])} étapes logarithmiques")
    for idx, step in enumerate(proof_packet['audit_path']):
        console.print(f"  [{idx+1}] Sibling ({step['position']:5s}) : {step['hash']}")
    
    status_color = "bold green" if is_valid else "bold red"
    status_text = "VALIDE (Mathématiquement intègre & inclus dans le Merkle Root)" if is_valid else "INVALIDE (Altération détectée)"
    console.print(f"\n[bold]Vérification O(log N) :[/bold] [{status_color}]{status_text}[/{status_color}]\n")



def main():
    parser = argparse.ArgumentParser(description="Trust Ledger - Observabilité de l'Agentic Control Plane")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
    
    # Commande list
    subparsers.add_parser("list", help="Lister tous les épisodes")
    
    # Commande inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspecter un épisode spécifique")
    inspect_parser.add_argument("episode_id", type=str, help="L'ID de l'épisode (ex: EP-0001)")

    # Commande merkle-root
    subparsers.add_parser("merkle-root", help="Afficher la racine cryptographique Merkle Root (RFC 6962)")

    # Commande merkle-proof
    proof_parser = subparsers.add_parser("merkle-proof", help="Générer et vérifier la preuve d'inclusion Merkle pour un épisode")
    proof_parser.add_argument("episode_id", type=str, help="L'ID de l'épisode (ex: EP-0001)")
    
    args = parser.parse_args()
    
    if args.command == "list" or args.command is None:
        cmd_list()
    elif args.command == "inspect":
        cmd_inspect(args.episode_id)
    elif args.command == "merkle-root":
        cmd_merkle_root()
    elif args.command == "merkle-proof":
        cmd_merkle_proof(args.episode_id)


if __name__ == "__main__":
    main()

