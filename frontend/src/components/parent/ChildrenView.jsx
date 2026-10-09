const ChildrenView = ({ children, loading }) => {
  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center">Loading children...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">My Children</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {children.map((child) => (
          <div key={child.student_id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center mb-4">
              <img
                src={`http://localhost:8000/${child.image_path}`}
                alt={`${child.first_name} ${child.last_name}`}
                className="w-16 h-16 rounded-full mr-4"
              />
              <div>
                <h3 className="text-lg font-semibold">{child.first_name} {child.last_name}</h3>
                <p className="text-gray-600">Grade {child.grade_level}</p>
                <p className="text-sm text-gray-500">ID: {child.student_id}</p>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                child.current_status === 'IN CAMPUS'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {child.current_status}
              </span>
              <div className="text-right">
                <p className="text-sm text-gray-600">Last seen</p>
                <p className="text-sm font-medium">
                  {new Date(child.last_seen).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
      {children.length === 0 && (
        <div className="text-center text-gray-500 mt-8">
          No children found
        </div>
      )}
    </div>
  );
};

export default ChildrenView;