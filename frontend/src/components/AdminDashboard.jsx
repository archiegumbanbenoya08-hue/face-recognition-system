import { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './Sidebar';
import DashboardOverview from './admin/DashboardOverview';
import StudentsManagement from './admin/StudentsManagement';
import LogsManagement from './admin/LogsManagement';
import Settings from './admin/Settings';

const AdminDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [students, setStudents] = useState([]);
  const [logs, setLogs] = useState([]);
  const [summary, setSummary] = useState({ total_entries: 0, total_exits: 0 });
  const [loading, setLoading] = useState(false);

  const fetchStudents = async () => {
    try {
      const response = await axios.get('http://localhost:8000/students/', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setStudents(response.data.students || []);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/logs/admin', {
        headers: { Authorization: `Bearer ${user.token}` }
      });
      setLogs(response.data.logs);
      setSummary(response.data.summary);
    } catch (error) {
      console.error('Error fetching logs:', error);
    }
  };

  useEffect(() => {
    if (activeTab === 'dashboard') {
      fetchStudents();
      fetchLogs();
    } else if (activeTab === 'students') {
      fetchStudents();
    } else if (activeTab === 'logs') {
      fetchLogs();
    }
  }, [activeTab, user.token]);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardOverview students={students} logs={logs} summary={summary} />;
      case 'students':
        return <StudentsManagement students={students} onUpdate={fetchStudents} user={user} />;
      case 'logs':
        return <LogsManagement logs={logs} summary={summary} onUpdate={fetchLogs} user={user} />;
      case 'settings':
        return <Settings />;
      default:
        return <DashboardOverview students={students} logs={logs} summary={summary} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} user={user} onLogout={onLogout} />
      <div className="flex-1 overflow-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default AdminDashboard;