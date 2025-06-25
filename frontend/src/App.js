import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  CheckCircle, 
  Clock, 
  Plus, 
  Target, 
  BarChart3, 
  Calendar,
  Edit3,
  Trash2,
  Star,
  Quote
} from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({});
  const [selectedProject, setSelectedProject] = useState(null);
  const [motivationalQuote, setMotivationalQuote] = useState('');
  const [loading, setLoading] = useState(false);

  // Fetch data
  const fetchTasks = async (projectId = null) => {
    try {
      const url = projectId ? `${API_BASE_URL}/api/tasks?project_id=${projectId}` : `${API_BASE_URL}/api/tasks`;
      const response = await axios.get(url);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const getMotivationalQuote = async (taskTitle, priority = 'medium') => {
    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/api/motivational-quote`, {
        task_title: taskTitle,
        priority: priority,
        context: 'Help me stay motivated to complete this task and beat procrastination'
      });
      setMotivationalQuote(response.data.quote);
    } catch (error) {
      console.error('Error getting motivational quote:', error);
      setMotivationalQuote("You've got this! Every small step counts towards your goal. Start now, start today!");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
    fetchProjects();
    fetchStats();
  }, []);

  // Task operations
  const createTask = async (taskData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/tasks`, taskData);
      fetchTasks(selectedProject?.id);
      fetchStats();
      return response.data;
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };

  const updateTask = async (taskId, taskData) => {
    try {
      await axios.put(`${API_BASE_URL}/api/tasks/${taskId}`, taskData);
      fetchTasks(selectedProject?.id);
      fetchStats();
    } catch (error) {
      console.error('Error updating task:', error);
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/tasks/${taskId}`);
      fetchTasks(selectedProject?.id);
      fetchStats();
    } catch (error) {
      console.error('Error deleting task:', error);
    }
  };

  // Project operations
  const createProject = async (projectData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/projects`, projectData);
      fetchProjects();
      return response.data;
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/projects/${projectId}`);
      fetchProjects();
      fetchStats();
      if (selectedProject?.id === projectId) {
        setSelectedProject(null);
        setCurrentView('home');
      }
    } catch (error) {
      console.error('Error deleting project:', error);
    }
  };

  const TaskForm = ({ onSubmit, initialTask = null, onCancel }) => {
    const [formData, setFormData] = useState({
      title: initialTask?.title || '',
      description: initialTask?.description || '',
      priority: initialTask?.priority || 'medium',
      due_date: initialTask?.due_date || '',
      project_id: selectedProject?.id || initialTask?.project_id || null
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
      if (!initialTask) {
        setFormData({ title: '', description: '', priority: 'medium', due_date: '', project_id: selectedProject?.id || null });
      }
    };

    return (
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-lg mb-6">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Task Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="What needs to be done?"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({...formData, priority: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="low">Low Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="high">High Priority</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Due Date</label>
            <input
              type="datetime-local"
              value={formData.due_date}
              onChange={(e) => setFormData({...formData, due_date: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Add more details..."
              rows="3"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button
            type="submit"
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus size={20} />
            {initialTask ? 'Update Task' : 'Create Task'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-all duration-200"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    );
  };

  const TaskCard = ({ task, onUpdate, onDelete, showProject = false }) => {
    const [isEditing, setIsEditing] = useState(false);
    
    const getPriorityColor = (priority) => {
      switch (priority) {
        case 'high': return 'text-red-600 bg-red-50';
        case 'medium': return 'text-yellow-600 bg-yellow-50';
        case 'low': return 'text-green-600 bg-green-50';
        default: return 'text-gray-600 bg-gray-50';
      }
    };

    const handleStatusChange = (newStatus) => {
      onUpdate(task.id, { ...task, status: newStatus });
    };

    const handleGetMotivation = () => {
      getMotivationalQuote(task.title, task.priority);
    };

    if (isEditing) {
      return (
        <TaskForm
          initialTask={task}
          onSubmit={(formData) => {
            onUpdate(task.id, { ...task, ...formData });
            setIsEditing(false);
          }}
          onCancel={() => setIsEditing(false)}
        />
      );
    }

    return (
      <div className="stats-card bg-white p-6 rounded-2xl shadow-sm hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-800 mb-2">{task.title}</h3>
            {task.description && (
              <p className="text-gray-600 text-sm mb-3">{task.description}</p>
            )}
            <div className="flex items-center gap-3 mb-3">
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(task.priority)}`}>
                {task.priority} priority
              </span>
              {task.due_date && (
                <span className="flex items-center gap-1 text-gray-500 text-sm">
                  <Calendar size={14} />
                  {new Date(task.due_date).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <select
              value={task.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
            >
              <option value="todo">To Do</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleGetMotivation}
              className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
              title="Get Motivation"
            >
              <Quote size={16} />
            </button>
            <button
              onClick={() => setIsEditing(true)}
              className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
            >
              <Edit3 size={16} />
            </button>
            <button
              onClick={() => onDelete(task.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  };

  const ProjectForm = ({ onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      name: '',
      description: '',
      color: '#a855f7'
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      onSubmit(formData);
      setFormData({ name: '', description: '', color: '#a855f7' });
    };

    return (
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-2xl shadow-lg mb-6">
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Project name..."
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Color</label>
            <input
              type="color"
              value={formData.color}
              onChange={(e) => setFormData({...formData, color: e.target.value})}
              className="w-full h-12 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Project description..."
              rows="3"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-6">
          <button
            type="submit"
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus size={20} />
            Create Project
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition-all duration-200"
            >
              Cancel
            </button>
          )}
        </div>
      </form>
    );
  };

  const KanbanBoard = ({ projectTasks, onUpdateTask }) => {
    const todoTasks = projectTasks.filter(task => task.status === 'todo');
    const inProgressTasks = projectTasks.filter(task => task.status === 'in_progress');
    const completedTasks = projectTasks.filter(task => task.status === 'completed');

    const KanbanColumn = ({ title, tasks, status, bgColor }) => (
      <div className="flex-1 min-w-80">
        <div className={`${bgColor} p-4 rounded-t-2xl border-b-2 border-white`}>
          <h3 className="font-semibold text-white flex items-center gap-2">
            {status === 'todo' && <Clock size={18} />}
            {status === 'in_progress' && <Target size={18} />}
            {status === 'completed' && <CheckCircle size={18} />}
            {title} ({tasks.length})
          </h3>
        </div>
        <div className="bg-gray-50 p-4 rounded-b-2xl min-h-96 space-y-4">
          {tasks.map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onUpdate={onUpdateTask}
              onDelete={deleteTask}
            />
          ))}
        </div>
      </div>
    );

    return (
      <div className="flex gap-6 overflow-x-auto pb-6">
        <KanbanColumn
          title="To Do"
          tasks={todoTasks}
          status="todo"
          bgColor="bg-gradient-to-r from-blue-500 to-blue-600"
        />
        <KanbanColumn
          title="In Progress"
          tasks={inProgressTasks}
          status="in_progress"
          bgColor="bg-gradient-to-r from-yellow-500 to-orange-500"
        />
        <KanbanColumn
          title="Completed"
          tasks={completedTasks}
          status="completed"
          bgColor="bg-gradient-to-r from-green-500 to-green-600"
        />
      </div>
    );
  };

  const HomeView = () => (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center py-8">
        <h1 className="text-4xl font-bold text-gray-800 mb-4">
          Beat Procrastination, Get Things Done! 🎯
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Your smart task manager with AI-powered motivation to help you stay focused and productive.
        </p>
      </div>

      {/* Motivational Quote Display */}
      {motivationalQuote && (
        <div className="stats-card bg-gradient-to-r from-purple-500 to-indigo-600 p-6 rounded-2xl text-white text-center">
          <Quote size={32} className="mx-auto mb-4 opacity-80" />
          <p className="text-lg font-medium italic mb-2">{motivationalQuote}</p>
          {loading && <div className="animate-pulse">Generating inspiration...</div>}
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid md:grid-cols-4 gap-6">
        <div className="stats-card stats-card-total">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">Total Tasks</p>
              <p className="text-2xl font-bold text-white">{stats.total_tasks || 0}</p>
            </div>
            <Target className="text-white/60" size={32} />
          </div>
        </div>
        <div className="stats-card stats-card-completed">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">Completed</p>
              <p className="text-2xl font-bold text-white">{stats.completed_tasks || 0}</p>
            </div>
            <CheckCircle className="text-white/60" size={32} />
          </div>
        </div>
        <div className="stats-card bg-gradient-to-br from-orange-400 to-orange-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">In Progress</p>
              <p className="text-2xl font-bold text-white">{stats.in_progress_tasks || 0}</p>
            </div>
            <Clock className="text-white/60" size={32} />
          </div>
        </div>
        <div className="stats-card bg-gradient-to-br from-indigo-400 to-indigo-600">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white/80 text-sm">Projects</p>
              <p className="text-2xl font-bold text-white">{stats.total_projects || 0}</p>
            </div>
            <BarChart3 className="text-white/60" size={32} />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-2 gap-6">
        <button
          onClick={() => setCurrentView('tasks')}
          className="stats-card bg-white hover:shadow-xl transition-all duration-200 hover:-translate-y-1 p-8 text-left"
        >
          <div className="flex items-center gap-4">
            <div className="p-4 bg-purple-100 text-purple-600 rounded-2xl">
              <Target size={32} />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-800">Manage Tasks</h3>
              <p className="text-gray-600">Create, organize, and track your individual tasks</p>
            </div>
          </div>
        </button>
        
        <button
          onClick={() => setCurrentView('projects')}
          className="stats-card bg-white hover:shadow-xl transition-all duration-200 hover:-translate-y-1 p-8 text-left"
        >
          <div className="flex items-center gap-4">
            <div className="p-4 bg-indigo-100 text-indigo-600 rounded-2xl">
              <BarChart3 size={32} />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-800">Manage Projects</h3>
              <p className="text-gray-600">Organize tasks into projects with Kanban boards</p>
            </div>
          </div>
        </button>
      </div>
    </div>
  );

  const TasksView = () => {
    const [showForm, setShowForm] = useState(false);

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">Task Management</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus size={20} />
            New Task
          </button>
        </div>

        {showForm && (
          <TaskForm
            onSubmit={(formData) => {
              createTask(formData);
              setShowForm(false);
            }}
            onCancel={() => setShowForm(false)}
          />
        )}

        <div className="grid gap-4">
          {tasks.filter(task => !task.project_id).map(task => (
            <TaskCard
              key={task.id}
              task={task}
              onUpdate={updateTask}
              onDelete={deleteTask}
            />
          ))}
        </div>
      </div>
    );
  };

  const ProjectsView = () => {
    const [showForm, setShowForm] = useState(false);

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-800">Project Management</h2>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {showForm && (
          <ProjectForm
            onSubmit={(formData) => {
              createProject(formData);
              setShowForm(false);
            }}
            onCancel={() => setShowForm(false)}
          />
        )}

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map(project => (
            <div
              key={project.id}
              className="stats-card bg-white hover:shadow-xl transition-all duration-200 hover:-translate-y-1 cursor-pointer"
              onClick={() => {
                setSelectedProject(project);
                setCurrentView('project-detail');
                fetchTasks(project.id);
              }}
            >
              <div className="flex items-center justify-between mb-4">
                <div 
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: project.color }}
                />
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteProject(project.id);
                  }}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">{project.name}</h3>
              {project.description && (
                <p className="text-gray-600 text-sm mb-4">{project.description}</p>
              )}
              <div className="flex items-center gap-4 text-sm text-gray-500">
                <span>Tasks: {tasks.filter(task => task.project_id === project.id).length}</span>
                <span>Completed: {tasks.filter(task => task.project_id === project.id && task.status === 'completed').length}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const ProjectDetailView = () => {
    const [showForm, setShowForm] = useState(false);
    const projectTasks = tasks.filter(task => task.project_id === selectedProject?.id);

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => {
                setCurrentView('projects');
                setSelectedProject(null);
              }}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back to Projects
            </button>
            <div className="flex items-center gap-3">
              <div 
                className="w-6 h-6 rounded-full"
                style={{ backgroundColor: selectedProject?.color }}
              />
              <h2 className="text-2xl font-bold text-gray-800">{selectedProject?.name}</h2>
            </div>
          </div>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all duration-200"
          >
            <Plus size={20} />
            Add Task
          </button>
        </div>

        {showForm && (
          <TaskForm
            onSubmit={(formData) => {
              createTask({ ...formData, project_id: selectedProject.id });
              setShowForm(false);
            }}
            onCancel={() => setShowForm(false)}
          />
        )}

        <KanbanBoard
          projectTasks={projectTasks}
          onUpdateTask={updateTask}
        />
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-xl">
                  <Target size={24} />
                </div>
                <span className="text-xl font-bold text-gray-800">Procrastinator</span>
              </div>
              
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => setCurrentView('home')}
                  className={`nav-item ${currentView === 'home' ? 'nav-item-active' : 'nav-item-inactive'}`}
                >
                  Home
                </button>
                <button
                  onClick={() => setCurrentView('tasks')}
                  className={`nav-item ${currentView === 'tasks' ? 'nav-item-active' : 'nav-item-inactive'}`}
                >
                  Tasks
                </button>
                <button
                  onClick={() => setCurrentView('projects')}
                  className={`nav-item ${currentView === 'projects' ? 'nav-item-active' : 'nav-item-inactive'}`}
                >
                  Projects
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'home' && <HomeView />}
        {currentView === 'tasks' && <TasksView />}
        {currentView === 'projects' && <ProjectsView />}
        {currentView === 'project-detail' && <ProjectDetailView />}
      </main>
    </div>
  );
}

export default App;