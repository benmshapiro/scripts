# Network Scripts

Utility scripts for DNS migration and controller provisioning. Output is staged conservatively — review before applying.

---

## gen_cnames.py

Generates commented BIND CNAME records for migrating static printer A records to DDNS-based CNAMEs, keyed on the last 2 octets of each host's MAC address. Output is printed to stdout for review and manual pasting into the target zone file.

### Usage

```bash
python3 gen_cnames.py <dhcp-file> <arp-file> <zone-file> <target-zone>
```

| Argument | Description |
|---|---|
| `dhcp-file` | ISC dhcpd config with `hardware ethernet` / `fixed-address` reservations |
| `arp-file` | Juniper `show arp no-resolve interface irb.X` output |
| `zone-file` | BIND zone file excerpt with the A records to migrate |
| `target-zone` | DDNS target zone FQDN with trailing dot (e.g. `printers.example.com.`) |

```bash
python3 gen_cnames.py dhcp-reservations.txt arp-table.txt zone-excerpt.txt printers.example.com.
```

### Output

```dns
; CNAME → DDNS migration
; Generated: 2026-06-11
; MAC suffix = last 2 octets, colons stripped, lowercase

;prt-example-1           CNAME   800a.printers.example.com.
;prt-example-2           CNAME   de2d.printers.example.com.
;prt-example-3           CNAME   469f.printers.example.com.  ; ⚠ not in ARP table
; ⚠ some-other-host (10.0.0.1) — no MAC found in DHCP, skipping
```

Records are commented out with `;` for safe staging. Remove the leading `;` on each record when cutting over. Output order follows zone file order. Join key is IP address — DHCP and DNS hostnames do not need to match.

---

## unifi_controller_install.sh

Installs the UniFi Network Controller on Debian/Ubuntu via APT. Adds the Ubiquiti and MongoDB 3.4 repositories, pins the Java 11 runtime for compatibility, installs the `unifi` package, and confirms service status.

### Usage

```bash
sudo bash unifi_controller_install.sh
```

No arguments. Run as a user with `sudo` privileges on a supported Debian or Ubuntu host.

### What it does

| Step | Action |
|---|---|
| Base packages | Installs `ca-certificates`, `apt-transport-https`, `openjdk-11-jre-headless` |
| Ubiquiti repo | Adds `https://www.ui.com/downloads/unifi/debian stable ubiquiti` |
| MongoDB repo | Adds MongoDB 3.4 from `repo.mongodb.org` (Ubuntu Xenial multiverse) |
| Repo trust | Imports GPG keys for both Ubiquiti and MongoDB sources |
| Java pin | Holds `openjdk-11-*` at installed version to prevent compatibility breakage on upgrades |
| Install | Runs `apt-get install unifi -y` |
| Verify | Prints `service unifi status` output |

### Notes

- Targets Ubuntu/Debian. Tested against distributions where `openjdk-11-jre-headless` is available in the default repos.
- MongoDB 3.4 EOL — required by older UniFi controller versions. Upgrade the repo pin alongside any controller major-version bump.
- Reference: [UI documentation — Install and Update via APT](https://help.ui.com/hc/en-us/articles/220066768-UniFi-How-to-Install-and-Update-via-APT-on-Debian-or-Ubuntu)
