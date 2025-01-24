# Obfucsate player names for basic privacy in public code repos
import base64


B64_PLAYERS = [
    "U3RlcGhhbmllIFBhcGFnZW9yZ2U=",  # St Pa
    "RGlvbiBLaW5n",  # Di Ki
    "QWxiZXJ0byBDYWxkZXJvbg==",  # Al Ca
    "Sm9lIEZsb3Jlcw==",  # Jo Fl
    "U2hhaHZpciBCdWhhcml3YWxsYQ==",  # Sh Bu
    "UGF1bCBTaGVsdG9u",  # Pa Sh
    "TWl0Y2hlbGwgVGlqZXJpbmE=" , # Mi Ti
    "QW5naWUgUGF5bmU=",  # An Pa
]


def player_names(names: list[str] = B64_PLAYERS) -> list[str]:
    return [base64.b64decode(encoded_name.encode()).decode() for encoded_name in names]
