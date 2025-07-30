from enum import Enum
from dataclasses import dataclass

class NodeType(Enum):
    PROVER = "prover"
    CHALLENGER = "challenger"
    

@dataclass(frozen=True)
class InfinitywatchNodeResponse:  
    node_id: str | None
    model_response: str
    model: str 
    challenge_id: str | None = None
    
    
