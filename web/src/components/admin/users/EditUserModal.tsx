import React from 'react';

interface User {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: string;
  phone_number?: string;
  is_active: boolean;
}

interface EditUserModalProps {
  isOpen: boolean;
  user: User | null;
  onClose: () => void;
  onUserUpdated: () => void;
}

const EditUserModal: React.FC<EditUserModalProps> = ({ 
  isOpen, 
  user, 
  onClose, 
  onUserUpdated 
}) => {
  
  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Edit User: {user.first_name} {user.last_name}
          </h2>
        </div>
        
        <div className="p-6 text-center">
          <div className="mb-4">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Edit User Coming Soon!</h3>
            <p className="text-gray-600 mb-4">
              Edit functionality will be implemented next. <br />
              This will include form validation, role updates, and profile management.
            </p>
            
            {/* Show current user info */}
            <div className="bg-gray-50 rounded-lg p-4 text-left">
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Email:</span> {user.email}</div>
                <div><span className="font-medium">Role:</span> 
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                    user.role === 'admin' ? 'bg-purple-100 text-purple-800' :
                    user.role === 'teacher' ? 'bg-blue-100 text-blue-800' :
                    user.role === 'student' ? 'bg-green-100 text-green-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {user.role}
                  </span>
                </div>
                <div><span className="font-medium">Status:</span> 
                  <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                    user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                {user.phone_number && (
                  <div><span className="font-medium">Phone:</span> {user.phone_number}</div>
                )}
              </div>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="w-full bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default EditUserModal;