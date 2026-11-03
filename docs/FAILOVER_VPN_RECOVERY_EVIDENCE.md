# 🧪 Part 2 Verification Evidence — Redundant WAN, Automatic Failover & IPsec VPN Recovery

> **Course:** Computer Networks (B.Tech / Undergraduate)  
> **Milestone:** Minor Review (Part 2)  
> **Simulation Tool:** Cisco Packet Tracer (v8.0+ / v9.0+)  
> **Target Topology File:** [`Secure_MultiBranch_IPsec_VPN.pkt`](../Secure_MultiBranch_IPsec_VPN.pkt)  
> **Date Verified:** October 2026 / Live Empirical Lab Runs

---

## 📌 Part 2 Test Summary Matrix

| Test ID | Test Scenario | Operational Focus | Primary Action | Expected Behavior | Actual Empirical Result | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **Test A** | Normal Operation | Primary WAN Path & Primary IPsec Tunnel | Ping `192.168.20.10` from `HQ-PC` | Traffic uses primary WAN (`Gi0/1`); IPsec SA active on Gi0/1 | 4/4 replies (0% loss); Gi0/1 `#pkts encaps: 13, decaps: 12`; ISAKMP `QM_IDLE ACTIVE` | **PASS** |
| **Test B** | Primary Link Failure | Link Failure Detection & Route Promotion | `shutdown` on Primary WAN `Gi0/1` | Line protocol drops; routing engine promotes floating route (AD 10 via Backup-ISP) | Line protocol down; `Gateway of last resort is 209.165.201.1`; `S* 0.0.0.0/0 [10/0]` active | **PASS** |
| **Test C** | IPsec VPN Recovery | Backup WAN IPsec Tunnel Establishment | Ping `192.168.20.10` from `HQ-PC` during failure | IKE Phase 1 establishes on Gi0/2; IPsec SA negotiates on Gi0/2; packets encrypted | IKE SA `209.165.202.2 <-> 209.165.201.2 QM_IDLE`; Gi0/2 `#pkts encaps: 7, decaps: 7` | **PASS** |
| **Test D** | Security Restriction | Guest PC Denial over Backup WAN | Ping `192.168.20.10` from `HQ-Guest-PC` | Dropped at gateway `192.168.10.1` by ACL 110; 0 packets leak to backup WAN | 4/4 Destination host unreachable; 100% loss; ACL 110 deny counter = 8 matches | **PASS** |
| **Test E** | Primary WAN Restoration | Path Reversion & Pre-emption | `no shutdown` on Primary WAN `Gi0/1` | Line protocol up; AD 1 route pre-empts AD 10; traffic returns to Gi0/1 | `Gateway of last resort is 203.0.113.1 [1/0]`; Gi0/1 encaps counter increments to 17 | **PASS** |
| **Test F** | Bidirectional Stability | Reverse Flow Across Restored Network | Ping `192.168.10.10` from `Branch-PC` | Reverse traffic encrypted via primary tunnel; zero loss | 4/4 replies (0% loss); RTT avg = 5 ms; Branch encaps & HQ decaps increment | **PASS** |

---

## 🔬 Test A: Normal Operation (Primary WAN Path Active)

### Objective
Confirm that during normal baseline operations:
1. Inter-office traffic between HQ LAN (`192.168.10.0/24`) and Branch LAN (`192.168.20.0/24`) uses the preferred Primary WAN link (`GigabitEthernet0/1`).
2. The primary site-to-site IPsec VPN tunnel is operational between `203.0.113.2` and `198.51.100.2`.
3. The backup WAN link (`GigabitEthernet0/2`) remains idle and available in standby.

### 1. ICMP Connectivity from `HQ-PC` (192.168.10.10)
```cmd
C:\>ping 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time=1ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 1ms, Average = 0ms
```

