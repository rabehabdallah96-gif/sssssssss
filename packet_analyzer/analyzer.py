"""
Packet Analyzer Module
تحليل حزم البيانات الشبكية باستخدام Scapy (بديل Wireshark)
"""

from scapy.all import sniff, IP, TCP, UDP, ICMP, ARP, DNS, DNSQR
from datetime import datetime
from typing import Dict, List, Optional
import threading
import logging


class PacketAnalyzer:
    """محلل حزم البيانات الشبكية"""
    
    def __init__(self, interface: str = None):
        """
        تهيئة محلل الباكتات
        
        Args:
            interface: واجهة الشبكة للمراقبة (None = كل الواجهات)
        """
        self.interface = interface
        self.is_capturing = False
        self.capture_thread = None
        self.packets_captured = []
        self.max_packets = 1000  # الحد الأقصى للباكتات المحفوظة
        self.statistics = {
            'total_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'icmp_packets': 0,
            'arp_packets': 0,
            'dns_packets': 0,
            'other_packets': 0,
            'total_bytes': 0
        }
        
        # إعداد السجلات
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    def start_capture(self, packet_count: int = 0, timeout: int = None):
        """
        بدء التقاط الباكتات
        
        Args:
            packet_count: عدد الباكتات المطلوب التقاطها (0 = غير محدود)
            timeout: المدة بالثواني (None = غير محدود)
        """
        if self.is_capturing:
            self.logger.warning("Packet capture already running")
            return False
        
        self.is_capturing = True
        self.packets_captured = []
        self.statistics = {key: 0 for key in self.statistics}
        
        # بدء الالتقاط في thread منفصل
        self.capture_thread = threading.Thread(
            target=self._capture_packets,
            args=(packet_count, timeout),
            daemon=True
        )
        self.capture_thread.start()
        self.logger.info(f"Packet capture started on interface: {self.interface or 'all'}")
        return True
    
    def stop_capture(self):
        """إيقاف التقاط الباكتات"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        self.logger.info("Packet capture stopped")
        return True
    
    def _capture_packets(self, packet_count: int, timeout: int):
        """
        الدالة الداخلية للالتقاط
        
        Args:
            packet_count: عدد الباكتات
            timeout: المدة الزمنية
        """
        try:
            sniff(
                iface=self.interface,
                prn=self._process_packet,
                count=packet_count if packet_count > 0 else 0,
                timeout=timeout,
                stop_filter=lambda x: not self.is_capturing,
                store=False  # لا نحفظ في الذاكرة لتوفير الموارد
            )
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
        finally:
            self.is_capturing = False
    
    def _process_packet(self, packet):
        """
        معالجة كل باكت يتم التقاطها
        
        Args:
            packet: الباكت الملتقط
        """
        try:
            # تحديث الإحصائيات
            self.statistics['total_packets'] += 1
            self.statistics['total_bytes'] += len(packet)
            
            # استخراج معلومات الباكت
            packet_info = self._extract_packet_info(packet)
            
            # تحديث إحصائيات البروتوكول
            protocol = packet_info.get('protocol', 'other').lower()
            stat_key = f'{protocol}_packets'
            if stat_key in self.statistics:
                self.statistics[stat_key] += 1
            else:
                self.statistics['other_packets'] += 1
            
            # حفظ الباكت (مع الحد الأقصى)
            if len(self.packets_captured) >= self.max_packets:
                self.packets_captured.pop(0)  # حذف أقدم باكت
            
            self.packets_captured.append(packet_info)
            
        except Exception as e:
            self.logger.error(f"Packet processing error: {e}")
    
    def _extract_packet_info(self, packet) -> Dict:
        """
        استخراج معلومات من الباكت
        
        Args:
            packet: الباكت
            
        Returns:
            قاموس بمعلومات الباكت
        """
        info = {
            'timestamp': datetime.now().isoformat(),
            'length': len(packet),
            'protocol': 'Unknown',
            'src_ip': None,
            'dst_ip': None,
            'src_port': None,
            'dst_port': None,
            'info': ''
        }
        
        # فحص طبقة IP
        if IP in packet:
            info['src_ip'] = packet[IP].src
            info['dst_ip'] = packet[IP].dst
            info['protocol'] = packet[IP].proto
            
            # فحص TCP
            if TCP in packet:
                info['protocol'] = 'TCP'
                info['src_port'] = packet[TCP].sport
                info['dst_port'] = packet[TCP].dport
                info['info'] = f"Flags: {packet[TCP].flags}"
            
            # فحص UDP
            elif UDP in packet:
                info['protocol'] = 'UDP'
                info['src_port'] = packet[UDP].sport
                info['dst_port'] = packet[UDP].dport
                
                # فحص DNS
                if DNS in packet and packet.haslayer(DNSQR):
                    info['protocol'] = 'DNS'
                    info['info'] = f"Query: {packet[DNSQR].qname.decode('utf-8', errors='ignore')}"
            
            # فحص ICMP
            elif ICMP in packet:
                info['protocol'] = 'ICMP'
                info['info'] = f"Type: {packet[ICMP].type}"
        
        # فحص ARP
        elif ARP in packet:
            info['protocol'] = 'ARP'
            info['src_ip'] = packet[ARP].psrc
            info['dst_ip'] = packet[ARP].pdst
            info['info'] = f"Op: {packet[ARP].op}"
        
        return info
    
    def get_recent_packets(self, limit: int = 50) -> List[Dict]:
        """
        الحصول على أحدث الباكتات
        
        Args:
            limit: عدد الباكتات المطلوبة
            
        Returns:
            قائمة بالباكتات
        """
        return self.packets_captured[-limit:]
    
    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات الالتقاط
        
        Returns:
            قاموس بالإحصائيات
        """
        stats = self.statistics.copy()
        stats['is_capturing'] = self.is_capturing
        stats['packets_stored'] = len(self.packets_captured)
        
        # حساب النسب المئوية
        total = stats['total_packets']
        if total > 0:
            stats['tcp_percentage'] = round((stats['tcp_packets'] / total) * 100, 2)
            stats['udp_percentage'] = round((stats['udp_packets'] / total) * 100, 2)
            stats['icmp_percentage'] = round((stats['icmp_packets'] / total) * 100, 2)
            stats['arp_percentage'] = round((stats['arp_packets'] / total) * 100, 2)
            stats['dns_percentage'] = round((stats['dns_packets'] / total) * 100, 2)
        
        return stats
    
    def get_protocol_distribution(self) -> Dict:
        """
        الحصول على توزيع البروتوكولات
        
        Returns:
            قاموس بتوزيع البروتوكولات
        """
        return {
            'TCP': self.statistics['tcp_packets'],
            'UDP': self.statistics['udp_packets'],
            'ICMP': self.statistics['icmp_packets'],
            'ARP': self.statistics['arp_packets'],
            'DNS': self.statistics['dns_packets'],
            'Other': self.statistics['other_packets']
        }
    
    def get_top_talkers(self, limit: int = 10) -> List[Dict]:
        """
        الحصول على أكثر IPs نشاطاً
        
        Args:
            limit: عدد النتائج
            
        Returns:
            قائمة بأكثر IPs نشاطاً
        """
        ip_stats = {}
        
        for packet in self.packets_captured:
            src_ip = packet.get('src_ip')
            dst_ip = packet.get('dst_ip')
            
            if src_ip:
                ip_stats[src_ip] = ip_stats.get(src_ip, 0) + 1
            if dst_ip:
                ip_stats[dst_ip] = ip_stats.get(dst_ip, 0) + 1
        
        # ترتيب حسب عدد الباكتات
        sorted_ips = sorted(
            ip_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        return [
            {'ip': ip, 'packets': count}
            for ip, count in sorted_ips
        ]
    
    def analyze_traffic_pattern(self) -> Dict:
        """
        تحليل نمط الترافيك
        
        Returns:
            قاموس بتحليل النمط
        """
        analysis = {
            'total_packets': self.statistics['total_packets'],
            'total_bytes': self.statistics['total_bytes'],
            'avg_packet_size': 0,
            'protocol_distribution': self.get_protocol_distribution(),
            'top_talkers': self.get_top_talkers(5),
            'capture_status': 'Active' if self.is_capturing else 'Stopped'
        }
        
        if self.statistics['total_packets'] > 0:
            analysis['avg_packet_size'] = round(
                self.statistics['total_bytes'] / self.statistics['total_packets'],
                2
            )
        
        return analysis
    
    def detect_suspicious_activity(self) -> List[Dict]:
        """
        كشف النشاطات المشبوهة
        
        Returns:
            قائمة بالنشاطات المشبوهة
        """
        suspicious = []
        
        # كشف Port Scanning (عدد كبير من الاتصالات لنفس IP)
        port_scan_threshold = 20
        ip_connections = {}
        
        for packet in self.packets_captured:
            src_ip = packet.get('src_ip')
            dst_port = packet.get('dst_port')
            
            if src_ip and dst_port:
                if src_ip not in ip_connections:
                    ip_connections[src_ip] = set()
                ip_connections[src_ip].add(dst_port)
        
        # فحص IPs المشبوهة
        for ip, ports in ip_connections.items():
            if len(ports) > port_scan_threshold:
                suspicious.append({
                    'type': 'Port Scanning',
                    'severity': 'high',
                    'source_ip': ip,
                    'description': f'Possible port scan detected from {ip} ({len(ports)} ports)',
                    'ports_count': len(ports)
                })
        
        # كشف DNS Tunneling (عدد كبير من DNS queries)
        dns_threshold = 50
        dns_count = self.statistics['dns_packets']
        if dns_count > dns_threshold:
            suspicious.append({
                'type': 'DNS Tunneling',
                'severity': 'medium',
                'description': f'Unusual DNS activity detected ({dns_count} queries)',
                'dns_count': dns_count
            })
        
        # كشف ICMP Flood
        icmp_threshold = 100
        icmp_count = self.statistics['icmp_packets']
        if icmp_count > icmp_threshold:
            suspicious.append({
                'type': 'ICMP Flood',
                'severity': 'high',
                'description': f'Possible ICMP flood attack ({icmp_count} packets)',
                'icmp_count': icmp_count
            })
        
        return suspicious
    
    def clear_capture(self):
        """مسح البيانات المحفوظة"""
        self.packets_captured = []
        self.statistics = {key: 0 for key in self.statistics}
        self.logger.info("Capture data cleared")