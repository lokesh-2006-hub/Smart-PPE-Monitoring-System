import React, { useState, useEffect } from 'react';
import { Edit2, Trash2, Plus, Camera, Upload } from 'lucide-react';
import client from '@/api/client';
import SearchInput from '@/components/SearchInput';
import StatusBadge from '@/components/StatusBadge';

const WorkersPage = () => {
    const [workers, setWorkers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [showAddModal, setShowAddModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showPhotoModal, setShowPhotoModal] = useState(false);
    const [selectedWorker, setSelectedWorker] = useState(null);
    const [photoFile, setPhotoFile] = useState(null);
    const [photoPreview, setPhotoPreview] = useState(null);
    const [uploadingPhoto, setUploadingPhoto] = useState(false);
    const [formData, setFormData] = useState({
        employee_id: '',
        name: '',
        department: '',
        rfid_tag: '',
        phone: '',
        email: ''
        // status removed - automatically managed by PPE system
    });

    useEffect(() => {
        fetchWorkers();
    }, [search]);

    const fetchWorkers = async () => {
        try {
            const res = await client.get('/api/workers', {
                params: { search, limit: 100 }
            });
            setWorkers(res.data.workers || []);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch workers', error);
            setLoading(false);
        }
    };

    const handleAdd = async (e) => {
        e.preventDefault();
        try {
            await client.post('/api/workers', formData);
            setShowAddModal(false);
            resetForm();
            fetchWorkers();
        } catch (error) {
            console.error('Failed to add worker', error);
            alert('Failed to add worker: ' + (error.response?.data?.detail || error.message));
        }
    };

    const handleEdit = async (e) => {
        e.preventDefault();
        try {
            await client.put(`/api/workers/${selectedWorker.id}`, formData);
            setShowEditModal(false);
            resetForm();
            fetchWorkers();
        } catch (error) {
            console.error('Failed to update worker', error);
            alert('Failed to update worker');
        }
    };

    const handleDelete = async (workerId) => {
        if (!confirm('Are you sure you want to deactivate this worker?')) return;

        try {
            await client.delete(`/api/workers/${workerId}`);
            fetchWorkers();
        } catch (error) {
            console.error('Failed to delete worker', error);
        }
    };

    const openEditModal = (worker) => {
        setSelectedWorker(worker);
        setFormData({
            employee_id: worker.employee_id || '',
            name: worker.name || '',
            department: worker.department || '',
            rfid_tag: worker.rfid_tag || '',
            phone: worker.phone || '',
            email: worker.email || ''
            // status removed - automatically managed by PPE system
        });
        setShowEditModal(true);
    };

    const resetForm = () => {
        setFormData({
            employee_id: '',
            name: '',
            department: '',
            rfid_tag: '',
            phone: '',
            email: ''
            // status removed - automatically managed by PPE system
        });
        setSelectedWorker(null);
    };

    const openPhotoModal = (worker) => {
        setSelectedWorker(worker);
        setShowPhotoModal(true);
        setPhotoFile(null);
        setPhotoPreview(null);
    };

    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setPhotoFile(file);
            // Create preview
            const reader = new FileReader();
            reader.onloadend = () => {
                setPhotoPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handlePhotoUpload = async () => {
        if (!photoFile || !selectedWorker) return;

        setUploadingPhoto(true);
        try {
            const formData = new FormData();
            formData.append('file', photoFile);

            await client.post(`/api/workers/${selectedWorker.id}/photo`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            alert(`Photo uploaded successfully for ${selectedWorker.name}!\nPhoto saved to known_faces/${selectedWorker.name}/ for facial recognition.`);
            setShowPhotoModal(false);
            setPhotoFile(null);
            setPhotoPreview(null);
            fetchWorkers(); // Refresh worker list
        } catch (error) {
            console.error('Failed to upload photo', error);
            alert('Failed to upload photo: ' + (error.response?.data?.detail || error.message));
        } finally {
            setUploadingPhoto(false);
        }
    };

    const handleSyncFromKnownFaces = async () => {
        if (!confirm('⚠️ WARNING: This will DELETE all current workers and sync from known_faces directory.\n\nAll worker details (employee ID, department, etc.) will be cleared.\nOnly workers with photos in known_faces will be kept.\n\nContinue?')) {
            return;
        }

        setLoading(true);
        try {
            const response = await client.post('/api/workers/sync-from-known-faces');
            alert(`✅ Success!\n\n${response.data.message}\n\nDeleted: ${response.data.details.deleted_old_workers} old workers\nCreated: ${response.data.details.created_new_workers} new workers\n\nYou can now update worker details.`);
            fetchWorkers(); // Refresh the list
        } catch (error) {
            console.error('Failed to sync workers', error);
            alert('Failed to sync workers: ' + (error.response?.data?.detail || error.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Workers Management</h1>
                    <p className="text-muted-foreground">Manage worker records and information</p>
                </div>
                <div className="flex items-center space-x-3">
                    <button
                        onClick={handleSyncFromKnownFaces}
                        className="flex items-center space-x-2 px-4 py-2 border border-primary text-primary rounded-lg font-medium hover:bg-primary/10 transition-colors"
                    >
                        <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Sync from Known Faces</span>
                    </button>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="flex items-center space-x-2 px-4 py-2 btn-primary rounded-lg font-medium transition-colors"
                    >
                        <Plus className="h-5 w-5" />
                        <span>Add Worker</span>
                    </button>
                </div>
            </div>

            {/* Workers Table */}
            <div className="bg-card rounded-xl border shadow-sm">
                <div className="p-4 border-b">
                    <h2 className="text-lg font-semibold mb-4">All Workers</h2>
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
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Photo</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Worker ID</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Name</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Department</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">RFID Tag</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Status</th>
                                <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan="7" className="px-4 py-8 text-center text-muted-foreground">
                                        Loading...
                                    </td>
                                </tr>
                            ) : workers.length === 0 ? (
                                <tr>
                                    <td colSpan="7" className="px-4 py-8 text-center text-muted-foreground">
                                        No workers found
                                    </td>
                                </tr>
                            ) : (
                                workers.map((worker) => (
                                    <tr key={worker.id} className="border-t hover:bg-muted/50 transition-colors">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center space-x-2">
                                                {worker.photo_url ? (
                                                    <img
                                                        src={`http://localhost:8000/api/workers/${worker.id}/photo`}
                                                        alt={worker.name}
                                                        className="h-10 w-10 rounded-full object-cover border-2 border-primary/20"
                                                        onError={(e) => {
                                                            e.target.style.display = 'none';
                                                            e.target.nextSibling.style.display = 'flex';
                                                        }}
                                                    />
                                                ) : null}
                                                <button
                                                    onClick={() => openPhotoModal(worker)}
                                                    className="h-10 w-10 rounded-full bg-muted hover:bg-primary/10 flex items-center justify-center transition-colors border border-border"
                                                    title="Upload Photo"
                                                >
                                                    <Camera className="h-5 w-5 text-muted-foreground" />
                                                </button>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-sm">{worker.employee_id || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm font-medium text-blue-600">{worker.name}</td>
                                        <td className="px-4 py-3 text-sm">{worker.department || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm">{worker.rfid_tag || 'N/A'}</td>
                                        <td className="px-4 py-3 text-sm">
                                            <StatusBadge status={worker.status} />
                                        </td>
                                        <td className="px-4 py-3 text-sm">
                                            <div className="flex space-x-2">
                                                <button
                                                    onClick={() => openEditModal(worker)}
                                                    className="p-2 hover:bg-muted rounded-lg transition-colors"
                                                    title="Edit"
                                                >
                                                    <Edit2 className="h-4 w-4 text-blue-600" />
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(worker.id)}
                                                    className="p-2 hover:bg-muted rounded-lg transition-colors"
                                                    title="Delete"
                                                >
                                                    <Trash2 className="h-4 w-4 text-red-600" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Add Worker Modal */}
            {showAddModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card rounded-xl p-6 w-full max-w-md shadow-xl">
                        <h2 className="text-xl font-bold mb-4">Add New Worker</h2>
                        <form onSubmit={handleAdd} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Employee ID *</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.employee_id}
                                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Department</label>
                                <input
                                    type="text"
                                    value={formData.department}
                                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">RFID Tag</label>
                                <input
                                    type="text"
                                    value={formData.rfid_tag}
                                    onChange={(e) => setFormData({ ...formData, rfid_tag: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => { setShowAddModal(false); resetForm(); }}
                                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-muted transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 btn-primary rounded-lg transition-colors"
                                >
                                    Add Worker
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Edit Worker Modal */}
            {showEditModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card rounded-xl p-6 w-full max-w-md shadow-xl">
                        <h2 className="text-xl font-bold mb-4">Edit Worker</h2>
                        <form onSubmit={handleEdit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Employee ID</label>
                                <input
                                    type="text"
                                    value={formData.employee_id}
                                    onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Name</label>
                                <input
                                    type="text"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Department</label>
                                <input
                                    type="text"
                                    value={formData.department}
                                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background text-foreground"
                                />
                            </div>
                            {/* Status removed - automatically managed by PPE compliance system */}
                            <div className="p-3 bg-muted/30 rounded-lg border border-border">
                                <p className="text-xs text-muted-foreground">
                                    ℹ️ <strong>Status Auto-Managed:</strong> Worker status is automatically updated based on PPE compliance checks.
                                    Pass = Active, Fail = Inactive.
                                </p>
                            </div>
                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => { setShowEditModal(false); resetForm(); }}
                                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-muted transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 btn-primary rounded-lg transition-colors"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Photo Upload Modal */}
            {showPhotoModal && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-card rounded-xl p-6 w-full max-w-md shadow-xl">
                        <h2 className="text-xl font-bold mb-4">Upload Worker Photo</h2>
                        <p className="text-sm text-muted-foreground mb-4">
                            Upload photo for <span className="font-semibold text-foreground">{selectedWorker?.name}</span>
                        </p>
                        <p className="text-xs text-muted-foreground mb-4 p-3 bg-muted/50 rounded-lg border border-border">
                            📸 Photo will be saved to <code className="text-primary font-mono">known_faces/{selectedWorker?.name}/</code> for facial recognition
                        </p>

                        <div className="space-y-4">
                            {/* Photo Preview */}
                            {photoPreview && (
                                <div className="flex justify-center">
                                    <img
                                        src={photoPreview}
                                        alt="Preview"
                                        className="max-w-full h-48 object-contain rounded-lg border-2 border-primary/20"
                                    />
                                </div>
                            )}

                            {/* File Input */}
                            <div>
                                <label className="block text-sm font-medium mb-2">Select Photo</label>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                    className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                                />
                                <p className="text-xs text-muted-foreground mt-1">
                                    Supported formats: JPG, PNG, BMP
                                </p>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => { setShowPhotoModal(false); setPhotoFile(null); setPhotoPreview(null); }}
                                    className="flex-1 px-4 py-2 border rounded-lg hover:bg-muted transition-colors"
                                    disabled={uploadingPhoto}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="button"
                                    onClick={handlePhotoUpload}
                                    disabled={!photoFile || uploadingPhoto}
                                    className="flex-1 px-4 py-2 btn-primary rounded-lg transition-colors flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {uploadingPhoto ? (
                                        <>
                                            <span className="animate-spin">⏳</span>
                                            <span>Uploading...</span>
                                        </>
                                    ) : (
                                        <>
                                            <Upload className="h-4 w-4" />
                                            <span>Upload Photo</span>
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WorkersPage;