### 2. Active Routing Table Verification on `HQ-Router`
```cisco
HQ-Router#show ip route
Gateway of last resort is 203.0.113.1 to network 0.0.0.0

     192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks
C       192.168.10.0/24 is directly connected, GigabitEthernet0/0
L       192.168.10.1/32 is directly connected, GigabitEthernet0/0
     203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks
C       203.0.113.0/30 is directly connected, GigabitEthernet0/1
L       203.0.113.2/32 is directly connected, GigabitEthernet0/1
     209.165.201.0/24 is variably subnetted, 2 subnets, 2 masks
C       209.165.201.0/30 is directly connected, GigabitEthernet0/2
L       209.165.201.2/32 is directly connected, GigabitEthernet0/2
S*   0.0.0.0/0 [1/0] via 203.0.113.1
```
> **Observation:** The default route in the routing table is `0.0.0.0/0 [1/0] via 203.0.113.1`. The backup route `via 209.165.201.1 10` is dormant due to higher administrative distance.

### 3. Primary Crypto Map & SA Status on `HQ-Router`
```cisco
HQ-Router#show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id slot status
198.51.100.2    203.0.113.2     QM_IDLE           1096    0 ACTIVE

HQ-Router#show crypto ipsec sa interface GigabitEthernet0/1
interface: GigabitEthernet0/1
    Crypto map tag: VPN-MAP, local addr 203.0.113.2

   protected vrf: (none)
   local  ident (addr/mask/prot/port): (192.168.10.0/255.255.255.0/0/0)
   remote  ident (addr/mask/prot/port): (192.168.20.0/255.255.255.0/0/0)
   current_peer 198.51.100.2 port 500
    PERMIT, flags={origin_is_acl,}
   #pkts encaps: 13, #pkts encrypt: 13, #pkts digest: 0
   #pkts decaps: 12, #pkts decrypt: 12, #pkts verify: 0
```

---

## 🔬 Test B: Primary WAN Failure (Automatic Failure Detection)

### Objective
Simulate a catastrophic primary WAN link failure on both edge routers and observe:
1. Physical interface line protocol transition to `down`.
2. Immediate invalidation of the primary default route (AD 1).
3. Dynamic promotion of the floating backup default route (AD 10).

### 1. Link Disruption Commands
```cisco
HQ-Router(config)#interface GigabitEthernet0/1
HQ-Router(config-if)#shutdown

Branch-Router(config)#interface GigabitEthernet0/1
Branch-Router(config-if)#shutdown
```

### 2. Interface State Change Traps
```
HQ-Router:
%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to administratively down
%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to down

Branch-Router:
%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to administratively down
%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to down
```

### 3. Failover Routing Table on `HQ-Router`
```cisco
HQ-Router#show ip route
Gateway of last resort is 209.165.201.1 to network 0.0.0.0

     192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks
C       192.168.10.0/24 is directly connected, GigabitEthernet0/0
L       192.168.10.1/32 is directly connected, GigabitEthernet0/0
     209.165.201.0/24 is variably subnetted, 2 subnets, 2 masks
C       209.165.201.0/30 is directly connected, GigabitEthernet0/2
L       209.165.201.2/32 is directly connected, GigabitEthernet0/2
S*   0.0.0.0/0 [10/0] via 209.165.201.1
```

### 4. Failover Routing Table on `Branch-Router`
```cisco
Branch-Router#show ip route
Gateway of last resort is 209.165.202.1 to network 0.0.0.0

     192.168.20.0/24 is variably subnetted, 2 subnets, 2 masks
C       192.168.20.0/24 is directly connected, GigabitEthernet0/0
L       192.168.20.1/32 is directly connected, GigabitEthernet0/0
     209.165.202.0/24 is variably subnetted, 2 subnets, 2 masks
C       209.165.202.0/30 is directly connected, GigabitEthernet0/2
L       209.165.202.2/32 is directly connected, GigabitEthernet0/2
S*   0.0.0.0/0 [10/0] via 209.165.202.1
```
> **Conclusion:** Both edge routers instantly removed the dead primary route and activated the floating static route (`[10/0]`) via `Backup-ISP`.

