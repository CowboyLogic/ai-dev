---
name: react-components
description: Specialized skill for React component development in the Happy Camper Planner project. Handles large single-file components with useState hooks, Tailwind CSS styling, Lucide React icons, Firebase authentication flows, and camping/RV domain UI patterns. Use when creating React components, managing state, implementing UI flows, or building collaborative features.
---

# React Components Skill for Happy Camper Planner

This skill provides specialized guidance for React component development in the Happy Camper Planner collaborative camping trip planning application.

## When to Use This Skill

Use this skill when you need to:
- Create or refactor React components and UI flows
- Implement state management with useState hooks
- Style components with Tailwind CSS patterns
- Integrate Lucide React icons consistently
- Build authentication and user management flows
- Create collaborative features (plans, trips, gear, meals)
- Implement RV compatibility and campground selection UIs
- Handle complex form interactions and modal dialogs
- Build responsive layouts for camping trip management
- Create reusable UI patterns and component libraries

## Technology Context

### Frontend Stack
- **React 18** with functional components and hooks
- **Tailwind CSS** for utility-first styling
- **Lucide React** for consistent iconography
- **Firebase Authentication** for user management
- **Vite** as build tool and development server
- **Docker** development environment on port 3000

### Component Architecture
- **Large single-file components** with embedded state and handlers
- **useState hooks** for local component state management
- **Inline event handlers** with clear state updates
- **Conditional rendering** patterns with `&&` and ternary operators
- **Mock data constants** at component top for development

## Component Development Patterns

### Base Component Structure
```jsx
import React, { useState, useEffect } from 'react';
import { 
  // Import specific Lucide icons
  Calendar, MapPin, Users, Plus, Settings, 
  Tent, Truck, CheckSquare, Utensils 
} from 'lucide-react';

const ComponentName = () => {
  // --- State Management ---
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showModal, setShowModal] = useState(false);
  
  // --- Mock Data (Development) ---
  const [mockData] = useState([
    { id: "1", title: "Sample Data", /* ... */ },
    { id: "2", title: "More Data", /* ... */ }
  ]);

  // --- Effects ---
  useEffect(() => {
    // Component initialization
  }, []);

  // --- Event Handlers ---
  const handleAction = (itemId) => {
    setIsLoading(true);
    // Handle action
    setIsLoading(false);
  };

  // --- Render Methods ---
  const renderSection = () => {
    return (
      <div className="space-y-4">
        {/* Section content */}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Main component content */}
    </div>
  );
};

export default ComponentName;
```

### State Management Patterns

**Local Component State**
```jsx
// Authentication state
const [isAuthenticated, setIsAuthenticated] = useState(false);
const [user, setUser] = useState(null);

// UI state
const [activeTab, setActiveTab] = useState('dashboard');
const [selectedTrip, setSelectedTrip] = useState(null);
const [showInviteModal, setShowInviteModal] = useState(false);
const [showWizard, setShowWizard] = useState(false);

// Data state with mock data for development
const [plans, setPlans] = useState([
  {
    id: "1",
    title: "2024 West Coast Tour",
    season: 2024,
    role: "Admin",
    members: [
      { id: "u1", name: "Alex T.", email: "alex.t@example.com", role: "Owner" },
      { id: "u2", name: "Sarah J.", email: "sarah.j@example.com", role: "Editor" }
    ],
    trips: [
      {
        id: "t1",
        campground: "Yosemite Valley",
        startDate: "2024-06-15",
        endDate: "2024-06-20",
        reservations: [
          { userId: "u1", siteNumber: "A23", confirmationCode: "YV2024-A23" }
        ]
      }
    ]
  }
]);

// Loading and error states
const [isLoading, setIsLoading] = useState(false);
const [error, setError] = useState(null);
```

