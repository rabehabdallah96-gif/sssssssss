"""
Network Topology Simulator
Simulates network devices and connections for topology visualization
"""

import json
import socket
import struct
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import platform


class NetworkTopologySimulator:
    """Network topology simulator and manager"""
    
    def __init__(self):
        self.devices = []
        self.connections = []
        self.next_device_id = 1
        self._initialize_default_topology()
    
    def _initialize_default_topology(self):
        """Initialize a default network topology"""
        # Add Router
        router = self.add_device('router', 'Core-Router-1', '192.168.1.1', '255.255.255.0')
        
        # Add Switches
        switch1 = self.add_device('switch', 'Access-Switch-1', '192.168.1.2', '255.255.255.0')
        switch2 = self.add_device('switch', 'Access-Switch-2', '192.168.1.3', '255.255.255.0')
        
        # Add PCs
        pc1 = self.add_device('pc', 'Workstation-1', '192.168.1.10', '255.255.255.0')
        pc2 = self.add_device('pc', 'Workstation-2', '192.168.1.11', '255.255.255.0')
        pc3 = self.add_device('pc', 'Server-1', '192.168.1.20', '255.255.255.0')
        
        # Add Connections
        self.add_connection(router['id'], switch1['id'], 'GigabitEthernet', '1000Mbps')
        self.add_connection(router['id'], switch2['id'], 'GigabitEthernet', '1000Mbps')
        self.add_connection(switch1['id'], pc1['id'], 'FastEthernet', '100Mbps')
        self.add_connection(switch1['id'], pc2['id'], 'FastEthernet', '100Mbps')
        self.add_connection(switch2['id'], pc3['id'], 'GigabitEthernet', '1000Mbps')
    
    def add_device(self, device_type: str, name: str, ip: str, netmask: str, 
                   mac: Optional[str] = None) -> Dict:
        """Add a network device"""
        if not mac:
            mac = self._generate_mac_address()
        
        device = {
            'id': self.next_device_id,
            'type': device_type,
            'name': name,
            'ip': ip,
            'netmask': netmask,
            'mac': mac,
            'status': 'active',
            'interfaces': self._get_default_interfaces(device_type),
            'created_at': datetime.now().isoformat()
        }
        
        self.devices.append(device)
        self.next_device_id += 1
        
        return device
    
    def add_connection(self, device1_id: int, device2_id: int, 
                       conn_type: str, bandwidth: str) -> Dict:
        """Add connection between two devices"""
        connection = {
            'id': len(self.connections) + 1,
            'from': device1_id,
            'to': device2_id,
            'type': conn_type,
            'bandwidth': bandwidth,
            'status': 'up',
            'created_at': datetime.now().isoformat()
        }
        
        self.connections.append(connection)
        return connection
    
    def get_topology(self) -> Dict:
        """Get complete network topology"""
        return {
            'devices': self.devices,
            'connections': self.connections,
            'statistics': {
                'total_devices': len(self.devices),
                'routers': len([d for d in self.devices if d['type'] == 'router']),
                'switches': len([d for d in self.devices if d['type'] == 'switch']),
                'pcs': len([d for d in self.devices if d['type'] == 'pc']),
                'total_connections': len(self.connections)
            }
        }
    
    def get_device(self, device_id: int) -> Optional[Dict]:
        """Get device by ID"""
        for device in self.devices:
            if device['id'] == device_id:
                return device
        return None
    
    def ping_test(self, source_id: int, dest_id: int) -> Dict:
        """Simulate ping test between devices"""
        source = self.get_device(source_id)
        dest = self.get_device(dest_id)
        
        if not source or not dest:
            return {
                'success': False,
                'error': 'Device not found'
            }
        
        # Check if devices are connected (directly or through path)
        path = self._find_path(source_id, dest_id)
        
        if not path:
            return {
                'success': False,
                'source': source['name'],
                'destination': dest['name'],
                'error': 'No route to host'
            }
        
        # Simulate real ping if IP is real
        real_ping = self._real_ping(dest['ip'])
        
        return {
            'success': True,
            'source': source['name'],
            'source_ip': source['ip'],
            'destination': dest['name'],
            'destination_ip': dest['ip'],
            'path_length': len(path),
            'hops': len(path) - 1,
            'latency': real_ping['latency'] if real_ping['success'] else f"{len(path) * 5}ms",
            'packet_loss': real_ping['packet_loss'] if real_ping['success'] else 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def traceroute(self, source_id: int, dest_id: int) -> Dict:
        """Simulate traceroute between devices"""
        source = self.get_device(source_id)
        dest = self.get_device(dest_id)
        
        if not source or not dest:
            return {
                'success': False,
                'error': 'Device not found'
            }
        
        path = self._find_path(source_id, dest_id)
        
        if not path:
            return {
                'success': False,
                'error': 'No route to host'
            }
        
        hops = []
        for i, device_id in enumerate(path):
            device = self.get_device(device_id)
            hops.append({
                'hop': i + 1,
                'name': device['name'],
                'ip': device['ip'],
                'latency': f"{(i + 1) * 5}ms"
            })
        
        return {
            'success': True,
            'source': source['name'],
            'destination': dest['name'],
            'hops': hops,
            'total_hops': len(hops),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_routing_table(self, device_id: int) -> Dict:
        """Get routing table for a device"""
        device = self.get_device(device_id)
        
        if not device:
            return {'error': 'Device not found'}
        
        if device['type'] not in ['router', 'switch']:
            return {'error': 'Device is not a router or switch'}
        
        # Build routing table based on connections
        routes = []
        
        for conn in self.connections:
            if conn['from'] == device_id:
                dest_device = self.get_device(conn['to'])
                routes.append({
                    'destination': dest_device['ip'],
                    'netmask': dest_device['netmask'],
                    'gateway': device['ip'],
                    'interface': f"Eth{conn['id']}",
                    'metric': 1
                })
            elif conn['to'] == device_id:
                dest_device = self.get_device(conn['from'])
                routes.append({
                    'destination': dest_device['ip'],
                    'netmask': dest_device['netmask'],
                    'gateway': device['ip'],
                    'interface': f"Eth{conn['id']}",
                    'metric': 1
                })
        
        return {
            'device': device['name'],
            'routes': routes,
            'total_routes': len(routes)
        }
    
    def get_interface_stats(self, device_id: int) -> Dict:
        """Get interface statistics for a device"""
        device = self.get_device(device_id)
        
        if not device:
            return {'error': 'Device not found'}
        
        interfaces = []
        
        for interface in device['interfaces']:
            # Find connections using this interface
            connected = False
            for conn in self.connections:
                if conn['from'] == device_id or conn['to'] == device_id:
                    connected = True
                    break
            
            interfaces.append({
                'name': interface['name'],
                'status': 'up' if connected else 'down',
                'speed': interface['speed'],
                'duplex': interface['duplex'],
                'mtu': interface['mtu'],
                'packets_in': interface.get('packets_in', 0),
                'packets_out': interface.get('packets_out', 0),
                'bytes_in': interface.get('bytes_in', 0),
                'bytes_out': interface.get('bytes_out', 0)
            })
        
        return {
            'device': device['name'],
            'interfaces': interfaces
        }
    
    def _find_path(self, source_id: int, dest_id: int) -> Optional[List[int]]:
        """Find path between two devices using BFS"""
        if source_id == dest_id:
            return [source_id]
        
        visited = set()
        queue = [[source_id]]
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            
            if node == dest_id:
                return path
            
            if node in visited:
                continue
            
            visited.add(node)
            
            # Find connected devices
            for conn in self.connections:
                if conn['from'] == node and conn['status'] == 'up':
                    new_path = list(path)
                    new_path.append(conn['to'])
                    queue.append(new_path)
                elif conn['to'] == node and conn['status'] == 'up':
                    new_path = list(path)
                    new_path.append(conn['from'])
                    queue.append(new_path)
        
        return None
    
    def _real_ping(self, ip: str) -> Dict:
        """Perform real ping to IP address"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', ip]
        
        try:
            output = subprocess.run(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                timeout=2
            )
            
            if output.returncode == 0:
                output_str = output.stdout.decode()
                # Parse latency
                if 'time=' in output_str:
                    time_str = output_str.split('time=')[1].split()[0]
                    return {
                        'success': True,
                        'latency': time_str,
                        'packet_loss': 0
                    }
            
            return {'success': False}
        except:
            return {'success': False}
    
    def _generate_mac_address(self) -> str:
        """Generate a random MAC address"""
        import random
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))
    
    def _get_default_interfaces(self, device_type: str) -> List[Dict]:
        """Get default interfaces for device type"""
        if device_type == 'router':
            return [
                {'name': 'GigabitEthernet0/0', 'speed': '1000Mbps', 'duplex': 'full', 'mtu': 1500},
                {'name': 'GigabitEthernet0/1', 'speed': '1000Mbps', 'duplex': 'full', 'mtu': 1500},
                {'name': 'GigabitEthernet0/2', 'speed': '1000Mbps', 'duplex': 'full', 'mtu': 1500}
            ]
        elif device_type == 'switch':
            return [
                {'name': f'FastEthernet0/{i}', 'speed': '100Mbps', 'duplex': 'full', 'mtu': 1500}
                for i in range(1, 25)
            ]
        else:  # PC
            return [
                {'name': 'Ethernet0', 'speed': '1000Mbps', 'duplex': 'full', 'mtu': 1500}
            ]
    
    def export_topology(self) -> str:
        """Export topology as JSON"""
        return json.dumps(self.get_topology(), indent=2)
    
    def get_statistics(self) -> Dict:
        """Get network statistics"""
        return {
            'total_devices': len(self.devices),
            'device_types': {
                'routers': len([d for d in self.devices if d['type'] == 'router']),
                'switches': len([d for d in self.devices if d['type'] == 'switch']),
                'pcs': len([d for d in self.devices if d['type'] == 'pc'])
            },
            'total_connections': len(self.connections),
            'active_connections': len([c for c in self.connections if c['status'] == 'up']),
            'network_health': self._calculate_health()
        }
    
    def _calculate_health(self) -> str:
        """Calculate overall network health"""
        total = len(self.devices)
        active = len([d for d in self.devices if d['status'] == 'active'])
        
        if active == total:
            return 'Excellent'
        elif active >= total * 0.8:
            return 'Good'
        elif active >= total * 0.5:
            return 'Fair'
        else:
            return 'Poor'