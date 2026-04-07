import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Announcements = () => {
    const [list, setList] = useState([]);
    const [message, setMessage] = useState("");
    const [author, setAuthor] = useState("");

    // 1. Fetch Data when page loads
    useEffect(() => {
        fetchAnnouncements();
    }, []);

    const fetchAnnouncements = async () => {
        try {
            // "Integration" happens here!
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const res = await axios.get(`${apiUrl}/announcement`);
            setList(res.data);
        } catch (err) {
            console.error("Error fetching:", err);
        }
    };

    const handleSubmit = async () => {
        try {
            // "Posting" data happens here!
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            await axios.post(`${apiUrl}/announcement`, {
                content: message,
                author: author
            });
            alert("Posted!");
            fetchAnnouncements(); // Refresh list
        } catch (err) {
            alert("Failed to post");
        }
    };

    return (
        <div className="p-10">
            <h1 className="text-2xl font-bold mb-4">Office Bulletin Board</h1>
            
            {/* Input Form */}
            <div className="mb-8 flex gap-2">
                <input 
                    className="border p-2 rounded" 
                    placeholder="Message..." 
                    value={message}
                    onChange={e => setMessage(e.target.value)}
                />
                <input 
                    className="border p-2 rounded" 
                    placeholder="Author..." 
                    value={author}
                    onChange={e => setAuthor(e.target.value)}
                />
                <button 
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                    onClick={handleSubmit}
                >
                    Post
                </button>
            </div>

            {/* List */}
            <div className="space-y-4">
                {list.map((item, index) => (
                    <div key={index} className="border p-4 rounded shadow bg-white">
                        <p className="font-bold">{item.author} says:</p>
                        <p>{item.content}</p>
                        <p className="text-xs text-gray-400 mt-2">{item.created_at}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Announcements;