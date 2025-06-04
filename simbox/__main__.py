import argparse
from pathlib import Path

from .manager import SimManager

DEFAULT_DB = Path("sims.json")

def main():
    parser = argparse.ArgumentParser(description="SIM management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_p = subparsers.add_parser("add", help="Add new SIM")
    add_p.add_argument("iccid")
    add_p.add_argument("phone_number")

    list_p = subparsers.add_parser("list", help="List SIMs")

    assign_p = subparsers.add_parser("assign", help="Assign SIM to owner")
    assign_p.add_argument("iccid")
    assign_p.add_argument("owner")

    block_p = subparsers.add_parser("block", help="Block SIM")
    block_p.add_argument("iccid")

    remove_p = subparsers.add_parser("remove", help="Remove SIM")
    remove_p.add_argument("iccid")

    args = parser.parse_args()

    manager = SimManager(DEFAULT_DB)

    if args.command == "add":
        manager.add_sim(args.iccid, args.phone_number)
    elif args.command == "list":
        for sim in manager.list_sims():
            print(sim)
    elif args.command == "assign":
        manager.assign_sim(args.iccid, args.owner)
    elif args.command == "block":
        manager.block_sim(args.iccid)
    elif args.command == "remove":
        manager.remove_sim(args.iccid)

if __name__ == "__main__":
    main()
