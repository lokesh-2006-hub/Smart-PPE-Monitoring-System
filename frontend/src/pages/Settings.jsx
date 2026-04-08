import React, { useState, useEffect } from 'react';
import {
    Settings as SettingsIcon, Camera, Bell, Users, Clock, FileBarChart,
    Database, Palette, Mail, Info, Shield, Save, RotateCcw, Plus, Trash2, Edit2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/contexts/ThemeContext';
import client from '@/api/client';

const Settings = () => {
    const [activeTab, setActiveTab] = useState('system');
    const { theme, toggleTheme } = useTheme();

    // System Configuration State
    const [ppeItems, setPpeItems] = useState({
        helmet: true,
        jacket: true,
        gloves: true,
        shoes: true,
        headphone: true
    });
    const [detectionThreshold, setDetectionThreshold] = useState(0.5);
    const [minCompliance, setMinCompliance] = useState(100);
    const [frameRate, setFrameRate] = useState(30);

    // Gate Management State
    const [gates, setGates] = useState([
        { id: 1, name: 'Gate 1 - Main Entrance', cameraUrl: 'http://localhost:5000/video_feed', enabled: true },
        { id: 2, name: 'Gate 2 - Side Entrance', cameraUrl: '', enabled: false }
    ]);

    // Alert Configuration State
    const [alertSettings, setAlertSettings] = useState({
        enableEmail: true,
        enableSMS: false,
        enableInApp: true,
        severity: 'critical',
        autoEscalate: true,
        escalationTime: 5,
        alertEmailList: 'admin@example.com,safety@example.com'
    });

    // Attendance Settings State
    const [attendanceSettings, setAttendanceSettings] = useState({
        startTime: '09:00',
        endTime: '17:00',
        gracePeriod: 15,
        autoClockOut: true,
        autoClockOutTime: '18:00'
    });

    // Report Settings State
    const [reportSettings, setReportSettings] = useState({
        frequency: 'daily',
        format: 'pdf',
        emailList: 'admin@example.com',
        retention: 90
    });

    // Database Settings State
    const [dbSettings, setDbSettings] = useState({
        host: 'localhost',
        database: 'ppe',
        backupSchedule: 'daily',
        lastBackup: '2025-11-22 10:00:00'
    });

    // Appearance Settings State
    const [appearanceSettings, setAppearanceSettings] = useState({
        companyName: 'Smart PPE Compliance',
        dateFormat: 'YYYY-MM-DD',
        language: 'en'
    });

    // Notification Settings State
    const [notificationSettings, setNotificationSettings] = useState({
        smtpHost: 'smtp.gmail.com',
        smtpPort: 587,
        smtpUser: '',
        smtpPassword: '',
        smsGateway: ''
    });

    const tabs = [
        { id: 'system', label: 'System Configuration', icon: SettingsIcon },
        { id: 'gates', label: 'Gate Management', icon: Camera },
        { id: 'alerts', label: 'Alert Configuration', icon: Bell },
        { id: 'users', label: 'User Management', icon: Users },
        { id: 'attendance', label: 'Attendance Settings', icon: Clock },
        { id: 'reports', label: 'Report Settings', icon: FileBarChart },
        { id: 'database', label: 'Database & Backup', icon: Database },
        { id: 'appearance', label: 'Appearance', icon: Palette },
        { id: 'notifications', label: 'Notifications', icon: Mail },
        { id: 'info', label: 'System Information', icon: Info }
    ];

    // Load settings from backend on mount
    useEffect(() => {
        const loadSettings = async () => {
            try {
                const response = await client.get('/api/settings');
                const data = response.data;

                // Update state with fetched settings
                if (data.system) {
                    if (data.system.ppe_items) setPpeItems(data.system.ppe_items);
                    if (data.system.detection_threshold !== undefined) setDetectionThreshold(data.system.detection_threshold);
                    if (data.system.min_compliance !== undefined) setMinCompliance(data.system.min_compliance);
                    if (data.system.frame_rate !== undefined) setFrameRate(data.system.frame_rate);
                }
                if (data.alerts) {
                    setAlertSettings(prev => ({
                        enableEmail: data.alerts.enable_email ?? prev.enableEmail,
                        enableSMS: data.alerts.enable_sms ?? prev.enableSMS,
                        enableInApp: data.alerts.enable_in_app ?? prev.enableInApp,
                        severity: data.alerts.severity ?? prev.severity,
                        autoEscalate: data.alerts.auto_escalate ?? prev.autoEscalate,
                        escalationTime: data.alerts.escalation_time ?? prev.escalationTime,
                        alertEmailList: data.alerts.alert_email_list ?? prev.alertEmailList
                    }));
                }
                if (data.reports) {
                    setReportSettings(prev => ({
                        frequency: data.reports.frequency ?? prev.frequency,
                        format: data.reports.format ?? prev.format,
                        emailList: data.reports.email_list ?? prev.emailList,
                        retention: data.reports.retention ?? prev.retention
                    }));
                }
                if (data.notifications) {
                    setNotificationSettings(prev => ({
                        smtpHost: data.notifications.smtp_host ?? prev.smtpHost,
                        smtpPort: data.notifications.smtp_port ?? prev.smtpPort,
                        smtpUser: data.notifications.smtp_user ?? prev.smtpUser,
                        smtpPassword: data.notifications.smtp_password ?? prev.smtpPassword,
                        smsGateway: data.notifications.sms_gateway ?? prev.smsGateway
                    }));
                }
                if (data.gates && data.gates.list) {
                    setGates(data.gates.list);
                }
            } catch (error) {
                console.error('Failed to load settings:', error);
            }
        };

        loadSettings();
    }, []);

    const handleSave = async (section) => {
        try {
            let settings = {};

            if (section === 'system') {
                settings = {
                    ppe_items: ppeItems,
                    detection_threshold: detectionThreshold,
                    min_compliance: minCompliance,
                    frame_rate: frameRate
                };
            } else if (section === 'alerts') {
                settings = {
                    enable_email: alertSettings.enableEmail,
                    enable_sms: alertSettings.enableSMS,
                    enable_in_app: alertSettings.enableInApp,
                    severity: alertSettings.severity,
                    auto_escalate: alertSettings.autoEscalate,
                    escalation_time: alertSettings.escalationTime,
                    alert_email_list: alertSettings.alertEmailList
                };
            } else if (section === 'reports') {
                settings = {
                    frequency: reportSettings.frequency,
                    format: reportSettings.format,
                    email_list: reportSettings.emailList,
                    retention: reportSettings.retention
                };
                settings = {
                    smtp_host: notificationSettings.smtpHost,
                    smtp_port: notificationSettings.smtpPort,
                    smtp_user: notificationSettings.smtpUser,
                    smtp_password: notificationSettings.smtpPassword,
                    sms_gateway: notificationSettings.smsGateway
                };
            } else if (section === 'gates') {
                settings = { list: gates };
            }

            await client.put('/api/settings', {
                category: section,
                settings: settings
            });

            alert('Settings saved successfully!');
        } catch (error) {
            console.error('Failed to save settings:', error);
            alert('Failed to save settings. Please try again.');
        }
    };

    return (
        <div className="p-6 h-full">
            <div className="mb-6">
                <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
                <p className="text-muted-foreground mt-1">Manage your system configuration and preferences</p>
            </div>

            <div className="grid grid-cols-12 gap-6 h-[calc(100vh-180px)]">
                {/* Vertical Tab Navigation */}
                <div className="col-span-3 bg-card border rounded-xl p-4 overflow-y-auto">
                    <nav className="space-y-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={cn(
                                    "w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-colors",
                                    activeTab === tab.id
                                        ? "bg-primary text-primary-foreground"
                                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                                )}
                            >
                                <tab.icon className="h-5 w-5 flex-shrink-0" />
                                <span className="font-medium text-sm">{tab.label}</span>
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Content Area */}
                <div className="col-span-9 bg-card border rounded-xl p-6 overflow-y-auto">
                    {/* System Configuration */}
                    {activeTab === 'system' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">System Configuration</h2>
                                <p className="text-sm text-muted-foreground">Configure PPE requirements and detection settings</p>
                            </div>

                            <div className="border-t pt-6">
                                <h3 className="text-lg font-semibold mb-4">PPE Requirements</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    {Object.entries(ppeItems).map(([item, enabled]) => (
                                        <div key={item} className="flex items-center justify-between p-3 border rounded-lg">
                                            <span className="capitalize font-medium">{item}</span>
                                            <button
                                                onClick={() => setPpeItems({ ...ppeItems, [item]: !enabled })}
                                                className={cn(
                                                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                    enabled ? "bg-primary" : "bg-muted"
                                                )}
                                            >
                                                <span
                                                    className={cn(
                                                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                        enabled ? "translate-x-6" : "translate-x-1"
                                                    )}
                                                />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="border-t pt-6">
                                <h3 className="text-lg font-semibold mb-4">Detection Settings</h3>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Confidence Threshold: {detectionThreshold.toFixed(1)}
                                        </label>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.1"
                                            value={detectionThreshold}
                                            onChange={(e) => setDetectionThreshold(parseFloat(e.target.value))}
                                            className="w-full"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">
                                            Minimum confidence level for PPE detection
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Minimum Compliance: {minCompliance}%
                                        </label>
                                        <input
                                            type="range"
                                            min="60"
                                            max="100"
                                            step="10"
                                            value={minCompliance}
                                            onChange={(e) => setMinCompliance(parseInt(e.target.value))}
                                            className="w-full"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">
                                            Required compliance percentage to pass
                                        </p>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-2">
                                            Frame Processing Rate: {frameRate} FPS
                                        </label>
                                        <input
                                            type="range"
                                            min="10"
                                            max="60"
                                            step="5"
                                            value={frameRate}
                                            onChange={(e) => setFrameRate(parseInt(e.target.value))}
                                            className="w-full"
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('system')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                                <button className="flex items-center space-x-2 px-4 py-2 border rounded-lg hover:bg-muted">
                                    <RotateCcw className="h-4 w-4" />
                                    <span>Reset</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Gate Management */}
                    {activeTab === 'gates' && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-bold mb-1">Gate Management</h2>
                                    <p className="text-sm text-muted-foreground">Configure monitoring gates and camera streams</p>
                                </div>
                                <button className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Plus className="h-4 w-4" />
                                    <span>Add Gate</span>
                                </button>
                            </div>

                            <div className="border-t pt-6 space-y-4">
                                {gates.map((gate, index) => (
                                    <div key={gate.id} className="border rounded-lg p-4 space-y-4">
                                        <div className="flex justify-between items-start">
                                            <div className="flex-1 space-y-2">
                                                <label className="text-sm font-medium">Gate Name</label>
                                                <input 
                                                    type="text"
                                                    value={gate.name}
                                                    onChange={(e) => {
                                                        const newGates = [...gates];
                                                        newGates[index].name = e.target.value;
                                                        setGates(newGates);
                                                    }}
                                                    className="w-full px-3 py-2 border rounded-lg bg-background"
                                                />
                                            </div>
                                            <div className="ml-4 flex items-center space-x-2">
                                                <button
                                                    onClick={() => {
                                                        const newGates = [...gates];
                                                        newGates[index].enabled = !newGates[index].enabled;
                                                        setGates(newGates);
                                                    }}
                                                    className={cn(
                                                        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                        gate.enabled ? "bg-primary" : "bg-muted"
                                                    )}
                                                >
                                                    <span className={cn(
                                                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                        gate.enabled ? "translate-x-6" : "translate-x-1"
                                                    )} />
                                                </button>
                                                <span className="text-sm font-medium">{gate.enabled ? 'Enabled' : 'Disabled'}</span>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-2">
                                            <label className="text-sm font-medium">Stream URL (MJPEG)</label>
                                            <input 
                                                type="text"
                                                value={gate.cameraUrl}
                                                placeholder="http://10.x.x.x:5000/video_feed"
                                                onChange={(e) => {
                                                    const newGates = [...gates];
                                                    newGates[index].cameraUrl = e.target.value;
                                                    setGates(newGates);
                                                }}
                                                className="w-full px-3 py-2 border rounded-lg bg-background font-mono text-xs"
                                            />
                                            <p className="text-[10px] text-muted-foreground">
                                                Use your Raspberry Pi's IP address and port 5000.
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('gates')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Gates Configuration</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Alert Configuration */}
                    {activeTab === 'alerts' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Alert Configuration</h2>
                                <p className="text-sm text-muted-foreground">Configure alert rules and notification preferences</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Notification Channels</h3>
                                    <div className="space-y-3">
                                        {[
                                            { key: 'enableEmail', label: 'Email Notifications' },
                                            { key: 'enableSMS', label: 'SMS Notifications' },
                                            { key: 'enableInApp', label: 'In-App Notifications' }
                                        ].map(({ key, label }) => (
                                            <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                                                <span className="font-medium">{label}</span>
                                                <button
                                                    onClick={() => setAlertSettings({ ...alertSettings, [key]: !alertSettings[key] })}
                                                    className={cn(
                                                        "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                        alertSettings[key] ? "bg-primary" : "bg-muted"
                                                    )}
                                                >
                                                    <span className={cn(
                                                        "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                        alertSettings[key] ? "translate-x-6" : "translate-x-1"
                                                    )} />
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Alert Settings</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Default Severity</label>
                                            <select
                                                value={alertSettings.severity}
                                                onChange={(e) => setAlertSettings({ ...alertSettings, severity: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            >
                                                <option value="info">Info</option>
                                                <option value="warning">Warning</option>
                                                <option value="critical">Critical</option>
                                            </select>
                                        </div>

                                        <div className="flex items-center justify-between p-3 border rounded-lg">
                                            <div>
                                                <span className="font-medium block">Auto-escalate Alerts</span>
                                                <span className="text-sm text-muted-foreground">Automatically escalate unresolved alerts</span>
                                            </div>
                                            <button
                                                onClick={() => setAlertSettings({ ...alertSettings, autoEscalate: !alertSettings.autoEscalate })}
                                                className={cn(
                                                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                    alertSettings.autoEscalate ? "bg-primary" : "bg-muted"
                                                )}
                                            >
                                                <span className={cn(
                                                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                    alertSettings.autoEscalate ? "translate-x-6" : "translate-x-1"
                                                )} />
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Email Recipients for Alerts</h3>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Alert Email List</label>
                                        <textarea
                                            value={alertSettings.alertEmailList}
                                            onChange={(e) => setAlertSettings({ ...alertSettings, alertEmailList: e.target.value })}
                                            placeholder="admin@example.com,safety@example.com"
                                            rows={3}
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        />
                                        <p className="text-xs text-muted-foreground mt-1">
                                            Enter email addresses separated by commas. These recipients will receive real-time PPE violation alerts.
                                        </p>
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('alerts')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* User Management */}
                    {activeTab === 'users' && (
                        <div className="space-y-6">
                            <div className="flex justify-between items-start">
                                <div>
                                    <h2 className="text-2xl font-bold mb-1">User Management</h2>
                                    <p className="text-sm text-muted-foreground">Manage system users and permissions</p>
                                </div>
                                <button className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Plus className="h-4 w-4" />
                                    <span>Add User</span>
                                </button>
                            </div>

                            <div className="border-t pt-6">
                                <div className="border rounded-lg overflow-hidden">
                                    <table className="w-full">
                                        <thead className="bg-muted/50">
                                            <tr>
                                                <th className="text-left p-3 font-semibold">Name</th>
                                                <th className="text-left p-3 font-semibold">Email</th>
                                                <th className="text-left p-3 font-semibold">Role</th>
                                                <th className="text-left p-3 font-semibold">Status</th>
                                                <th className="text-left p-3 font-semibold">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {[
                                                { name: 'Admin User', email: 'admin@example.com', role: 'Admin', status: 'Active' },
                                                { name: 'Gate Operator', email: 'gate@example.com', role: 'Gate Operator', status: 'Active' },
                                                { name: 'Safety Manager', email: 'safety@example.com', role: 'Safety Manager', status: 'Active' }
                                            ].map((user, idx) => (
                                                <tr key={idx} className="border-t">
                                                    <td className="p-3">{user.name}</td>
                                                    <td className="p-3 text-muted-foreground">{user.email}</td>
                                                    <td className="p-3">
                                                        <span className="text-xs px-2 py-1 bg-primary/10 text-primary rounded-full">
                                                            {user.role}
                                                        </span>
                                                    </td>
                                                    <td className="p-3">
                                                        <span className="text-xs px-2 py-1 bg-green-500/10 text-green-500 rounded-full">
                                                            {user.status}
                                                        </span>
                                                    </td>
                                                    <td className="p-3">
                                                        <div className="flex space-x-2">
                                                            <button className="p-1 hover:bg-muted rounded">
                                                                <Edit2 className="h-4 w-4" />
                                                            </button>
                                                            <button className="p-1 hover:bg-destructive/10 text-destructive rounded">
                                                                <Trash2 className="h-4 w-4" />
                                                            </button>
                                                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Attendance Settings */}
                    {activeTab === 'attendance' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Attendance Settings</h2>
                                <p className="text-sm text-muted-foreground">Configure working hours and attendance rules</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Working Hours</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Start Time</label>
                                            <input
                                                type="time"
                                                value={attendanceSettings.startTime}
                                                onChange={(e) => setAttendanceSettings({ ...attendanceSettings, startTime: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2">End Time</label>
                                            <input
                                                type="time"
                                                value={attendanceSettings.endTime}
                                                onChange={(e) => setAttendanceSettings({ ...attendanceSettings, endTime: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Attendance Rules</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">
                                                Grace Period: {attendanceSettings.gracePeriod} minutes
                                            </label>
                                            <input
                                                type="range"
                                                min="0"
                                                max="30"
                                                step="5"
                                                value={attendanceSettings.gracePeriod}
                                                onChange={(e) => setAttendanceSettings({ ...attendanceSettings, gracePeriod: parseInt(e.target.value) })}
                                                className="w-full"
                                            />
                                        </div>

                                        <div className="flex items-center justify-between p-3 border rounded-lg">
                                            <div>
                                                <span className="font-medium block">Auto Clock-Out</span>
                                                <span className="text-sm text-muted-foreground">Automatically clock out workers at end of shift</span>
                                            </div>
                                            <button
                                                onClick={() => setAttendanceSettings({ ...attendanceSettings, autoClockOut: !attendanceSettings.autoClockOut })}
                                                className={cn(
                                                    "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                    attendanceSettings.autoClockOut ? "bg-primary" : "bg-muted"
                                                )}
                                            >
                                                <span className={cn(
                                                    "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                    attendanceSettings.autoClockOut ? "translate-x-6" : "translate-x-1"
                                                )} />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('attendance')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Report Settings */}
                    {activeTab === 'reports' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Report Settings</h2>
                                <p className="text-sm text-muted-foreground">Configure automated report generation and distribution</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Report Frequency</label>
                                        <select
                                            value={reportSettings.frequency}
                                            onChange={(e) => setReportSettings({ ...reportSettings, frequency: e.target.value })}
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        >
                                            <option value="daily">Daily</option>
                                            <option value="weekly">Weekly</option>
                                            <option value="monthly">Monthly</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Report Format</label>
                                        <select
                                            value={reportSettings.format}
                                            onChange={(e) => setReportSettings({ ...reportSettings, format: e.target.value })}
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        >
                                            <option value="pdf">PDF</option>
                                            <option value="csv">CSV</option>
                                            <option value="excel">Excel</option>
                                        </select>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Email Distribution List</label>
                                    <textarea
                                        value={reportSettings.emailList}
                                        onChange={(e) => setReportSettings({ ...reportSettings, emailList: e.target.value })}
                                        placeholder="Enter email addresses separated by commas"
                                        rows={3}
                                        className="w-full px-3 py-2 border rounded-lg bg-background"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">
                                        Data Retention: {reportSettings.retention} days
                                    </label>
                                    <input
                                        type="range"
                                        min="30"
                                        max="365"
                                        step="30"
                                        value={reportSettings.retention}
                                        onChange={(e) => setReportSettings({ ...reportSettings, retention: parseInt(e.target.value) })}
                                        className="w-full"
                                    />
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('reports')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Database & Backup */}
                    {activeTab === 'database' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Database & Backup</h2>
                                <p className="text-sm text-muted-foreground">Manage database connections and backup settings</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Database Connection</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Host</label>
                                            <input
                                                type="text"
                                                value={dbSettings.host}
                                                disabled
                                                className="w-full px-3 py-2 border rounded-lg bg-muted"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Database</label>
                                            <input
                                                type="text"
                                                value={dbSettings.database}
                                                disabled
                                                className="w-full px-3 py-2 border rounded-lg bg-muted"
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Backup Settings</h3>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">Backup Schedule</label>
                                            <select
                                                value={dbSettings.backupSchedule}
                                                onChange={(e) => setDbSettings({ ...dbSettings, backupSchedule: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            >
                                                <option value="hourly">Hourly</option>
                                                <option value="daily">Daily</option>
                                                <option value="weekly">Weekly</option>
                                            </select>
                                        </div>

                                        <div className="p-4 border rounded-lg bg-muted/50">
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <p className="font-medium">Last Backup</p>
                                                    <p className="text-sm text-muted-foreground">{dbSettings.lastBackup}</p>
                                                </div>
                                                <button className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                                    Backup Now
                                                </button>
                                            </div>
                                        </div>

                                        <button className="w-full px-4 py-2 border border-primary text-primary rounded-lg hover:bg-primary/10">
                                            Export All Data
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('database')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Appearance */}
                    {activeTab === 'appearance' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Appearance & Preferences</h2>
                                <p className="text-sm text-muted-foreground">Customize the look and feel of the application</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-medium mb-2">Company Name</label>
                                    <input
                                        type="text"
                                        value={appearanceSettings.companyName}
                                        onChange={(e) => setAppearanceSettings({ ...appearanceSettings, companyName: e.target.value })}
                                        className="w-full px-3 py-2 border rounded-lg bg-background"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-2">Theme</label>
                                    <div className="flex items-center justify-between p-3 border rounded-lg">
                                        <div>
                                            <span className="font-medium block">Dark Mode</span>
                                            <span className="text-sm text-muted-foreground">Current: {theme}</span>
                                        </div>
                                        <button
                                            onClick={toggleTheme}
                                            className={cn(
                                                "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
                                                theme === 'dark' ? "bg-primary" : "bg-muted"
                                            )}
                                        >
                                            <span className={cn(
                                                "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                                                theme === 'dark' ? "translate-x-6" : "translate-x-1"
                                            )} />
                                        </button>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Date Format</label>
                                        <select
                                            value={appearanceSettings.dateFormat}
                                            onChange={(e) => setAppearanceSettings({ ...appearanceSettings, dateFormat: e.target.value })}
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        >
                                            <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                                            <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                                            <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Language</label>
                                        <select
                                            value={appearanceSettings.language}
                                            onChange={(e) => setAppearanceSettings({ ...appearanceSettings, language: e.target.value })}
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        >
                                            <option value="en">English</option>
                                            <option value="es">Spanish</option>
                                            <option value="fr">French</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('appearance')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* Notifications */}
                    {activeTab === 'notifications' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">Notification Settings</h2>
                                <p className="text-sm text-muted-foreground">Configure email and SMS notification services</p>
                            </div>

                            <div className="border-t pt-6 space-y-6">
                                <div>
                                    <h3 className="text-lg font-semibold mb-4">Email (SMTP) Configuration</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium mb-2">SMTP Host</label>
                                            <input
                                                type="text"
                                                value={notificationSettings.smtpHost}
                                                onChange={(e) => setNotificationSettings({ ...notificationSettings, smtpHost: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium mb-2">SMTP Port</label>
                                            <input
                                                type="number"
                                                value={notificationSettings.smtpPort}
                                                onChange={(e) => setNotificationSettings({ ...notificationSettings, smtpPort: e.target.value })}
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                        </div>
                                        <div className="col-span-2">
                                            <label className="block text-sm font-medium mb-2">SMTP Username</label>
                                            <input
                                                type="email"
                                                value={notificationSettings.smtpUser}
                                                onChange={(e) => setNotificationSettings({ ...notificationSettings, smtpUser: e.target.value })}
                                                placeholder="email@example.com"
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                        </div>
                                        <div className="col-span-2">
                                            <label className="block text-sm font-medium mb-2">SMTP Password</label>
                                            <input
                                                type="password"
                                                value={notificationSettings.smtpPassword}
                                                onChange={(e) => setNotificationSettings({ ...notificationSettings, smtpPassword: e.target.value })}
                                                placeholder="App Password or SMTP Password"
                                                className="w-full px-3 py-2 border rounded-lg bg-background"
                                            />
                                            <p className="text-xs text-muted-foreground mt-1">
                                                For Gmail, use an App Password (not your regular password)
                                            </p>
                                        </div>
                                    </div>
                                    <button className="mt-4 px-4 py-2 border rounded-lg hover:bg-muted">
                                        Test Email Connection
                                    </button>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold mb-4">SMS Gateway</h3>
                                    <div>
                                        <label className="block text-sm font-medium mb-2">Gateway API Key</label>
                                        <input
                                            type="password"
                                            value={notificationSettings.smsGateway}
                                            onChange={(e) => setNotificationSettings({ ...notificationSettings, smsGateway: e.target.value })}
                                            placeholder="Enter API key"
                                            className="w-full px-3 py-2 border rounded-lg bg-background"
                                        />
                                    </div>
                                    <button className="mt-4 px-4 py-2 border rounded-lg hover:bg-muted">
                                        Test SMS Connection
                                    </button>
                                </div>
                            </div>

                            <div className="flex space-x-3 pt-4 border-t">
                                <button onClick={() => handleSave('notifications')} className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90">
                                    <Save className="h-4 w-4" />
                                    <span>Save Changes</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {/* System Information */}
                    {activeTab === 'info' && (
                        <div className="space-y-6">
                            <div>
                                <h2 className="text-2xl font-bold mb-1">System Information</h2>
                                <p className="text-sm text-muted-foreground">View system details and status</p>
                            </div>

                            <div className="border-t pt-6 space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="p-4 border rounded-lg">
                                        <p className="text-sm text-muted-foreground mb-1">Version</p>
                                        <p className="text-xl font-bold">v1.0.0</p>
                                    </div>
                                    <div className="p-4 border rounded-lg">
                                        <p className="text-sm text-muted-foreground mb-1">System Status</p>
                                        <div className="flex items-center space-x-2">
                                            <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                                            <p className="text-xl font-bold">Online</p>
                                        </div>
                                    </div>
                                    <div className="p-4 border rounded-lg">
                                        <p className="text-sm text-muted-foreground mb-1">Backend API</p>
                                        <div className="flex items-center space-x-2">
                                            <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                                            <p className="text-xl font-bold">Connected</p>
                                        </div>
                                    </div>
                                    <div className="p-4 border rounded-lg">
                                        <p className="text-sm text-muted-foreground mb-1">Database</p>
                                        <div className="flex items-center space-x-2">
                                            <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                                            <p className="text-xl font-bold">Connected</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="p-4 border rounded-lg space-y-2">
                                    <h3 className="font-semibold">License Information</h3>
                                    <p className="text-sm text-muted-foreground">License Type: Enterprise</p>
                                    <p className="text-sm text-muted-foreground">Valid Until: 2026-12-31</p>
                                    <p className="text-sm text-muted-foreground">Licensed To: Smart PPE Inc.</p>
                                </div>

                                <div className="p-4 border rounded-lg space-y-2">
                                    <h3 className="font-semibold">Support Contact</h3>
                                    <p className="text-sm text-muted-foreground">Email: support@smartppe.com</p>
                                    <p className="text-sm text-muted-foreground">Phone: +1 (555) 123-4567</p>
                                    <p className="text-sm text-muted-foreground">Website: www.smartppe.com</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Settings;
