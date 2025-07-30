
from dataclasses import dataclass
from enum import Enum

@dataclass(frozen=True)
class Constants:
    BASE_URL = "https://testnet.witnesschain.com/proof"
    API_VERSION = "v1"
    
    PROOF_OF_MODEL= "pom"
    


@dataclass(frozen=True)
class InfinitywatchEndpoints:
    CHALLENGE_REQUEST = "/challenge-request"
    CHALLENGE_STATUS = "/challenge-status"
    CHALLENGERS = "/challengers"
    

class DataTypes(Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    


def wtns_get_base_url(proof_type: str) -> str:
    match proof_type:
        case Constants.PROOF_OF_MODEL:
            return f"{Constants.BASE_URL}/{Constants.API_VERSION}/{Constants.PROOF_OF_MODEL}"
        
        case _:
            raise ValueError(f"Unknown proof type: {proof_type}")
