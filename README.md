# smsbox

This project implements a simple SIM management system with a command line
interface. You can add, list, assign, block and remove SIM cards. Data is stored
in a JSON file `sims.json` by default.

## Usage

Run the CLI using Python:

```bash
python -m simbox add 8901 5551234
python -m simbox list
```

## Running tests

Install pytest and run:

```bash
pytest
```
