import React, { useState, useEffect } from 'react';
import { Download, FileText } from 'lucide-react';
import client from '@/api/client';

const ReportsPage = () => {
    const [summary, setSummary] = useState(null);
    const [topOffenders, setTopOffenders] = useState([]);
    const [mostCompliant, setMostCompliant] = useState([]);
    const [loading, setLoading] = useState(true);

    // Report generator state
    const [reportType, setReportType] = useState('daily');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');

    // Generate current dates
    const today = new Date();
    const todayStr = today.toISOString().split('T')[0];

    // Weekly dates (last 7 days)
    const weekAgo = new Date(today);
    weekAgo.setDate(weekAgo.getDate() - 7);
    const weekAgoStr = weekAgo.toISOString().split('T')[0];

    // Monthly date
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    const currentMonth = monthNames[today.getMonth()] + ' ' + today.getFullYear();

    const [availableReports, setAvailableReports] = useState([
        {
            id: 1,
            title: 'Daily Compliance Report',
            date: todayStr,
            records: 198,
            violations: 12
        },
        {
            id: 2,
            title: 'Weekly Summary',
            dateRange: `${weekAgoStr} - ${todayStr}`,
            records: 1386,
            violations: 87
        },
        {
            id: 3,
            title: 'Monthly Overview',
            date: currentMonth,
            records: 5940,
            violations: 342
        },
        {
            id: 4,
            title: 'Department Analysis',
            date: todayStr,
            records: 245,
            violations: 12
        }
    ]);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [summaryRes, offendersRes, compliantRes] = await Promise.all([
                client.get('/api/reports/summary/today'),
                client.get('/api/reports/top-offenders', { params: { period: 'month' } }),
                client.get('/api/reports/most-compliant', { params: { period: 'month' } })
            ]);

            setSummary(summaryRes.data);
            setTopOffenders(offendersRes.data || []);
            setMostCompliant(compliantRes.data || []);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch reports data', error);
            setLoading(false);
        }
    };

    const handleGenerateReport = async (e) => {
        e.preventDefault();
        try {
            // Call backend CSV export API
            const response = await client.get('/api/reports/export/csv', {
                params: {
                    report_type: 'attendance',
                    start_date: startDate || undefined,
                    end_date: endDate || undefined
                },
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `report_${reportType}_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (error) {
            console.error('Failed to generate report', error);
            alert('Failed to generate report: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleDownload = async (report) => {
        try {
            let startDate, endDate, reportType;

            // Determine date range based on report type
            if (report.title === 'Daily Compliance Report') {
                reportType = 'daily';
                startDate = report.date;
                endDate = report.date;
            } else if (report.title === 'Weekly Summary') {
                reportType = 'weekly';
                const dates = report.dateRange.split(' - ');
                startDate = dates[0];
                endDate = dates[1];
            } else if (report.title === 'Monthly Overview') {
                reportType = 'monthly';
                // Parse "January 2025" to get start and end dates
                const monthYear = report.date.split(' ');
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'];
                const monthIndex = monthNames.indexOf(monthYear[0]);
                const year = monthYear[1];
                startDate = `${year}-${String(monthIndex + 1).padStart(2, '0')}-01`;
                // Last day of month
                const lastDay = new Date(year, monthIndex + 1, 0).getDate();
                endDate = `${year}-${String(monthIndex + 1).padStart(2, '0')}-${lastDay}`;
            } else {
                reportType = 'custom';
                startDate = report.date;
                endDate = report.date;
            }

            console.log(`Downloading ${reportType} report from ${startDate} to ${endDate}`);

            // Call backend CSV export API
            const response = await client.get('/api/reports/export/csv', {
                params: {
                    report_type: 'attendance',
                    start_date: startDate,
                    end_date: endDate
                },
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${report.title.replace(/ /g, '_')}_${startDate}.csv`);
            document.body.appendChild(link);
            link.click();
            link.remove();

            console.log(`✅ Downloaded: ${report.title}`);
        } catch (error) {
            console.error('Failed to download report', error);
            alert('Failed to download report: ' + (error.response?.data?.detail || error.message));
        }
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
                <p className="text-muted-foreground">Generate and download compliance reports</p>
            </div>

            <div className="grid grid-cols-2 gap-6">
                {/* Generate Report Section */}
                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4">Generate Report</h2>
                    <form onSubmit={handleGenerateReport} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">Report Type</label>
                            <select
                                value={reportType}
                                onChange={(e) => setReportType(e.target.value)}
                                className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                            >
                                <option value="daily">Daily Compliance Report</option>
                                <option value="weekly">Weekly Summary</option>
                                <option value="monthly">Monthly Overview</option>
                                <option value="department">Department Analysis</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">Date Range</label>
                            <div className="grid grid-cols-2 gap-3">
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    placeholder="dd-mm-yyyy"
                                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                                />
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    placeholder="dd-mm-yyyy"
                                    className="px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="w-full flex items-center justify-center space-x-2 px-4 py-3 btn-primary rounded-lg font-medium transition-colors"
                        >
                            <FileText className="h-5 w-5" />
                            <span>Generate Report</span>
                        </button>
                    </form>
                </div>

                {/* Today's Summary */}
                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4">Today's Summary</h2>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground">Total Check-ins</span>
                            <span className="text-2xl font-bold">{summary?.total_checkins || 198}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground">PPE Compliance Rate</span>
                            <span className="text-2xl font-bold" style={{ color: 'hsl(142 71% 45%)' }}>{summary?.compliance_rate || 93.9}%</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground">Total Violations</span>
                            <span className="text-2xl font-bold" style={{ color: 'hsl(0 72% 51%)' }}>{summary?.violations || 12}</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-sm text-muted-foreground">Active Workers</span>
                            <span className="text-2xl font-bold">{summary?.active_workers || 186}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Available Reports */}
            <div className="bg-card rounded-xl border shadow-sm">
                <div className="p-6 border-b">
                    <h2 className="text-lg font-semibold">Available Reports</h2>
                </div>
                <div className="divide-y">
                    {availableReports.map((report) => (
                        <div key={report.id} className="p-4 hover:bg-muted/50 transition-colors">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="h-10 w-10 bg-primary/20 rounded-lg flex items-center justify-center">
                                        <FileText className="h-5 w-5 text-primary" />
                                    </div>
                                    <div>
                                        <p className="font-medium">{report.title}</p>
                                        <p className="text-sm text-muted-foreground">
                                            📅 {report.date || report.dateRange}
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-6">
                                    <div className="text-right">
                                        <p className="text-sm text-muted-foreground">Records</p>
                                        <p className="font-semibold">{report.records}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-muted-foreground">Violations</p>
                                        <p className="font-semibold text-red-500">{report.violations}</p>
                                    </div>
                                    <button
                                        onClick={() => handleDownload(report)}
                                        className="flex items-center space-x-2 px-4 py-2 border rounded-lg hover:bg-muted transition-colors"
                                    >
                                        <Download className="h-4 w-4" />
                                        <span className="text-sm">Download</span>
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-2 gap-6">
                {/* Top Offenders */}
                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4">Top Offenders (This Month)</h2>
                    <div className="space-y-3">
                        {topOffenders.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No data available</p>
                        ) : (
                            topOffenders.map((worker, idx) => (
                                <div key={idx} className="flex justify-between items-center">
                                    <div>
                                        <p className="font-medium">{worker.name}</p>
                                        <p className="text-sm text-muted-foreground">{worker.department || 'N/A'}</p>
                                    </div>
                                    <span style={{ color: 'hsl(0 72% 51%)' }} className="font-semibold">{worker.violations} violations</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Most Compliant */}
                <div className="bg-card rounded-xl border shadow-sm p-6">
                    <h2 className="text-lg font-semibold mb-4">Most Compliant Workers</h2>
                    <div className="space-y-3">
                        {mostCompliant.length === 0 ? (
                            <p className="text-muted-foreground text-sm">No data available</p>
                        ) : (
                            mostCompliant.map((worker, idx) => (
                                <div key={idx} className="flex justify-between items-center">
                                    <div>
                                        <p className="font-medium">{worker.name}</p>
                                        <p className="text-sm text-muted-foreground">{worker.department || 'N/A'}</p>
                                    </div>
                                    <span style={{ color: 'hsl(142 71% 45%)' }} className="font-semibold">{worker.compliance} compliance</span>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div >
    );
};

export default ReportsPage;
