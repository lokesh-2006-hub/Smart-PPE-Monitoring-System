import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Users, FileBarChart, Settings, LogOut, Shield, ClipboardList, AlertTriangle, Sun, Moon, User } from 'lucide-react';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Reports from './pages/Reports';
import Workers from './pages/Workers';
import Attendance from './pages/Attendance';
import Alerts from './pages/Alerts';
import Announcements from './pages/Announcements';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import { UserRoleProvider, useUserRole } from './contexts/UserRoleContext';
import SettingsPage from './pages/Settings';
import { cn } from '@/lib/utils';

// Navigation configuration with role-based permissions
const navigationItems = [
    { icon: LayoutDashboard, label: "Live View", to: "/dashboard", roles: ['admin', 'gate_operator', 'safety_manager'] },
    { icon: Users, label: "Workers", to: "/workers", roles: ['admin'] },
    { icon: ClipboardList, label: "Attendance", to: "/attendance", roles: ['admin', 'gate_operator', 'safety_manager'] },
    { icon: FileBarChart, label: "Reports", to: "/reports", roles: ['admin', 'safety_manager'] },
    { icon: AlertTriangle, label: "Alerts", to: "/alerts", roles: ['admin', 'gate_operator', 'safety_manager'] },
    { icon: Settings, label: "Settings", to: "/settings", roles: ['admin'] },
    { icon: AlertTriangle, label: "Announcements", to: "/announcements", roles: ['admin', 'gate_operator', 'safety_manager'] },
];

const SidebarItem = ({ icon: Icon, label, to }) => {
    const location = useLocation();
    const isActive = location.pathname === to;

    return (
        <Link
            to={to}
            className={cn(
                "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors",
                isActive
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
            )}
        >
            <Icon className="h-5 w-5" />
            <span className="font-medium">{label}</span>
        </Link>
    );
};

const Layout = ({ children }) => {
    const { theme, toggleTheme } = useTheme();
    const { userRole, setUserRole } = useUserRole();

    // Filter navigation items based on user role
    const visibleNavItems = navigationItems.filter(item => item.roles.includes(userRole));

    // Role display names
    const roleNames = {
        'admin': 'Admin',
        'gate_operator': 'Gate Operator',
        'safety_manager': 'Safety Manager'
    };

    return (
        <div className="flex h-screen bg-background text-foreground">
            {/* Sidebar */}
            <aside className="w-64 border-r bg-card flex flex-col">
                <div className="p-6 flex items-center justify-between border-b">
                    <div className="flex items-center space-x-2">
                        <div className="h-8 w-8 bg-primary rounded-lg flex items-center justify-center">
                            <Shield className="h-5 w-5 text-primary-foreground" />
                        </div>
                        <span className="font-bold text-lg">Smart PPE</span>
                    </div>
                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-lg hover:bg-muted transition-colors"
                        title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
                    >
                        {theme === 'light' ? (
                            <Moon className="h-5 w-5" />
                        ) : (
                            <Sun className="h-5 w-5" />
                        )}
                    </button>
                </div>

                <nav className="flex-1 p-4 space-y-2">
                    {visibleNavItems.map((item) => (
                        <SidebarItem
                            key={item.to}
                            icon={item.icon}
                            label={item.label}
                            to={item.to}
                        />
                    ))}
                </nav>

                <div className="p-4 border-t space-y-2">
                    {/* Role Switcher */}
                    <div className="mb-2 p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span className="text-xs font-medium text-muted-foreground">Current Role</span>
                        </div>
                        <select
                            value={userRole}
                            onChange={(e) => setUserRole(e.target.value)}
                            className="w-full px-2 py-1.5 text-sm rounded border bg-background"
                        >
                            <option value="admin">Admin</option>
                            <option value="gate_operator">Gate Operator</option>
                            <option value="safety_manager">Safety Manager</option>
                        </select>
                    </div>

                    <Link to="/" className="flex items-center space-x-3 px-3 py-2 rounded-lg text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors">
                        <LogOut className="h-5 w-5" />
                        <span className="font-medium">Sign Out</span>
                    </Link>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto">
                {children}
            </main>
        </div>
    );
};

const App = () => {
    return (
        <ThemeProvider>
            <UserRoleProvider>
                <Router>
                    <Routes>
                        <Route path="/" element={<Login />} />
                        <Route path="/dashboard" element={<Layout><Dashboard /></Layout>} />
                        <Route path="/workers" element={<Layout><Workers /></Layout>} />
                        <Route path="/attendance" element={<Layout><Attendance /></Layout>} />
                        <Route path="/reports" element={<Layout><Reports /></Layout>} />
                        <Route path="/alerts" element={<Layout><Alerts /></Layout>} />
                        <Route path="/settings" element={<Layout><SettingsPage /></Layout>} />
                        <Route path="/announcements" element={<Announcements />} />
                    </Routes>
                </Router>
            </UserRoleProvider>
        </ThemeProvider>
    );
};

export default App;
