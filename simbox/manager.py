import json
from pathlib import Path
from typing import List, Optional

from .sim import SimCard

class SimManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.sims: List[SimCard] = []
        self.load()

    def load(self) -> None:
        if self.db_path.exists():
            data = json.loads(self.db_path.read_text())
            self.sims = [SimCard(**item) for item in data]
        else:
            self.sims = []

    def save(self) -> None:
        data = [s.__dict__ for s in self.sims]
        self.db_path.write_text(json.dumps(data, indent=2))

    def list_sims(self) -> List[SimCard]:
        return list(self.sims)

    def add_sim(self, iccid: str, phone_number: str) -> SimCard:
        if any(s.iccid == iccid for s in self.sims):
            raise ValueError(f"SIM {iccid} already exists")
        sim = SimCard(iccid=iccid, phone_number=phone_number)
        self.sims.append(sim)
        self.save()
        return sim

    def remove_sim(self, iccid: str) -> None:
        before = len(self.sims)
        self.sims = [s for s in self.sims if s.iccid != iccid]
        if len(self.sims) == before:
            raise ValueError(f"SIM {iccid} not found")
        self.save()

    def assign_sim(self, iccid: str, owner: str) -> None:
        sim = self._find(iccid)
        sim.owner = owner
        sim.status = "assigned"
        self.save()

    def block_sim(self, iccid: str) -> None:
        sim = self._find(iccid)
        sim.status = "blocked"
        self.save()

    def _find(self, iccid: str) -> SimCard:
        for sim in self.sims:
            if sim.iccid == iccid:
                return sim
        raise ValueError(f"SIM {iccid} not found")
