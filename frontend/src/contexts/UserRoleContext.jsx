import React, { createContext, useContext, useState } from 'react';

const UserRoleContext = createContext();

export const UserRoleProvider = ({ children }) => {
    // Default role - can be 'admin', 'gate_operator', or 'safety_manager'
    const [userRole, setUserRole] = useState('admin');

    return (
        <UserRoleContext.Provider value={{ userRole, setUserRole }}>
            {children}
        </UserRoleContext.Provider>
    );
};

export const useUserRole = () => {
    const context = useContext(UserRoleContext);
    if (!context) {
        throw new Error('useUserRole must be used within UserRoleProvider');
    }
    return context;
};
