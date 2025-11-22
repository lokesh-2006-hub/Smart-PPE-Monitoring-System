import React, { useState, useEffect } from 'react';
import { Calendar } from 'lucide-react';
import client from '@/api/client';
import SearchInput from '@/components/SearchInput';
import StatusBadge from '@/components/StatusBadge';

const AttendancePage = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

    useEffect(() => {
        fetchLogs();
    }, [selectedDate, search]);

    const fetchLogs = async () => {
        try {
            const res = await client.get('/api/attendance/logs', {
                params: {
                    date: selectedDate,
                    limit: 100
                }
            });
            let data = res.data || [];

            // Filter by search if provided
            if (search) {
                data = data.filter(log =>
                    log.worker_name?.toLowerCase().includes(search.toLowerCase()) ||
                    log.worker_id?.toString().includes(search)
                );
            }

            setLogs(data);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch attendance logs', error);
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Attendance Management</h1>
                <p className="text-muted-foreground">Track worker attendance and PPE compliance</p>
            </div>

            {/* Attendance Logs */}
            <div className="bg-card rounded-xl border shadow-sm">
                <div className="p-4 border-b">
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-semibold">Attendance Logs</h2>
                        <div className="flex items-center space-x-2">
                            <Calendar className="h-5 w-5 text-muted-foreground" />
                            <input
                                type="date"
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.target.value)}
                                className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                    </div>
                    <SearchInput
                        value={search}
                        onChange={setSearch}
                        placeholder="Search workers..."
                    />
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-muted/50">
                            <tr>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Worker ID</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Name</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Time In</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Time Out</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">PPE Status</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Location</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="6" className="px-4 py-8 text-center text-muted-foreground">
                                        Loading...
                                    </td>
                                </tr>
                            ) : logs.length === 0 ? (
                                <tr>
                                    <td colSpan="6" className="px-4 py-8 text-center text-muted-foreground">
                                        No attendance records found for this date
                                    </td>
                                </tr>
                            ) : (
                                logs.map((log) => (
                                    <tr key={log.id} className="border-t hover:bg-muted/50 transition-colors">
                                        <td className="px-4 py-3 text-sm">{log.employee_id || log.worker_id || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm font-medium text-blue-600">{log.worker_name}</td>
                                        <td className="px-4 py-3 text-sm">{log.time_in || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm">{log.time_out}</td>
                                        <td className="px-4 py-3 text-sm">
                                            <StatusBadge status={log.ppe_status} />
                                        </td>
                                        <td className="px-4 py-3 text-sm">{log.location || log.gate || 'N/A'}</td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default AttendancePage;
