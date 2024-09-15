import re

DEFAULT_PATTERN = r"(?i)(?:\bBuy\b\s+)?(?P<token>[a-zA-Z0-9]{27,})"
class Extractor:
    def __init__(self):
        # Matches Buy sjnfbaousinb123naisbcaiusASAOISNdfunasnubf
        self.pattern = DEFAULT_PATTERN

    def setPattern(self, pattern):
        self.defaultPattern = pattern

    # Method to extract a token based on the current pattern
    def extractToken(self, s) -> None | str:
        match = re.search(self.pattern, s)
        if match:
            return match.group("token")  # Return the extracted token if a match is found
        return None  # Return None if no match is found
    