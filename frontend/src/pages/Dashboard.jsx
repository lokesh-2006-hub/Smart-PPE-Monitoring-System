// Dashboard.jsx - Cleaned up version
import React, { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Camera, History, User, Video, Image } from 'lucide-react';
import client from '@/api/client';
import { cn } from '@/lib/utils';

const Dashboard = () => {
    const [latestScan, setLatestScan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, pass: 0, fail: 0 });
    const [ppeRequirements, setPpeRequirements] = useState(null);

    useEffect(() => {
        const fetchLatest = async () => {
            try {
                // Fetch PPE requirements from settings
                const settingsRes = await client.get('/api/settings');
                if (settingsRes.data && settingsRes.data.system && settingsRes.data.system.ppe_items) {
                    setPpeRequirements(settingsRes.data.system.ppe_items);
                }

                // Fetch daily report for stats
                const reportRes = await client.get('/reports/daily');
                if (reportRes.data) {
                    setStats({
                        total: reportRes.data.total,
                        pass: reportRes.data.pass,
                        fail: reportRes.data.fail,
                    });
                }
                // Fetch latest scan
                const latestRes = await client.get('/attendance/latest');
                if (latestRes.data && latestRes.data.person_name) {
                    setLatestScan({
                        name: latestRes.data.person_name,
                        id: latestRes.data.id,
                        status: latestRes.data.status,
                        source: latestRes.data.source,
                        ppe: latestRes.data.ppe_status,
                    });
                }
                setLoading(false);
            } catch (error) {
                console.error('Failed to fetch data', error);
                setLoading(false);
            }
        };
        fetchLatest();
        const interval = setInterval(fetchLatest, 2000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="p-6 space-y-6">
            <header className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Gate 1 - Live View</h1>
                <div className="flex items-center space-x-2">
                    <span className="flex h-3 w-3 rounded-full bg-green-500 animate-pulse" />
                    <span className="text-sm text-muted-foreground">System Online</span>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Live Feed Area */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="relative aspect-video bg-black rounded-xl overflow-hidden border border-border shadow-lg group">
                        <img
                            src="http://localhost:5000/video_feed"
                            alt="Live PPE Detection Feed"
                            className="w-full h-full object-cover"
                            onError={(e) => {
                                e.target.style.display = 'none';
                                e.target.nextSibling.style.display = 'flex';
                            }}
                        />
                        {/* Fallback if stream is offline */}
                        <div className="absolute inset-0 flex items-center justify-center bg-black hidden">
                            <Camera className="h-16 w-16 text-muted-foreground/20" />
                            <p className="absolute mt-24 text-muted-foreground/40 font-mono">CAMERA FEED SIGNAL LOST</p>
                        </div>
                        {/* Overlay for status */}
                        <div className="absolute top-4 right-4 bg-black/50 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
                            <span className="text-xs font-mono text-white">LIVE • 1080p</span>
                        </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-card p-4 rounded-xl border shadow-sm">
                            <p className="text-sm font-medium text-muted-foreground">Entries Today</p>
                            <p className="text-2xl font-bold">{stats.total}</p>
                        </div>
                        <div className="bg-card p-4 rounded-xl border shadow-sm">
                            <p className="text-sm font-medium text-muted-foreground">Compliance Rate</p>
                            <p className="text-2xl font-bold" style={{ color: 'hsl(142 71% 45%)' }}>
                                {stats.total ? Math.round((stats.pass / stats.total) * 100) : 0}%
                            </p>
                        </div>
                        <div className="bg-card p-4 rounded-xl border shadow-sm">
                            <p className="text-sm font-medium text-muted-foreground">Violations</p>
                            <p className="text-2xl font-bold" style={{ color: 'hsl(0 72% 51%)' }}>{stats.fail}</p>
                        </div>
                    </div>
                </div>

                {/* Latest Scan Card */}
                <div className="bg-card rounded-xl border shadow-sm p-6 flex flex-col h-full">
                    <h2 className="text-lg font-semibold mb-4 flex items-center">
                        <History className="mr-2 h-5 w-5" />
                        Latest Scan
                    </h2>
                    {latestScan ? (
                        <div className="space-y-6 flex-1">
                            <div className="flex items-center space-x-4">
                                <div className="h-20 w-20 rounded-full bg-muted flex items-center justify-center overflow-hidden">
                                    <User className="h-10 w-10 text-muted-foreground" />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold">{latestScan.name}</h3>
                                    <p className="text-sm text-muted-foreground">ID: {latestScan.id || 'Unknown'}</p>
                                    <p className="text-xs text-muted-foreground mt-1">{new Date().toLocaleTimeString()}</p>
                                </div>
                            </div>

                            {/* Overall Status Badge */}
                            <div className={cn(
                                "p-4 rounded-lg border-2 text-center",
                                latestScan.status === 'pass'
                                    ? "bg-green-500/10 border-green-500"
                                    : "bg-red-500/10 border-red-500"
                            )}>
                                <p className="text-sm font-medium text-muted-foreground mb-1">PPE Status</p>
                                <p className={cn(
                                    "text-2xl font-bold uppercase tracking-wider",
                                    latestScan.status === 'pass' ? "text-green-500" : "text-red-500"
                                )}>
                                    {latestScan.status}
                                </p>
                            </div>

                            {/* PPE Checklist */}
                            {latestScan.ppe && Object.keys(latestScan.ppe).length > 0 && (
                                <div className="p-3 bg-muted/50 rounded-lg">
                                    <p className="font-medium mb-2">PPE Checklist</p>
                                    <div className="space-y-1">
                                        {Object.entries(latestScan.ppe)
                                            .filter(([item]) => {
                                                // Only show items that are required in settings
                                                if (!ppeRequirements) return true; // Show all if settings not loaded
                                                return ppeRequirements[item] === true;
                                            })
                                            .map(([item, status]) => (
                                                <div key={item} className="flex items-center justify-between text-sm">
                                                    <span className="capitalize">{item.replace(/_/g, ' ')}</span>
                                                    {status ? (
                                                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                                                    ) : (
                                                        <XCircle className="h-4 w-4 text-red-500" />
                                                    )}
                                                </div>
                                            ))}
                                    </div>
                                </div>
                            )}

                            {/* Source Display */}
                            {latestScan.source && (
                                <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                                    <span className="font-medium">Source</span>
                                    <div className="flex items-center space-x-2">
                                        {latestScan.source === 'camera' && <Camera className="h-4 w-4 text-blue-500" />}
                                        {latestScan.source === 'video' && <Video className="h-4 w-4 text-purple-500" />}
                                        {latestScan.source === 'image' && <Image className="h-4 w-4 text-green-500" />}
                                    </div>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
                            <AlertTriangle className="h-12 w-12 mb-4" />
                            <p className="text-lg font-medium">No recent scans</p>
                            <p className="text-sm">Waiting for first entry...</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
