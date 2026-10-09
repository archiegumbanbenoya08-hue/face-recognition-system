const ParentSidebar = ({ activeTab, setActiveTab, user, onLogout }) => {
  const menuItems = [
    { id: 'children', label: 'My Children', icon: '👨‍👩‍👧‍👦' },
    { id: 'logs', label: 'Activity Logs', icon: '📝' },
  ];

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-800">Parent Portal</h1>
        <p className="text-gray-600 mt-1">Welcome, {user.name}</p>
      </div>
      <nav className="mt-6">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveTab(item.id)}
            className={`w-full flex items-center px-6 py-3 text-left ${
              activeTab === item.id
                ? 'bg-indigo-50 border-r-4 border-indigo-500 text-indigo-700'
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            }`}
          >
            <span className="mr-3">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="absolute bottom-0 w-64 p-6">
        <button
          onClick={onLogout}
          className="w-full bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600"
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default ParentSidebar;