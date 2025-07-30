"""
MDIS - Malware Detection and Identification System
--------------------------------------------------

A minimal yet expressive malware identifier system,
designed for fast parsing, clarity, and extensibility.
"""

import re
import json

DICTIONARIES = {
    "target_os": {
        "Win": "Windows",
        "Lin": "Linux",
        "And": "Android",
        "Mac": "macOS",
        "iOS": "iOS",
        "IoT": "Internet of Things",
        "BSD": "BSD-based OS",
        "Web": "Web Applications",
        "MSE": "Multi-Platform",
        "VM": "Virtualization Environments",
        "Kai": "KaiOS",
        "Tiz": "Tizen",
        "Palm": "Palm OS",
        "Chrome": "Chrome OS",
        "RTOS": "Generic RTOS",
        "Zeph": "Zephyr",
        "Contiki": "Contiki",
        "RIOT": "RIOT OS",
        "Tiny": "TinyOS",
        "ZOS": "IBM z/OS",
        "AIX": "IBM AIX",
        "OpenVMS": "OpenVMS",
        "Solaris": "Solaris",
        "Alpine": "Alpine Linux",
        "Photon": "Photon OS",
        "Clear": "Clear Linux",
        "RHEL": "Red Hat Enterprise",
        "SLES": "SUSE Enterprise",
        "Nix": "NixOS"
    },
    "behaviors": {
        "Ransom": "Encrypts data for ransom",
        "Spy": "Espionage/data collection",
        "Banker": "Financial theft",
        "DDoS": "Denial-of-service attacks",
        "Miner": "Cryptocurrency mining",
        "Dropper": "Deploys other malware",
        "Worm": "Self-replicating network spread",
        "Backdoor": "Maintains remote access",
        "RAT": "Remote Access Trojan",
        "Wiper": "Data destruction",
        "Stealer": "Information theft",
        "Adware": "Unwanted advertising",
        "Rootkit": "System concealment",
        "Keylogger": "Records keystrokes",
        "Bootkit": "Affects the boot process",
        "Hijacker": "Takes control of browser or application",
        "FakeAV": "Fake antivirus software",
        "Rogue": "Fake legitimate software for fraud",
        "Locker": "Locks the screen or device",
        "Injector": "Injects code into another process",
        "Sniffer": "Monitors network traffic",
        "Bypass": "Evades detection techniques",
        "Resurrector": "Self-recovers after being deleted",
        "FileInfector": "Infects legitimate files",
        "Polymorph": "Self-modifies code to avoid detection",
        "Obfuscator": "Obfuscates code to hinder analysis",
        "Downloader": "Downloads additional payloads remotely",
        "Trojan": "Disguises as legitimate software",
        "Joker": "Tricks users with fake threats",
        "RogueModule": "Malicious plugin or extension",
        "C2": "Used as a Command-and-Control",
        "Loader": "Used to load other malware",
        "Packer": "Packed to avoid detection",
        "Scanner": "Scans for vulnerabilities",
    },
    "infection_vectors": {
        "Phish": "Phishing emails/websites",
        "Exploit": "Software vulnerability exploitation",
        "Removable": "USB/removable devices",
        "PUA": "Potentially Unwanted Applications",
        "DriveBy": "Malicious websites",
        "NetShare": "Network shares",
        "Social": "Social media platforms",
        "IM": "Instant messaging apps",
        "Watering": "Watering hole attacks",
        "Supply": "Supply chain compromise",
        "Brute": "Brute-force attacks",
        "EmailAttach": "Email attachments",
        "FakeApp": "Fake apps in app stores",
        "Torrent": "Peer-to-peer file sharing software",
        "Malvertise": "Malicious advertising",
        "Preload": "Pre-installed (OEM, cracked OS)",
        "Script": "Malicious macros, PowerShell, JS, etc.",
        "DriveAuto": "Spreads via autorun.inf (old Windows)",
        "Unknown": "Vector not identified (needs deeper analysis)",
        "None": "No self-propagation (manual install only)",
    },
}


def _build_mdis_regex(dictionaries):
    os_keys = "|".join(dictionaries["target_os"].keys())
    behavior_keys = "|".join(dictionaries["behaviors"].keys())
    vector_keys = "|".join(dictionaries["infection_vectors"].keys())
    os_pattern = f"(?P<os>{os_keys})"
    family_pattern = r"(?P<family>[A-Z][a-zA-Z0-9]*)"
    version_pattern = r"(?P<version>(?:[IVXLCDM]+\.)?[A-Z])"
    behaviors_pattern = f"(?P<behavior>(?:{behavior_keys})(?:_(?:{behavior_keys}))*)"
    vectors_pattern = f"(?P<vector>(?:{vector_keys})(?:_(?:{vector_keys}))*)"
    full_pattern = (
        f"^{os_pattern}"
        f":{family_pattern}"
        f"\\.{version_pattern}"
        f"#{behaviors_pattern}"
        f"!{vectors_pattern}$"
    )
    # print(full_pattern)
    return re.compile(full_pattern, re.IGNORECASE)


