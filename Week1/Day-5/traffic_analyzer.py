
from __future__ import annotations
from scapy.all import rdpcap, DNSQR, IP, IPv6, TCP, UDP, Ether
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
from typing import Dict, Tuple, List
import math
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

def safe_ip(pkt) -> str | None:
    if IP in pkt:
        return pkt[IP].src, pkt[IP].dst
    if IPv6 in pkt:
        return pkt[IPv6].src, pkt[IPv6].dst
    return None

def proto_name(pkt) -> str:
    if TCP in pkt: return "TCP"
    if UDP in pkt: return "UDP"
    if ICMP in pkt or getattr(pkt, 'proto', None) == 1: return "ICMP"
    if IP in pkt or IPv6 in pkt: return "IP"
    return "Ethernet"

try:
    from scapy.layers.inet import ICMP
except Exception:
    ICMP = object  # placeholder

def analyze_pcap(file_path: str) -> pd.DataFrame:
    packets = rdpcap(file_path)

    rows = []
    talker_bytes: Dict[str, int] = defaultdict(int)
    proto_counts: Dict[str, int] = defaultdict(int)

    dns_minute_counts: Dict[str, int] = defaultdict(int)
    dns_queries: List[Tuple[float, str]] = []  # (epoch, qname)

    for i, pkt in enumerate(packets, start=1):
        length = int(len(pkt))
        src, dst = None, None
        proto = "Ethernet"

        if Ether in pkt:
            src_mac = pkt[Ether].src
            dst_mac = pkt[Ether].dst
        else:
            src_mac = dst_mac = ""

        if IP in pkt or IPv6 in pkt:
            ips = safe_ip(pkt)
            if ips:
                src, dst = ips
            proto = proto_name(pkt)

        # track talker bytes (count per endpoint)
        if src:
            talker_bytes[src] += length
        if dst:
            talker_bytes[dst] += 0  # keep key stable, don’t double-count outbound

        # track protocol counts
        proto_counts[proto] += 1

        # DNS tracking (UDP/53 or TCP/53 with DNS layer)
        try:
            if UDP in pkt and (pkt[UDP].sport == 53 or pkt[UDP].dport == 53):
                if pkt.haslayer(DNSQR):
                    q = pkt[DNSQR].qname.decode(errors="ignore").rstrip(".")
                    ts = float(pkt.time)
                    minute_key = pd.to_datetime(ts, unit='s').strftime('%Y-%m-%d %H:%M')
                    dns_minute_counts[minute_key] += 1
                    dns_queries.append((ts, q))
            elif TCP in pkt and (pkt[TCP].sport == 53 or pkt[TCP].dport == 53):
                if pkt.haslayer(DNSQR):
                    q = pkt[DNSQR].qname.decode(errors="ignore").rstrip(".")
                    ts = float(pkt.time)
                    minute_key = pd.to_datetime(ts, unit='s').strftime('%Y-%m-%d %H:%M')
                    dns_minute_counts[minute_key] += 1
                    dns_queries.append((ts, q))
        except Exception:
            pass

        rows.append({
            "No.": i,
            "SrcMAC": src_mac,
            "DstMAC": dst_mac,
            "Src": src if src else "",
            "Dst": dst if dst else "",
            "Protocol": proto,
            "Length": length
        })

    df = pd.DataFrame(rows)

    # Save all-packet metadata
    df.to_csv("packet_metadata.csv", index=False)
    print("Packet metadata saved to packet_metadata.csv")

    # Top talkers (by bytes)
    df_talkers = pd.DataFrame(
        [{"IP": ip, "Bytes": b} for ip, b in sorted(talker_bytes.items(), key=lambda x: x[1], reverse=True)]
    )
    df_talkers.to_csv("top_talkers.csv", index=False)
    print("Top talkers saved to top_talkers.csv")

    # Protocol breakdown
    df_proto = pd.DataFrame([{"Protocol": k, "Count": v} for k, v in proto_counts.items()]).sort_values(
        "Count", ascending=False)
    df_proto.to_csv("protocol_breakdown.csv", index=False)
    print("Protocol breakdown saved to protocol_breakdown.csv")

    # DNS timeseries
    if dns_minute_counts:
        df_dns = (pd.DataFrame([{"Minute": k, "Queries": v} for k, v in dns_minute_counts.items()])
                  .sort_values("Minute"))
        df_dns.to_csv("dns_timeseries.csv", index=False)
        print("DNS timeseries saved to dns_timeseries.csv")

        # Spike detection: spike if > mean + 2*std (and >= 10 queries)
        mean_q = df_dns["Queries"].mean()
        std_q = df_dns["Queries"].std(ddof=0)
        threshold = max(10, mean_q + 2 * std_q)
        spikes = df_dns[df_dns["Queries"] >= threshold]

        with open("dns_spike_report.txt", "w") as f:
            f.write(f"Spike threshold: {threshold:.2f} queries/min (mean={mean_q:.2f}, std={std_q:.2f})\n")
            if spikes.empty:
                f.write("No DNS spikes detected.\n")
            else:
                f.write("DNS spikes:\n")
                for _, r in spikes.iterrows():
                    f.write(f"- {r['Minute']} -> {r['Queries']} queries\n")
        print("DNS spike report saved to dns_spike_report.txt")
    else:
        print("No DNS queries observed.")

    # Charts
    # 1) Packet size distribution
    plt.figure()
    df["Length"].plot(kind="hist", bins=30, title="Packet Size Distribution")
    plt.xlabel("Packet length (bytes)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig("packet_size_distribution.png", dpi=120)
    print("Packet size distribution chart saved to packet_size_distribution.png")

    # 2) Protocol breakdown
    if not df_proto.empty:
        plt.figure()
        plt.bar(df_proto["Protocol"], df_proto["Count"])
        plt.title("Protocol Breakdown")
        plt.xlabel("Protocol")
        plt.ylabel("Packets")
        plt.tight_layout()
        plt.savefig("protocol_breakdown.png", dpi=120)
        print("Protocol breakdown chart saved to protocol_breakdown.png")

    # 3) Top talkers (top 10)
    if not df_talkers.empty:
        head = df_talkers.head(10)
        plt.figure()
        plt.bar(head["IP"].astype(str), head["Bytes"])
        plt.title("Top Talkers (Bytes)")
        plt.xlabel("IP")
        plt.ylabel("Total bytes (approx.)")
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig("top_talkers.png", dpi=120)
        print("Top talkers chart saved to top_talkers.png")

    # 4) DNS queries per minute
    if dns_minute_counts:
        df_dns = pd.read_csv("dns_timeseries.csv")
        plt.figure()
        plt.plot(pd.to_datetime(df_dns["Minute"]), df_dns["Queries"])
        plt.title("DNS Queries per Minute")
        plt.xlabel("Time")
        plt.ylabel("Queries")
        plt.tight_layout()
        plt.savefig("dns_queries_per_minute.png", dpi=120)
        print("DNS queries per minute chart saved to dns_queries_per_minute.png")

    # Console: Top 5 largest packets
    if not df.empty:
        print("\nTop 5 largest packets:")
        print(df.sort_values("Length", ascending=False)[["No.", "Src", "Dst", "Protocol", "Length"]].head(5))

    return df

if __name__ == "__main__":
    import sys
    pcap = sys.argv[1] if len(sys.argv) > 1 else "traffic_10min.pcap"
    analyze_pcap(pcap)
