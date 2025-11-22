import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import client from '@/api/client';
import StatusBadge from '@/components/StatusBadge';

const AlertsPage = () => {
    const [alerts, setAlerts] = useState([]);
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('active');

    useEffect(() => {
        fetchData();
    }, [filter]);

    const fetchData = async () => {
        try {
            const [alertsRes, statsRes] = await Promise.all([
                client.get('/api/alerts', { params: { status: filter, limit: 50 } }),
                client.get('/api/alerts/stats')
            ]);

            setAlerts(alertsRes.data || []);
            setStats(statsRes.data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch alerts', error);
            setLoading(false);
        }
    };

    const handleResolve = async (alertId) => {
        try {
            await client.put(`/api/alerts/${alertId}/resolve`, {
                resolution_note: "Resolved from dashboard"
            });
            fetchData();
        } catch (error) {
            console.error('Failed to resolve alert', error);
        }
    };

    const getSeverityIcon = (severity) => {
        if (severity === 'critical') return <AlertTriangle className="h-5 w-5 text-red-500" />;
        if (severity === 'warning') return <AlertTriangle className="h-5 w-5 text-amber-500" />;
        return <AlertTriangle className="h-5 w-5 text-blue-500" />;
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Alert System</h1>
                <p className="text-muted-foreground">Monitor PPE violations and security alerts</p>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-3 gap-6">
                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Active Alerts</p>
                            <p className="text-3xl font-bold">{stats?.active_alerts || 0}</p>
                        </div>
                        <div className="h-12 w-12 bg-red-500/20 rounded-full flex items-center justify-center">
                            <AlertTriangle className="h-6 w-6 text-red-500" />
                        </div>
                    </div>
                </div>

                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Resolved Today</p>
                            <p className="text-3xl font-bold">{stats?.resolved_today || 0}</p>
                        </div>
                        <div className="h-12 w-12 bg-green-500/20 rounded-full flex items-center justify-center">
                            <CheckCircle className="h-6 w-6 text-green-500" />
                        </div>
                    </div>
                </div>

                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-muted-foreground">Avg Response Time</p>
                            <p className="text-3xl font-bold">{stats?.avg_response_time || '0m'}</p>
                        </div>
                        <div className="h-12 w-12 bg-amber-500/20 rounded-full flex items-center justify-center">
                            <Clock className="h-6 w-6 text-amber-500" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Alert History */}
            <div className="bg-card rounded-xl border shadow-sm">
                <div className="p-4 border-b">
                    <div className="flex justify-between items-center">
                        <h2 className="text-lg font-semibold">Alert History</h2>
                        <div className="flex space-x-2">
                            <button
                                onClick={() => setFilter('active')}
                                className={`px-4 py-2 rounded-lg transition-colors ${filter === 'active'
                                    ? 'btn-primary'
                                    : 'bg-muted text-foreground hover:bg-muted/80'
                                    }`}
                            >
                                Active
                            </button>
                            <button
                                onClick={() => setFilter('resolved')}
                                className={`px-4 py-2 rounded-lg transition-colors ${filter === 'resolved'
                                    ? 'btn-primary'
                                    : 'bg-muted text-foreground hover:bg-muted/80'
                                    }`}
                            >
                                Resolved
                            </button>
                        </div>
                    </div>
                </div>

                <div className="divide-y">
                    {loading ? (
                        <div className="p-8 text-center text-muted-foreground">Loading...</div>
                    ) : alerts.length === 0 ? (
                        <div className="p-8 text-center text-muted-foreground">No alerts found</div>
                    ) : (
                        alerts.map((alert) => (
                            <div key={alert.id} className="p-4 hover:bg-muted/50 transition-colors">
                                <div className="flex items-start justify-between">
                                    <div className="flex space-x-3 flex-1">
                                        {getSeverityIcon(alert.severity)}
                                        <div className="flex-1">
                                            {/* Worker Information */}
                                            <div className="flex items-center space-x-3 mb-2">
                                                {/* Worker Avatar/Initial */}
                                                <div className="h-10 w-10 bg-primary/10 rounded-full flex items-center justify-center text-primary font-semibold">
                                                    {alert.worker_name ? alert.worker_name.charAt(0).toUpperCase() : '?'}
                                                </div>

                                                {/* Worker Details */}
                                                <div>
                                                    <p className="font-semibold text-foreground">
                                                        {alert.worker_name || 'Unknown Worker'}
                                                    </p>
                                                    <p className="text-xs text-muted-foreground">
                                                        Worker ID: {alert.employee_id || alert.worker_id || 'N/A'}
                                                    </p>
                                                </div>
                                            </div>

                                            {/* Alert Badges */}
                                            <div className="flex items-center space-x-2 mb-1">
                                                <StatusBadge status={alert.severity} />
                                                <StatusBadge status={alert.status} />
                                            </div>

                                            {/* Alert Message */}
                                            <p className="font-medium">{alert.message}</p>

                                            {/* Metadata */}
                                            <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                                                <span>⏰ {alert.time_ago || 'Recently'}</span>
                                                {alert.location && <span>📍 {alert.location}</span>}
                                                {alert.gate && alert.gate !== alert.location && <span>🚪 {alert.gate}</span>}
                                            </div>
                                        </div>
                                    </div>
                                    {alert.status === 'active' && (
                                        <button
                                            onClick={() => handleResolve(alert.id)}
                                            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm transition-colors"
                                        >
                                            Resolve
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};

export default AlertsPage;
