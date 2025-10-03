from scapy.all import sniff, IP, TCP, ICMP, Raw

def packet_callback(packet):
    if packet.haslayer(ICMP):
        payload_len = len(packet[ICMP].payload)
        print(f"[ICMP] {packet[IP].src} → {packet[IP].dst} Type={packet[ICMP].type} Payload={payload_len} bytes")
    elif packet.haslayer(TCP):
        payload_len = len(packet[TCP].payload)
        print(f"[TCP] {packet[IP].src}:{packet[TCP].sport} → {packet[IP].dst}:{packet[TCP].dport} "
              f"Flags={packet[TCP].flags} Payload={payload_len} bytes")

# Capture packets on eth0 continuously
sniff(iface="eth0", prn=packet_callback)
