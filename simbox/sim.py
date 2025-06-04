from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SimCard:
    iccid: str
    phone_number: str
    status: str = field(default="available")
    owner: Optional[str] = field(default=None)