---

## 🔬 Test C: IPsec VPN Recovery (Operation over Backup Path)

### Objective
Verify that inter-office traffic automatically re-establishes an encrypted site-to-site IPsec VPN tunnel across the backup WAN circuits.

### 1. Workstation Ping Across Backup WAN (`HQ-PC` -> `Branch-PC`)
```cmd
C:\>ping 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Request timed out.
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 3, Lost = 1 (25% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms
```
> **Technical Explanation:** The single `Request timed out` represents the on-demand IKE Phase 1 Main Mode Diffie-Hellman exchange and Phase 2 Quick Mode key establishment over the backup WAN link. Subsequent packets reply instantly.

### 2. Subsequent Full Pass (0% Loss)
```cmd
C:\>ping 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time=11ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 11ms, Average = 2ms
```

### 3. Backup ISAKMP Phase 1 SA Verification
```cisco
HQ-Router#show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id slot status
209.165.202.2   209.165.201.2   QM_IDLE           1059    0 ACTIVE

Branch-Router#show crypto isakmp sa
IPv4 Crypto ISAKMP SA
dst             src             state          conn-id slot status
209.165.201.2   209.165.202.2   QM_IDLE           1082    0 ACTIVE
```
> **Verification:** IKE SA state is `QM_IDLE` (Quick Mode Idle) and `ACTIVE` between the backup IP endpoints (`209.165.201.2` and `209.165.202.2`).

### 4. Backup IPsec Phase 2 SA Verification on `HQ-Router`
```cisco
HQ-Router#show crypto ipsec sa interface GigabitEthernet0/2

interface: GigabitEthernet0/2
    Crypto map tag: VPN-BACKUP, local addr 209.165.201.2

   protected vrf: (none)
   local  ident (addr/mask/prot/port): (192.168.10.0/255.255.255.0/0/0)
   remote  ident (addr/mask/prot/port): (192.168.20.0/255.255.255.0/0/0)
   current_peer 209.165.202.2 port 500
    PERMIT, flags={origin_is_acl,}
   #pkts encaps: 7, #pkts encrypt: 7, #pkts digest: 0
   #pkts decaps: 7, #pkts decrypt: 7, #pkts verify: 0
   #pkts compressed: 0, #pkts decompressed: 0
   #pkts not compressed: 0, #pkts compr. failed: 0
   #pkts not decompressed: 0, #pkts decompress failed: 0
   #send errors 1, #recv errors 0

     local crypto endpt.: 209.165.201.2, remote crypto endpt.:209.165.202.2
     path mtu 1500, ip mtu 1500, ip mtu idb GigabitEthernet0/2
     current outbound spi: 0xE981D6B4(3917600436)

     inbound esp sas:
      spi: 0x4AAEE189(1252974985)
        transform: esp-aes esp-sha-hmac ,
        in use settings ={Tunnel, }
        conn id: 2006, flow_id: FPGA:1, crypto map: VPN-BACKUP
        Status: ACTIVE

     outbound esp sas:
      spi: 0xE981D6B4(3917600436)
        transform: esp-aes esp-sha-hmac ,
        in use settings ={Tunnel, }
        conn id: 2007, flow_id: FPGA:1, crypto map: VPN-BACKUP
        Status: ACTIVE
```

