
class WTNS_Exception(Exception):
    """Exception raised by the WitnessChain library."""
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

        