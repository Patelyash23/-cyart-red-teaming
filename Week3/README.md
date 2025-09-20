# CYART Red Teaming - Week 3

## Project Overview
This repository contains artefacts, scripts, logs, and documentation related to Week 3 of the CYART Red Teaming Practical Course. The focus was on reconnaissance, service enumeration, and controlled phishing simulation in a contained Kali Linux lab environment.

## Objectives
- Perform passive and active reconnaissance (OSINT) against a demo target.
- Conduct web and network service enumeration.
- Setup and execute a phishing campaign using GoPhish and MailHog.
- Document the entire workflow and produce a submission-ready report.

## Repository Structure
Week3/

├─ docs/ # Final report documents (Word, PDF)

├─ tools/ # Raw command outputs, JSON, scripts

├─ screenshots/ # Captured screenshots for the report

├─ scripts/ # Scripts used in phishing simulation and enumeration

└─ workflow/ # Step-by-step instructions and checklists

## Usage / Workflow

### 1. Reconnaissance (Passive & Active)
- Use tools like `amass`, `subfinder`, `nmap`, `gobuster`, `nikto` to gather information.
- Example commands:
amass enum -passive -d target.com
nmap -sV target.com
gobuster dir -u http://target.com
nikto -h http://target.com

text

### 2. Phishing Lab Setup
- Start services:
sudo systemctl start gophish
sudo docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog

text
- Create SMTP profiles, templates, and campaigns using GoPhish UI or API.

### 3. Campaign Execution & Monitoring
- Launch the phishing campaign through GoPhish.
- Monitor incoming emails via MailHog UI.
- Export captured messages:
curl -s http://127.0.0.1:8025/api/v2/messages > tools/mailhog_messages.json

text

### 4. Post-Phishing Reporting
- Collect artifacts and screenshots.
- Finalize the report document in `docs/`.

## Contributing
Feel free to submit bug reports or improvements.

## License
Specify your license here.
