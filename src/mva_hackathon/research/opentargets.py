"""Open Targets GraphQL helpers for the BUB1B axis."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from mva_hackathon.drug.targets import AXIS_TARGETS

OT_URL = "https://api.platform.opentargets.org/api/v4/graphql"
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(iterable, **kwargs):
        return iterable


def graphql(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        OT_URL,
        data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return json.loads(exc.read().decode())


def ensembl_from_symbol(symbol: str) -> str | None:
    query = """
    query TargetSearch($q: String!) {
      search(queryString: $q, entityNames: ["target"], page: {index: 0, size: 5}) {
        hits { id name entity }
      }
    }
    """
    data = graphql(query, {"q": symbol})
    hits = (data.get("data") or {}).get("search", {}).get("hits") or []
    for hit in hits:
        hid = (hit.get("id") or "").split(".")[0]
        name = (hit.get("name") or "").upper()
        if hid.startswith("ENSG") and (name == symbol.upper() or symbol.upper() in name):
            return hid
    for hit in hits:
        hid = (hit.get("id") or "").split(".")[0]
        if hid.startswith("ENSG"):
            return hid
    return None


def search_mva_diseases(size: int = 8) -> list[dict[str, Any]]:
    query = """
    query MvaSearch($q: String!, $size: Int!) {
      search(queryString: $q, entityNames: ["disease"], page: {index: 0, size: $size}) {
        hits { id name entity score }
      }
    }
    """
    data = graphql(query, {"q": "mosaic variegated aneuploidy", "size": size})
    return data.get("data", {}).get("search", {}).get("hits", []) or []


KNOWN_DRUGS_QUERY = """
query DrugCandidates($ensemblId: String!) {
  target(ensemblId: $ensemblId) {
    id
    approvedSymbol
    drugAndClinicalCandidates {
      count
      rows {
        maxClinicalStage
        drug { id name }
        diseases { disease { id name } }
      }
    }
  }
}
"""


def known_drugs(ensembl_id: str) -> dict[str, Any]:
    data = graphql(KNOWN_DRUGS_QUERY, {"ensemblId": ensembl_id})
    target = (data.get("data") or {}).get("target")
    return target or {}


def fetch_axis_known_drugs(max_workers: int = 8) -> list[dict[str, Any]]:
    """Resolve Ensembl IDs in parallel, then pull known drugs per target."""
    ensembl: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut = {pool.submit(ensembl_from_symbol, sym): sym for sym in AXIS_TARGETS}
        for task in tqdm(as_completed(fut), total=len(fut), desc="symbol→Ensembl"):
            sym = fut[task]
            eid = task.result()
            if eid:
                ensembl[sym] = eid

    rows: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut2 = {pool.submit(known_drugs, eid): sym for sym, eid in ensembl.items()}
        for task in tqdm(as_completed(fut2), total=len(fut2), desc="Open Targets drugs"):
            sym = fut2[task]
            try:
                payload = task.result()
            except Exception as exc:
                print(f"{sym}: {exc}")
                continue
            if not payload:
                continue
            drugs = (payload.get("drugAndClinicalCandidates") or {}).get("rows") or []
            for row in drugs:
                drug = row.get("drug") or {}
                diseases = [
                    (d.get("disease") or {})
                    for d in (row.get("diseases") or [])
                    if d.get("disease")
                ]
                rows.append(
                    {
                        "gene": sym,
                        "ensembl_id": ensembl[sym],
                        "drug_id": drug.get("id", ""),
                        "drug_name": drug.get("name", ""),
                        "disease_id": ";".join(x.get("id", "") for x in diseases),
                        "disease_name": ";".join(x.get("name", "") for x in diseases),
                        "phase": row.get("maxClinicalStage", ""),
                        "mechanism_of_action": "",
                    }
                )
    return rows
