# 🎓 Live Project Demonstration Guide
## Secure Multi-Branch Enterprise Network Using Site-to-Site IPsec VPN, ACLs, VLANs, and Redundant WAN Failover

**Target Audience:** College Professor / External Examiner / Evaluators  
**Student Presenter:** BTech Computer Science & Engineering / Computer Networks  
**Project Topology File:** `Secure_MultiBranch_Enterprise_Network_Final.pkt`  
**Software Required:** Cisco Packet Tracer (v8.0+ / v9.0.1+)

---

## 📋 Demonstration Overview & Preparation Checklist

Before the examiner calls your name:
1. Open Cisco Packet Tracer.
2. Open `Secure_MultiBranch_Enterprise_Network_Final.pkt`.
3. Ensure simulation time has settled for 30–45 seconds so Spanning Tree (PVST+) transitions from Listening/Learning to Forwarding (all link lights turn green or amber for blocked ports).
4. Keep this guide open on your phone, second screen, or printed notes.
5. In Packet Tracer, open the following device windows as tabs so you can switch instantly without searching:
   - `Admin-PC1` (Desktop → Command Prompt)
   - `Guest-PC1` (Desktop → Command Prompt & Desktop → Web Browser)
   - `Branch1-Guest-PC` (Desktop → Command Prompt)
   - `HQ-Router` (CLI tab)
   - `HQ-SW1` & `HQ-Admin-SW` (CLI tabs)

---

## 🚀 Stage 1 — Network Architecture & Enterprise Overview

### Objective
Present the big-picture view of the enterprise topology, business rationale, and physical/logical layout.

### Action in Packet Tracer
- Maximize the Packet Tracer window showing the entire logical workspace.
- Point with your mouse or laser pointer to each zone:
  1. **Headquarters (HQ) Core & Access:** Top and left center.
  2. **HQ Server Farm (VLAN 100):** Bottom left (`DNS-Server`, `DHCP-Server`, `File-Server`).
  3. **Demilitarized Zone (DMZ - VLAN 50):** Bottom center (`DMZ-Web-Server`).
  4. **Dual WAN Providers:**
     - **Primary ISP (`ISP-Router`):** Top center (`203.0.113.0/30`, `198.51.100.0/30`, `198.51.100.4/30`).
     - **Secondary ISP (`Backup-ISP`):** Below primary ISP (`209.165.201.0/30`, `209.165.202.0/30`, `209.165.202.4/30`).
  5. **Branch Office 1:** Middle right (`Branch1-Router`, `Branch1-SW`, PCs).
  6. **Branch Office 2:** Bottom right (`Branch2-Router`, `Branch2-SW`, PCs).

### What to Explain to Your Professor
> *"Respected Professor, this project simulates a geographically dispersed corporate enterprise comprising a Headquarters and two remote regional branch offices connected across untrusted public service provider networks.*
>
> *Key design highlights:*
> 1. *Internal Network Segmentation:* HQ is divided into four departmental VLANs (Admin, IT, Finance, Guest) plus a dedicated Server Farm and an isolated DMZ, routed using Router-on-a-Stick dot1Q subinterfaces on `HQ-Router`.*
> 2. *Distribution Layer Redundancy:* HQ uses dual distribution switches (`HQ-SW1` and `HQ-SW2`) running PVST+ where `HQ-SW1` is hardcoded as Primary Root Bridge (priority 4096) and `HQ-SW2` as Secondary Root Bridge (priority 8192).*
> 3. *Confidential Inter-Branch Connectivity:* All branch-to-HQ communications traverse dynamic Site-to-Site IPsec VPN tunnels with AES-128 encryption and SHA-1 HMAC integrity over public IPv4 WAN blocks.*
> 4. *High Availability WAN:* HQ and both branches maintain dual homed uplinks. The primary WAN route operates at Administrative Distance 1, while a floating static route at AD 10 guarantees seamless failover to Backup-ISP if the primary link is severed."*

---

## 🏢 Stage 2 — Departmental Network & Core Services

