# Internet Cafe Network Architecture & Technical Design

## 1. Overview
This document specifies the network architecture, IP address allocation (VLSM), VLAN segmentation, routing policies, and security controls for a modern commercial Internet Cafe.

The design implements a hierarchical, scalable network model capable of isolating general customer traffic, high-bandwidth gaming traffic, administrative systems, and local servers while providing secure, translated Internet connectivity via Cisco NAT/PAT.

---

## 2. Logical Topology

```
                  +-------------------------+
                  |       ISP-Router        |
                  |     (Cisco 2911)        |
                  | Loopback0: 8.8.8.8/32   |
                  +------------+------------+
                               | Gi0/0 (203.0.113.1/30)
                               | WAN Link
                               | Gi0/0 (203.0.113.2/30)
                  +------------+------------+
                  |       Edge-Router       |
                  |     (Cisco 2911)        |
                  | NAT Overload / OSPF     |
                  +------------+------------+
                               | Gi0/1 (802.1Q Trunk)
                               |
                               | Gi0/1 (802.1Q Trunk)
                  +------------+------------+
                  |       Core-Switch       |
                  |  (Catalyst 2960-24TT)   |
                  +---+--------+--------+---+
                      |        |        |   +-- Fa0/4 (Access VLAN 40) --> [ Cafe-Server ]
                      |        |        |                                  192.168.100.114/29
                      |        |        +-- Fa0/3 (Trunk)
                      |        +----------- Fa0/2 (Trunk)
                      +-------------------- Fa0/1 (Trunk)
                      |                     |                   |
               +------+------+       +------+------+     +------+------+
               | Customer-SW |       |  Gaming-SW  |     |  Admin-SW   |
               | (VLAN 10)   |       |  (VLAN 20)  |     |  (VLAN 30)  |
               +------+------+       +------+------+     +------+------+
                      |                     |                   |
            +---------+---------+   +-------+-------+           |
            |                   |   |               |           |
        [Cust-PC1]          [Cust-PC2] [Game-PC1] [Game-PC2] [Admin-PC]
```

---

## 3. Variable Length Subnet Masking (VLSM) Plan

The entire private network is allocated from the `192.168.100.0/24` address space, sub-divided using VLSM to optimize address consumption and minimize broadcast domains:

| Subnet / Zone | VLAN ID | Network Address | Subnet Mask | Usable Host Range | Default Gateway | Total Usable Hosts |
| :--- | :---: | :--- | :--- | :--- | :--- | :---: |
| **Customer Area** | 10 | `192.168.100.0/26` | `255.255.255.192` | `192.168.100.2 - 192.168.100.62` | `192.168.100.1` | 62 |
| **Gaming Area** | 20 | `192.168.100.64/27` | `255.255.255.224` | `192.168.100.66 - 192.168.100.94` | `192.168.100.65` | 30 |
| **Admin & Billing** | 30 | `192.168.100.96/28` | `255.255.255.240` | `192.168.100.98 - 192.168.100.110`| `192.168.100.97` | 14 |
| **Cafe Server Farm** | 40 | `192.168.100.112/29`| `255.255.255.248` | `192.168.100.114 - 192.168.100.118`| `192.168.100.113` | 6 |
| **WAN ISP Uplink** | N/A | `203.0.113.0/30` | `255.255.255.252` | `203.0.113.1 - 203.0.113.2` | `203.0.113.1` | 2 |
| **Internet / DNS** | N/A | `8.8.8.8/32` | `255.255.255.255` | Public Loopback | N/A | 1 |

---

## 4. Layer 2 Implementation (Switching & Trunking)

1. **VLAN Segmentation**:
   - Isolates regular cafe visitors (VLAN 10) from low-latency competitive gaming rigs (VLAN 20).
   - Secures billing, accounting, and staff computers (VLAN 30) from public access.
   - Centralizes cafe local billing and media servers in a dedicated server segment (VLAN 40).
2. **802.1Q Trunking**:
   - `Edge-Router (Gi0/1)` <-> `Core-Switch (Gi0/1)` carries all VLAN tags (`10, 20, 30, 40`).
   - `Core-Switch (Fa0/1)` <-> `Customer-SW (Gi0/1)` carries VLAN 10.
   - `Core-Switch (Fa0/2)` <-> `Gaming-SW (Gi0/1)` carries VLAN 20.
   - `Core-Switch (Fa0/3)` <-> `Admin-SW (Gi0/1)` carries VLAN 30.
3. **Access Ports**:
   - Configured with `switchport mode access` and explicitly assigned to the corresponding VLAN.

---

## 5. Layer 3 Implementation (Routing & NAT)

1. **Router-on-a-Stick (Inter-VLAN Routing)**:
   - Configured on `Edge-Router` sub-interfaces `Gi0/1.10`, `Gi0/1.20`, `Gi0/1.30`, and `Gi0/1.40` with `encapsulation dot1Q <vlan-id>`.
2. **Dynamic Routing**:
   - OSPF Process 1 runs in Area 0 between `Edge-Router` and `ISP-Router` for routing exchange and reachability.
   - Default route `0.0.0.0 0.0.0.0 203.0.113.1` on `Edge-Router` points all outbound Internet traffic toward the ISP gateway.
3. **NAT / PAT (Port Address Translation)**:
   - Sub-interfaces `Gi0/1.10 - Gi0/1.40` configured as `ip nat inside`.
   - WAN interface `Gi0/0` configured as `ip nat outside`.
   - Access-List 1 permits `192.168.100.0 0.0.0.255`.
   - `ip nat inside source list 1 interface GigabitEthernet0/0 overload` dynamically translates all internal cafe traffic to the public WAN IP `203.0.113.2`.

---

## 6. Verification and Health Checks

- **End-to-End ICMP Tests**:
  - `Cust-PC1` (192.168.100.2) -> Gateway (192.168.100.1): 100% Success (0% loss)
  - `Cust-PC1` (192.168.100.2) -> Public Internet (8.8.8.8): 100% Success (0% loss)
  - `Game-PC1` (192.168.100.66) -> Public Internet (8.8.8.8): 100% Success (0% loss)
  - `Admin-PC` (192.168.100.98) -> Cafe-Server (192.168.100.114): 100% Success
