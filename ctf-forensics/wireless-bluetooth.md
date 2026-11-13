# Wireless, Bluetooth and RF captures

Analyze passively from supplied captures unless the challenge explicitly assigns a radio/network target.

## Identify the layer

- 802.11: monitor-mode PCAP, radiotap headers, channel, encryption (open/WEP/WPA/WPA2/WPA3), management vs data frames.
- Bluetooth Classic: RFCOMM/L2CAP, pairing/bonding, SDP, HID, OBEX.
- BLE: advertising vs connection events, GATT handles, ATT opcodes, pairing/encryption, link-layer AA/CRC.
- Zigbee/802.15.4: PAN ID, channel, addressing, APS/ZCL payloads.
- Sub-GHz/ISM: modulation, symbol rate, framing, preamble/sync, CRC; use IQ captures when available.
- Custom RF: sample rate, center frequency, IQ format, pulse shaping, differential encoding.

## Cheap discriminators

```bash
tshark -r capture.pcapng -Y "wlan.fc.type_subtype == 0x08" -T fields -e wlan.ssid -e wlan.bssid
tshark -r capture.pcapng -Y "btatt" -T fields -e btatt.handle -e btatt.value
tshark -r capture.pcapng -Y "zbee_aps" -T fields -e zbee_aps.dst_endpoint -e zbee_aps.payload
```

For IQ files, estimate the sample rate and center frequency from metadata/filename/challenge text, plot the spectrogram, and test the simplest demodulator (ASK/OOK, FSK/GFSK, PSK) before a full receiver.

## Decode order

1. Preserve the capture and hash it.
2. Extract the protocol hierarchy and a small set of relevant fields.
3. Reassemble fragmented payloads and pair directions by address/sequence.
4. Identify encryption and recover keys from supplied material, known plaintext or a challenge-specific weakness.
5. Decode the application layer only after the link layer is consistent.
6. Verify the payload length/checksum and round-trip a sample.

## Common traps

- Wrong channel or missing radiotap metadata.
- BLE connection events split across multiple captures.
- RF captures with a frequency offset or inverted IQ.
- Whitening/scrambling applied before FEC.
- Payload split across USB/HID reports or Bluetooth frames.
- Timestamps in a different timezone/clock domain.

## Verification

A decoded message is a candidate. Verify against a second frame, a checksum, a known header, or the challenge checker. Report the layer-by-layer decode and the tool/version used.
