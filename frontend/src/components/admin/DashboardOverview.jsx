import { useState, useEffect } from 'react';
import axios from 'axios';

const DashboardOverview = ({ students, logs, summary }) => {
  const [stats, setStats] = useState({
    totalStudents: 0,
    studentsInCampus: 0,
    entriesToday: 0,
    exitsToday: 0
  });

  useEffect(() => {
    // Calculate stats from data
    const totalStudents = students.length;
    const studentsInCampus = students.filter(s => s.current_status === 'IN CAMPUS').length;
    const entriesToday = summary.total_entries;
    const exitsToday = summary.total_exits;

    setStats({ totalStudents, studentsInCampus, entriesToday, exitsToday });
  }, [students, summary]);

  const recentLogs = logs.slice(0, 10);

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Dashboard Overview</h2>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Total Students</h3>
          <p className="text-3xl font-bold text-blue-600">{stats.totalStudents}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Students in Campus</h3>
          <p className="text-3xl font-bold text-green-600">{stats.studentsInCampus}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Entries Today</h3>
          <p className="text-3xl font-bold text-indigo-600">{stats.entriesToday}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold text-gray-700">Exits Today</h3>
          <p className="text-3xl font-bold text-red-600">{stats.exitsToday}</p>
        </div>
      </div>

      {/* Recent Logs */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b">
          <h3 className="text-lg font-semibold">Recent Activity</h3>
        </div>
        <div className="p-6">
          {recentLogs.length === 0 ? (
            <p className="text-gray-500">No recent activity</p>
          ) : (
            <div className="space-y-4">
              {recentLogs.map((log) => (
                <div key={log.log_id} className="flex items-center justify-between border-b pb-2">
                  <div className="flex items-center">
                    <img
                      src={`http://localhost:8000/${log.image_path}`}
                      alt={`${log.first_name} ${log.last_name}`}
                      className="w-10 h-10 rounded-full mr-3"
                    />
                    <div>
                      <p className="font-semibold">{log.first_name} {log.last_name}</p>
                      <p className="text-sm text-gray-600">Grade {log.grade_level}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded text-sm ${
                      log.event_type === 'ENTRY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {log.event_type}
                    </span>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(log.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardOverview;