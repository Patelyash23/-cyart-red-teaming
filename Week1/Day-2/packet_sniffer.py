from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP, ICMP
import matplotlib.pyplot as plt
from collections import Counter


packets = sniff(count=100, iface="eth0")  



protocols = []

for pkt in packets:
    if IP in pkt:
        if TCP in pkt:
            protocols.append("TCP")
        elif UDP in pkt:
            protocols.append("UDP")
        elif ICMP in pkt:
            protocols.append("ICMP")
        else:
            protocols.append("Other")


count = Counter(protocols)
print("Captured Protocols:", count)


plt.bar(count.keys(), count.values())
plt.xlabel("Protocols")
plt.ylabel("Count")
plt.title("Protocol Distribution of Captured Packets")
plt.savefig("protocol_distribution.png")
plt.show()
