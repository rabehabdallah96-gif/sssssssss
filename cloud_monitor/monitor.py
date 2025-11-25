"""
Cloud Services Monitor
Real monitoring for cloud infrastructure using system metrics and Docker
"""

import psutil
import subprocess
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional
import socket
import platform


class CloudServicesMonitor:
    """Monitor cloud services and containerized applications"""
    
    def __init__(self):
        self.docker_available = self._check_docker()
        self.system_info = self._get_system_info()
    
    def _check_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(['docker', '--version'], 
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE, 
                         timeout=2)
            return True
        except:
            return False
    
    def _get_system_info(self) -> Dict:
        """Get real system information"""
        return {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'total_memory_gb': round(psutil.virtual_memory().total / (1024**3), 2)
        }
    
    def get_cloud_overview(self) -> Dict:
        """Get comprehensive cloud services overview"""
        return {
            'timestamp': datetime.now().isoformat(),
            'infrastructure': self._get_infrastructure_status(),
            'containers': self._get_container_stats(),
            'services': self._get_services_status(),
            'resources': self._get_resource_usage(),
            'network': self._get_network_status(),
            'system_info': self.system_info
        }
    
    def _get_infrastructure_status(self) -> Dict:
        """Get infrastructure status (real system metrics)"""
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Simulate cloud regions based on actual location
        hostname = socket.gethostname()
        
        return {
            'provider': 'Local Infrastructure',
            'region': self._detect_region(),
            'availability_zone': hostname,
            'instance_type': self._detect_instance_type(),
            'status': 'running',
            'uptime_seconds': self._get_uptime(),
            'health': 'healthy' if cpu < 80 and memory.percent < 85 else 'warning'
        }
    
    def _detect_region(self) -> str:
        """Detect approximate region based on IP"""
        try:
            # Try to get public IP and location
            response = requests.get('https://ipapi.co/json/', timeout=2)
            data = response.json()
            return f"{data.get('country_name', 'Unknown')}/{data.get('city', 'Unknown')}"
        except:
            return 'Local/Private'
    
    def _detect_instance_type(self) -> str:
        """Detect instance type based on resources"""
        cpu_count = psutil.cpu_count()
        memory_gb = round(psutil.virtual_memory().total / (1024**3))
        
        if cpu_count >= 8 and memory_gb >= 16:
            return 'c5.2xlarge (equivalent)'
        elif cpu_count >= 4 and memory_gb >= 8:
            return 't3.xlarge (equivalent)'
        elif cpu_count >= 2 and memory_gb >= 4:
            return 't3.medium (equivalent)'
        else:
            return 't3.micro (equivalent)'
    
    def _get_uptime(self) -> int:
        """Get system uptime in seconds"""
        try:
            return int(datetime.now().timestamp() - psutil.boot_time())
        except:
            return 0
    
    def _get_container_stats(self) -> Dict:
        """Get real Docker container statistics"""
        if not self.docker_available:
            return {
                'available': False,
                'total': 0,
                'running': 0,
                'stopped': 0,
                'containers': []
            }
        
        try:
            # Get container list
            result = subprocess.run(
                ['docker', 'ps', '-a', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            containers = []
            running = 0
            stopped = 0
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    container = json.loads(line)
                    status = container.get('State', 'unknown')
                    
                    if status == 'running':
                        running += 1
                    else:
                        stopped += 1
                    
                    # Get container stats
                    stats = self._get_single_container_stats(container['Names'])
                    
                    containers.append({
                        'id': container.get('ID', '')[:12],
                        'name': container.get('Names', 'unknown'),
                        'image': container.get('Image', 'unknown'),
                        'status': status,
                        'created': container.get('CreatedAt', ''),
                        'cpu_percent': stats.get('cpu_percent', 0),
                        'memory_usage': stats.get('memory_usage', '0MB'),
                        'memory_percent': stats.get('memory_percent', 0),
                        'network_io': stats.get('network_io', '0B / 0B')
                    })
            
            return {
                'available': True,
                'total': len(containers),
                'running': running,
                'stopped': stopped,
                'containers': containers
            }
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'total': 0,
                'running': 0,
                'stopped': 0,
                'containers': []
            }
    
    def _get_single_container_stats(self, container_name: str) -> Dict:
        """Get stats for a single container"""
        try:
            result = subprocess.run(
                ['docker', 'stats', '--no-stream', '--format', 
                 '{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}},{{.NetIO}}', 
                 container_name],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0 and result.stdout:
                parts = result.stdout.strip().split(',')
                return {
                    'cpu_percent': float(parts[0].replace('%', '')),
                    'memory_usage': parts[1].split('/')[0].strip(),
                    'memory_percent': float(parts[2].replace('%', '')),
                    'network_io': parts[3].strip()
                }
        except:
            pass
        
        return {
            'cpu_percent': 0,
            'memory_usage': '0MB',
            'memory_percent': 0,
            'network_io': '0B / 0B'
        }
    
    def _get_services_status(self) -> List[Dict]:
        """Get status of running services"""
        services = []
        
        # Check common ports for services
        service_ports = {
            80: 'HTTP Server',
            443: 'HTTPS Server',
            22: 'SSH Server',
            3306: 'MySQL Database',
            5432: 'PostgreSQL Database',
            6379: 'Redis Cache',
            27017: 'MongoDB',
            8080: 'Application Server',
            9000: 'SonarQube',
            3000: 'Development Server'
        }
        
        for port, service_name in service_ports.items():
            status = self._check_port(port)
            if status:
                services.append({
                    'name': service_name,
                    'port': port,
                    'status': 'running',
                    'protocol': 'tcp',
                    'health': 'healthy'
                })
        
        return services
    
    def _check_port(self, port: int) -> bool:
        """Check if a port is listening"""
        connections = psutil.net_connections()
        for conn in connections:
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False
    
    def _get_resource_usage(self) -> Dict:
        """Get real-time resource usage"""
        cpu = psutil.cpu_percent(interval=0.5, percpu=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        return {
            'cpu': {
                'overall_percent': round(sum(cpu) / len(cpu), 2),
                'per_core': [round(c, 2) for c in cpu],
                'cores': len(cpu)
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'used_gb': round(disk.used / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'percent': disk.percent
            },
            'network': {
                'bytes_sent_mb': round(network.bytes_sent / (1024**2), 2),
                'bytes_recv_mb': round(network.bytes_recv / (1024**2), 2),
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv,
                'errors_in': network.errin,
                'errors_out': network.errout
            }
        }
    
    def _get_network_status(self) -> Dict:
        """Get network connectivity status"""
        interfaces = {}
        
        for iface_name, iface_addresses in psutil.net_if_addrs().items():
            for addr in iface_addresses:
                if addr.family == socket.AF_INET:
                    interfaces[iface_name] = {
                        'ip': addr.address,
                        'netmask': addr.netmask,
                        'status': 'up'
                    }
        
        # Test internet connectivity
        internet_status = self._test_internet_connection()
        
        return {
            'interfaces': interfaces,
            'internet': internet_status,
            'dns_status': self._test_dns(),
            'public_ip': self._get_public_ip()
        }
    
    def _test_internet_connection(self) -> Dict:
        """Test internet connectivity"""
        try:
            response = requests.get('https://www.google.com', timeout=3)
            return {
                'status': 'connected',
                'latency_ms': round(response.elapsed.total_seconds() * 1000, 2)
            }
        except:
            return {
                'status': 'disconnected',
                'latency_ms': 0
            }
    
    def _test_dns(self) -> str:
        """Test DNS resolution"""
        try:
            socket.gethostbyname('www.google.com')
            return 'working'
        except:
            return 'failed'
    
    def _get_public_ip(self) -> str:
        """Get public IP address"""
        try:
            response = requests.get('https://api.ipify.org', timeout=2)
            return response.text
        except:
            return 'unknown'
    
    def get_docker_images(self) -> List[Dict]:
        """Get list of Docker images"""
        if not self.docker_available:
            return []
        
        try:
            result = subprocess.run(
                ['docker', 'images', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            images = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    img = json.loads(line)
                    images.append({
                        'repository': img.get('Repository', 'unknown'),
                        'tag': img.get('Tag', 'latest'),
                        'id': img.get('ID', '')[:12],
                        'size': img.get('Size', '0MB'),
                        'created': img.get('CreatedSince', '')
                    })
            
            return images
        except:
            return []
    
    def get_docker_networks(self) -> List[Dict]:
        """Get Docker networks"""
        if not self.docker_available:
            return []
        
        try:
            result = subprocess.run(
                ['docker', 'network', 'ls', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            networks = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    net = json.loads(line)
                    networks.append({
                        'id': net.get('ID', '')[:12],
                        'name': net.get('Name', 'unknown'),
                        'driver': net.get('Driver', 'unknown'),
                        'scope': net.get('Scope', 'local')
                    })
            
            return networks
        except:
            return []
    
    def get_docker_volumes(self) -> List[Dict]:
        """Get Docker volumes"""
        if not self.docker_available:
            return []
        
        try:
            result = subprocess.run(
                ['docker', 'volume', 'ls', '--format', '{{json .}}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            volumes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    vol = json.loads(line)
                    volumes.append({
                        'name': vol.get('Name', 'unknown'),
                        'driver': vol.get('Driver', 'local')
                    })
            
            return volumes
        except:
            return []
    
    def get_cost_estimate(self) -> Dict:
        """Estimate cloud costs based on resource usage"""
        resources = self._get_resource_usage()
        uptime_hours = self._get_uptime() / 3600
        
        # Estimate based on AWS pricing (approximate)
        instance_cost_per_hour = 0.05  # t3.medium equivalent
        data_transfer_cost_per_gb = 0.09
        storage_cost_per_gb_month = 0.10
        
        estimated_monthly_instance = instance_cost_per_hour * 730  # 730 hours/month
        estimated_data_transfer = resources['network']['bytes_sent_mb'] / 1024 * data_transfer_cost_per_gb
        estimated_storage = resources['disk']['used_gb'] * storage_cost_per_gb_month
        
        return {
            'currency': 'USD',
            'estimated_monthly': {
                'compute': round(estimated_monthly_instance, 2),
                'storage': round(estimated_storage, 2),
                'data_transfer': round(estimated_data_transfer, 2),
                'total': round(estimated_monthly_instance + estimated_storage + estimated_data_transfer, 2)
            },
            'current_usage': {
                'uptime_hours': round(uptime_hours, 2),
                'cpu_utilization': resources['cpu']['overall_percent'],
                'memory_utilization': resources['memory']['percent'],
                'storage_gb': resources['disk']['used_gb']
            }
        }