**State Update Patterns**
```jsx
// Adding new items to collections
const addTrip = (planId, newTrip) => {
  setPlans(prev => prev.map(plan => 
    plan.id === planId 
      ? { ...plan, trips: [...plan.trips, { ...newTrip, id: generateId() }] }
      : plan
  ));
};

// Updating nested objects
const updateTripReservation = (tripId, reservationData) => {
  setPlans(prev => prev.map(plan => ({
    ...plan,
    trips: plan.trips.map(trip => 
      trip.id === tripId
        ? { ...trip, reservations: [...trip.reservations, reservationData] }
        : trip
    )
  })));
};

// Removing items with confirmation
const removePlanMember = (planId, userId) => {
  if (window.confirm('Remove member from plan?')) {
    setPlans(prev => prev.map(plan => 
      plan.id === planId
        ? { ...plan, members: plan.members.filter(m => m.id !== userId) }
        : plan
    ));
  }
};
```

## Tailwind CSS Styling Patterns

### Layout Patterns
```jsx
// Main application layout
<div className="min-h-screen bg-gray-50">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div className="py-8">
      {/* Content */}
    </div>
  </div>
</div>

// Card layouts for camping content
<div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
  <div className="p-6">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-semibold text-gray-900">
        Plan Title
      </h3>
      <span className="text-sm text-gray-500">2024 Season</span>
    </div>
    {/* Card content */}
  </div>
</div>

// Responsive grid layouts
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {items.map(item => (
    <div key={item.id} className="...">
      {/* Grid item */}
    </div>
  ))}
</div>
```

### Interactive Elements
```jsx
// Primary buttons for main actions
<button 
  onClick={handleCreatePlan}
  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
>
  <Plus className="w-4 h-4 mr-2" />
  Create New Plan
</button>

// Secondary buttons for supporting actions
<button 
  onClick={handleInviteMembers}
  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
>
  <Users className="w-4 h-4 mr-2" />
  Invite Members
</button>

// Tab navigation
<div className="border-b border-gray-200">
  <nav className="-mb-px flex space-x-8">
    {['dashboard', 'plans', 'profile'].map((tab) => (
      <button
        key={tab}
        onClick={() => setActiveTab(tab)}
        className={`py-2 px-1 border-b-2 font-medium text-sm ${
          activeTab === tab
            ? 'border-blue-500 text-blue-600'
            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
        }`}
      >
        {tab.charAt(0).toUpperCase() + tab.slice(1)}
      </button>
    ))}
  </nav>
</div>
```

### Form Patterns
```jsx
// Form container with proper spacing
<form onSubmit={handleSubmit} className="space-y-6">
  <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
    <div>
      <label htmlFor="planTitle" className="block text-sm font-medium text-gray-700">
        Plan Title
      </label>
      <input
        type="text"
        id="planTitle"
        name="planTitle"
        value={formData.planTitle}
        onChange={handleInputChange}
        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
        placeholder="Enter plan title"
      />
    </div>
    
    <div>
      <label htmlFor="seasonYear" className="block text-sm font-medium text-gray-700">
        Season Year
      </label>
      <select
        id="seasonYear"
        name="seasonYear"
        value={formData.seasonYear}
        onChange={handleInputChange}
        className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="2024">2024</option>
        <option value="2025">2025</option>
        <option value="2026">2026</option>
      </select>
    </div>
  </div>
</form>
```

## Lucide Icons Integration

### Icon Usage Patterns
```jsx
import { 
  // Navigation and UI
  Calendar, MapPin, Users, Plus, Settings, ChevronRight, ArrowLeft,
  // Camping specific
  Tent, Truck, Compass, Mountain, Trees,
  // Actions
  CheckSquare, Circle, CheckCircle2, X, Check,
  // Communication
  Mail, MessageSquare, Share2, Link as LinkIcon,
  // Status and feedback
  Clock, Info, Star, Activity, Zap, Sparkles, ShieldCheck
} from 'lucide-react';

// Icon with consistent sizing and colors
const IconButton = ({ icon: Icon, label, onClick, variant = 'primary' }) => (
  <button
    onClick={onClick}
    className={`inline-flex items-center px-3 py-2 rounded-md text-sm font-medium ${
      variant === 'primary' 
        ? 'text-blue-600 bg-blue-50 hover:bg-blue-100'
        : 'text-gray-600 bg-gray-50 hover:bg-gray-100'
    }`}
  >
    <Icon className="w-4 h-4 mr-2" />
    {label}
  </button>
);

// Status indicators with icons
const TripStatus = ({ status }) => {
  const statusConfig = {
    planned: { icon: Clock, color: 'text-yellow-600 bg-yellow-100', label: 'Planned' },
    confirmed: { icon: CheckCircle2, color: 'text-green-600 bg-green-100', label: 'Confirmed' },
    completed: { icon: Check, color: 'text-gray-600 bg-gray-100', label: 'Completed' }
  };
  
  const config = statusConfig[status] || statusConfig.planned;
  const Icon = config.icon;
  
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
      <Icon className="w-3 h-3 mr-1" />
      {config.label}
    </span>
  );
};
```