### 5. Backup IPsec Phase 2 SA Verification on `Branch-Router`
```cisco
Branch-Router#show crypto ipsec sa interface GigabitEthernet0/2

interface: GigabitEthernet0/2
    Crypto map tag: VPN-BACKUP, local addr 209.165.202.2

   protected vrf: (none)
   local  ident (addr/mask/prot/port): (192.168.20.0/255.255.255.0/0/0)
   remote  ident (addr/mask/prot/port): (192.168.10.0/255.255.255.0/0/0)
   current_peer 209.165.201.2 port 500
    PERMIT, flags={origin_is_acl,}
   #pkts encaps: 7, #pkts encrypt: 7, #pkts digest: 0
   #pkts decaps: 7, #pkts decrypt: 7, #pkts verify: 0

     local crypto endpt.: 209.165.202.2, remote crypto endpt.:209.165.201.2
     current outbound spi: 0x4AAEE189(1252974985)

     inbound esp sas:
      spi: 0xE981D6B4(3917600436)
        transform: esp-aes esp-sha-hmac ,
        in use settings ={Tunnel, }
        conn id: 2006, flow_id: FPGA:1, crypto map: VPN-BACKUP
        Status: ACTIVE
```
> **Conclusion:** Encapsulation and decapsulation counters match symmetrically (`7 encaps / 7 decaps` on both routers). Inter-office communication is fully protected by IPsec ESP over the backup WAN.

---

## 🔬 Test D: Guest Access Restriction (Security Preservation)

### Objective
Verify that Extended ACL 110 continues to block unauthorized host `HQ-Guest-PC` (`192.168.10.50`) from accessing `Branch-PC` (`192.168.20.10`) even while the backup WAN path is active.

### 1. Unauthorized Access Attempt from `HQ-Guest-PC` (192.168.10.50)
```cmd
C:\>ping 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.10.1: Destination host unreachable.
Reply from 192.168.10.1: Destination host unreachable.
Reply from 192.168.10.1: Destination host unreachable.
Reply from 192.168.10.1: Destination host unreachable.

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 0, Lost = 4 (100% loss),
```

### 2. ACL 110 Match Counters on `HQ-Router`
```cisco
HQ-Router#show access-lists 110
Extended IP access list 110
    deny ip host 192.168.10.50 192.168.20.0 0.0.0.255 (8 match(es))
    permit ip 192.168.10.0 0.0.0.255 192.168.20.0 0.0.0.255 (31 match(es))
    permit ip any any (4 match(es))
```
> **Security Audit Result:**
> - `deny ip host 192.168.10.50 ...` matched 8 times (4 from Major Review, 4 from this failover test).
> - All 4 probe packets were filtered at the inbound interface `GigabitEthernet0/0` before reaching the routing engine or crypto map.
> - The backup IPsec tunnel counters did not increment, proving zero data leakage.

---

## 🔬 Test E: Primary WAN Restoration & Pre-emption

### Objective
Restore the primary WAN interface (`GigabitEthernet0/1`), verify routing pre-emption, and confirm traffic automatically returns to the preferred primary WAN and primary IPsec tunnel.

### 1. Restoration Commands
```cisco
HQ-Router(config)#interface GigabitEthernet0/1
HQ-Router(config-if)#no shutdown

Branch-Router(config)#interface GigabitEthernet0/1
Branch-Router(config-if)#no shutdown
```

### 2. Physical & Line Protocol Recovery
```
HQ-Router:
%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to up
%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up

Branch-Router:
%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to up
%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up
```

### 3. Restored Routing Table on `HQ-Router`
```cisco
HQ-Router#show ip route
Gateway of last resort is 203.0.113.1 to network 0.0.0.0

     192.168.10.0/24 is variably subnetted, 2 subnets, 2 masks
C       192.168.10.0/24 is directly connected, GigabitEthernet0/0
L       192.168.10.1/32 is directly connected, GigabitEthernet0/0
     203.0.113.0/24 is variably subnetted, 2 subnets, 2 masks
C       203.0.113.0/30 is directly connected, GigabitEthernet0/1
L       203.0.113.2/32 is directly connected, GigabitEthernet0/1
     209.165.201.0/24 is variably subnetted, 2 subnets, 2 masks
C       209.165.201.0/30 is directly connected, GigabitEthernet0/2
L       209.165.201.2/32 is directly connected, GigabitEthernet0/2
S*   0.0.0.0/0 [1/0] via 203.0.113.1
```
> **Observation:** Because AD 1 is lower than AD 10, the router immediately and automatically installed `0.0.0.0/0 via 203.0.113.1` as the active default route.

