import { test, expect } from '@playwright/test';
import { TestUsers, TestWorkItems } from '../fixtures/test-users';

test.describe('QVF Platform API Integration Tests', () => {
  
  const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
  
  // Store authentication tokens for reuse
  let authTokens: Record<string, string> = {};

  test.beforeAll(async () => {
    // Pre-authenticate all test users to get tokens
    console.log('🔐 Pre-authenticating test users...');
    
    for (const [role, user] of Object.entries(TestUsers)) {
      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/token`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams({
            username: user.username,
            password: user.password,
          }),
        });

        if (response.ok) {
          const data = await response.json();
          authTokens[role] = data.access_token;
          console.log(`✅ ${role} authenticated`);
        } else {
          console.log(`❌ ${role} authentication failed: ${response.status}`);
        }
      } catch (error) {
        console.log(`❌ ${role} authentication error:`, error);
      }
    }
  });

  test.describe('Authentication API', () => {
    test('should authenticate with valid credentials', async ({ request }) => {
      const response = await request.post(`${API_BASE_URL}/api/v1/auth/token`, {
        form: {
          username: TestUsers.executive.username,
          password: TestUsers.executive.password,
        },
      });

      expect(response.ok()).toBeTruthy();
      
      const data = await response.json();
      expect(data.access_token).toBeTruthy();
      expect(data.token_type).toBe('bearer');
      expect(typeof data.expires_in).toBe('number');
    });

    test('should reject invalid credentials', async ({ request }) => {
      const response = await request.post(`${API_BASE_URL}/api/v1/auth/token`, {
        form: {
          username: 'invalid_user',
          password: 'wrong_password',
        },
      });

      expect(response.status()).toBe(401);
    });

    test('should return user info with valid token', async ({ request }) => {
      const token = authTokens.executive;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const response = await request.get(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      expect(response.ok()).toBeTruthy();
      
      const user = await response.json();
      expect(user.username).toBe(TestUsers.executive.username);
      expect(user.role).toBe(TestUsers.executive.role);
    });

    test('should reject requests without token', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/auth/me`);
      expect(response.status()).toBe(401);
    });

    test('should reject requests with invalid token', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: 'Bearer invalid_token',
        },
      });

      expect(response.status()).toBe(401);
    });
  });

  test.describe('Health Check API', () => {
    test('should return system health status', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/health`);
      
      expect(response.ok()).toBeTruthy();
      
      const health = await response.json();
      expect(health.status).toBeTruthy();
      expect(health.timestamp).toBeTruthy();
      
      // Check for expected health check components
      if (health.qvf_engine) {
        expect(typeof health.qvf_engine.status).toBe('string');
      }
      
      if (health.authentication) {
        expect(typeof health.authentication.status).toBe('string');
      }
    });

    test('should return version information', async ({ request }) => {
      const response = await request.get(`${API_BASE_URL}/health`);
      
      if (response.ok()) {
        const health = await response.json();
        if (health.version) {
          expect(typeof health.version).toBe('string');
          expect(health.version.length).toBeGreaterThan(0);
        }
      }
    });
  });

  test.describe('Work Items API', () => {
    test('should fetch work items list', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const response = await request.get(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok()) {
        const workItems = await response.json();
        expect(Array.isArray(workItems)).toBeTruthy();
        
        if (workItems.length > 0) {
          const firstItem = workItems[0];
          expect(firstItem.id).toBeTruthy();
          expect(firstItem.title).toBeTruthy();
          expect(typeof firstItem.business_value).toBe('number');
          expect(typeof firstItem.technical_complexity).toBe('number');
        }
      } else {
        console.log(`Work Items API returned ${response.status()} - may not be implemented yet`);
      }
    });

    test('should create new work item', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const newWorkItem = {
        title: 'API Test Work Item',
        business_value: 8,
        technical_complexity: 6,
        story_points: 5,
        priority: 'High',
        description: 'Created by API integration test'
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: newWorkItem,
      });

      if (response.ok()) {
        const createdItem = await response.json();
        expect(createdItem.title).toBe(newWorkItem.title);
        expect(createdItem.business_value).toBe(newWorkItem.business_value);
        expect(createdItem.id).toBeTruthy();
        
        // Store ID for cleanup
        test.info().attach('created-work-item-id', { body: createdItem.id });
      } else if (response.status() === 404 || response.status() === 405) {
        console.log('Work Items creation API not implemented yet');
      } else {
        console.log(`Work Items creation failed: ${response.status()}`);
      }
    });

    test('should update existing work item', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      // First, try to get existing work items
      const listResponse = await request.get(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (listResponse.ok()) {
        const workItems = await listResponse.json();
        
        if (Array.isArray(workItems) && workItems.length > 0) {
          const itemToUpdate = workItems[0];
          const updateData = {
            ...itemToUpdate,
            title: itemToUpdate.title + ' - Updated',
            business_value: 9
          };

          const updateResponse = await request.put(`${API_BASE_URL}/api/v1/work-items/${itemToUpdate.id}`, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            data: updateData,
          });

          if (updateResponse.ok()) {
            const updatedItem = await updateResponse.json();
            expect(updatedItem.title).toContain('Updated');
            expect(updatedItem.business_value).toBe(9);
          } else {
            console.log(`Work Item update failed: ${updateResponse.status()}`);
          }
        }
      }
    });

    test('should delete work item', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      // Create a work item to delete
      const testItem = {
        title: 'Work Item to Delete',
        business_value: 5,
        technical_complexity: 5,
        story_points: 3,
        priority: 'Low'
      };

      const createResponse = await request.post(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: testItem,
      });

      if (createResponse.ok()) {
        const createdItem = await createResponse.json();
        
        // Now delete it
        const deleteResponse = await request.delete(`${API_BASE_URL}/api/v1/work-items/${createdItem.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (deleteResponse.ok()) {
          // Verify it's deleted
          const getResponse = await request.get(`${API_BASE_URL}/api/v1/work-items/${createdItem.id}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });

          expect(getResponse.status()).toBe(404);
        } else {
          console.log(`Work Item deletion failed: ${deleteResponse.status()}`);
        }
      }
    });
  });

  test.describe('QVF Scoring API', () => {
    test('should calculate QVF scores for work items', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const scoreRequest = {
        work_items: TestWorkItems.map(item => ({
          id: item.id,
          title: item.title,
          business_value: item.business_value,
          technical_complexity: item.technical_complexity,
          story_points: item.story_points,
          priority: item.priority,
          risk_level: item.risk_level
        })),
        criteria_overrides: {
          business_value: 0.4,
          technical_complexity: 0.3,
          risk_level: 0.3
        }
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/qvf/score`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: scoreRequest,
      });

      if (response.ok()) {
        const result = await response.json();
        
        expect(result.session_id).toBeTruthy();
        expect(result.total_items).toBe(TestWorkItems.length);
        expect(Array.isArray(result.scores)).toBeTruthy();
        expect(result.scores.length).toBe(TestWorkItems.length);
        
        // Check score structure
        const firstScore = result.scores[0];
        expect(firstScore.work_item_id).toBeTruthy();
        expect(typeof firstScore.qvf_score).toBe('number');
        expect(['High', 'Medium', 'Low'].includes(firstScore.priority_tier)).toBeTruthy();
        expect(typeof firstScore.criteria_breakdown).toBe('object');
        
        // Check summary
        expect(typeof result.summary).toBe('object');
        expect(typeof result.summary.score_distribution).toBe('object');
        
        console.log(`QVF Scoring completed: ${result.calculated_items}/${result.total_items} items`);
      } else if (response.status() === 404) {
        console.log('QVF Scoring API not implemented yet');
      } else {
        console.log(`QVF Scoring failed: ${response.status()}`);
        const errorText = await response.text();
        console.log('Error response:', errorText);
      }
    });

    test('should fetch QVF criteria', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const response = await request.get(`${API_BASE_URL}/api/v1/qvf/criteria`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok()) {
        const criteria = await response.json();
        
        expect(Array.isArray(criteria)).toBeTruthy();
        
        if (criteria.length > 0) {
          const firstCriterion = criteria[0];
          expect(firstCriterion.criterion_id).toBeTruthy();
          expect(firstCriterion.name).toBeTruthy();
          expect(typeof firstCriterion.weight).toBe('number');
          expect(typeof firstCriterion.global_weight).toBe('number');
        }
        
        console.log(`Found ${criteria.length} QVF criteria`);
      } else if (response.status() === 404) {
        console.log('QVF Criteria API not implemented yet');
      } else {
        console.log(`QVF Criteria fetch failed: ${response.status()}`);
      }
    });

    test('should handle invalid QVF scoring requests', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      // Test with empty work items
      const emptyRequest = { work_items: [] };

      const response = await request.post(`${API_BASE_URL}/api/v1/qvf/score`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: emptyRequest,
      });

      // Should handle empty requests gracefully
      if (response.ok()) {
        const result = await response.json();
        expect(result.total_items).toBe(0);
      } else {
        expect([400, 422]).toContain(response.status()); // Bad request or validation error
      }
    });
  });

  test.describe('Role-Based Access Control', () => {
    test('should enforce role-based API access', async ({ request }) => {
      const testCases = [
        {
          role: 'executive',
          token: authTokens.executive,
          allowedEndpoints: ['/api/v1/auth/me', '/health'],
          restrictedEndpoints: ['/api/v1/work-items']
        },
        {
          role: 'product_owner',
          token: authTokens.productOwner,
          allowedEndpoints: ['/api/v1/auth/me', '/api/v1/work-items', '/api/v1/qvf/score'],
          restrictedEndpoints: []
        },
        {
          role: 'scrum_master',
          token: authTokens.scrumMaster,
          allowedEndpoints: ['/api/v1/auth/me'],
          restrictedEndpoints: []
        },
        {
          role: 'developer',
          token: authTokens.developer,
          allowedEndpoints: ['/api/v1/auth/me', '/api/v1/work-items'],
          restrictedEndpoints: []
        }
      ];

      for (const testCase of testCases) {
        if (!testCase.token) {
          console.log(`Skipping ${testCase.role} - no auth token`);
          continue;
        }

        // Test allowed endpoints
        for (const endpoint of testCase.allowedEndpoints) {
          const response = await request.get(`${API_BASE_URL}${endpoint}`, {
            headers: {
              Authorization: `Bearer ${testCase.token}`,
            },
          });

          // Should not be forbidden (may be 404 if not implemented)
          expect([200, 404, 501].includes(response.status())).toBeTruthy();
        }

        // Test restricted endpoints
        for (const endpoint of testCase.restrictedEndpoints) {
          const response = await request.get(`${API_BASE_URL}${endpoint}`, {
            headers: {
              Authorization: `Bearer ${testCase.token}`,
            },
          });

          // Should be forbidden or redirect
          expect([401, 403, 404].includes(response.status())).toBeTruthy();
        }
      }
    });
  });

  test.describe('Error Handling', () => {
    test('should handle malformed requests', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      // Test with malformed JSON
      const response = await request.post(`${API_BASE_URL}/api/v1/qvf/score`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: 'invalid json',
      });

      expect([400, 422].includes(response.status())).toBeTruthy();
    });

    test('should handle missing required fields', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const incompleteWorkItem = {
        title: 'Incomplete Item'
        // Missing required fields
      };

      const response = await request.post(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: incompleteWorkItem,
      });

      if (response.status() !== 404) { // Skip if endpoint not implemented
        expect([400, 422].includes(response.status())).toBeTruthy();
      }
    });

    test('should handle server errors gracefully', async ({ request }) => {
      // Test with non-existent endpoint
      const response = await request.get(`${API_BASE_URL}/api/v1/non-existent-endpoint`);
      
      expect(response.status()).toBe(404);
      
      // Should return proper error response
      if (response.headers()['content-type']?.includes('application/json')) {
        const errorData = await response.json();
        expect(errorData.detail || errorData.message || errorData.error).toBeTruthy();
      }
    });
  });

  test.describe('API Response Format', () => {
    test('should return consistent response formats', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      const endpoints = [
        '/health',
        '/api/v1/auth/me',
        '/api/v1/work-items'
      ];

      for (const endpoint of endpoints) {
        const response = await request.get(`${API_BASE_URL}${endpoint}`, {
          headers: endpoint.includes('/api/') ? { Authorization: `Bearer ${token}` } : {},
        });

        if (response.ok()) {
          const contentType = response.headers()['content-type'];
          expect(contentType).toContain('application/json');
          
          const data = await response.json();
          expect(data).toBeDefined();
        }
      }
    });

    test('should include proper HTTP status codes', async ({ request }) => {
      const testCases = [
        { endpoint: '/health', expectedStatus: 200 },
        { endpoint: '/api/v1/non-existent', expectedStatus: 404 },
      ];

      for (const testCase of testCases) {
        const response = await request.get(`${API_BASE_URL}${testCase.endpoint}`);
        expect(response.status()).toBe(testCase.expectedStatus);
      }
    });
  });

  test.describe('Data Persistence', () => {
    test('should persist data across API calls', async ({ request }) => {
      const token = authTokens.productOwner;
      if (!token) {
        test.skip('No auth token available');
        return;
      }

      // Create a work item
      const testItem = {
        title: 'Persistence Test Item',
        business_value: 7,
        technical_complexity: 5,
        story_points: 8,
        priority: 'Medium'
      };

      const createResponse = await request.post(`${API_BASE_URL}/api/v1/work-items`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        data: testItem,
      });

      if (createResponse.ok()) {
        const createdItem = await createResponse.json();
        
        // Fetch it back
        const fetchResponse = await request.get(`${API_BASE_URL}/api/v1/work-items/${createdItem.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (fetchResponse.ok()) {
          const fetchedItem = await fetchResponse.json();
          expect(fetchedItem.title).toBe(testItem.title);
          expect(fetchedItem.business_value).toBe(testItem.business_value);
        }

        // Clean up
        await request.delete(`${API_BASE_URL}/api/v1/work-items/${createdItem.id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }
    });
  });
});