### Objective
Show departmental VLAN segmentation, Router-on-a-Stick inter-VLAN routing, centralized DHCP address leasing via `ip helper-address`, and DNS resolution.

### Step 2.1: Verify Dynamic DHCP Allocation
1. **Device to Open:** `Admin-PC1`
2. **Action / Command:**
   - Click `Admin-PC1` → **Desktop** → **Command Prompt**.
   - Execute:
     ```cmd
     ipconfig /renew
     ```
3. **Expected Output:**
   ```
   FastEthernet0 Connection:(default port)
      IP Address......................: 192.168.10.11
      Subnet Mask.....................: 255.255.255.0
      Default Gateway.................: 192.168.10.1
      DNS Server......................: 192.168.100.10
   ```
4. **Repeat for Guest:**
   - Click `Guest-PC1` → **Desktop** → **Command Prompt**.
   - Execute `ipconfig /renew`.
   - Result: Assigned `192.168.40.11`, Gateway `192.168.40.1`, DNS `192.168.100.10`.

### Step 2.2: Inter-VLAN Authorized Communication
1. **Device:** `Admin-PC1` (VLAN 10: `192.168.10.11`)
2. **Commands:**
   ```cmd
   ping 192.168.20.11
   ping 192.168.30.11
   ```
3. **Expected Output:**
   ```
   Pinging 192.168.20.11 with 32 bytes of data:
   Reply from 192.168.20.11: bytes=32 time<1ms TTL=127
   Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)

   Pinging 192.168.30.11 with 32 bytes of data:
   Reply from 192.168.30.11: bytes=32 time<1ms TTL=127
   Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
   ```

### Step 2.3: DNS Domain Name Resolution
1. **Device:** `Admin-PC1`
2. **Commands:**
   ```cmd
   nslookup web.corp.local
   nslookup enterprise.corp
   nslookup fileserver.corp.local
   ```
3. **Expected Output:**
   ```
   Server: [192.168.100.10]
   Address: 192.168.100.10

   Non-authoritative answer:
   Name: web.corp.local
   Address: 172.16.1.10

   Name: enterprise.corp
   Address: 172.16.1.10

   Name: fileserver.corp.local
   Address: 192.168.100.30
   ```

### What to Explain to Your Professor
> *"Here we demonstrate that 802.1Q trunking and subinterface routing are operating on `HQ-Router`. When `Admin-PC1` issues a DHCP broadcast (DISCOVER), the router's subinterface `Gi0/0.10` catches the broadcast and, via `ip helper-address 192.168.100.20`, unicasts it to the server subnet. The PC receives an IP lease, gateway, and corporate DNS pointer. DNS resolution translates both internal hostnames (`web.corp.local`, `enterprise.corp`) to the DMZ web server without hardcoded host IP entry."*

---

## 🖥️ Stage 3 — Server Farm & DMZ Web Services

### Objective
Demonstrate authenticated access to the internal File Server and accessibility of the DMZ Web Server via both IP and DNS.

### Step 3.1: File Server Connectivity
1. **Device:** `Admin-PC1`
2. **Command:**
   ```cmd
   ping 192.168.100.30
   ```
3. **Expected Output:**
   ```
   Reply from 192.168.100.30: bytes=32 time<1ms TTL=127
   Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
   ```

### Step 3.2: DMZ Web Server GUI Access
1. **Device:** `Admin-PC1` (or `Guest-PC1`)
2. **Action:**
   - Click **Desktop** → **Web Browser**.
   - In the URL field, type:
     ```
     http://web.corp.local
     ```
     *(or `http://enterprise.corp` or `http://172.16.1.10`)*
   - Click **Go**.
3. **Expected Output:**
   - The Packet Tracer default Cisco/Enterprise web page renders immediately with *"Welcome to Cisco Packet Tracer"* or company portal banner.

### What to Explain to Your Professor
> *"Notice that the DMZ sits on an isolated subnet `172.16.1.0/24` with dedicated ingress access-group 150 on `Gi0/0.50`. Unlike private corporate subnets, the DMZ Web Server is reachable by both corporate workstations and external/guest users, while ACL 150 strictly blocks the DMZ server from initiating inbound connections back into corporate VLANs, thwarting pivot attacks if compromised."*

