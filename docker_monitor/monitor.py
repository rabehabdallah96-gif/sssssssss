"""
Docker Monitor Module
مراقبة حاويات Docker والموارد
"""

import subprocess
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging


class DockerMonitor:
    """مراقب حاويات Docker"""
    
    def __init__(self):
        self.docker_available = self._check_docker()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def _check_docker(self) -> bool:
        """التحقق من تثبيت وتشغيل Docker"""
        try:
            result = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.logger.warning(f"Docker not available: {e}")
            return False
    
    def _run_command(self, command: List[str]) -> Optional[str]:
        """تنفيذ أمر Docker"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                timeout=15,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Docker command failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error running Docker command: {e}")
            return None
    
    def get_containers(self, all_containers: bool = True) -> List[Dict]:
        """الحصول على قائمة الحاويات"""
        if not self.docker_available:
            return []
        
        cmd = ['docker', 'ps', '--format', '{{json .}}']
        if all_containers:
            cmd.insert(2, '-a')
        
        output = self._run_command(cmd)
        if not output:
            return []
        
        containers = []
        for line in output.split('\n'):
            if line.strip():
                try:
                    container = json.loads(line)
                    containers.append({
                        'id': container.get('ID', ''),
                        'name': container.get('Names', ''),
                        'image': container.get('Image', ''),
                        'status': container.get('State', ''),
                        'ports': container.get('Ports', ''),
                        'created': container.get('CreatedAt', '')
                    })
                except json.JSONDecodeError:
                    continue
        
        return containers
    
    def get_container_stats(self, container_id: str) -> Optional[Dict]:
        """الحصول على إحصائيات الحاوية"""
        if not self.docker_available:
            return None
        
        cmd = ['docker', 'stats', container_id, '--no-stream', '--format', '{{json .}}']
        output = self._run_command(cmd)
        
        if not output:
            return None
        
        try:
            stats = json.loads(output)
            return {
                'container_id': stats.get('ID', '')[:12],
                'name': stats.get('Name', ''),
                'cpu_percent': self._parse_percent(stats.get('CPUPerc', '0%')),
                'memory_usage': stats.get('MemUsage', ''),
                'memory_percent': self._parse_percent(stats.get('MemPerc', '0%')),
                'network_io': stats.get('NetIO', ''),
                'block_io': stats.get('BlockIO', ''),
                'pids': stats.get('PIDs', '0'),
                'timestamp': datetime.now().isoformat()
            }
        except json.JSONDecodeError:
            return None
    
    def get_all_container_stats(self) -> List[Dict]:
        """الحصول على إحصائيات جميع الحاويات"""
        if not self.docker_available:
            return []
        
        cmd = ['docker', 'stats', '--no-stream', '--format', '{{json .}}']
        output = self._run_command(cmd)
        
        if not output:
            return []
        
        stats_list = []
        for line in output.split('\n'):
            if line.strip():
                try:
                    stats = json.loads(line)
                    stats_list.append({
                        'container_id': stats.get('ID', '')[:12],
                        'name': stats.get('Name', ''),
                        'cpu_percent': self._parse_percent(stats.get('CPUPerc', '0%')),
                        'memory_percent': self._parse_percent(stats.get('MemPerc', '0%')),
                        'network_io': stats.get('NetIO', ''),
                        'block_io': stats.get('BlockIO', ''),
                        'pids': stats.get('PIDs', '0')
                    })
                except json.JSONDecodeError:
                    continue
        
        return stats_list
    
    def get_images(self) -> List[Dict]:
        """الحصول على قائمة الصور"""
        if not self.docker_available:
            return []
        
        cmd = ['docker', 'images', '--format', '{{json .}}']
        output = self._run_command(cmd)
        
        if not output:
            return []
        
        images = []
        for line in output.split('\n'):
            if line.strip():
                try:
                    image = json.loads(line)
                    images.append({
                        'id': image.get('ID', ''),
                        'repository': image.get('Repository', ''),
                        'tag': image.get('Tag', ''),
                        'size': image.get('Size', ''),
                        'created': image.get('CreatedAt', '')
                    })
                except json.JSONDecodeError:
                    continue
        
        return images
    
    def get_system_info(self) -> Optional[Dict]:
        """الحصول على معلومات نظام Docker"""
        if not self.docker_available:
            return None
        
        cmd = ['docker', 'info', '--format', '{{json .}}']
        output = self._run_command(cmd)
        
        if not output:
            return None
        
        try:
            info = json.loads(output)
            return {
                'containers_running': info.get('ContainersRunning', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'containers_total': info.get('Containers', 0),
                'images': info.get('Images', 0),
                'server_version': info.get('ServerVersion', ''),
                'storage_driver': info.get('Driver', ''),
                'timestamp': datetime.now().isoformat()
            }
        except json.JSONDecodeError:
            return None
    
    def get_all_metrics(self) -> Dict:
        """الحصول على جميع مقاييس Docker"""
        return {
            'docker_available': self.docker_available,
            'system_info': self.get_system_info(),
            'containers': self.get_containers(all_containers=True),
            'container_stats': self.get_all_container_stats(),
            'images': self.get_images(),
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def _parse_percent(percent_str: str) -> float:
        """تحويل نص النسبة المئوية إلى رقم"""
        try:
            return float(percent_str.replace('%', '').strip())
        except (ValueError, AttributeError):
            return 0.0