import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import os
from pathlib import Path

from simbox.manager import SimManager


def test_add_and_list(tmp_path):
    db = tmp_path / "db.json"
    mgr = SimManager(db)
    mgr.add_sim("123", "555")
    sims = mgr.list_sims()
    assert len(sims) == 1
    assert sims[0].iccid == "123"


def test_assign_and_block(tmp_path):
    db = tmp_path / "db.json"
    mgr = SimManager(db)
    mgr.add_sim("123", "555")
    mgr.assign_sim("123", "Alice")
    sim = mgr.list_sims()[0]
    assert sim.owner == "Alice"
    assert sim.status == "assigned"
    mgr.block_sim("123")
    assert mgr.list_sims()[0].status == "blocked"