---

## 🔒 Stage 4 — Site-to-Site IPsec VPN Demonstration

### Objective
Demonstrate encrypted inter-branch communication across public WANs, trigger IKE Phase 1/Phase 2 negotiation, and inspect cryptographic Security Associations (SAs).

### Step 4.1: Generate "Interesting Traffic"
1. **Device:** `Admin-PC1` (`192.168.10.11`)
2. **Commands:**
   ```cmd
   ping 192.168.50.11
   ping 192.168.60.11
   ```
3. **Expected Output:**
   - If SAs were idle, the very first packet may show `Request timed out` during IKE key negotiation; the subsequent 3 packets reply with `TTL=126` (decremented by 2 router hops: HQ-Router and Branch-Router).
   - Running the ping a second time yields:
     ```
     Reply from 192.168.50.11: bytes=32 time<1ms TTL=126
     Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
     ```

### Step 4.2: Inspect IKE Phase 1 State (ISAKMP SA)
1. **Device:** `HQ-Router`
2. **Action:** Click **CLI** tab.
3. **Commands:**
   ```cisco
   enable
   show crypto isakmp sa
   ```
4. **Expected Output:**
   ```
   HQ-Router#show crypto isakmp sa
   IPv4 Crypto ISAKMP SA
   dst             src             state          conn-id slot status
   198.51.100.2    203.0.113.2     QM_IDLE           1076    0 ACTIVE
   198.51.100.6    203.0.113.2     QM_IDLE           1067    0 ACTIVE
   ```
5. **Key Observation:**
   - Both remote Branch 1 (`198.51.100.2`) and Branch 2 (`198.51.100.6`) peers display state **`QM_IDLE`** and status **`ACTIVE`**.

### Step 4.3: Inspect IKE Phase 2 IPsec Security Associations & Encryption Counters
1. **Device:** `HQ-Router`
2. **Command:**
   ```cisco
   show crypto ipsec sa
   ```
3. **Expected Output:**
   ```
   interface: GigabitEthernet0/1
       Crypto map tag: VPN-MAP, local addr 203.0.113.2
      protected vrf: (none)
      local  ident (addr/mask/prot/port): (192.168.10.0/255.255.255.0/0/0)
      remote ident (addr/mask/prot/port): (192.168.50.0/255.255.255.0/0/0)
      current_peer 198.51.100.2 port 500
       PERMIT, flags={origin_is_acl,}
      #pkts encaps: 26, #pkts encrypt: 26, #pkts digest: 0
      #pkts decaps: 32, #pkts decrypt: 32, #pkts verify: 0
   ```
4. **Cross-Check on `Branch1-Router`:**
   - Open `Branch1-Router` CLI → `show crypto ipsec sa`.
   - Point out that `#pkts encaps` on HQ matches `#pkts decaps` on Branch 1, and the outbound SPI on HQ matches the inbound SPI on Branch 1.

### What to Explain to Your Professor
> *"Professor, this verifies real hardware-level cryptographic tunneling. When traffic matches crypto ACL 101 ('interesting traffic'), the router triggers IKE Phase 1 using ISAKMP Policy 10 (AES-128, Pre-shared Key `ciscoVPN2026`, Diffie-Hellman Group 2). Upon reaching `QM_IDLE`, Phase 2 negotiates the IPsec transform-set (`esp-aes esp-sha-hmac`).*
>
> *As seen here, every ping incremented `#pkts encrypt` and `#pkts decrypt`. The public transit ISP routers (`ISP-Router`) only see ESP (IP protocol 50) packets and have no visibility into the encapsulated private payloads."*

---

## 🛡️ Stage 5 — Enterprise Security & Guest Isolation

### Objective
Demonstrate that the Extended Access Control Lists (ACLs) enforce the zero-trust departmental and guest security policy across HQ, Branch 1, and Branch 2.

