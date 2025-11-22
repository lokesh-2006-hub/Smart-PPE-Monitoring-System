import React from 'react';
import { cn } from '@/lib/utils';

export const StatusBadge = ({ status, className }) => {
    const variants = {
        active: 'bg-orange-500/20 text-orange-600',
        inactive: 'bg-gray-500/20 text-gray-600',
        pass: 'bg-green-500/20 text-green-600',
        fail: 'bg-red-500/20 text-red-600',
        critical: 'bg-red-500/20 text-red-600',
        warning: 'bg-amber-500/20 text-amber-600',
        info: 'bg-blue-500/20 text-blue-600',
        resolved: 'bg-green-500/20 text-green-600'
    };

    return (
        <span className={cn(
            'px-2 py-1 rounded-full text-xs font-semibold uppercase inline-block',
            variants[status?.toLowerCase()] || 'bg-gray-500/20 text-gray-600',
            className
        )}>
            {status}
        </span>
    );
};

export default StatusBadge;
