import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, User, Eye, Lock } from 'lucide-react';
import { cn } from '@/lib/utils';

const Login = () => {
    const navigate = useNavigate();
    const [selectedRole, setSelectedRole] = useState(null);

    const roles = [
        { id: 'admin', name: 'Admin', icon: Shield, color: 'bg-red-500/10 text-red-500 border-red-500/20' },
        { id: 'gate', name: 'Gate Operator', icon: Eye, color: 'bg-blue-500/10 text-blue-500 border-blue-500/20' },
        { id: 'safety', name: 'Safety Manager', icon: User, color: 'bg-green-500/10 text-green-500 border-green-500/20' },
    ];

    const handleLogin = (e) => {
        e.preventDefault();
        if (selectedRole) {
            // In a real app, perform auth here
            navigate('/dashboard');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-background p-4">
            <div className="w-full max-w-md space-y-8">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-primary rounded-full flex items-center justify-center">
                        <Shield className="h-6 w-6 text-primary-foreground" />
                    </div>
                    <h2 className="mt-6 text-3xl font-bold tracking-tight">Smart PPE Compliance</h2>
                    <p className="mt-2 text-sm text-muted-foreground">Select your role to continue</p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleLogin}>
                    <div className="grid grid-cols-1 gap-4">
                        {roles.map((role) => {
                            const Icon = role.icon;
                            return (
                                <div
                                    key={role.id}
                                    onClick={() => setSelectedRole(role.id)}
                                    className={cn(
                                        "relative flex items-center space-x-3 rounded-lg border px-6 py-5 shadow-sm focus-within:ring-2 focus-within:ring-primary hover:border-primary cursor-pointer transition-all",
                                        selectedRole === role.id ? "border-primary ring-1 ring-primary bg-primary/5" : "border-border"
                                    )}
                                >
                                    <div className={cn("flex-shrink-0 rounded-lg p-2", role.color)}>
                                        <Icon className="h-6 w-6" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <span className="absolute inset-0" aria-hidden="true" />
                                        <p className="text-sm font-medium text-foreground">{role.name}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={!selectedRole}
                            className="group relative flex w-full justify-center rounded-md bg-primary px-3 py-2 text-sm font-semibold text-primary-foreground hover:bg-primary/90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                                <Lock className="h-5 w-5 text-primary-foreground/50 group-hover:text-primary-foreground" aria-hidden="true" />
                            </span>
                            Sign in
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default Login;