### Step 5.1: Test HQ Guest Isolation
1. **Device:** `Guest-PC1` (`192.168.40.11`)
2. **Action / Commands:**
   ```cmd
   ping 192.168.10.11
   ping 192.168.100.30
   ping 172.16.1.10
   ```
3. **Expected Output:**
   - Attempting to ping `Admin-PC1` (`192.168.10.11`):
     ```
     Reply from 192.168.40.1: Destination host unreachable.
     Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
     ```
   - Attempting to ping `File-Server` (`192.168.100.30`):
     ```
     Reply from 192.168.40.1: Destination host unreachable.
     Packets: Sent = 4, Received = 0, Lost = 4 (100% loss)
     ```
   - Attempting to ping `DMZ-Web-Server` (`172.16.1.10`):
     ```
     Reply from 172.16.1.10: bytes=32 time<1ms TTL=127
     Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
     ```

### Step 5.2: Test Branch 1 & Branch 2 Guest Isolation
1. **Device:** `Branch1-Guest-PC` (`192.168.50.50`)
2. **Commands:**
   ```cmd
   ping 192.168.10.11
   ping 172.16.1.10
   ```
3. **Expected Output:**
   - `ping 192.168.10.11` → `Reply from 192.168.50.1: Destination host unreachable` (**BLOCKED**)
   - `ping 172.16.1.10` → 4/4 replies received (**PERMITTED**)
4. **Device:** `Branch2-Guest-PC` (`192.168.60.50`)
   - Repeat the pings: corporate LAN is blocked; DMZ is permitted.

### Step 5.3: Verify Live ACL Match Counters on Routers
1. **Device:** `HQ-Router` CLI
2. **Command:**
   ```cisco
   show access-lists 140
   ```
3. **Expected Output:**
   ```
   Extended IP access list 140
       10 permit udp 192.168.40.0 0.0.0.255 host 192.168.100.10 eq domain (1 match(es))
       20 permit tcp 192.168.40.0 0.0.0.255 host 172.16.1.10 eq www
       30 permit icmp 192.168.40.0 0.0.0.255 host 172.16.1.10 (8 match(es))
       40 deny ip 192.168.40.0 0.0.0.255 192.168.10.0 0.0.0.255 (4 match(es))
       70 deny ip 192.168.40.0 0.0.0.255 192.168.100.0 0.0.0.255 (8 match(es))
       100 permit ip any any (4 match(es))
   ```
4. **Device:** `Branch1-Router` CLI
   - Command: `show access-lists 110`
   - Shows explicit matches under `10 deny ip host 192.168.50.50 192.168.10.0 0.0.0.255 (8 match(es))` and `60 permit ip host 192.168.50.50 172.16.1.0 0.0.0.255 (4 match(es))`.

### What to Explain to Your Professor
> *"Here we prove that security is enforced at the network ingress point. On `HQ-Router`, ACL 140 is applied inbound on `Gi0/0.40`. When a guest transmits packets to private corporate subnets (`192.168.10.0`, `192.168.100.0`), the router immediately matches the deny rule, drops the frame, and returns an ICMP Type 3 Code 13 (Communication administratively prohibited) unreachable message.*
>
> *Crucially, guest traffic is filtered before it can ever touch the crypto engine, guaranteeing zero leakage of unauthorized traffic into the VPN tunnel."*

---

## ⚡ Stage 6 — Redundant WAN Failover & Path Restoration

### Objective
Demonstrate high-availability enterprise routing using floating static routes and dynamic IPsec crypto-map failover.

### Step 6.1: Show Normal Primary Routing Table
1. **Device:** `HQ-Router` CLI
2. **Command:**
   ```cisco
   show ip route static
   ```
3. **Expected Output:**
   ```
   HQ-Router#show ip route static
   S    209.165.202.0/24 [1/0] via 209.165.201.1
   S*   0.0.0.0/0 [1/0] via 203.0.113.1
   ```
4. **Observation:** The default gateway points to `203.0.113.1` (Primary ISP) with Administrative Distance **1**.

