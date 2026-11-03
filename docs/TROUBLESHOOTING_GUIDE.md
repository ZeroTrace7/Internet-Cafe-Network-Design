# 🛠️ Troubleshooting & Diagnostic Guide — Secure Multi-Branch Network with IPsec VPN & Redundant WAN

> **Course:** Computer Networks (B.Tech / Undergraduate)  
> **Simulation Tool:** Cisco Packet Tracer (v8.0+ / v9.0+)  
> **Topology:** [`Secure_MultiBranch_IPsec_VPN.pkt`](../Secure_MultiBranch_IPsec_VPN.pkt)

---

## 📑 Diagnostic Index
1. [General Diagnostic Workflow](#1-general-diagnostic-workflow)
2. [IPsec VPN Tunnel Troubleshooting](#2-ipsec-vpn-tunnel-troubleshooting)
3. [WAN Failover & Routing Troubleshooting](#3-wan-failover--routing-troubleshooting)
4. [Access Control List (ACL) Issues](#4-access-control-list-acl-issues)
5. [Cisco Packet Tracer Platform Limitations](#5-cisco-packet-tracer-platform-limitations)
6. [Essential Diagnostic Command Reference](#6-essential-diagnostic-command-reference)

---

## 1. General Diagnostic Workflow

When encountering connectivity issues in the dual-WAN VPN topology, troubleshoot bottom-up according to the OSI model:

```
[Layer 1/2: Physical & Data Link] -> show ip interface brief
         │ (Are all interfaces up/up? Correct cables: Crossover router-router, Straight router-switch?)
         ▼
[Layer 3: IP Routing]           -> show ip route / ping <next-hop>
         │ (Is the default route active? Does next-hop ping succeed?)
         ▼
[Layer 4/Security: ACLs]         -> show access-lists
         │ (Are authorized packets permitted? Is guest traffic filtered?)
         ▼
[Crypto: IKE Phase 1]           -> show crypto isakmp sa
         │ (Is the state QM_IDLE and status ACTIVE?)
         ▼
[Crypto: IPsec Phase 2]          -> show crypto ipsec sa
           (Are #pkts encaps and #pkts decaps incrementing symmetrically?)
```

---

## 2. IPsec VPN Tunnel Troubleshooting

### Issue 2.1: `show crypto isakmp sa` shows `MM_NO_STATE` or is Empty
- **Symptom:** Pings between LAN PCs fail, and `show crypto isakmp sa` on the router displays:
  ```
  209.165.202.2   209.165.201.2   MM_NO_STATE          0    0 ACTIVE (deleted)
  ```
- **Cause 1: Remote Peer IP is Unreachable.** The router cannot route UDP port 500 packets to the remote peer.
  - *Fix:* Test basic IP reachability to the peer address:
    ```cisco
    HQ-Router#ping 209.165.202.2
    ```
    If pings fail, check that the intermediate ISP router (`Backup-ISP` or `ISP-Router`) has active routes and connected interfaces.
- **Cause 2: Pre-Shared Key (PSK) Mismatch.**
  - *Fix:* Ensure the pre-shared key is configured identically on both routers for both primary and backup peer addresses:
    ```cisco
    crypto isakmp key ciscoVPN2026 address 198.51.100.2
    crypto isakmp key ciscoVPN2026 address 209.165.202.2
    ```
- **Cause 3: ISAKMP Policy Inconsistency.**
  - *Fix:* Ensure `crypto isakmp policy 10` has identical encryption (`aes`), authentication (`pre-share`), and Diffie-Hellman group (`group 2`) on both peers.

### Issue 2.2: Phase 1 is `QM_IDLE`, but Phase 2 SAs Do Not Increment (`#pkts encaps: 0`)
- **Symptom:** Phase 1 is active, but pings fail and `show crypto ipsec sa` counters remain zero.
- **Cause: Interesting Traffic ACL Mismatch.**
  - *Explanation:* Packet Tracer requires strict symmetrical mirror-image ACLs for interesting traffic.
  - *HQ-Router ACL 101:*
    ```cisco
    access-list 101 permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255
    ```
  - *Branch-Router ACL 101:*
    ```cisco
    access-list 101 permit ip 192.168.20.0 0.0.0.255 192.168.10.0 0.0.0.255
    ```
  - If source and destination subnets do not exactly mirror each other, Quick Mode Phase 2 will reject the SA proposal.

### Issue 2.3: Crypto Map Not Bound to Interface
- **Symptom:** Packets egress unencrypted in plain text.
- **Fix:** Verify crypto map binding under the WAN interface:
  ```cisco
  interface GigabitEthernet0/1
   crypto map VPN-MAP
  interface GigabitEthernet0/2
   crypto map VPN-BACKUP
  ```

---

## 3. WAN Failover & Routing Troubleshooting

### Issue 3.1: Traffic Does Not Switch to Backup Link After Primary Failure
- **Symptom:** When `GigabitEthernet0/1` is shut down, pings time out indefinitely.
- **Cause 1: Floating Static Route Missing or Metric Equal to Primary.**
  - *Check:*
    ```cisco
    show run | include ip route
    ```
  - *Fix:* Ensure the backup default route has a higher administrative distance (e.g., AD = 10):
    ```cisco
    HQ-Router(config)#ip route 0.0.0.0 0.0.0.0 209.165.201.1 10
    Branch-Router(config)#ip route 0.0.0.0 0.0.0.0 209.165.202.1 10
    ```
- **Cause 2: Backup WAN Interface is Administratively Down.**
  - *Fix:* Check `show ip interface brief`. If `GigabitEthernet0/2` is `administratively down`, issue:
    ```cisco
    interface GigabitEthernet0/2
     no shutdown
    ```
- **Cause 3: `Backup-ISP` Router Lacks Return Routes.**
  - *Fix:* Ensure `Backup-ISP` has static routes to forward return packets to each router's LAN:
    ```cisco
    Backup-ISP(config)#ip route 192.168.10.0 255.255.255.0 209.165.201.2
    Backup-ISP(config)#ip route 192.168.20.0 255.255.255.0 209.165.202.2
    ```

### Issue 3.2: Traffic Does Not Return to Primary Path After Restoration
- **Symptom:** Primary link is restored, but traffic continues crossing the backup path.
- **Cause: Primary Interface Not Fully Up.**
  - *Check:* Verify `show ip interface brief` on both `HQ-Router` and `Branch-Router`. Both ends of the primary link (`Gi0/1`) must report `up/up`.
  - If one end remains in `shutdown`, line protocol cannot transition to `up`, and the primary route (AD 1) will not re-enter the routing table.
  - *Fix:* Issue `no shutdown` on `GigabitEthernet0/1` on both edge routers.

---

## 4. Access Control List (ACL) Issues

### Issue 4.1: Authorized `HQ-PC` is Denied Access
- **Symptom:** `HQ-PC` (`192.168.10.10`) receives `Destination host unreachable`.
- **Cause: ACL 110 Statement Order or Wrong IP Address.**
  - Extended ACLs are processed sequentially top-to-bottom on first-match basis.
  - *Correct ACL 110 Structure:*
    ```cisco
    access-list 110 deny ip host 192.168.10.50 192.168.20.0 0.0.0.255   ! Line 10: Deny specific guest
    access-list 110 permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 ! Line 20: Permit rest of LAN
    access-list 110 permit ip any any                                    ! Line 30: Permit all other
    ```
  - If `HQ-PC` was accidentally assigned `192.168.10.50`, it will match the deny rule. Verify with `ipconfig` on `HQ-PC`.

### Issue 4.2: Guest PC Can Access Branch Office
- **Symptom:** `HQ-Guest-PC` (`192.168.10.50`) successfully pings `Branch-PC`.
- **Cause: ACL 110 Not Bound Inbound on Gateway Interface.**
  - *Fix:* Apply ACL 110 inbound on `GigabitEthernet0/0`:
    ```cisco
    interface GigabitEthernet0/0
     ip access-group 110 in
    ```

---

## 5. Cisco Packet Tracer Platform Limitations

When working with Packet Tracer, be aware of commands that exist in real Cisco IOS but are **unsupported in Packet Tracer**:

| Command | Real IOS Role | Packet Tracer Behavior | Supported Workaround |
| :--- | :--- | :--- | :--- |
| `ip sla <num>` | Active probe for remote next-hop reachability | `% Unrecognized command` | Rely on physical interface carrier-detect (`up/down`). |
| `track <num> ip sla` | Binds IP SLA reachability to route validity | `% Unrecognized command` | Interface-driven route invalidation. |
| `crypto isakmp keepalive` | Dead Peer Detection (DPD) | `% Unrecognized command` | Dual crypto maps with interface-level binding. |
| `terminal length 0` | Disable `--More--` paging | Works in privileged exec | Use before long diagnostic commands to prevent console lockups. |

---

## 6. Essential Diagnostic Command Reference

```cisco
! === ROUTING & INTERFACE STATUS ===
show ip interface brief          ! Check line/protocol status of all interfaces
show ip route                    ! Inspect active routes and gateway of last resort
show ip route static             ! Filter view to static routes only

! === IPSEC & ISAKMP STATUS ===
show crypto isakmp sa            ! Check Phase 1 control-plane SA (must show QM_IDLE)
show crypto ipsec sa             ! Check Phase 2 data-plane SA, endpoints, and packet counters
show crypto map                  ! View crypto map parameters and interface bindings

! === SECURITY & ACCESS CONTROL ===
show access-lists                ! Display all ACLs and per-rule hit counters
show access-lists 110            ! Check ACL 110 permit vs deny matches
show ip access-group             ! Check interface ACL bindings

! === CONFIGURATION INTEGRITY ===
show running-config              ! Review active device configuration
copy running-config startup-config ! Save running configuration to NVRAM
```
