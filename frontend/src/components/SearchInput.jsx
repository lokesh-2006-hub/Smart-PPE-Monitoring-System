import React from 'react';
import { Search } from 'lucide-react';

export const SearchInput = ({ value, onChange, placeholder = "Search..." }) => {
    return (
        <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
                type="text"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                placeholder={placeholder}
                className="pl-10 pr-4 py-2 border border-border rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
            />
        </div>
    );
};

export default SearchInput;
