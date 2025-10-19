'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';
import { Modal } from '@/components/common/Modal';
import { usersAPI } from '@/lib/api';
import type { User } from '@/lib/types';
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export default function UsersPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'viewer' as 'admin' | 'engineer' | 'viewer',
    is_active: true,
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('demo_token');
      if (!token) {
        router.push('/login');
        return;
      }

      const data: any = await usersAPI.list();
      // Backend returns { items: User[], total: number, ... }
      setUsers(data.items || data || []);
    } catch (error: any) {
      console.error('Failed to fetch users:', error);
      toast.error('Failed to load users');
      if (error.message.includes('401') || error.message.includes('Unauthorized')) {
        router.push('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setSelectedUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'viewer',
      is_active: true,
    });
    setIsModalOpen(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: '', // Don't pre-fill password
      role: user.role,
      is_active: user.is_active,
    });
    setIsModalOpen(true);
  };

  const handleDeleteClick = (user: User) => {
    setSelectedUser(user);
    setIsDeleteModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (selectedUser) {
        // Update existing user
        const updateData: any = {
          email: formData.email,
          role: formData.role,
          is_active: formData.is_active,
        };
        if (formData.password) {
          updateData.password = formData.password;
        }
        await usersAPI.update(selectedUser.id, updateData);
        toast.success('User updated successfully');
      } else {
        // Create new user
        await usersAPI.create(formData);
        toast.success('User created successfully');
      }
      setIsModalOpen(false);
      fetchUsers();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save user');
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;
    try {
      await usersAPI.delete(selectedUser.id);
      toast.success('User deleted successfully');
      setIsDeleteModalOpen(false);
      fetchUsers();
    } catch (error: any) {
      toast.error(error.message || 'Failed to delete user');
    }
  };

  if (loading) {
    return (
      <DashboardLayout title="User Management">
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner size="lg" text="Loading users..." />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="User Management">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
            <p className="mt-1 text-sm text-gray-600">Manage user accounts and permissions</p>
          </div>
          <Button onClick={handleCreateUser} variant="primary">
            <PlusIcon className="h-5 w-5 mr-2" />
            Add User
          </Button>
        </div>

        {/* Users Table */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Username
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Email
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created At
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users && users.length > 0 ? users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{user.username}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant="default">
                        <span className="capitalize">{user.role}</span>
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={user.is_active ? 'status' : 'default'}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleEditUser(user)}
                          className="text-[#3B7DDD] hover:text-[#2F66BD]"
                          title="Edit"
                        >
                          <PencilIcon className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => handleDeleteClick(user)}
                          className="text-red-600 hover:text-red-900"
                          title="Delete"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={6} className="px-6 py-12 text-center text-sm text-gray-500">
                      No users found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Create/Edit User Modal */}
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={selectedUser ? 'Edit User' : 'Create New User'}
          size="md"
        >
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Username <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                disabled={!!selectedUser}
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD] disabled:bg-gray-100"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password {!selectedUser && <span className="text-red-500">*</span>}
              </label>
              <input
                type="password"
                required={!selectedUser}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder={selectedUser ? 'Leave blank to keep current password' : ''}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Role <span className="text-red-500">*</span>
              </label>
              <select
                value={formData.role}
                onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-[#3B7DDD] focus:ring-[#3B7DDD]"
              >
                <option value="viewer">Viewer</option>
                <option value="engineer">Engineer</option>
                <option value="admin">Admin</option>
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="h-4 w-4 text-[#3B7DDD] focus:ring-[#3B7DDD] border-gray-300 rounded"
              />
              <label htmlFor="is_active" className="ml-2 block text-sm text-gray-700">
                Active
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <Button type="button" variant="outline" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" variant="primary">
                {selectedUser ? 'Update User' : 'Create User'}
              </Button>
            </div>
          </form>
        </Modal>

        {/* Delete Confirmation Modal */}
        <Modal
          isOpen={isDeleteModalOpen}
          onClose={() => setIsDeleteModalOpen(false)}
          title="Delete User"
          size="sm"
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Are you sure you want to delete user <strong>{selectedUser?.username}</strong>? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
              <Button variant="outline" onClick={() => setIsDeleteModalOpen(false)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDelete}>
                Delete User
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
