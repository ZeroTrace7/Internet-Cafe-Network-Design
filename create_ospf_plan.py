import json

plan = {
  "name": "ospf_single_area",
  "devices": [
    {
      "name": "R1",
      "model": "1941",
      "category": "router",
      "x": 200,
      "y": 100,
      "interfaces": {
        "GigabitEthernet0/0": "209.10.3.1/27",
        "Serial0/0/0": "209.10.3.97/30"
      }
    },
    {
      "name": "R2",
      "model": "1941",
      "category": "router",
      "x": 450,
      "y": 100,
      "interfaces": {
        "GigabitEthernet0/0": "209.10.3.33/27",
        "Serial0/0/0": "209.10.3.98/30",
        "Serial0/0/1": "209.10.3.101/30"
      }
    },
    {
      "name": "R3",
      "model": "1941",
      "category": "router",
      "x": 700,
      "y": 100,
      "interfaces": {
        "GigabitEthernet0/0": "209.10.3.65/27",
        "Serial0/0/0": "209.10.3.102/30"
      }
    },
    {"name": "SW1", "model": "2960-24TT", "category": "switch", "x": 200, "y": 300, "interfaces": {}},
    {"name": "SW2", "model": "2960-24TT", "category": "switch", "x": 450, "y": 300, "interfaces": {}},
    {"name": "SW3", "model": "2960-24TT", "category": "switch", "x": 700, "y": 300, "interfaces": {}},
    {"name": "PC1", "model": "PC-PT", "category": "pc", "x": 100, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.10/27"}, "gateway": "209.10.3.1"},
    {"name": "PC2", "model": "PC-PT", "category": "pc", "x": 250, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.20/27"}, "gateway": "209.10.3.1"},
    {"name": "PC3", "model": "PC-PT", "category": "pc", "x": 350, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.40/27"}, "gateway": "209.10.3.33"},
    {"name": "PC4", "model": "PC-PT", "category": "pc", "x": 500, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.50/27"}, "gateway": "209.10.3.33"},
    {"name": "PC5", "model": "PC-PT", "category": "pc", "x": 600, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.70/27"}, "gateway": "209.10.3.65"},
    {"name": "PC6", "model": "PC-PT", "category": "pc", "x": 750, "y": 450, "interfaces": {"FastEthernet0": "209.10.3.80/27"}, "gateway": "209.10.3.65"}
  ],
  "modules": [
    {"device": "R1", "slot": "0/0", "module": "HWIC-2T"},
    {"device": "R2", "slot": "0/0", "module": "HWIC-2T"},
    {"device": "R3", "slot": "0/0", "module": "HWIC-2T"}
  ],
  "links": [
    {"device_a": "R1", "port_a": "Serial0/0/0", "device_b": "R2", "port_b": "Serial0/0/0", "cable": "serial"},
    {"device_a": "R2", "port_a": "Serial0/0/1", "device_b": "R3", "port_b": "Serial0/0/0", "cable": "serial"},
    {"device_a": "R1", "port_a": "GigabitEthernet0/0", "device_b": "SW1", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "R2", "port_a": "GigabitEthernet0/0", "device_b": "SW2", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "R3", "port_a": "GigabitEthernet0/0", "device_b": "SW3", "port_b": "FastEthernet0/1", "cable": "straight"},
    {"device_a": "SW1", "port_a": "FastEthernet0/2", "device_b": "PC1", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "SW1", "port_a": "FastEthernet0/3", "device_b": "PC2", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "SW2", "port_a": "FastEthernet0/2", "device_b": "PC3", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "SW2", "port_a": "FastEthernet0/3", "device_b": "PC4", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "SW3", "port_a": "FastEthernet0/2", "device_b": "PC5", "port_b": "FastEthernet0", "cable": "straight"},
    {"device_a": "SW3", "port_a": "FastEthernet0/3", "device_b": "PC6", "port_b": "FastEthernet0", "cable": "straight"}
  ],
  "dhcp_pools": [],
  "static_routes": [],
  "ospf_configs": [
    {
      "router": "R1",
      "process_id": 1,
      "networks": [
        {"network": "209.10.3.0", "wildcard": "0.0.0.255", "area": 0}
      ]
    },
    {
      "router": "R2",
      "process_id": 1,
      "networks": [
        {"network": "209.10.3.0", "wildcard": "0.0.0.255", "area": 0}
      ]
    },
    {
      "router": "R3",
      "process_id": 1,
      "networks": [
        {"network": "209.10.3.0", "wildcard": "0.0.0.255", "area": 0}
      ]
    }
  ],
  "rip_configs": []
}

with open("ospf_plan.json", "w") as f:
    json.dump(plan, f, indent=2)
