# 🎓 Comprehensive Viva Examination Guide
## Secure Multi-Branch Enterprise Network Using Site-to-Site IPsec VPN, ACLs, VLANs, and Redundant WAN Failover

**Academic Level:** Bachelor of Technology (BTech) — Computer Science & Engineering / Information Technology  
**Subject:** Computer Networks / Data Communications / Advanced Network Security  
**Laboratory Project Evaluation & Oral Defense**

---

## 📑 Table of Contents
1. [Project Objective & Problem Statement](#1-project-objective--problem-statement)
2. [Network Architecture & Device Roles](#2-network-architecture--device-roles)
3. [IP Addressing Scheme & VLSM Subnetting](#3-ip-addressing-scheme--vlsm-subnetting)
4. [VLANs, 802.1Q Trunking & Router-on-a-Stick (ROAS)](#4-vlans-8021q-trunking--router-on-a-stick-roas)
5. [Centralized DHCP Relay & DNS Resolution](#5-centralized-dhcp-relay--dns-resolution)
6. [IPsec Architecture: Phase 1 (IKE) & Phase 2 (IPsec SA)](#6-ipsec-architecture-phase-1-ike--phase-2-ipsec-sa)
7. [Interesting Traffic, Crypto ACLs & Transform Sets](#7-interesting-traffic-crypto-acls--transform-sets)
8. [Extended Access Control Lists (ACLs) & Zero-Trust Guest Isolation](#8-extended-access-control-lists-acls--zero-trust-guest-isolation)
9. [High Availability: Floating Static Routes & Dual-WAN Failover](#9-high-availability-floating-static-routes--dual-wan-failover)
10. [Spanning Tree Protocol (PVST+) & Layer 2 Loop Prevention](#10-spanning-tree-protocol-pvst--layer-2-loop-prevention)
11. [Enterprise Server Farm & Isolated DMZ](#11-enterprise-server-farm--isolated-dmz)
12. [Project Limitations & Future Enhancements](#12-project-limitations--future-enhancements)
13. [25 Essential Viva Questions & Concise Model Answers](#13-25-essential-viva-questions--concise-model-answers)

---

## 1. Project Objective & Problem Statement

### The Problem
Modern distributed enterprises have employees, branch offices, and guests who require access to corporate resources and the Internet. However:
- Transmitting raw corporate data over public Internet Service Provider (ISP) connections exposes sensitive data to packet sniffing, eavesdropping, and man-in-the-middle (MITM) attacks.
- A single WAN connection introduces a single point of failure (SPOF); a fiber cut or ISP outage halts enterprise operations.
- Flat internal LANs permit unauthorized lateral movement (e.g., guest laptops attacking database/file servers or sniffing finance records).
- Uncontrolled redundant switch uplinks cause broadcast storms, MAC table thrashing, and switch crashes.

### The Solution
This project implements an end-to-end, resilient, and compartmentalized enterprise network infrastructure in Cisco Packet Tracer:
1. **Confidentiality & Integrity:** Site-to-Site IPsec VPN tunnels between HQ and remote branches using AES-128 encryption and SHA-1 HMAC authentication.
2. **High Availability:** Dual-homed WAN connections with automatic floating static route failover and pre-emption.
3. **Segmentation & Defense-in-Depth:** Per-department VLANs, Router-on-a-Stick inter-VLAN routing, DMZ boundary filtering, and granular Extended ACLs enforcing strict guest isolation.
4. **Loop-Free Redundancy:** PVST+ spanning-tree hierarchy across primary and secondary distribution switches.

---

## 2. Network Architecture & Device Roles

The enterprise topology follows the classic **Cisco Hierarchical 3-Layer Design** (Core, Distribution, Access):

```
                       [ Primary ISP Router ] (203.0.113.0/30)
                                 |   \
   [ Backup ISP Router ] --------+    \
   (209.165.201.0/30)            |     \
         |                       |      \
    (Gi0/2 Backup)          (Gi0/1 Pri)  \
         \                      /         \
       +--------------------------+        +--------------------------+
       |        HQ-Router         |        |      Branch1-Router      |
       +--------------------------+        +--------------------------+
                    | (Gi0/0 Trunk)                     | (Gi0/0)
       +--------------------------+        +--------------------------+
       |   HQ-SW1 (Root Bridge)   |        |        Branch1-SW        |
       |  Priority: 4096 (PVST+)  |        +--------------------------+
       +--------------------------+                     |
            |   |   |   |   |                           |
  +---------+   |   |   |   +---------+        +------------------+
  |             |   |   |             |        | Corporate & Guest|
[Admin-SW]   [IT] [Fin] [Guest]   [Server-SW]  | Workstations     |
                                  & [DMZ-SW]   +------------------+
```

### Device Inventory & Functions
- **`HQ-Router` (Cisco 2911):** Enterprise edge gateway. Terminates dual WAN links, runs 802.1Q subinterfaces for ROAS, hosts IP helper-addresses, applies ingress ACL security filters, and manages crypto maps for both branches.
- **`Branch1-Router` & `Branch2-Router` (Cisco 2911):** Branch customer premises equipment (CPE) gateways. Provide local LAN default gateways, enforce local guest isolation ACLs, and terminate IPsec tunnels to HQ.
- **`ISP-Router` & `Backup-ISP` (Cisco 2911):** Independent public Internet Service Providers. Route public IPv4 transit traffic (`203.0.113.0/30`, `198.51.100.0/30`, `209.165.201.0/30`, `209.165.202.0/30`) without participating in customer routing or decryption.
- **`HQ-SW1` (Cisco Catalyst 2960-24TT):** Primary Distribution Switch. Configured with priority 4096 to act as the PVST+ Root Bridge for all enterprise VLANs.
- **`HQ-SW2` (Cisco Catalyst 2960-24TT):** Secondary Distribution Switch. Configured with priority 8192 as hot-standby Root Bridge.
- **Access Switches (`HQ-Admin-SW`, `HQ-IT-SW`, `HQ-Finance-SW`, `HQ-Guest-SW`, `HQ-Server-SW`, `DMZ-SW`, `Branch-SW`):** Layer 2 switches providing dedicated access ports for endpoints and dual 802.1Q uplinks to distribution switches.

---

## 3. IP Addressing Scheme & VLSM Subnetting

The enterprise utilizes RFC 1918 private IPv4 space for internal networks and RFC 5737 documentation space for public WAN interfaces:

| Network Domain | Subnet CIDR | Subnet Mask | Usable Range | Default Gateway | Purpose |
|---|---|---|---|---|---|
| **HQ Admin (VLAN 10)** | `192.168.10.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.10.1` | Corporate administration |
| **HQ IT (VLAN 20)** | `192.168.20.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.20.1` | Network & systems admins |
| **HQ Finance (VLAN 30)** | `192.168.30.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.30.1` | Accounting & payroll |
| **HQ Guest (VLAN 40)** | `192.168.40.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.40.1` | Untrusted visitor access |
| **DMZ Network (VLAN 50)** | `172.16.1.0/24` | `255.255.255.0` | `.2` – `.254` | `172.16.1.1` | Publicly exposed web server |
| **Server Farm (VLAN 100)** | `192.168.100.0/24` | `255.255.255.0` | `.31` – `.254` | `192.168.100.1` | DNS, DHCP, File Server |
| **Branch 1 LAN** | `192.168.50.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.50.1` | Regional office 1 hosts |
| **Branch 2 LAN** | `192.168.60.0/24` | `255.255.255.0` | `.11` – `.254` | `192.168.60.1` | Regional office 2 hosts |
| **Primary WAN (HQ ↔ ISP)** | `203.0.113.0/30` | `255.255.255.252` | `.1` – `.2` | `203.0.113.1` | Point-to-point Primary WAN |
| **Primary WAN (B1 ↔ ISP)** | `198.51.100.0/30` | `255.255.255.252` | `.1` – `.2` | `198.51.100.1` | Point-to-point Primary WAN |
| **Primary WAN (B2 ↔ ISP)** | `198.51.100.4/30` | `255.255.255.252` | `.5` – `.6` | `198.51.100.5` | Point-to-point Primary WAN |
| **Backup WAN (HQ ↔ ISP2)** | `209.165.201.0/30` | `255.255.255.252` | `.1` – `.2` | `209.165.201.1` | Point-to-point Backup WAN |
| **Backup WAN (B1 ↔ ISP2)** | `209.165.202.0/30` | `255.255.255.252` | `.1` – `.2` | `209.165.202.1` | Point-to-point Backup WAN |
| **Backup WAN (B2 ↔ ISP2)** | `209.165.202.4/30` | `255.255.255.252` | `.5` – `.6` | `209.165.202.5` | Point-to-point Backup WAN |

---

## 4. VLANs, 802.1Q Trunking & Router-on-a-Stick (ROAS)

### Virtual Local Area Networks (VLANs)
VLANs divide a single physical Layer 2 broadcast domain into multiple logical broadcast domains. In this project:
- VLAN 10 (Admin), VLAN 20 (IT), VLAN 30 (Finance), VLAN 40 (Guest), VLAN 50 (DMZ), VLAN 100 (Server Farm).
- Workstations inside VLAN 10 cannot receive broadcasts from VLAN 40, stopping ARP spoofing, broadcast floods, and unauthorized sniffing.

### IEEE 802.1Q Trunking
Trunk ports carry traffic from multiple VLANs across a single physical link by inserting a 4-byte 802.1Q tag into the Ethernet frame header (containing a 12-bit VLAN ID).
- Configured with `switchport mode trunk` and `switchport trunk allowed vlan 10,20,30,40,50,100`.

### Router-on-a-Stick (ROAS)
Instead of dedicating a separate physical router port to each VLAN (which would exhaust router interfaces), ROAS uses logical **subinterfaces** on a single physical GigabitEthernet link (`Gi0/0`):
```cisco
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.10
 description Administration VLAN 10
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
```
Frames arriving with 802.1Q tag 10 are stripped and routed by `Gi0/0.10`. Outbound frames have tag 10 inserted.

---

## 5. Centralized DHCP Relay & DNS Resolution

### DHCP Relay via `ip helper-address`
DHCP DISCOVER packets are broadcast (`255.255.255.255:67`). By definition, routers do NOT forward broadcast packets across subnets.
- Solution: Under each subinterface, the router is configured with:
  ```cisco
  ip helper-address 192.168.100.20
  ```
- How it works:
  1. PC broadcasts `DHCPDISCOVER`.
  2. `HQ-Router` subinterface intercepts the broadcast.
  3. The router converts the broadcast into a unicast packet (source: subinterface IP `192.168.10.1`, destination: `192.168.100.20`).
  4. The router populates the `giaddr` (Gateway IP Address) field in the DHCP header with `192.168.10.1`.
  5. The DHCP server inspects `giaddr`, identifies that the client resides on `192.168.10.0/24`, allocates an IP from `ADMIN_POOL`, and unicasts the `DHCPOFFER` back to the router.

### Domain Name System (DNS)
- `DNS-Server` operates at `192.168.100.10`.
- Authoritative A records:
  - `web.corp.local` & `enterprise.corp` → `172.16.1.10` (DMZ Web Server)
  - `fileserver.corp.local` → `192.168.100.30` (File Server)
  - `dns.corp.local` → `192.168.100.10`
  - `dhcp.corp.local` → `192.168.100.20`

---

## 6. IPsec Architecture: Phase 1 (IKE) & Phase 2 (IPsec SA)

IPsec operates in two distinct phases to provide authenticated, encrypted communication:

```
+-------------------------------------------------------------------------+
| Phase 1: IKE / ISAKMP (Internet Key Exchange)                           |
| Purpose: Authenticate peers and build a secure management channel.     |
| Protocol: UDP Port 500                                                  |
| Negotiation Suite:                                                      |
|   - Encryption: AES-128                                                 |
|   - Hash / Integrity: SHA-1                                             |
|   - Authentication: Pre-Shared Key ('ciscoVPN2026')                     |
|   - Diffie-Hellman: Group 2 (1024-bit key exchange)                     |
| Result State: QM_IDLE (Quick Mode Idle) - Tunnel management channel UP  |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
| Phase 2: IPsec SA (Security Association)                                |
| Purpose: Negotiate data channel security parameters for user payloads.  |
| Trigger: "Interesting traffic" matched by crypto ACL                    |
| Transform Set: esp-aes esp-sha-hmac                                     |
| Encapsulation: ESP (Encapsulating Security Payload - IP Protocol 50)    |
| Mode: Tunnel Mode (Original IP packet completely encrypted & wrapped)   |
| Result: Outbound/Inbound SPI pairs and active encrypt/decrypt counters   |
+-------------------------------------------------------------------------+
```

---

## 7. Interesting Traffic, Crypto ACLs & Transform Sets

### Crypto ACLs ("Interesting Traffic")
IPsec does not encrypt all traffic exiting an interface. It inspects egress packets against an access list:
- On `HQ-Router`:
  ```cisco
  access-list 101 permit ip 192.168.10.0 0.0.0.255 192.168.50.0 0.0.0.255
  access-list 101 permit ip 192.168.20.0 0.0.0.255 192.168.50.0 0.0.0.255
  access-list 101 permit ip 192.168.30.0 0.0.0.255 192.168.50.0 0.0.0.255
  access-list 101 permit ip 192.168.100.0 0.0.0.255 192.168.50.0 0.0.0.255
  ```
- On `Branch1-Router` (Mirrored):
  ```cisco
  access-list 101 permit ip 192.168.50.0 0.0.0.255 192.168.10.0 0.0.0.255
  ...
  access-list 101 permit ip 192.168.50.0 0.0.0.255 192.168.100.0 0.0.0.255
  ```
- **Why Mirroring is Mandatory:** If source and destination in Branch 1's ACL do not exactly invert HQ's ACL, Phase 2 Quick Mode SA negotiation fails (`proxy ID mismatch`).

### Transform Set & Crypto Map
- Transform set defines the cryptographic protocols:
  `crypto ipsec transform-set VPN-TS esp-aes esp-sha-hmac`
- Crypto map binds peer IP, transform-set, and matching ACL together, and is applied directly to the outgoing WAN interface:
  ```cisco
  crypto map VPN-MAP 10 ipsec-isakmp
   set peer 198.51.100.2
   set transform-set VPN-TS
   match address 101
  ```

---

## 8. Extended Access Control Lists (ACLs) & Zero-Trust Guest Isolation

Security policy is enforced at the earliest ingress point:

### HQ Guest Isolation (ACL 140 applied `in` on `Gi0/0.40`)
```cisco
access-list 140 permit udp 192.168.40.0 0.0.0.255 host 192.168.100.10 eq domain
access-list 140 permit tcp 192.168.40.0 0.0.0.255 host 172.16.1.10 eq www
access-list 140 permit icmp 192.168.40.0 0.0.0.255 host 172.16.1.10
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.10.0 0.0.0.255
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.20.0 0.0.0.255
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.30.0 0.0.0.255
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.100.0 0.0.0.255
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.50.0 0.0.0.255
access-list 140 deny ip 192.168.40.0 0.0.0.255 192.168.60.0 0.0.0.255
access-list 140 permit ip any any
```
- **Rules 10–30:** Permit DNS resolution to `.100.10` (UDP port 53 only, no other access) and HTTP/ICMP to DMZ Web Server (`172.16.1.10`).
- **Rules 40–90:** Explicitly drop any packets destined for corporate VLANs, server farm, or remote branch networks.
- **Rule 100:** Permit remaining traffic to the public Internet.

### Branch Guest Isolation (ACL 110 on `Branch1-Router` & `Branch2-Router`)
Applied on LAN interface `Gi0/0`:
- Blocks `192.168.50.50` from accessing any `192.168.x.x` subnet.
- Permits access to DMZ `172.16.1.0/24` and Internet.

---

## 9. High Availability: Floating Static Routes & Dual-WAN Failover

### Administrative Distance (AD)
Administrative Distance is the measure of trustworthiness of a routing information source in Cisco IOS (lower is preferred):
- Connected: 0
- Static: 1
- EIGRP: 90
- OSPF: 110
- RIP: 120

### Floating Static Route Design
HQ and branch routers maintain two default routes:
```cisco
ip route 0.0.0.0 0.0.0.0 203.0.113.1     ! Primary WAN (AD = 1)
ip route 0.0.0.0 0.0.0.0 209.165.201.1 10 ! Backup WAN (AD = 10, Floating)
```
1. **Normal State:** The primary route has AD 1 and is installed in the routing table. The AD 10 route "floats" invisibly in the configuration.
2. **Failure State:** If `Gi0/1` goes administratively down or carrier detect fails, the AD 1 route is flushed. The AD 10 route via `Backup-ISP` is immediately installed into the FIB.
3. **Restoration State:** When `Gi0/1` is restored, IOS compares AD 1 against AD 10, reinstalls the primary route, and evicts the backup route back to standby.

---

## 10. Spanning Tree Protocol (PVST+) & Layer 2 Loop Prevention

### The Danger: Switching Loops
Without STP, redundant links in Layer 2 networks create loops. Broadcast frames circulate indefinitely, saturating switch backplanes in a **broadcast storm**, and MAC address tables constantly rewrite (MAC flapping), crippling communication.

### PVST+ Implementation
Cisco Per-VLAN Spanning Tree Plus maintains an independent spanning tree instance for every VLAN.
- **Root Bridge Election Formula:** Lowest Bridge ID (BID = Priority + System ID Extension + MAC Address).
- **Configuration on `HQ-SW1` (Primary Root Bridge):**
  ```cisco
  spanning-tree mode pvst
  spanning-tree vlan 1,10,20,30,40,50,100 priority 4096
  ```
  Priority `4096` guarantees that `HQ-SW1` always wins against default switch priority `32768`.
- **Configuration on `HQ-SW2` (Secondary Root Bridge):**
  ```cisco
  spanning-tree vlan 1,10,20,30,40,50,100 priority 8192
  ```
- **Port Roles & States:**
  - `Root Port (FWD)`: Forwarding port with lowest cost path to root bridge.
  - `Designated Port (FWD)`: Forwarding port on a network segment.
  - `Alternate Port (BLK)`: Redundant port blocked from forwarding user frames; continuously listens to BPDUs to activate if the root port drops.

---

## 11. Enterprise Server Farm & Isolated DMZ

### Server Farm (VLAN 100)
Hosts internal business-critical infrastructure:
- `DNS-Server` (`192.168.100.10`): Translates corporate hostnames.
- `DHCP-Server` (`192.168.100.20`): Centralized address leasing.
- `File-Server` (`192.168.100.30`): Central repository for departments and branch offices over VPN.

### Demilitarized Zone (DMZ - VLAN 50)
The DMZ houses servers that must be accessed from untrusted networks (Internet, guest users) without granting those networks access to internal databases.
- Subnet: `172.16.1.0/24`
- Host: `DMZ-Web-Server` (`172.16.1.10`)
- Security Enforcement: ACL 150 on `Gi0/0.50` only permits established TCP connections (`established` keyword) and ICMP echo-replies originating from the server, forbidding the DMZ server from initiating new sessions into corporate subnets.

---

## 12. Project Limitations & Future Enhancements

| Current Project Scope | Real-World Production Enhancement |
|---|---|
| Static IPsec Site-to-Site Tunnels | Dynamic Multipoint VPN (DMVPN) with mGRE and NHRP for scalable spoke-to-spoke communication. |
| Floating Static Routes | Dynamic BGP peering with ISPs or IP SLA tracking with route track objects. |
| Classical PVST+ (30–50s convergence) | Rapid Per-VLAN Spanning Tree (RPVST+ / 802.1w) with sub-second convergence. |
| Pre-Shared Key (PSK) Authentication | Public Key Infrastructure (PKI) with X.509 digital certificates and CA server. |
| Cisco IOS Software Router ACLs | Next-Generation Firewall (NGFW) with Deep Packet Inspection (DPI) and IPS. |
| Single Core Router | First Hop Redundancy Protocols (HSRP/VRRP) on redundant gateway routers. |

---

## 13. 25 Essential Viva Questions & Concise Model Answers

### Q1: What is the main objective of this project?
**Answer:** To design and implement a secure, redundant multi-branch enterprise network providing encrypted inter-branch communication via IPsec VPN, high availability through dual-WAN failover, and internal policy enforcement using VLANs, ROAS, and Extended ACLs.

### Q2: What is the difference between a VLAN and a subnet?
**Answer:** A VLAN is a Layer 2 broadcast domain created on switches; a subnet is a Layer 3 logical network defined by IP addresses and subnet masks. Typically, one VLAN corresponds to one IP subnet.

### Q3: Why is 802.1Q trunking required between switches and routers?
**Answer:** A standard access port carries traffic for only one VLAN without tags. 802.1Q trunking inserts a 4-byte tag with a 12-bit VLAN ID into the Ethernet frame header, allowing multiple VLANs to traverse a single physical link.

### Q4: Explain how Router-on-a-Stick works.
**Answer:** A single physical router interface is divided into logical subinterfaces (e.g., `Gi0/0.10`, `Gi0/0.20`). Each subinterface is assigned an 802.1Q VLAN encapsulation tag and an IP address that acts as the default gateway for that VLAN.

### Q5: How does a host in VLAN 10 obtain an IP address from a DHCP server in VLAN 100?
**Answer:** The router subinterface `Gi0/0.10` uses `ip helper-address 192.168.100.20` to intercept the client's broadcast `DHCPDISCOVER`, converts it to a unicast packet with its own IP in the `giaddr` field, and forwards it to the DHCP server.

### Q6: What are the two phases of IPsec?
**Answer:** Phase 1 (IKE/ISAKMP) authenticates the router peers and establishes a secure management channel. Phase 2 (IPsec SA) negotiates encryption parameters for user payload data and creates the actual unidirectional data tunnels.

### Q7: What state indicates that IKE Phase 1 is successful?
**Answer:** `QM_IDLE` (Quick Mode Idle) with status `ACTIVE`, verified using `show crypto isakmp sa`.

### Q8: What is "interesting traffic" in IPsec terminology?
**Answer:** Traffic specified in a crypto access list that matches predetermined source and destination subnets, instructing the router to encrypt the payload and tunnel it rather than routing it normally in plaintext.

### Q9: Why must crypto ACLs be mirrored between VPN endpoints?
**Answer:** IPsec requires symmetric agreement on the identity of both endpoints during Phase 2 Quick Mode. If HQ specifies permit `A to B`, the branch must mirror it as permit `B to A`; otherwise, a proxy ID mismatch occurs and negotiation fails.

### Q10: What is the purpose of a Transform Set?
**Answer:** It defines the acceptable combination of security protocols, encryption algorithms, and authentication mechanisms (e.g., `esp-aes esp-sha-hmac`) that peers agree to use for Phase 2 data protection.

### Q11: What is the difference between ESP and AH in IPsec?
**Answer:** AH (Authentication Header, protocol 51) provides data integrity and authentication but no encryption (payload is plaintext). ESP (Encapsulating Security Payload, protocol 50) provides encryption, data confidentiality, integrity, and authentication.

### Q12: Why did we choose Tunnel Mode instead of Transport Mode for IPsec?
**Answer:** Transport mode encrypts only the payload and preserves the original IP header, making it unsuitable for routing private RFC 1918 traffic over the public Internet. Tunnel mode encrypts the entire original IP packet and wraps it in a new public routable IP header.

### Q13: What is a Floating Static Route?
**Answer:** A backup static route configured with a higher Administrative Distance than the primary route (e.g., AD 10 vs AD 1). It remains dormant until the primary route disappears from the routing table.

### Q14: How does HQ-Router failover to Backup-ISP when Primary ISP fails?
**Answer:** When the primary WAN interface `Gi0/1` goes down, the primary default route (AD 1) is withdrawn from the routing table. The floating static route pointing to `Backup-ISP` (AD 10) is immediately installed, routing traffic over `Gi0/2`.

### Q15: What is Administrative Distance (AD)?
**Answer:** A rating of trustworthiness from 0 to 255 assigned to routing sources in Cisco IOS. When multiple routes to the same destination exist, the route with the lowest AD is selected.

### Q16: Why is Spanning Tree Protocol (STP) necessary in the HQ distribution layer?
**Answer:** Because redundant physical links between `HQ-SW1`, `HQ-SW2`, and access switches create physical loops. Without STP, broadcast frames loop endlessly, causing broadcast storms and crashing the switches.

### Q17: How is the STP Root Bridge elected?
**Answer:** The switch with the lowest Bridge ID (BID = Priority + MAC address) becomes the Root Bridge. We forced `HQ-SW1` to win by assigning it priority `4096`, lower than all other switches.

### Q18: What are the STP port states in 802.1D?
**Answer:** Blocking, Listening, Learning, Forwarding, and Disabled.

### Q19: What is the difference between a Standard ACL and an Extended ACL?
**Answer:** Standard ACLs (numbered 1–99) filter traffic based solely on source IP address and should be placed close to the destination. Extended ACLs (numbered 100–199) filter based on source IP, destination IP, protocol (TCP/UDP/ICMP), and port numbers, and should be placed close to the source.

### Q20: Where is ACL 140 applied and what does it achieve?
**Answer:** Applied inbound on `HQ-Router` subinterface `Gi0/0.40`. It permits guest hosts to perform DNS lookups and browse the DMZ Web Server, but strictly denies all access to private corporate subnets and server farm resources.

### Q21: What is a DMZ and why is it separated from the internal LAN?
**Answer:** A Demilitarized Zone is an isolated subnet for publicly accessible services. It prevents external users from directly contacting private internal corporate subnets and prevents an exploited web server from attacking the enterprise core.

### Q22: What does the command `show crypto ipsec sa` verify?
**Answer:** It displays active Phase 2 Security Associations, showing the inbound and outbound Security Parameter Index (SPI), local/remote proxy IDs, and live counters for `#pkts encaps`, `#pkts encrypt`, and `#pkts decrypt`.

### Q23: Why do we exclude IP addresses in DHCP pools?
**Answer:** Using `ip dhcp excluded-address` prevents the DHCP server from dynamically assigning static infrastructure addresses (default gateways, server IPs, network printers), avoiding IP address collisions.

### Q24: What command checks the live status of STP on a switch?
**Answer:** `show spanning-tree` or `show spanning-tree vlan <id>`, which details the Root ID, Bridge ID, interface roles (Root, Desg, Altn), and states (FWD, BLK).

### Q25: How would you scale this design to 50 branch offices?
**Answer:** Replacing point-to-point static IPsec crypto maps with Dynamic Multipoint VPN (DMVPN) using Multipoint GRE (mGRE) and Next Hop Resolution Protocol (NHRP), coupled with dynamic routing like OSPF or BGP, eliminating the need to manually configure static crypto maps on the hub.
