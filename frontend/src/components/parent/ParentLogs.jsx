import { useState } from 'react';

const ParentLogs = ({ logs, children, loading }) => {
  const [selectedChild, setSelectedChild] = useState('');

  const filteredLogs = selectedChild
    ? logs.filter(log => log.student_id === selectedChild)
    : logs;

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">Loading logs...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Activity Logs</h2>

      {children.length > 1 && (
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Child</label>
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            className="w-full max-w-xs px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">All Children</option>
            {children.map((child) => (
              <option key={child.student_id} value={child.student_id}>
                {child.first_name} {child.last_name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Event</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Child</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredLogs.map((log) => (
              <tr key={log.log_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 rounded text-sm ${
                    log.event_type === 'ENTRY' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {log.event_type}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {log.first_name} {log.last_name}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredLogs.length === 0 && (
          <div className="p-6 text-center text-gray-500">
            No logs found
          </div>
        )}
      </div>
    </div>
  );
};

export default ParentLogs;