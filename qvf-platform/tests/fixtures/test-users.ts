/**
 * Test user definitions for QVF Platform E2E tests
 * These users should match the test users configured in the backend
 */

export interface TestUser {
  username: string;
  password: string;
  role: string;
  fullName: string;
  full_name: string; // Added for compatibility
  permissions: string[];
  defaultRoute: string;
}

export const TestUsers = {
  executive: {
    username: 'executive',
    password: 'executive123',
    role: 'executive',
    fullName: 'Executive User',
    full_name: 'Executive User',
    permissions: ['view_portfolio', 'view_analytics', 'view_executive_dashboard'],
    defaultRoute: '/dashboard/executive'
  } as TestUser,

  productOwner: {
    username: 'product_owner',
    password: 'po123',
    role: 'product_owner', 
    fullName: 'Product Owner',
    full_name: 'Product Owner',
    permissions: ['manage_epics', 'view_planning', 'view_analytics', 'manage_backlog'],
    defaultRoute: '/dashboard/product-owner'
  } as TestUser,

  scrumMaster: {
    username: 'scrum_master',
    password: 'sm123',
    role: 'scrum_master',
    fullName: 'Scrum Master',
    full_name: 'Scrum Master',
    permissions: ['manage_sprints', 'view_team_metrics', 'view_analytics', 'manage_impediments'],
    defaultRoute: '/dashboard/scrum-master'
  } as TestUser,

  developer: {
    username: 'developer',
    password: 'dev123',
    role: 'developer',
    fullName: 'Developer User',
    full_name: 'Developer User',
    permissions: ['view_work_items', 'update_tasks', 'view_team_dashboard'],
    defaultRoute: '/work-items'
  } as TestUser,
} as const;

/**
 * Get all test users as an array
 */
export const getAllTestUsers = (): TestUser[] => {
  return Object.values(TestUsers);
};

/**
 * Get test user by role
 */
export const getTestUserByRole = (role: string): TestUser | undefined => {
  return getAllTestUsers().find(user => user.role === role);
};

/**
 * Test data for work items
 */
export const TestWorkItems = [
  {
    id: 'WI-001',
    title: 'User Authentication Feature',
    business_value: 8,
    technical_complexity: 6,
    story_points: 8,
    priority: 'High' as const,
    risk_level: 3,
    state: 'New',
    assigned_to: 'developer'
  },
  {
    id: 'WI-002', 
    title: 'Dashboard Performance Optimization',
    business_value: 6,
    technical_complexity: 8,
    story_points: 13,
    priority: 'Medium' as const,
    risk_level: 5,
    state: 'Active',
    assigned_to: 'developer'
  },
  {
    id: 'WI-003',
    title: 'QVF Algorithm Enhancement',
    business_value: 9,
    technical_complexity: 9,
    story_points: 21,
    priority: 'High' as const,
    risk_level: 7,
    state: 'New',
    assigned_to: 'developer'
  }
] as const;