### Domain-Specific Icon Usage
```jsx
// RV and camping context icons
const RvProfile = ({ rv }) => (
  <div className="flex items-center space-x-4">
    <Truck className="w-5 h-5 text-blue-600" />
    <div>
      <p className="font-medium">{rv.manufacturer} {rv.model}</p>
      <p className="text-sm text-gray-500">{rv.length}ft • {rv.electric}</p>
    </div>
  </div>
);

// Activity type indicators
const ActivityIcon = ({ type }) => {
  const icons = {
    gear: CheckSquare,
    meal: Utensils,
    reservation: Calendar,
    member: Users,
    campground: Tent
  };
  
  const Icon = icons[type] || Activity;
  return <Icon className="w-4 h-4" />;
};
```

## Authentication Flow Patterns

### Authentication State Management
```jsx
const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication
    const checkAuth = async () => {
      try {
        // Firebase auth check
        const token = localStorage.getItem('firebase-token');
        if (token) {
          // Validate token and set user
          setIsAuthenticated(true);
          setUser(/* decoded user data */);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    setIsLoading(true);
    try {
      // Firebase authentication
      const result = await signInWithEmailAndPassword(auth, credentials.email, credentials.password);
      setUser(result.user);
      setIsAuthenticated(true);
    } catch (error) {
      throw new Error('Login failed: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null);
      setIsAuthenticated(false);
      localStorage.removeItem('firebase-token');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### Protected Route Patterns
```jsx
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginComponent />;
  }
  
  return children;
};

// Usage in main app
const App = () => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <OnboardingFlow />;
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <MainContent />
    </div>
  );
};
```

## Modal and Dialog Patterns

### Modal Component Pattern
```jsx
const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg', 
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4">
        <div className="fixed inset-0 bg-black bg-opacity-25" onClick={onClose}></div>
        
        <div className={`relative bg-white rounded-lg shadow-xl ${sizeClasses[size]} w-full`}>
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            <button 
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};

