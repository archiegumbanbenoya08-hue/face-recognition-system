import { useState, useEffect } from 'react';
import axios from 'axios';
import ParentSidebar from './ParentSidebar';
import ChildrenView from './parent/ChildrenView';
import ParentLogs from './parent/ParentLogs';

const ParentDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('children');
  const [children, setChildren] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'children') {
      fetchChildren();
    } else if (activeTab === 'logs') {
      fetchLogs();
    }
  }, [activeTab, user.token]);

  const fetchChildren = async () => {
    setLoading(true);
    try {
      // In a real app, you'd have an endpoint to get children for a parent
      // For now, we'll simulate with sample data
      setChildren([
        {
          student_id: 'S001',
          first_name: 'Kent',
          last_name: 'Navarro',
          grade_level: '10',
          image_path: 'student_images/kent.jpg',
          current_status: 'IN CAMPUS',
          last_seen: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Error fetching children:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/logs/parent/${user.id}`, {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setLogs(response.data);
    } catch (error) {
      console.error('Error fetching logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'children':
        return <ChildrenView children={children} loading={loading} />;
      case 'logs':
        return <ParentLogs logs={logs} children={children} loading={loading} />;
      default:
        return <ChildrenView children={children} loading={loading} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <ParentSidebar activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={onLogout} />
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default ParentDashboard;