### Step 6.2: Simulate Primary WAN Link Failure
1. **Device:** `HQ-Router` CLI
2. **Commands:**
   ```cisco
   configure terminal
   interface GigabitEthernet0/1
   shutdown
   end
   show ip route static
   ```
3. **Expected Output:**
   ```
   %LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to administratively down
   %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to down

   HQ-Router#show ip route static
   S    209.165.202.0/24 [1/0] via 209.165.201.1
   S*   0.0.0.0/0 [10/0] via 209.165.201.1
   ```
4. **Key Observation:**
   - Because `Gi0/1` went DOWN, IOS immediately flushed the AD 1 route.
   - The **floating static route** `0.0.0.0/0 [10/0] via 209.165.201.1` was instantly promoted to the active routing table!

### Step 6.3: Verify Connectivity over Backup Path
1. **Device:** `Admin-PC1`
2. **Command:**
   ```cmd
   ping 192.168.50.11
   ```
3. **Expected Output:**
   - Packets route via `Gi0/2` to `Backup-ISP` (`209.165.201.1`) and `VPN-BACKUP` map negotiates:
     ```
     Reply from 192.168.50.11: bytes=32 time<1ms TTL=126
     Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
     ```

### Step 6.4: Restore Primary WAN Link (Recovery)
1. **Device:** `HQ-Router` CLI
2. **Commands:**
   ```cisco
   configure terminal
   interface GigabitEthernet0/1
   no shutdown
   end
   show ip route static
   ```
3. **Expected Output:**
   ```
   %LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to up
   %LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up

   HQ-Router#show ip route static
   S    209.165.202.0/24 [1/0] via 209.165.201.1
   S*   0.0.0.0/0 [1/0] via 203.0.113.1
   ```
4. **Key Observation:**
   - As soon as `Gi0/1` returns to UP/UP, the AD 1 route has lower administrative distance than AD 10, pre-empting the backup route and automatically restoring traffic to Primary ISP.

### What to Explain to Your Professor
> *"This test proves our network meets the 99.99% enterprise availability requirement without needing complex dynamic routing peering with the ISP. We implemented a Floating Static Route configured with `ip route 0.0.0.0 0.0.0.0 209.165.201.1 10`. When the primary link is healthy, the routing engine suppresses the AD 10 route. The millisecond the primary interface drops, the floating route becomes active. When the link heals, the router automatically pre-empts back to the primary path."*

---

## 🌳 Stage 7 — Spanning Tree Protocol (PVST+) & Loop Prevention

### Objective
Demonstrate loop prevention, deterministic Root Bridge election, and redundant port blocking in the Layer 2 distribution mesh.

### Step 7.1: Verify Primary Root Bridge on `HQ-SW1`
1. **Device:** `HQ-SW1` CLI
2. **Commands:**
   ```cisco
   enable
   show spanning-tree vlan 10
   ```
3. **Expected Output:**
   ```
   HQ-SW1#show spanning-tree vlan 10
   VLAN0010
     Spanning tree enabled protocol ieee
     Root ID    Priority    4106
                Address     0009.7C1C.32E1
                This bridge is the root
                Hello Time  2 sec  Max Age 20 sec  Forward Delay 15 sec

     Bridge ID  Priority    4106  (priority 4096 sys-id-ext 10)
                Address     0009.7C1C.32E1
   ```
4. **Observation:**
   - `HQ-SW1` displays **`This bridge is the root`**.
   - All its ports (`Fa0/1` through `Fa0/6`, `Fa0/23`, `Fa0/24`, `Gi0/1`) are in role **`Desg`** and state **`FWD`**.

### Step 7.2: Verify Blocked Alternate Port on Secondary Switch `HQ-SW2`
1. **Device:** `HQ-SW2` CLI
2. **Commands:**
   ```cisco
   enable
   show spanning-tree vlan 10
   ```
3. **Expected Output:**
   ```
   HQ-SW2#show spanning-tree vlan 10
     Bridge ID  Priority    8202  (priority 8192 sys-id-ext 10)
   Interface        Role Sts Cost      Prio.Nbr Type
   ---------------- ---- --- --------- -------- --------------------------------
   Fa0/23           Root FWD 19        128.23   P2p
   Fa0/24           Altn BLK 19        128.24   P2p
   ```