// Usage for invite modal
const InviteMemberModal = ({ isOpen, onClose, planId }) => {
  const [email, setEmail] = useState('');
  const [permission, setPermission] = useState('Viewer');

  const handleInvite = async () => {
    try {
      // Send invitation
      await inviteMember(planId, { email, permission });
      onClose();
      setEmail('');
      setPermission('Viewer');
    } catch (error) {
      console.error('Invite failed:', error);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Invite Team Member" size="md">
      <form onSubmit={(e) => { e.preventDefault(); handleInvite(); }} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Email Address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="colleague@example.com"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700">Permission Level</label>
          <select
            value={permission}
            onChange={(e) => setPermission(e.target.value)}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="Viewer">Viewer</option>
            <option value="Editor">Editor</option>
            <option value="Admin">Admin</option>
          </select>
        </div>

        <div className="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
          >
            <Mail className="w-4 h-4 mr-2 inline" />
            Send Invitation
          </button>
        </div>
      </form>
    </Modal>
  );
};
```

## Camping Domain UI Patterns

### Trip Planning Components
```jsx
const TripCard = ({ trip, onEdit, onViewDetails }) => (
  <div className="bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
    <div className="p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <Tent className="w-5 h-5 text-green-600" />
          <div>
            <h3 className="font-semibold text-gray-900">{trip.campground}</h3>
            <p className="text-sm text-gray-500">{trip.location}</p>
          </div>
        </div>
        <TripStatus status={trip.status} />
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <Calendar className="w-4 h-4 mr-2" />
          {formatDateRange(trip.startDate, trip.endDate)}
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <Users className="w-4 h-4 mr-2" />
          {trip.reservations.length} reservation{trip.reservations.length !== 1 ? 's' : ''}
        </div>
        {trip.rvCompatible && (
          <div className="flex items-center text-sm text-green-600">
            <Truck className="w-4 h-4 mr-2" />
            RV Compatible
          </div>
        )}
      </div>

      <div className="flex justify-between items-center pt-4 border-t border-gray-100">
        <button
          onClick={() => onViewDetails(trip.id)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          View Details
        </button>
        <button
          onClick={() => onEdit(trip.id)}
          className="inline-flex items-center px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded-full hover:bg-gray-200"
        >
          <Settings className="w-3 h-3 mr-1" />
          Edit
        </button>
      </div>
    </div>
  </div>
);
```

### RV Compatibility Component
```jsx
const RvCompatibilityCheck = ({ userRv, campgroundSpecs }) => {
  const checkCompatibility = (spec, required, available) => {
    if (!required) return { status: 'ok', message: 'Not specified' };
    if (!available) return { status: 'unknown', message: 'Unknown' };
    
    const isCompatible = available >= required;
    return {
      status: isCompatible ? 'ok' : 'warning',
      message: isCompatible ? 'Compatible' : `Requires ${required}, available ${available}`
    };
  };

  const checks = [
    {
      label: 'Length',
      check: checkCompatibility('length', userRv?.length, campgroundSpecs?.maxLength)
    },
    {
      label: 'Width', 
      check: checkCompatibility('width', userRv?.width, campgroundSpecs?.maxWidth)
    },
    {
      label: 'Height',
      check: checkCompatibility('height', userRv?.height, campgroundSpecs?.maxHeight)
    }
  ];

  return (
    <div className="bg-gray-50 rounded-lg p-4">
      <div className="flex items-center mb-3">
        <Truck className="w-4 h-4 text-blue-600 mr-2" />
        <span className="font-medium text-gray-900">RV Compatibility</span>
      </div>
      
      <div className="space-y-2">
        {checks.map((item, index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-sm text-gray-600">{item.label}</span>
            <div className="flex items-center">
              {item.check.status === 'ok' && <CheckCircle2 className="w-4 h-4 text-green-500 mr-1" />}
              {item.check.status === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-500 mr-1" />}
              {item.check.status === 'unknown' && <Info className="w-4 h-4 text-gray-400 mr-1" />}
              <span className="text-sm text-gray-700">{item.check.message}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Gear and Meal Planning Components
```jsx
const GearItem = ({ item, onClaim, onUnclaim, currentUserId }) => {
  const isClaimed = item.claimedBy;
  const isClaimedByUser = item.claimedBy?.id === currentUserId;

  return (
    <div className={`flex items-center justify-between p-3 rounded-md border ${
      isClaimed 
        ? isClaimedByUser 
          ? 'bg-green-50 border-green-200' 
          : 'bg-gray-50 border-gray-200'
        : 'bg-white border-gray-300'
    }`}>
      <div className="flex items-center space-x-3">
        <CheckSquare className={`w-4 h-4 ${isClaimed ? 'text-green-600' : 'text-gray-400'}`} />
        <div>
          <p className="font-medium text-gray-900">{item.name}</p>
          {item.notes && (
            <p className="text-sm text-gray-500">{item.notes}</p>
          )}
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        {isClaimed ? (
          <>
            <span className="text-sm text-gray-600">
              {isClaimedByUser ? 'You' : item.claimedBy.name}
            </span>
            {isClaimedByUser && (
              <button
                onClick={() => onUnclaim(item.id)}
                className="text-xs text-red-600 hover:text-red-700"
              >
                Unclaim
              </button>
            )}
          </>
        ) : (
          <button
            onClick={() => onClaim(item.id)}
            className="text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            Claim
          </button>
        )}
      </div>
    </div>
  );
};
```

## Loading and Error State Patterns

### Loading States
```jsx
const LoadingSpinner = ({ size = 'md', message = 'Loading...' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8', 
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex flex-col items-center justify-center py-8">
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
      <p className="mt-4 text-gray-600 text-sm">{message}</p>
    </div>
  );
};

// Skeleton loading for cards
const TripCardSkeleton = () => (
  <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-6">
    <div className="animate-pulse">
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-5 h-5 bg-gray-300 rounded"></div>
        <div className="flex-1">
          <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-gray-300 rounded w-1/2"></div>
        </div>
      </div>
      <div className="space-y-2 mb-4">
        <div className="h-3 bg-gray-300 rounded"></div>
        <div className="h-3 bg-gray-300 rounded w-2/3"></div>
      </div>
    </div>
  </div>
);
```

### Error State Components
```jsx
const ErrorBoundary = ({ error, onRetry, children }) => {
  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <AlertTriangle className="h-5 w-5 text-red-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Something went wrong</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error.message || 'An unexpected error occurred'}</p>
            </div>
            {onRetry && (
              <div className="mt-4">
                <button
                  onClick={onRetry}
                  className="bg-red-100 px-2 py-1 text-xs font-semibold text-red-800 rounded"
                >
                  Try again
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  return children;
};
```

## Testing Patterns

### Component Testing Setup
```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import TripCard from './TripCard';

const mockTrip = {
  id: 't1',
  campground: 'Yosemite Valley',
  location: 'California',
  startDate: '2024-06-15',
  endDate: '2024-06-20',
  status: 'confirmed',
  reservations: [{ userId: 'u1', siteNumber: 'A23' }],
  rvCompatible: true
};

describe('TripCard', () => {
  const mockOnEdit = vi.fn();
  const mockOnViewDetails = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders trip information correctly', () => {
    render(
      <TripCard 
        trip={mockTrip} 
        onEdit={mockOnEdit} 
        onViewDetails={mockOnViewDetails}
      />
    );

    expect(screen.getByText('Yosemite Valley')).toBeInTheDocument();
    expect(screen.getByText('California')).toBeInTheDocument();
    expect(screen.getByText('RV Compatible')).toBeInTheDocument();
    expect(screen.getByText('1 reservation')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    render(
      <TripCard 
        trip={mockTrip} 
        onEdit={mockOnEdit} 
        onViewDetails={mockOnViewDetails}
      />
    );

    fireEvent.click(screen.getByText('Edit'));
    expect(mockOnEdit).toHaveBeenCalledWith('t1');
  });

  it('calls onViewDetails when view details button is clicked', () => {
    render(
      <TripCard 
        trip={mockTrip} 
        onEdit={mockOnEdit} 
        onViewDetails={mockOnViewDetails}
      />
    );

    fireEvent.click(screen.getByText('View Details'));
    expect(mockOnViewDetails).toHaveBeenCalledWith('t1');
  });
});
```

## Performance Optimization

### React.memo for Expensive Components
```jsx
const TripCard = React.memo(({ trip, onEdit, onViewDetails }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison for optimization
  return (
    prevProps.trip.id === nextProps.trip.id &&
    prevProps.trip.status === nextProps.trip.status &&
    prevProps.trip.reservations.length === nextProps.trip.reservations.length
  );
});
```

### useCallback for Event Handlers
```jsx
const PlanManager = () => {
  const [plans, setPlans] = useState([]);

  const handleEditPlan = useCallback((planId) => {
    // Edit logic
  }, []);

  const handleDeletePlan = useCallback((planId) => {
    setPlans(prev => prev.filter(p => p.id !== planId));
  }, []);

  return (
    <div>
      {plans.map(plan => (
        <PlanCard 
          key={plan.id}
          plan={plan}
          onEdit={handleEditPlan}
          onDelete={handleDeletePlan}
        />
      ))}
    </div>
  );
};
```

Remember: This skill automatically activates when working on React component tasks. Always prioritize user experience, accessibility, and the collaborative camping domain context in your component implementations.