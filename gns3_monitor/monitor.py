"""
GNS3 Network Simulator Monitor - Complete with Authentication
Real integration with GNS3 server with fallback support
"""

import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
from typing import Dict, List, Optional
import subprocess
import os


class GNS3Monitor:
    """Monitor GNS3 network simulations"""
    
    def __init__(self, server_url: str = None, 
                 username: str = None, password: str = None):
        self.server_url = (server_url or 
                          os.getenv('GNS3_SERVER_URL', 
                          'http://127.0.0.1:3080')).rstrip('/')
        self.username = username or os.getenv('GNS3_USERNAME')
        self.password = password or os.getenv('GNS3_PASSWORD')
        self.connected = False
        self.version = None
        self._check_connection()
    
    def _get_auth(self):
        """Get authentication object if credentials provided"""
        if self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)
        return None
    
    def _check_connection(self):
        """Check if GNS3 server is available"""
        try:
            response = requests.get(
                f'{self.server_url}/v2/version',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                data = response.json()
                self.version = data.get('version', 'unknown')
                self.connected = True
                print(f"✅ Connected to GNS3 Server v{self.version} at {self.server_url}")
                return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to GNS3 Server at {self.server_url}")
        except Exception as e:
            print(f"❌ GNS3 Connection Error: {e}")
        
        self.connected = False
        return False
    
    def get_status(self) -> Dict:
        """Get GNS3 server status"""
        if not self.connected:
            return {
                'status': 'disconnected',
                'server_url': self.server_url,
                'message': f'GNS3 server not available at {self.server_url}. Make sure GNS3 server is running.',
                'fallback_mode': True,
                'instructions': 'Run: gns3server --host 0.0.0.0 --port 3080'
            }
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/version',
                auth=self._get_auth(),
                timeout=2
            )
            data = response.json()
            
            return {
                'status': 'connected',
                'server_url': self.server_url,
                'version': data.get('version'),
                'local': data.get('local', False),
                'fallback_mode': False
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'fallback_mode': True
            }
    
    def get_projects(self) -> List[Dict]:
        """Get all GNS3 projects"""
        if not self.connected:
            return self._get_fallback_projects()
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/projects',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                projects = response.json()
                return [{
                    'project_id': p.get('project_id'),
                    'name': p.get('name'),
                    'status': p.get('status'),
                    'path': p.get('path'),
                    'filename': p.get('filename'),
                    'auto_close': p.get('auto_close'),
                    'auto_open': p.get('auto_open'),
                    'auto_start': p.get('auto_start')
                } for p in projects]
        except Exception as e:
            print(f"Error fetching projects: {e}")
        
        return self._get_fallback_projects()
    
    def get_project_details(self, project_id: str) -> Optional[Dict]:
        """Get detailed information about a project"""
        if not self.connected:
            return self._get_fallback_project_details(project_id)
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/projects/{project_id}',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching project details: {e}")
        
        return self._get_fallback_project_details(project_id)
    
    def get_nodes(self, project_id: str) -> List[Dict]:
        """Get all nodes in a project"""
        if not self.connected:
            return self._get_fallback_nodes(project_id)
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/projects/{project_id}/nodes',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                nodes = response.json()
                return [{
                    'node_id': n.get('node_id'),
                    'name': n.get('name'),
                    'node_type': n.get('node_type'),
                    'status': n.get('status'),
                    'console': n.get('console'),
                    'console_type': n.get('console_type'),
                    'x': n.get('x'),
                    'y': n.get('y'),
                    'z': n.get('z'),
                    'symbol': n.get('symbol'),
                    'label': n.get('label', {})
                } for n in nodes]
        except Exception as e:
            print(f"Error fetching nodes: {e}")
        
        return self._get_fallback_nodes(project_id)
    
    def get_links(self, project_id: str) -> List[Dict]:
        """Get all links in a project"""
        if not self.connected:
            return self._get_fallback_links(project_id)
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/projects/{project_id}/links',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                links = response.json()
                return [{
                    'link_id': l.get('link_id'),
                    'link_type': l.get('link_type'),
                    'capturing': l.get('capturing'),
                    'suspend': l.get('suspend'),
                    'nodes': l.get('nodes', [])
                } for l in links]
        except Exception as e:
            print(f"Error fetching links: {e}")
        
        return self._get_fallback_links(project_id)
    
    def start_all_nodes(self, project_id: str) -> Dict:
        """Start all nodes in a project"""
        if not self.connected:
            return {
                'success': False,
                'message': 'GNS3 server not available'
            }
        
        try:
            response = requests.post(
                f'{self.server_url}/v2/projects/{project_id}/nodes/start',
                auth=self._get_auth(),
                timeout=5
            )
            return {
                'success': response.status_code == 204,
                'message': 'All nodes started' if response.status_code == 204 else 'Failed to start nodes'
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def stop_all_nodes(self, project_id: str) -> Dict:
        """Stop all nodes in a project"""
        if not self.connected:
            return {
                'success': False,
                'message': 'GNS3 server not available'
            }
        
        try:
            response = requests.post(
                f'{self.server_url}/v2/projects/{project_id}/nodes/stop',
                auth=self._get_auth(),
                timeout=5
            )
            return {
                'success': response.status_code == 204,
                'message': 'All nodes stopped' if response.status_code == 204 else 'Failed to stop nodes'
            }
        except Exception as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_compute_resources(self) -> List[Dict]:
        """Get available compute resources"""
        if not self.connected:
            return self._get_fallback_computes()
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/computes',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error fetching computes: {e}")
        
        return self._get_fallback_computes()
    
    def get_templates(self) -> List[Dict]:
        """Get available device templates"""
        if not self.connected:
            return self._get_fallback_templates()
        
        try:
            response = requests.get(
                f'{self.server_url}/v2/templates',
                auth=self._get_auth(),
                timeout=3
            )
            if response.status_code == 200:
                templates = response.json()
                return [{
                    'template_id': t.get('template_id'),
                    'name': t.get('name'),
                    'category': t.get('category'),
                    'template_type': t.get('template_type'),
                    'builtin': t.get('builtin', False)
                } for t in templates]
        except Exception as e:
            print(f"Error fetching templates: {e}")
        
        return self._get_fallback_templates()
    
    def get_statistics(self) -> Dict:
        """Get overall GNS3 statistics"""
        projects = self.get_projects()
        
        stats = {
            'total_projects': len(projects),
            'active_projects': len([p for p in projects if p.get('status') == 'opened']),
            'total_nodes': 0,
            'running_nodes': 0,
            'total_links': 0
        }
        
        for project in projects:
            if project.get('status') == 'opened':
                project_id = project.get('project_id')
                nodes = self.get_nodes(project_id)
                links = self.get_links(project_id)
                
                stats['total_nodes'] += len(nodes)
                stats['running_nodes'] += len([n for n in nodes if n.get('status') == 'started'])
                stats['total_links'] += len(links)
        
        return stats
    
    # ========== Fallback Methods ==========
    
    def _get_fallback_projects(self) -> List[Dict]:
        """Return simulated projects when GNS3 is not available"""
        return [
            {
                'project_id': 'demo-project-1',
                'name': 'Enterprise Network Simulation',
                'status': 'opened',
                'path': '/gns3/projects/enterprise',
                'filename': 'enterprise.gns3',
                'auto_close': True,
                'auto_open': False,
                'auto_start': False
            },
            {
                'project_id': 'demo-project-2',
                'name': 'Data Center Network',
                'status': 'closed',
                'path': '/gns3/projects/datacenter',
                'filename': 'datacenter.gns3',
                'auto_close': True,
                'auto_open': False,
                'auto_start': False
            }
        ]
    
    def _get_fallback_project_details(self, project_id: str) -> Dict:
        """Return simulated project details"""
        return {
            'project_id': project_id,
            'name': 'Enterprise Network Simulation',
            'status': 'opened',
            'path': '/gns3/projects/enterprise',
            'scene_height': 1000,
            'scene_width': 2000,
            'zoom': 100,
            'show_layers': False,
            'snap_to_grid': False,
            'show_grid': False,
            'grid_size': 75,
            'drawing_grid_size': 25,
            'show_interface_labels': True
        }
    
    def _get_fallback_nodes(self, project_id: str) -> List[Dict]:
        """Return simulated nodes"""
        return [
            {
                'node_id': 'node-1',
                'name': 'Core-Router-1',
                'node_type': 'dynamips',
                'status': 'started',
                'console': 5000,
                'console_type': 'telnet',
                'x': -200,
                'y': -150,
                'z': 1,
                'symbol': ':/symbols/router.svg',
                'label': {'text': 'Core-Router-1', 'x': 0, 'y': -25}
            },
            {
                'node_id': 'node-2',
                'name': 'Distribution-Switch-1',
                'node_type': 'ethernet_switch',
                'status': 'started',
                'console': None,
                'console_type': 'none',
                'x': 100,
                'y': -150,
                'z': 1,
                'symbol': ':/symbols/ethernet_switch.svg',
                'label': {'text': 'Distribution-Switch-1', 'x': 0, 'y': -25}
            },
            {
                'node_id': 'node-3',
                'name': 'Access-Switch-1',
                'node_type': 'ethernet_switch',
                'status': 'started',
                'console': None,
                'console_type': 'none',
                'x': -100,
                'y': 100,
                'z': 1,
                'symbol': ':/symbols/ethernet_switch.svg',
                'label': {'text': 'Access-Switch-1', 'x': 0, 'y': -25}
            },
            {
                'node_id': 'node-4',
                'name': 'PC-1',
                'node_type': 'vpcs',
                'status': 'started',
                'console': 5001,
                'console_type': 'telnet',
                'x': -200,
                'y': 250,
                'z': 1,
                'symbol': ':/symbols/computer.svg',
                'label': {'text': 'PC-1', 'x': 0, 'y': -25}
            },
            {
                'node_id': 'node-5',
                'name': 'PC-2',
                'node_type': 'vpcs',
                'status': 'started',
                'console': 5002,
                'console_type': 'telnet',
                'x': 0,
                'y': 250,
                'z': 1,
                'symbol': ':/symbols/computer.svg',
                'label': {'text': 'PC-2', 'x': 0, 'y': -25}
            }
        ]
    
    def _get_fallback_links(self, project_id: str) -> List[Dict]:
        """Return simulated links"""
        return [
            {
                'link_id': 'link-1',
                'link_type': 'ethernet',
                'capturing': False,
                'suspend': False,
                'nodes': [
                    {'node_id': 'node-1', 'port_number': 0},
                    {'node_id': 'node-2', 'port_number': 0}
                ]
            },
            {
                'link_id': 'link-2',
                'link_type': 'ethernet',
                'capturing': False,
                'suspend': False,
                'nodes': [
                    {'node_id': 'node-2', 'port_number': 1},
                    {'node_id': 'node-3', 'port_number': 0}
                ]
            },
            {
                'link_id': 'link-3',
                'link_type': 'ethernet',
                'capturing': False,
                'suspend': False,
                'nodes': [
                    {'node_id': 'node-3', 'port_number': 1},
                    {'node_id': 'node-4', 'port_number': 0}
                ]
            },
            {
                'link_id': 'link-4',
                'link_type': 'ethernet',
                'capturing': False,
                'suspend': False,
                'nodes': [
                    {'node_id': 'node-3', 'port_number': 2},
                    {'node_id': 'node-5', 'port_number': 0}
                ]
            }
        ]
    
    def _get_fallback_computes(self) -> List[Dict]:
        """Return simulated compute resources"""
        import psutil
        
        return [
            {
                'compute_id': 'local',
                'name': 'Local',
                'protocol': 'http',
                'host': 'localhost',
                'port': 3080,
                'user': '',
                'connected': True,
                'cpu_usage_percent': psutil.cpu_percent(interval=1),
                'memory_usage_percent': psutil.virtual_memory().percent
            }
        ]
    
    def _get_fallback_templates(self) -> List[Dict]:
        """Return simulated templates"""
        return [
            {
                'template_id': 'template-1',
                'name': 'Cisco IOSv',
                'category': 'router',
                'template_type': 'qemu',
                'builtin': False
            },
            {
                'template_id': 'template-2',
                'name': 'Cisco IOU L3',
                'category': 'router',
                'template_type': 'iou',
                'builtin': False
            },
            {
                'template_id': 'template-3',
                'name': 'Ethernet switch',
                'category': 'switch',
                'template_type': 'ethernet_switch',
                'builtin': True
            },
            {
                'template_id': 'template-4',
                'name': 'VPCS',
                'category': 'guest',
                'template_type': 'vpcs',
                'builtin': True
            }
        ]
    
    def check_gns3_installation(self) -> Dict:
        """Check if GNS3 is installed"""
        result = {
            'server_installed': False,
            'server_running': self.connected,
            'server_url': self.server_url,
            'version': self.version
        }
        
        try:
            subprocess.run(
                ['which', 'gns3server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2
            )
            result['server_installed'] = True
        except:
            pass
        
        return result