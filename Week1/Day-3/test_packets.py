#!/usr/bin/env python3
"""
test_packets.py

This script generates test traffic using Scapy to simulate network activity that Snort can detect.
It sends SYN packets to a range of TCP ports on a target host to mimic a port scan.
"""

from scapy.all import IP, TCP, send
from typing import List

# Target IP to test
TARGET_IP: str = "10.0.2.15"

# List of TCP ports to scan (can be adjusted)
PORTS_TO_SCAN: List[int] = [21, 22, 23, 25, 80, 443, 8080]

def generate_syn_packets(target_ip: str, ports: List[int]) -> None:
    """
    Generate SYN packets for each port in the list.

    Args:
        target_ip (str): IP address of the target machine
        ports (List[int]): List of TCP ports to send SYN packets to
    """
    for port in ports:
        packet = IP(dst=target_ip)/TCP(dport=port, flags="S")  # SYN packet
        send(packet, verbose=True)
        print(f"[+] Sent SYN packet to {target_ip}:{port}")

if __name__ == "__main__":
    generate_syn_packets(TARGET_IP, PORTS_TO_SCAN)
