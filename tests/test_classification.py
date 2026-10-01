from classify_challenge import classify


def facts(description: str, files: list[str], remote: str | None = None) -> dict:
    return {
        "description": description,
        "files": [{"name": name, "suffix": "." + name.rsplit(".", 1)[-1].lower() if "." in name else "", "size": 1} for name in files],
        "remote_target": remote,
    }


def test_native_remote_crash_routes_to_pwn() -> None:
    result = classify(facts("ELF remote service crashes after a buffer overflow", ["chall.elf"], "target.example:31337"))
    assert result["primary_category"] == "ctf-pwn"


def test_native_without_primitive_routes_to_reverse() -> None:
    result = classify(facts("Understand this obfuscated binary and custom VM", ["chall.elf"]))
    assert result["primary_category"] == "ctf-reverse"


def test_pcap_timing_routes_to_forensics() -> None:
    result = classify(facts("Find the packet timing covert channel", ["capture.pcapng"]))
    assert result["primary_category"] == "ctf-forensics"


def test_nextjs_chunks_route_to_web() -> None:
    result = classify(facts("Next.js application with JavaScript chunks and JWT", ["app.js"]))
    assert result["primary_category"] == "ctf-web"


def test_custom_cipher_binary_has_crypto_secondary() -> None:
    result = classify(facts("Reverse a custom cipher implemented in this ELF", ["chall.elf"]))
    assert result["primary_category"] == "ctf-reverse"
    assert "ctf-crypto" in result["secondary_categories"]


def test_remote_endpoint_alone_does_not_imply_pwn():
    assert classify(facts('Connect to this service', [], 'target.example:31337'))['primary_category']=='solve-challenge'
    assert classify(facts('Understand this binary', ['chall.elf'], 'target.example:31337'))['primary_category']=='ctf-reverse'


def test_short_signal_does_not_match_inside_words():
    assert 'ctf-misc' not in classify(facts('perform careful analysis', []))['scores']