4. **Key Observation:**
   - Between `HQ-SW1` and `HQ-SW2`, dual cross-links (`Fa0/23` and `Fa0/24`) provide redundancy.
   - STP placed `Fa0/23` in **`Root FWD`** and `Fa0/24` in **`Altn BLK`** (Alternate Blocking).
   - This prevents switching broadcast storms while keeping a hot-standby link ready.

### Step 7.3: Verify Access Switch Loop Prevention
1. **Device:** `HQ-Admin-SW` CLI
2. **Command:**
   ```cisco
   enable
   show spanning-tree vlan 10
   ```
3. **Expected Output:**
   ```
   Interface        Role Sts Cost      Prio.Nbr Type
   ---------------- ---- --- --------- -------- --------------------------------
   Fa0/1            Desg FWD 19        128.1    P2p
   Fa0/2            Desg FWD 19        128.2    P2p
   Gi0/1            Root FWD 19        128.25   P2p
   Gi0/2            Altn BLK 19        128.26   P2p
   ```
4. **Key Observation:**
   - `Gi0/1` (uplink to primary distribution switch `HQ-SW1`) is **`Root FWD`**.
   - `Gi0/2` (uplink to secondary distribution switch `HQ-SW2`) is in **`Altn BLK`** state.
   - If the cable to `HQ-SW1` is unplugged, `Gi0/2` transitions through Listening and Learning to Forwarding within 30 seconds, maintaining continuous access.

### What to Explain to Your Professor
> *"In a multi-switch corporate campus, redundant links are essential for uptime but create lethal switching loops and broadcast storms if unmanaged. We configured Cisco Per-VLAN Spanning Tree Plus (PVST+). We explicitly configured `spanning-tree vlan 1,10,20,30,40,50,100 priority 4096` on `HQ-SW1` to guarantee it wins the Root Bridge election over all VLANs. The secondary distribution switch `HQ-SW2` is configured with priority 8192.*
>
> *As a result, access switch ports to `HQ-SW2` are logically blocked (`Altn BLK`). No frames loop, yet if `HQ-SW1` suffers a power failure, `HQ-SW2` takes over the root role seamlessly."*

---

## 🎯 Quick Reference Summary Sheet for Live Demo

| Stage | What to Open | What to Run / Show | Success Indicator |
|---|---|---|---|
| **1. Overview** | Topology Workspace | Explain zones, subnets, routers | Clean layout, color-coded regions |
| **2. Dept & DHCP** | `Admin-PC1` Command Prompt | `ipconfig /renew`<br>`ping 192.168.20.11`<br>`nslookup web.corp.local` | IP `192.168.10.11`<br>0% loss inter-VLAN<br>Resolves to `172.16.1.10` |
| **3. Server & DMZ** | `Admin-PC1` & Web Browser | `ping 192.168.100.30`<br>URL `http://web.corp.local` | 0% loss to File Server<br>Web page loads |
| **4. IPsec VPN** | `Admin-PC1` & `HQ-Router` | `ping 192.168.50.11`<br>`show crypto isakmp sa`<br>`show crypto ipsec sa` | 0% loss (TTL=126)<br>`QM_IDLE ACTIVE`<br>`#pkts encrypt` increments |
| **5. Security** | `Guest-PC1` & `HQ-Router` | `ping 192.168.10.11` (Guest)<br>`show access-lists 140` | `Destination host unreachable`<br>Match counters increment |
| **6. Failover** | `HQ-Router` CLI | `int g0/1` → `shutdown`<br>`show ip route static`<br>`int g0/1` → `no shutdown` | Default route switches to AD 10 `209.165.201.1`<br>Preempts back to AD 1 |
| **7. STP** | `HQ-SW1` & `HQ-Admin-SW` | `show spanning-tree vlan 10` | `HQ-SW1` is Root<br>`Gi0/2` on Access is `Altn BLK` |
