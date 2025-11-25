"""
SentraOS Dashboard - Updated with Authentication & Packet Analyzer
Main Flask application with login/registration system and packet capture
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from network_monitor.monitor import SystemMonitor
from security_scanner.scanner import SecurityScanner
from automation.auto_responder import AutoResponder
from packet_analyzer.analyzer import PacketAnalyzer
from network_topology.simulator import NetworkTopologySimulator
from cloud_monitor.monitor import CloudServicesMonitor
from gns3_monitor.monitor import GNS3Monitor
from models import get_session, SystemMetric, ScanResult, Alert, PacketCapture, log_activity, User
from dashboard.auth import login_required, authenticate_user, register_user, logout_user, get_current_user

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'sentra-dev-secret-key-change-in-production')

# Initialize modules
system_monitor = SystemMonitor()
security_scanner = SecurityScanner()
auto_responder = AutoResponder()
packet_analyzer = PacketAnalyzer()  # تهيئة محلل الباكتات
network_simulator = NetworkTopologySimulator()
cloud_monitor = CloudServicesMonitor()
# تهيئة GNS3 Monitor مع credentials
gns3_monitor = GNS3Monitor(
    server_url=os.getenv('GNS3_SERVER_URL', 'http://127.0.0.1:3080'),
    username=os.getenv('GNS3_USERNAME'),
    password=os.getenv('GNS3_PASSWORD')
)


# ===== Authentication Routes =====

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    # لو المستخدم مسجل دخول، ارجعه للـ Dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user, error = authenticate_user(username, password)
        
        if user:
            # حفظ بيانات المستخدم في الـ session
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=error)
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """صفحة إنشاء حساب جديد"""
    # لو المستخدم مسجل دخول، ارجعه للـ Dashboard
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        
        # التحقق من تطابق كلمات المرور
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        # التحقق من طول كلمة المرور
        if len(password) < 6:
            return render_template('register.html', error='Password must be at least 6 characters')
        
        # تسجيل المستخدم
        user, error = register_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        if user:
            # تسجيل دخول تلقائي بعد التسجيل
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', error=error)
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    """تسجيل الخروج"""
    logout_user()
    return redirect(url_for('login'))


# ===== Dashboard Routes =====

@app.route('/')
@login_required
def dashboard():
    """الصفحة الرئيسية - Dashboard"""
    user = get_current_user()
    return render_template('index.html', user=user)


@app.route('/gns3')
@login_required
def gns3_page():
    """GNS3 Network Simulator page"""
    user = get_current_user()
    return render_template('gns3.html', user=user)

@app.route('/api/gns3/status')
@login_required
def get_gns3_status():
    """Get GNS3 server status"""
    try:
        status = gns3_monitor.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects')
@login_required
def get_gns3_projects():
    """Get all GNS3 projects"""
    try:
        projects = gns3_monitor.get_projects()
        return jsonify(projects)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects/<project_id>')
@login_required
def get_gns3_project_details(project_id):
    """Get project details"""
    try:
        details = gns3_monitor.get_project_details(project_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects/<project_id>/nodes')
@login_required
def get_gns3_nodes(project_id):
    """Get project nodes"""
    try:
        nodes = gns3_monitor.get_nodes(project_id)
        return jsonify(nodes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects/<project_id>/links')
@login_required
def get_gns3_links(project_id):
    """Get project links"""
    try:
        links = gns3_monitor.get_links(project_id)
        return jsonify(links)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects/<project_id>/start', methods=['POST'])
@login_required
def start_gns3_project(project_id):
    """Start all nodes in project"""
    try:
        result = gns3_monitor.start_all_nodes(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/projects/<project_id>/stop', methods=['POST'])
@login_required
def stop_gns3_project(project_id):
    """Stop all nodes in project"""
    try:
        result = gns3_monitor.stop_all_nodes(project_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/statistics')
@login_required
def get_gns3_statistics():
    """Get GNS3 statistics"""
    try:
        stats = gns3_monitor.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gns3/templates')
@login_required
def get_gns3_templates():
    """Get available templates"""
    try:
        templates = gns3_monitor.get_templates()
        return jsonify(templates)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/cloud')
@login_required
def cloud_page():
    """Cloud Services page"""
    user = get_current_user()
    return render_template('cloud.html', user=user)

@app.route('/api/cloud/overview')
@login_required
def get_cloud_overview():
    """Get cloud services overview"""
    try:
        overview = cloud_monitor.get_cloud_overview()
        return jsonify(overview)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloud/containers')
@login_required
def get_cloud_containers():
    """Get container statistics"""
    try:
        stats = cloud_monitor._get_container_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloud/images')
@login_required
def get_docker_images():
    """Get Docker images"""
    try:
        images = cloud_monitor.get_docker_images()
        return jsonify(images)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloud/networks')
@login_required
def get_docker_networks():
    """Get Docker networks"""
    try:
        networks = cloud_monitor.get_docker_networks()
        return jsonify(networks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloud/volumes')
@login_required
def get_docker_volumes():
    """Get Docker volumes"""
    try:
        volumes = cloud_monitor.get_docker_volumes()
        return jsonify(volumes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cloud/cost')
@login_required
def get_cost_estimate():
    """Get cost estimation"""
    try:
        cost = cloud_monitor.get_cost_estimate()
        return jsonify(cost)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/topology')
@login_required
def topology_page():
    """Network Topology page"""
    user = get_current_user()
    return render_template('topology.html', user=user)

@app.route('/api/topology/devices')
@login_required
def get_topology_devices():
    """Get all network devices"""
    try:
        topology = network_simulator.get_topology()
        return jsonify(topology)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/ping', methods=['POST'])
@login_required
def ping_device():
    """Ping between devices"""
    try:
        data = request.json
        source_id = int(data.get('source_id'))
        dest_id = int(data.get('dest_id'))
        result = network_simulator.ping_test(source_id, dest_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/traceroute', methods=['POST'])
@login_required
def traceroute_device():
    """Traceroute between devices"""
    try:
        data = request.json
        source_id = int(data.get('source_id'))
        dest_id = int(data.get('dest_id'))
        result = network_simulator.traceroute(source_id, dest_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/routing/<int:device_id>')
@login_required
def get_routing_table(device_id):
    """Get routing table for device"""
    try:
        result = network_simulator.get_routing_table(device_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/interfaces/<int:device_id>')
@login_required
def get_interface_stats(device_id):
    """Get interface statistics"""
    try:
        result = network_simulator.get_interface_stats(device_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topology/statistics')
@login_required
def get_topology_statistics():
    """Get topology statistics"""
    try:
        stats = network_simulator.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/packets')
@login_required
def packets_page():
    """صفحة Packet Analyzer"""
    user = get_current_user()
    return render_template('packets.html', user=user)


# ===== API Routes (Protected) =====

@app.route('/api/metrics/current')
@login_required
def get_current_metrics():
    """Get current system metrics - للمستخدم الحالي فقط"""
    try:
        metrics = system_monitor.get_all_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/metrics/history')
@login_required
def get_metrics_history():
    """Get historical metrics data - للمستخدم الحالي فقط"""
    db_session = None
    try:
        metric_type = request.args.get('type', 'cpu')
        limit = int(request.args.get('limit', 20))
        user_id = session['user_id']
        
        db_session = get_session()
        metrics = db_session.query(SystemMetric)\
            .filter_by(metric_type=metric_type, user_id=user_id)\
            .order_by(SystemMetric.timestamp.desc())\
            .limit(limit)\
            .all()
        
        data = [{
            'timestamp': m.timestamp.isoformat(),
            'value': m.value,
            'unit': m.unit,
            'details': m.details
        } for m in reversed(metrics)]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db_session:
            db_session.close()


@app.route('/api/security/scan', methods=['POST'])
@login_required
def run_security_scan():
    """Trigger a security scan - للمستخدم الحالي"""
    db_session = None
    try:
        data = request.json or {}
        target = data.get('target', 'localhost')
        scan_type = data.get('type', 'quick')
        user_id = session['user_id']
        
        # Security: Validate target to prevent SSRF
        allowed_targets = ['localhost', '127.0.0.1', '::1']
        if target not in allowed_targets:
            return jsonify({
                'error': 'Invalid target. Only localhost scanning is permitted.',
                'allowed_targets': allowed_targets
            }), 403
        
        if scan_type == 'quick':
            result = security_scanner.quick_vulnerability_scan(target)
        else:
            port_range = data.get('port_range', '1-1000')
            result = security_scanner.scan_host(target, port_range)
        
        # Store scan result with user_id
        db_session = get_session()
        scan_record = ScanResult(
            user_id=user_id,
            target=result['target'],
            scan_type=scan_type,
            status=result['status'],
            open_ports=result.get('open_ports', []),
            vulnerabilities=result.get('vulnerabilities', []),
            risk_level=result.get('risk_level', 'low')
        )
        db_session.add(scan_record)
        db_session.commit()
        
        log_activity('security_scan', f'Security scan performed on {target}', user_id=user_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db_session:
            db_session.close()


@app.route('/api/security/scans')
@login_required
def get_scan_history():
    """Get scan history - للمستخدم الحالي فقط"""
    db_session = None
    try:
        limit = int(request.args.get('limit', 10))
        user_id = session['user_id']
        
        db_session = get_session()
        scans = db_session.query(ScanResult)\
            .filter_by(user_id=user_id)\
            .order_by(ScanResult.timestamp.desc())\
            .limit(limit)\
            .all()
        
        data = [{
            'id': s.id,
            'target': s.target,
            'scan_type': s.scan_type,
            'status': s.status,
            'open_ports': s.open_ports,
            'vulnerabilities': s.vulnerabilities,
            'risk_level': s.risk_level,
            'timestamp': s.timestamp.isoformat()
        } for s in scans]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db_session:
            db_session.close()


@app.route('/api/alerts')
@login_required
def get_alerts():
    """Get recent alerts - للمستخدم الحالي فقط"""
    try:
        limit = int(request.args.get('limit', 20))
        severity = request.args.get('severity')
        
        # Get alerts from auto_responder (in-memory)
        alerts = auto_responder.get_alerts(limit, severity)
        
        return jsonify(alerts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@login_required
def acknowledge_alert(alert_id):
    """Acknowledge an alert"""
    try:
        success = auto_responder.acknowledge_alert(alert_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/network/connections')
@login_required
def get_network_connections():
    """Get active network connections"""
    try:
        connections = system_monitor.get_network_connections()
        return jsonify(connections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
@login_required
def get_dashboard_stats():
    """Get overall dashboard statistics - للمستخدم الحالي"""
    db_session = None
    try:
        user_id = session['user_id']
        db_session = get_session()
        
        total_scans = db_session.query(ScanResult).filter_by(user_id=user_id).count()
        critical_alerts = db_session.query(Alert).filter_by(user_id=user_id, severity='critical').count()
        
        recent_scans = db_session.query(ScanResult)\
            .filter_by(user_id=user_id)\
            .order_by(ScanResult.timestamp.desc())\
            .limit(5)\
            .all()
        
        high_risk_scans = sum(1 for s in recent_scans if s.risk_level == 'high')
        
        metrics = system_monitor.get_all_metrics()
        
        stats = {
            'total_scans': total_scans,
            'critical_alerts': critical_alerts,
            'high_risk_scans': high_risk_scans,
            'current_cpu': metrics['cpu']['usage_percent'],
            'current_memory': metrics['memory']['percent'],
            'current_disk': metrics['disk']['percent'],
            'system_status': 'healthy' if metrics['cpu']['usage_percent'] < 80 else 'warning'
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db_session:
            db_session.close()


# ===== Packet Analyzer Routes =====

@app.route('/api/packets/start', methods=['POST'])
@login_required
def start_packet_capture():
    """بدء التقاط الباكتات"""
    db_session = None
    try:
        data = request.json or {}
        interface = data.get('interface', None)
        packet_count = int(data.get('packet_count', 0))
        timeout = int(data.get('timeout', 60)) if data.get('timeout') else None
        
        # إنشاء PacketAnalyzer جديد للمستخدم
        global packet_analyzer
        packet_analyzer = PacketAnalyzer(interface=interface)
        
        # بدء الالتقاط
        success = packet_analyzer.start_capture(packet_count, timeout)
        
        if success:
            # حفظ في قاعدة البيانات
            db_session = get_session()
            try:
                capture = PacketCapture(
                    user_id=session['user_id'],
                    interface=interface or 'all',
                    status='active'
                )
                db_session.add(capture)
                db_session.commit()
                
                log_activity('packet_capture_start', 
                           f'Packet capture started on {interface or "all interfaces"}',
                           user_id=session['user_id'])
                
                return jsonify({
                    'success': True,
                    'message': 'Packet capture started',
                    'capture_id': capture.id
                })
            finally:
                if db_session:
                    db_session.close()
        else:
            return jsonify({'error': 'Failed to start capture'}), 500
            
    except Exception as e:
        if db_session:
            db_session.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/stop', methods=['POST'])
@login_required
def stop_packet_capture():
    """إيقاف التقاط الباكتات"""
    db_session = None
    try:
        packet_analyzer.stop_capture()
        
        # تحديث قاعدة البيانات
        db_session = get_session()
        try:
            user_id = session['user_id']
            capture = db_session.query(PacketCapture)\
                .filter_by(user_id=user_id, status='active')\
                .order_by(PacketCapture.start_time.desc())\
                .first()
            
            if capture:
                stats = packet_analyzer.get_statistics()
                capture.end_time = datetime.now()
                capture.total_packets = stats['total_packets']
                capture.total_bytes = stats['total_bytes']
                capture.protocol_stats = packet_analyzer.get_protocol_distribution()
                capture.suspicious_activities = packet_analyzer.detect_suspicious_activity()
                capture.top_talkers = packet_analyzer.get_top_talkers(10)
                capture.status = 'completed'
                db_session.commit()
            
            log_activity('packet_capture_stop', 'Packet capture stopped',
                       user_id=user_id)
            
            return jsonify({
                'success': True,
                'statistics': stats
            })
        finally:
            if db_session:
                db_session.close()
            
    except Exception as e:
        if db_session:
            db_session.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/status')
@login_required
def get_packet_capture_status():
    """الحصول على حالة الالتقاط"""
    try:
        stats = packet_analyzer.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/recent')
@login_required
def get_recent_packets():
    """الحصول على أحدث الباكتات"""
    try:
        limit = int(request.args.get('limit', 50))
        packets = packet_analyzer.get_recent_packets(limit)
        return jsonify(packets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/analysis')
@login_required
def get_traffic_analysis():
    """الحصول على تحليل الترافيك"""
    try:
        analysis = packet_analyzer.analyze_traffic_pattern()
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/suspicious')
@login_required
def get_suspicious_activities():
    """الحصول على النشاطات المشبوهة"""
    try:
        suspicious = packet_analyzer.detect_suspicious_activity()
        return jsonify(suspicious)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/history')
@login_required
def get_capture_history():
    """الحصول على سجل الالتقاطات"""
    db_session = None
    try:
        limit = int(request.args.get('limit', 10))
        user_id = session['user_id']
        
        db_session = get_session()
        captures = db_session.query(PacketCapture)\
            .filter_by(user_id=user_id)\
            .order_by(PacketCapture.start_time.desc())\
            .limit(limit)\
            .all()
        
        data = [{
            'id': c.id,
            'interface': c.interface,
            'start_time': c.start_time.isoformat(),
            'end_time': c.end_time.isoformat() if c.end_time else None,
            'total_packets': c.total_packets,
            'total_bytes': c.total_bytes,
            'status': c.status,
            'suspicious_count': len(c.suspicious_activities) if c.suspicious_activities else 0
        } for c in captures]
        
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if db_session:
            db_session.close()


@app.route('/api/packets/protocols')
@login_required
def get_protocol_distribution():
    """الحصول على توزيع البروتوكولات"""
    try:
        distribution = packet_analyzer.get_protocol_distribution()
        return jsonify(distribution)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/packets/top-talkers')
@login_required
def get_top_talkers():
    """الحصول على أكثر IPs نشاطاً"""
    try:
        limit = int(request.args.get('limit', 10))
        talkers = packet_analyzer.get_top_talkers(limit)
        return jsonify(talkers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Automated Monitoring Tasks =====

def periodic_system_check():
    """Periodic system metrics check - لكل المستخدمين"""
    db_session = None
    try:
        metrics = system_monitor.get_all_metrics()
        
        # Store metrics for all active users
        db_session = get_session()
        active_users = db_session.query(User).filter_by(is_active=True).all()
        
        for user in active_users:
            # Check for performance issues
            if metrics['cpu']['usage_percent'] > 80:
                auto_responder.create_alert(
                    'performance',
                    'high',
                    f"High CPU usage detected: {metrics['cpu']['usage_percent']}%",
                    {'cpu_data': metrics['cpu'], 'user_id': user.id}
                )
            
            if metrics['memory']['percent'] > 85:
                auto_responder.create_alert(
                    'performance',
                    'high',
                    f"High memory usage detected: {metrics['memory']['percent']}%",
                    {'memory_data': metrics['memory'], 'user_id': user.id}
                )
            
            # Store metrics
            db_session.add(SystemMetric(
                user_id=user.id,
                metric_type='cpu',
                value=metrics['cpu']['usage_percent'],
                unit='percent',
                details=metrics['cpu']
            ))
            db_session.add(SystemMetric(
                user_id=user.id,
                metric_type='memory',
                value=metrics['memory']['percent'],
                unit='percent',
                details=metrics['memory']
            ))
        
        db_session.commit()
        
    except Exception as e:
        print(f"Error in periodic system check: {e}")
        if db_session:
            db_session.rollback()
    finally:
        if db_session:
            db_session.close()


def periodic_security_scan():
    """Periodic security scan - لكل المستخدمين"""
    db_session = None
    try:
        db_session = get_session()
        active_users = db_session.query(User).filter_by(is_active=True).all()
        
        for user in active_users:
            scan_result = security_scanner.quick_vulnerability_scan('localhost')
            
            # Store scan result
            db_session.add(ScanResult(
                user_id=user.id,
                target=scan_result['target'],
                scan_type='vulnerability',
                status=scan_result['status'],
                open_ports=scan_result.get('open_ports', []),
                vulnerabilities=scan_result.get('vulnerabilities', []),
                risk_level=scan_result.get('risk_level', 'low')
            ))
            
            # Create alerts for vulnerabilities
            if scan_result.get('vulnerabilities'):
                for vuln in scan_result['vulnerabilities']:
                    auto_responder.create_alert(
                        'security',
                        vuln['severity'],
                        f"Vulnerability detected: {vuln['name']}",
                        {'vulnerability': vuln, 'target': scan_result['target'], 'user_id': user.id}
                    )
        
        db_session.commit()
        
    except Exception as e:
        print(f"Error in periodic security scan: {e}")
        if db_session:
            db_session.rollback()
    finally:
        if db_session:
            db_session.close()


# Start automation tasks
auto_responder.add_periodic_task(periodic_system_check, 30, 'system_check')
auto_responder.add_periodic_task(periodic_security_scan, 300, 'security_scan')
auto_responder.start()

# ===== Docker Monitor Routes =====
from docker_monitor.monitor import DockerMonitor

docker_monitor = DockerMonitor()

@app.route('/api/docker/status')
@login_required
def docker_status():
    """حالة Docker"""
    try:
        return jsonify({
            'available': docker_monitor.docker_available,
            'system_info': docker_monitor.get_system_info()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/containers')
@login_required
def docker_containers():
    """قائمة الحاويات"""
    try:
        containers = docker_monitor.get_containers()
        return jsonify(containers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/stats')
@login_required
def docker_stats():
    """إحصائيات الحاويات"""
    try:
        stats = docker_monitor.get_all_container_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/images')
@login_required
def docker_images():
    """قائمة الصور"""
    try:
        images = docker_monitor.get_images()
        return jsonify(images)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/docker/metrics')
@login_required
def docker_all_metrics():
    """جميع مقاييس Docker"""
    try:
        metrics = docker_monitor.get_all_metrics()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    log_activity('system_start', 'SentraOS Dashboard started')
    app.run(host='0.0.0.0', port=5000, debug=True)