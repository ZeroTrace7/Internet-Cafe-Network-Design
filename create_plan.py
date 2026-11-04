import json

plan = {
  "name": "three_routers_rip",
  "devices": [
    {"name": "R1", "model": "1941", "category": "router", "x": 300, "y": 100, "interfaces": {"GigabitEthernet0/0": "192.168.1.1/24", "Serial0/0/0": "10.0.12.1/30", "Serial0/0/1": "10.0.13.2/30"}},
    {"name": "R2", "model": "1941", "category": "router", "x": 100, "y": 300, "interfaces": {"GigabitEthernet0/0": "192.168.2.1/24", "Serial0/0/0": "10.0.12.2/30", "Serial0/0/1": "10.0.23.1/30"}},
    {"name": "R3", "model": "1941", "category": "router", "x": 500, "y": 300, "interfaces": {"GigabitEthernet0/0": "192.168.3.1/24", "Serial0/0/0": "10.0.23.2/30", "Serial0/0/1": "10.0.13.1/30"}},
    {"name": "Switch0", "model": "2960-24TT", "category": "switch", "x": 300, "y": 10, "interfaces": {}},
    {"name": "Switch1", "model": "2960-24TT", "category": "switch", "x": 10, "y": 300, "interfaces": {}},
    {"name": "Switch2", "model": "2960-24TT", "category": "switch", "x": 600, "y": 300, "interfaces": {}},
    {"name": "PC0", "model": "PC-PT", "category": "pc", "x": 300, "y": -50, "interfaces": {"FastEthernet0": "192.168.1.10/24"}, "gateway": "192.168.1.1"},
    {"name": "PC1", "model": "PC-PT", "category": "pc", "x": -50, "y": 300, "interfaces": {"FastEthernet0": "192.168.2.10/24"}, "gateway": "192.168.2.1"},
    {"name": "PC2", "model": "PC-PT", "category": "pc", "x": 700, "y": 300, "interfaces": {"FastEthernet0": "192.168.3.10/24"}, "gateway": "192.168.3.1"}
  ],
  "modules": [
    {"device": "R1", "slot": "0/0", "module": "HWIC-2T"},
    {"device": "R2", "slot": "0/0", "module": "HWIC-2T"},
    {"device": "R3", "slot": "0/0", "module": "HWIC-2T"}
  ],
  "links": [
    {"device_a": "R1", "port_a": "Serial0/0/0", "device_b": "R2", "port_b": "Serial0/0/0", "cable": "serial"},
    {"device_a": "R2", "port_a": "Serial0/0/1", "device_b": "R3", "port_b": "Serial0/0/0", "cable": "serial"},
    {"device_a": "R3", "port_a": "Serial0/0/1", "device_b": "R1", "port_b": "Serial0/0/1", "cable": "serial"},
    {"device_a": "R1", "port_a": "GigabitEthernet0/0", "device_b": "Switch0", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "R2", "port_a": "GigabitEthernet0/0", "device_b": "Switch1", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "R3", "port_a": "GigabitEthernet0/0", "device_b": "Switch2", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "Switch0", "port_a": "FastEthernet0/2", "device_b": "PC0", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "Switch1", "port_a": "FastEthernet0/2", "device_b": "PC1", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "Switch2", "port_a": "FastEthernet0/2", "device_b": "PC2", "port_b": "FastEthernet0", "cable": "straight"}
  ],
  "dhcp_pools": [],
  "static_routes": [],
  "ospf_configs": [],
  "rip_configs": [
    {
      "router": "R1",
      "version": 2,
      "networks": ["192.168.1.0", "10.0.0.0"],
      "no_auto_summary": True
    },
    {
      "router": "R2",
      "version": 2,
      "networks": ["192.168.2.0", "10.0.0.0"],
      "no_auto_summary": True
    },
    {
      "router": "R3",
      "version": 2,
      "networks": ["192.168.3.0", "10.0.0.0"],
      "no_auto_summary": True
    }
  ]
}

with open("custom_plan.json", "w") as f:
    json.dump(plan, f, indent=2)