def _roman_to_int(s):
    roman_map = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100, "D": 500, "M": 1000}
    result = 0
    for i in range(len(s) - 1, -1, -1):
        if i < len(s) - 1 and roman_map[s[i]] < roman_map[s[i + 1]]:
            result -= roman_map[s[i]]
        else:
            result += roman_map[s[i]]
    return result


def _describe_version(version_code):
    parts = version_code.split(".")
    major_num = 1
    minor_char = ""
    minor_num = 0
    if len(parts) == 2:
        major_roman, minor_char = parts
        major_num = _roman_to_int(major_roman)
    elif len(parts) == 1:
        minor_char = parts[0]
    minor_num = ord(minor_char.upper()) - 64
    description = f"Build {minor_num} of Major Variant {major_num}"
    structured_data = {
        "major": major_num,
        "minor": minor_num,
        "full_description": description,
    }
    return description, structured_data


class MDISParserError(Exception):
    """
    Custom exception raised when an MDIS identifier fails validation or parsing.

    Args:
        err (str): Error message to display.
    """

    def __init__(self, err):
        super().__init__(err)


class MDISParser:
    """
    A parser for MDIS malware identifiers.

    Parses and optionally enriches identifiers based on the official MDIS dictionaries.
    The parser supports extracting raw data as well as generating natural language reports.

    Attributes:
        identifier (str): The MDIS-formatted identifier to parse.
        _match (re.Match): The match object after applying regex to the identifier.
    """

    REGEX_PATTERN = _build_mdis_regex(DICTIONARIES)

    def __init__(self, identifier):
        """
        Initialize the parser with an identifier.

        Args:
            identifier (str): The MDIS identifier string to be parsed.
        """
        self.identifier = identifier
        self._match = self.REGEX_PATTERN.match(self.identifier)

    def is_valid(self):
        """
        Check if the identifier is valid based on MDIS regex rules.

        Returns:
            bool: True if valid, False otherwise.
        """
        return self._match is not None

    def parse(self, more_info=False):
        """
        Parse the MDIS identifier and extract structured data.

        Args:
            more_info (bool): If True, includes detailed descriptions from dictionaries.

        Returns:
            dict: Parsed data containing identifier components. Raises MDISParserError if invalid.
        """
        if not self.is_valid():
            raise MDISParserError(f"'{self.identifier}' is an invalid identifier.")
        data = self._match.groupdict()
        if more_info:
            os_code = data["os"]
            os_desc = DICTIONARIES["target_os"].get(os_code.capitalize())
            family_desc = data["family"]
            version_code = data["version"]
            version = _describe_version(version_code)
            _ = version[0]
            version_structured = version[1]
            behaviors = data["behavior"].split("_")
            behavior_descs = [
                {"code": b, "description": DICTIONARIES["behaviors"].get(b.capitalize())}
                for b in behaviors
            ]
            vectors = data["vector"].split("_")
            vector_descs = [
                {"code": v, "description": DICTIONARIES["infection_vectors"].get(v.capitalize())}
                for v in vectors
            ]
            result = {
                "mdis_identifier": self.identifier,
                "os": {"code": os_code, "description": os_desc},
                "family": family_desc,
                "version": {
                    "code": version_code,
                    "major_variant": version_structured["major"],
                    "minor_build": version_structured["minor"],
                    "description": version_structured["full_description"],
                },
                "behaviors": behavior_descs,
                "vectors": vector_descs,
            }
            return result
        return data

    def to_natural(self):
        """
        Convert the MDIS identifier into a human-readable description.

        Returns:
            str: A natural language representation of the identifier.
        """
        data = self.parse(more_info=True)
        os_desc = data["os"]["description"]
        family = data["family"]
        version = data["version"]["description"]
        behaviors = ", ".join([b["description"] for b in data["behaviors"]])
        vectors = ", ".join([v["description"] for v in data["vectors"]])
        return f"{os_desc}, {behaviors}, Family {family} {version}, {vectors}-based delivery"

    def dump_report_file(self):
        """
        Dump the enriched parsed result into a JSON report file.

        The output filename will be based on the malware family and version.

        Returns:
            None
        """
        data = self.parse(more_info=True)
        output_filename = f'report_{data["family"]}_{data["version"]["code"]}.json'
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    @staticmethod
    def build_id(fields):
        """
        Build MDIS identifier string from structured fields.

        Args:
            fields (dict): Must include keys 'os', 'family', 'behavior', 'version', and 'vector'.

        Returns:
            str: MDIS-formatted identifier.
        """
        try:
            os_code = fields["os"]
            family = fields["family"]
            behavior = fields["behavior"]
            version = fields["version"]
            vector = fields["vector"]
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        id_str = f"{os_code}:{family}.{version}#{behavior}!{vector}"
        return id_str
