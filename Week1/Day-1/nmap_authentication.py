import nmap
import datetime


target_ip = input("Enter target IP address: ")

nm = nmap.PortScanner()
scan_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
nm.scan(target_ip, arguments='-sS')


host = nm[target_ip]
open_ports = []
for proto in host.all_protocols():
    lport = host[proto].keys()
    for port in lport:
        service = host[proto][port]['name']
        version = host[proto][port].get('version', 'Unknown')
        open_ports.append({'port': port, 'service': service, 'version': version})

with open("scan_report.txt", "w") as f:
    f.write(f"Scan Time: {scan_time}\n")
    f.write(f"Target IP: {target_ip}\n")
    f.write("Open Ports and Services:\n")
    f.write("Port\tService\tVersion\n")
    for entry in open_ports:
        f.write(f"{entry['port']}\t{entry['service']}\t{entry['version']}\n")
    f.write("Scan complete.\n")
print("Scan complete. Results saved to scan_report.txt.")