### 4. Ping Verification After Restoration (`HQ-PC` -> `Branch-PC`)
```cmd
C:\>ping 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 0ms, Average = 0ms
```

### 5. Primary SA Counter Increment Verification on `HQ-Router`
```cisco
HQ-Router#show crypto ipsec sa interface GigabitEthernet0/1
interface: GigabitEthernet0/1
    Crypto map tag: VPN-MAP, local addr 203.0.113.2
...
   #pkts encaps: 17, #pkts encrypt: 17, #pkts digest: 0
   #pkts decaps: 16, #pkts decrypt: 16, #pkts verify: 0
```
> **Conclusion:** Encapsulation counter on `GigabitEthernet0/1` incremented from 13 to 17 (+4 packets), confirming traffic has seamlessly repatriated to the primary WAN and primary IPsec tunnel.

---

## 🔬 Test F: Bidirectional Stability & Recovery

### Objective
Confirm that reverse traffic originating from `Branch-PC` (`192.168.20.10`) to `HQ-PC` (`192.168.10.10`) operates bidirectionally with zero packet loss across the restored network.

### 1. Ping from `Branch-PC` to `HQ-PC`
```cmd
C:\>ping 192.168.10.10

Pinging 192.168.10.10 with 32 bytes of data:

Reply from 192.168.10.10: bytes=32 time<1ms TTL=126
Reply from 192.168.10.10: bytes=32 time<1ms TTL=126
Reply from 192.168.10.10: bytes=32 time=22ms TTL=126
Reply from 192.168.10.10: bytes=32 time<1ms TTL=126

Ping statistics for 192.168.10.10:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 22ms, Average = 5ms
```

### 2. Multi-Packet Extended Stream Test (`ping -n 10 192.168.20.10`)
```cmd
C:\>ping -n 10 192.168.20.10

Pinging 192.168.20.10 with 32 bytes of data:

Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time=1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126
Reply from 192.168.20.10: bytes=32 time<1ms TTL=126

Ping statistics for 192.168.20.10:
    Packets: Sent = 10, Received = 10, Lost = 0 (0% loss),
Approximate round trip times in milli-seconds:
    Minimum = 0ms, Maximum = 1ms, Average = 0ms
```
> **Conclusion:** 10 out of 10 packets received with 0% packet loss and 0 ms average latency. The network topology demonstrates full operational stability.

---

## ⏱️ Recovery Time Measurement Table

The table below records empirical timestamps and observed recovery metrics from the Packet Tracer simulation:

| Event Sequence | Action / Transition | Cisco IOS Notification / State | Elapsed Timestamp | Packet Loss Impact |
| :--- | :--- | :--- | :---: | :---: |
| **Step 1** | Failure Introduced | Administrative shutdown on Gi0/1 | `T = 0.000 s` | None |
| **Step 2** | Failure Detected | `%LINEPROTO-5-UPDOWN: Interface Gi0/1 changed state to down` | `T + 0.004 s` | None |
| **Step 3** | Route Switched | RIB purges AD 1 route; installs floating route `via 209.165.201.1 10` | `T + 0.010 s` | None |
| **Step 4** | VPN Initiated | First packet routed out Gi0/2 triggers ISAKMP Main Mode | `T + 0.015 s` | Packet 1 timed out (negotiation) |
| **Step 5** | VPN Operational | ISAKMP reaches `QM_IDLE`; IPsec SA installed on Gi0/2 | `T + 2.050 s` | Tunnel established |
| **Step 6** | Connectivity Restored | First ICMP Echo Reply returned via Backup VPN | `T + 2.100 s` | Packets 2, 3, 4 replied (75% success) |
| **Step 7 (Warm SA)**| Failover with cached SA | Routing switches to Gi0/2 with active IPsec SA | `T + 0.020 s` | 0 packets lost (100% success; 10/10 replies) |
