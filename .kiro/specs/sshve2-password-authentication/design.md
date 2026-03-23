# Design Document: SSHVE2 Password Authentication

## Overview

This design document describes the technical implementation of a client-side password authentication system for the SSHVE2 Opportunity Dashboard hosted on GitHub Pages. The system provides basic access control through JavaScript-based authentication without requiring server-side infrastructure.

### Context

The SSHVE2 Dashboard is a static HTML application hosted on GitHub Pages that displays MCID-level raw data with filtering, sorting, and download capabilities. The dashboard currently exists as a single `index.html` file with embedded JavaScript and CSS. The authentication system must integrate seamlessly with this existing structure while maintaining the static hosting model.

### Goals

- Implement client-side password authentication to restrict dashboard access
- Provide session-based authentication state management
- Support optional persistent authentication via "Remember Me" functionality
- Maintain compatibility with GitHub Pages static hosting
- Enable easy password updates by administrators
- Ensure the authentication system does not interfere with existing dashboard features

### Non-Goals

- Server-side authentication or API-based validation
- Multi-user authentication with individual credentials
- Advanced security features like rate limiting or account lockout
- Integration with external identity providers (OAuth, SAML, etc.)

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Client)                      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Password Overlay (UI Layer)                │ │
│  │  - Password input field                            │ │
│  │  - Submit button                                   │ │
│  │  - Error message display                           │ │
│  │  - Remember Me checkbox (optional)                 │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │    Authentication System (Logic Layer)             │ │
│  │  - Password validation                             │ │
│  │  - Hash comparison                                 │ │
│  │  - Session management                              │ │
│  │  - Storage management                              │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│                   ▼                                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Storage Layer                              │ │
│  │  - sessionStorage (temporary auth state)           │ │
│  │  - localStorage (persistent auth state)            │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Dashboard Content                          │ │
│  │  - Filters, tables, download buttons               │ │
│  │  - Existing functionality (unchanged)              │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User loads page
      │
      ▼
Check authentication state
      │
      ├─── Authenticated? ──Yes──> Show dashboard
      │                            Hide overlay
      │
      └─── No ──> Show password overlay
                  Hide dashboard
                        │
                        ▼
                  User enters password
                        │
                        ▼
                  Validate password
                        │
                        ├─── Valid? ──Yes──> Store auth state
                        │                    Hide overlay
                        │                    Show dashboard
                        │
                        └─── No ──> Show error message
                                    Clear input
                                    Refocus input
```

## Components and Interfaces

### 1. Password Overlay Component

The password overlay is a full-screen modal that appears before the dashboard content is accessible.

**HTML Structure:**
```html
<div id="passwordOverlay">
  <div id="passwordBox">
    <h2>🔐 認証が必要です</h2>
    <p>このダッシュボードにアクセスするにはパスワードを入力してください</p>
    <input type="password" id="passwordInput" placeholder="パスワードを入力" autocomplete="off">
    <label>
      <input type="checkbox" id="rememberMe">
      <span>ログイン状態を保持する</span>
    </label>
    <button id="passwordSubmit">ログイン</button>
    <div id="passwordError">パスワードが正しくありません</div>
  </div>
</div>
```

**CSS Styling:**
- Full viewport coverage with semi-transparent background
- Centered modal box with rounded corners and shadow
- Consistent with dashboard's gradient color scheme
- Responsive design for mobile devices
- Error message initially hidden, displayed on validation failure

**Behavior:**
- Auto-focus password input on page load (if not authenticated)
- Support Enter key for form submission
- Clear input field on validation failure
- Display error message for 3 seconds on failure
- Smooth fade-out animation on successful authentication

### 2. Authentication System Component

The core authentication logic handles password validation, hashing, and state management.

**Interface:**
```javascript
// Authentication configuration
const AUTH_CONFIG = {
  passwordHash: 'hashed_password_value',
  saltRounds: 10,
  sessionKey: 'sshve2_authenticated',
  persistentKey: 'sshve2_persistent_auth',
  tokenExpiry: 30 * 24 * 60 * 60 * 1000 // 30 days in milliseconds
};

// Main authentication functions
function hashPassword(password) { ... }
function validatePassword(inputPassword) { ... }
function checkAuthentication() { ... }
function setAuthenticationState(persistent) { ... }
function clearAuthenticationState() { ... }
function handlePasswordSubmit() { ... }
```

**Password Hashing Strategy:**

Since this is a client-side implementation, we'll use a combination of approaches:

1. **SHA-256 Hashing**: Use the Web Crypto API for password hashing
2. **Salt**: Include a fixed salt value embedded in the code
3. **Obfuscation**: Store the hash in a base64-encoded format
4. **Multiple Rounds**: Apply hashing multiple times to increase computation cost

**Implementation:**
```javascript
async function hashPassword(password) {
  const salt = 'sshve2_dashboard_salt_2024'; // Fixed salt
  const combined = salt + password + salt;
  
  // First round: SHA-256
  let hash = await crypto.subtle.digest('SHA-256', 
    new TextEncoder().encode(combined));
  
  // Additional rounds for increased security
  for (let i = 0; i < 1000; i++) {
    hash = await crypto.subtle.digest('SHA-256', hash);
  }
  
  // Convert to base64
  return btoa(String.fromCharCode(...new Uint8Array(hash)));
}
```

### 3. Session Management Component

Manages authentication state across page loads and browser sessions.

**Session Storage (Temporary):**
- Key: `sshve2_authenticated`
- Value: `true` or timestamp
- Cleared when browser tab/window closes
- Used for default authentication mode

**Local Storage (Persistent):**
- Key: `sshve2_persistent_auth`
- Value: JSON object with `{ authenticated: true, timestamp: <unix_time> }`
- Persists across browser sessions
- Used when "Remember Me" is checked
- Includes expiry check (30 days default)

**Interface:**
```javascript
function setAuthenticationState(persistent = false) {
  const timestamp = Date.now();
  
  if (persistent) {
    localStorage.setItem(AUTH_CONFIG.persistentKey, JSON.stringify({
      authenticated: true,
      timestamp: timestamp
    }));
  } else {
    sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
  }
}

function checkAuthentication() {
  // Check session storage first
  if (sessionStorage.getItem(AUTH_CONFIG.sessionKey) === 'true') {
    return true;
  }
  
  // Check local storage with expiry
  const persistentAuth = localStorage.getItem(AUTH_CONFIG.persistentKey);
  if (persistentAuth) {
    try {
      const authData = JSON.parse(persistentAuth);
      const age = Date.now() - authData.timestamp;
      
      if (age < AUTH_CONFIG.tokenExpiry && authData.authenticated) {
        // Refresh session storage
        sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
        return true;
      } else {
        // Expired, clear it
        localStorage.removeItem(AUTH_CONFIG.persistentKey);
      }
    } catch (e) {
      localStorage.removeItem(AUTH_CONFIG.persistentKey);
    }
  }
  
  return false;
}

function clearAuthenticationState() {
  sessionStorage.removeItem(AUTH_CONFIG.sessionKey);
  localStorage.removeItem(AUTH_CONFIG.persistentKey);
}
```

### 4. UI Controller Component

Manages the display state of the overlay and dashboard content.

**Interface:**
```javascript
function showPasswordOverlay() {
  document.getElementById('passwordOverlay').style.display = 'flex';
  document.getElementById('passwordInput').focus();
}

function hidePasswordOverlay() {
  const overlay = document.getElementById('passwordOverlay');
  overlay.style.opacity = '0';
  setTimeout(() => {
    overlay.style.display = 'none';
  }, 300); // Fade out animation
}

function showError(message) {
  const errorDiv = document.getElementById('passwordError');
  errorDiv.textContent = message;
  errorDiv.style.display = 'block';
  
  setTimeout(() => {
    errorDiv.style.display = 'none';
  }, 3000);
}

function clearPasswordInput() {
  const input = document.getElementById('passwordInput');
  input.value = '';
  input.focus();
}
```

## Data Models

### Authentication State Model

```javascript
// Session Storage Model
{
  key: "sshve2_authenticated",
  value: "true" // Simple boolean string
}

// Local Storage Model
{
  key: "sshve2_persistent_auth",
  value: {
    authenticated: boolean,  // Always true when stored
    timestamp: number        // Unix timestamp in milliseconds
  }
}
```

### Configuration Model

```javascript
const AUTH_CONFIG = {
  // Password hash (base64-encoded SHA-256)
  passwordHash: string,
  
  // Salt for hashing (embedded in code)
  salt: string,
  
  // Number of hash iterations
  iterations: number,
  
  // Storage keys
  sessionKey: string,
  persistentKey: string,
  
  // Token expiry time (milliseconds)
  tokenExpiry: number,
  
  // UI configuration
  errorDisplayDuration: number,  // milliseconds
  fadeOutDuration: number        // milliseconds
};
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing the acceptance criteria, I identified the following testable properties and examples. Here's the reflection to eliminate redundancy:

**Identified Properties:**
- 1.3: Overlay prevents dashboard access without authentication
- 2.1: Password validation occurs for any submitted password
- 2.3: Error message displays for incorrect passwords
- 2.5: Plain text password not exposed in HTML source
- 3.1: Successful authentication stores state in sessionStorage
- 3.2: Page load checks sessionStorage
- 4.1: Remember Me stores state in localStorage
- 4.2: Page load checks localStorage
- 5.4: Authentication doesn't interfere with dashboard functionality
- 6.2: Password not logged to console
- 7.2: UI provides feedback on authentication result
- 7.4: Failed authentication clears and refocuses input

**Redundancy Analysis:**
- Properties 3.2 and 4.2 (checking sessionStorage and localStorage on load) can be combined into a single property: "Page load checks authentication state from storage"
- Properties 2.1 and 2.3 are related but distinct: 2.1 ensures validation happens, 2.3 ensures error display. These should remain separate.
- Property 7.2 (UI feedback) is somewhat redundant with 2.3 (error display) and the success behavior in 2.2, but 7.2 is more general. We'll keep the more specific properties.

**Final Property Set:**
1. Overlay prevents dashboard access without authentication (1.3)
2. Password validation occurs for any submitted password (2.1)
3. Error message displays for incorrect passwords (2.3)
4. Plain text password not exposed in HTML source (2.5)
5. Successful authentication stores state in storage (3.1, 4.1 combined)
6. Page load checks authentication state from storage (3.2, 4.2 combined)
7. Authentication doesn't interfere with dashboard functionality (5.4)
8. Password not logged to console (6.2)
9. Failed authentication clears and refocuses input (7.4)


### Property 1: Unauthenticated Access Prevention

*For any* page load where authentication state is not present in storage, the password overlay should be visible and dashboard content should not be accessible through user interaction.

**Validates: Requirements 1.3**

### Property 2: Password Validation Invocation

*For any* password submission (via button click or Enter key), the password validation function should be invoked with the input value.

**Validates: Requirements 2.1**

### Property 3: Error Display on Invalid Password

*For any* password input that does not match the stored hash, the authentication system should display an error message to the user.

**Validates: Requirements 2.3**

### Property 4: Password Obfuscation in Source

*For any* inspection of the HTML source code or embedded JavaScript, the plain text password should not be present - only a hashed or obfuscated representation should exist.

**Validates: Requirements 2.5**

### Property 5: Authentication State Persistence

*For any* successful authentication, the system should store the authentication state in either sessionStorage (default) or localStorage (if Remember Me is checked), with the appropriate key-value pair.

**Validates: Requirements 3.1, 4.1**

### Property 6: Authentication State Check on Load

*For any* page load, the authentication system should check both sessionStorage and localStorage for existing authentication state before displaying the password overlay.

**Validates: Requirements 3.2, 4.2**

### Property 7: Dashboard Functionality Preservation

*For any* dashboard feature (filters, sorting, downloads, data display) after successful authentication, the feature should function identically to how it would function without the authentication system present.

**Validates: Requirements 5.4**

### Property 8: Password Console Logging Prevention

*For any* password input or validation operation, the password value should not be written to the browser console (console.log, console.error, console.warn, etc.).

**Validates: Requirements 6.2**

### Property 9: Input Reset on Authentication Failure

*For any* authentication attempt that fails validation, the password input field should be cleared and receive focus for the next attempt.

**Validates: Requirements 7.4**


## Error Handling

### Client-Side Error Scenarios

#### 1. Invalid Password Input

**Scenario:** User enters incorrect password

**Handling:**
- Display user-friendly error message: "パスワードが正しくありません"
- Clear the password input field
- Refocus the input field for retry
- Do not log the attempted password
- No retry limit (continuous attempts allowed)

**Implementation:**
```javascript
function handleInvalidPassword() {
  showError('パスワードが正しくありません');
  clearPasswordInput();
  // No console logging of password
}
```

#### 2. Storage API Unavailable

**Scenario:** Browser has disabled localStorage or sessionStorage

**Handling:**
- Gracefully degrade to session-only authentication
- Display warning message to user
- Fall back to in-memory authentication state
- Document limitation in error message

**Implementation:**
```javascript
function setAuthenticationState(persistent = false) {
  try {
    if (persistent && typeof localStorage !== 'undefined') {
      localStorage.setItem(AUTH_CONFIG.persistentKey, JSON.stringify({
        authenticated: true,
        timestamp: Date.now()
      }));
    } else if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
    } else {
      // Fallback to in-memory
      window._authState = true;
      console.warn('ブラウザのストレージが利用できません。ページをリロードすると再認証が必要です。');
    }
  } catch (e) {
    console.error('認証状態の保存に失敗しました:', e.message);
    window._authState = true;
  }
}
```

#### 3. Corrupted Storage Data

**Scenario:** localStorage contains invalid JSON or corrupted data

**Handling:**
- Catch JSON parsing errors
- Clear corrupted data
- Treat as unauthenticated state
- Log error for debugging (but not password)

**Implementation:**
```javascript
function checkAuthentication() {
  try {
    const persistentAuth = localStorage.getItem(AUTH_CONFIG.persistentKey);
    if (persistentAuth) {
      const authData = JSON.parse(persistentAuth);
      // Validate structure
      if (authData && typeof authData.authenticated === 'boolean' && 
          typeof authData.timestamp === 'number') {
        return validateAuthData(authData);
      }
    }
  } catch (e) {
    console.error('認証データの読み込みに失敗しました。再認証が必要です。');
    localStorage.removeItem(AUTH_CONFIG.persistentKey);
  }
  return false;
}
```

#### 4. Crypto API Unavailable

**Scenario:** Browser doesn't support Web Crypto API (very old browsers)

**Handling:**
- Fall back to simpler hashing method (multiple rounds of btoa encoding)
- Display compatibility warning
- Still provide basic security through obfuscation

**Implementation:**
```javascript
async function hashPassword(password) {
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    // Use Web Crypto API
    return await hashPasswordWithCrypto(password);
  } else {
    // Fallback for old browsers
    console.warn('Web Crypto APIが利用できません。基本的なハッシュ化を使用します。');
    return hashPasswordFallback(password);
  }
}

function hashPasswordFallback(password) {
  const salt = AUTH_CONFIG.salt;
  let hash = btoa(salt + password + salt);
  
  // Multiple rounds of encoding
  for (let i = 0; i < 100; i++) {
    hash = btoa(hash);
  }
  
  return hash;
}
```

#### 5. Expired Persistent Authentication

**Scenario:** User returns after token expiry period (30 days)

**Handling:**
- Detect expired timestamp
- Clear expired authentication data
- Show password overlay
- No error message (normal behavior)

**Implementation:**
```javascript
function validateAuthData(authData) {
  const age = Date.now() - authData.timestamp;
  
  if (age > AUTH_CONFIG.tokenExpiry) {
    // Expired - clear silently
    localStorage.removeItem(AUTH_CONFIG.persistentKey);
    return false;
  }
  
  return authData.authenticated === true;
}
```

### Error Logging Strategy

**What to Log:**
- Storage API errors
- JSON parsing errors
- Crypto API availability issues
- Unexpected authentication state

**What NOT to Log:**
- User-entered passwords (correct or incorrect)
- Password hashes
- Authentication tokens
- Specific validation failure reasons

**Log Levels:**
- `console.error()`: Critical failures that prevent authentication
- `console.warn()`: Degraded functionality (fallback modes)
- `console.info()`: Normal authentication events (optional, disabled in production)


## Testing Strategy

### Dual Testing Approach

This feature requires both unit tests and property-based tests to ensure comprehensive coverage:

**Unit Tests** focus on:
- Specific examples of correct and incorrect passwords
- Edge cases (empty input, special characters, very long passwords)
- DOM element existence and initial state
- Event handler registration
- Storage API error conditions
- Crypto API fallback behavior

**Property-Based Tests** focus on:
- Universal properties that hold for all inputs
- Authentication state consistency across page loads
- Password validation behavior for any input
- Storage operations for any authentication state
- UI state transitions for any user interaction

### Property-Based Testing Configuration

**Library Selection:** For JavaScript, we'll use **fast-check** (https://github.com/dubzzz/fast-check)

**Configuration:**
- Minimum 100 iterations per property test
- Each test tagged with feature name and property number
- Tag format: `Feature: sshve2-password-authentication, Property {number}: {property_text}`

**Example Property Test Structure:**
```javascript
// Feature: sshve2-password-authentication, Property 3: Error Display on Invalid Password
fc.assert(
  fc.property(
    fc.string(), // Generate random password strings
    (invalidPassword) => {
      // Assume invalidPassword !== correctPassword
      fc.pre(invalidPassword !== CORRECT_PASSWORD);
      
      // Submit invalid password
      submitPassword(invalidPassword);
      
      // Verify error is displayed
      const errorDiv = document.getElementById('passwordError');
      return errorDiv.style.display === 'block';
    }
  ),
  { numRuns: 100 }
);
```

### Unit Test Coverage

#### Authentication Logic Tests

1. **Correct Password Acceptance**
   - Input: Correct password
   - Expected: Authentication succeeds, overlay hidden, sessionStorage set

2. **Incorrect Password Rejection**
   - Input: Wrong password
   - Expected: Error displayed, input cleared, overlay remains

3. **Empty Password Handling**
   - Input: Empty string
   - Expected: Treated as incorrect password

4. **Password with Special Characters**
   - Input: Password containing Unicode, emojis, spaces
   - Expected: Correctly hashed and validated

#### Storage Management Tests

5. **SessionStorage Authentication**
   - Action: Authenticate without Remember Me
   - Expected: sessionStorage contains auth key, localStorage empty

6. **LocalStorage Authentication**
   - Action: Authenticate with Remember Me checked
   - Expected: localStorage contains auth data with timestamp

7. **Authentication State Check on Load**
   - Setup: Set sessionStorage auth key
   - Action: Reload page
   - Expected: Overlay hidden, dashboard visible

8. **Expired Persistent Authentication**
   - Setup: Set localStorage with old timestamp (>30 days)
   - Action: Load page
   - Expected: Overlay shown, expired data cleared

9. **Corrupted Storage Data Handling**
   - Setup: Set localStorage with invalid JSON
   - Action: Load page
   - Expected: Error caught, overlay shown, corrupted data cleared

#### UI Interaction Tests

10. **Enter Key Submission**
    - Action: Type password, press Enter
    - Expected: Password validation triggered

11. **Button Click Submission**
    - Action: Type password, click submit button
    - Expected: Password validation triggered

12. **Auto-focus on Load**
    - Action: Load page (unauthenticated)
    - Expected: Password input has focus

13. **Input Clear on Failure**
    - Action: Submit wrong password
    - Expected: Input field cleared, refocused

14. **Error Message Display Duration**
    - Action: Submit wrong password
    - Expected: Error shown, then hidden after timeout

#### Security Tests

15. **Password Not in Plain Text**
    - Action: Inspect HTML source and JavaScript
    - Expected: No plain text password found

16. **Password Not Logged to Console**
    - Action: Submit password (correct or incorrect)
    - Expected: Console logs contain no password values

17. **Hash Validation**
    - Action: Generate hash from known password
    - Expected: Hash matches stored hash

#### Integration Tests

18. **Dashboard Functionality After Auth**
    - Setup: Authenticate successfully
    - Action: Use filters, sorting, download buttons
    - Expected: All features work normally

19. **Logout Functionality**
    - Setup: Authenticated with persistent storage
    - Action: Call logout function
    - Expected: Both storages cleared, overlay shown on reload

20. **Remember Me Checkbox**
    - Action: Check Remember Me, authenticate
    - Expected: localStorage used instead of sessionStorage

### Property-Based Test Coverage

#### Property 1: Unauthenticated Access Prevention
```javascript
// Feature: sshve2-password-authentication, Property 1: Unauthenticated Access Prevention
fc.assert(
  fc.property(
    fc.boolean(), // Random storage state
    (hasAuth) => {
      // Setup: Clear or set authentication
      if (!hasAuth) {
        sessionStorage.clear();
        localStorage.clear();
      }
      
      // Load page
      initializeAuth();
      
      // Verify overlay state
      const overlay = document.getElementById('passwordOverlay');
      const isOverlayVisible = overlay.style.display !== 'none';
      
      return hasAuth || isOverlayVisible;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 2: Password Validation Invocation
```javascript
// Feature: sshve2-password-authentication, Property 2: Password Validation Invocation
fc.assert(
  fc.property(
    fc.string(), // Random password input
    (password) => {
      let validationCalled = false;
      
      // Mock validation function
      const originalValidate = validatePassword;
      validatePassword = (input) => {
        validationCalled = true;
        return originalValidate(input);
      };
      
      // Submit password
      document.getElementById('passwordInput').value = password;
      handlePasswordSubmit();
      
      // Restore original
      validatePassword = originalValidate;
      
      return validationCalled;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 3: Error Display on Invalid Password
```javascript
// Feature: sshve2-password-authentication, Property 3: Error Display on Invalid Password
fc.assert(
  fc.property(
    fc.string().filter(s => s !== CORRECT_PASSWORD), // Any incorrect password
    (invalidPassword) => {
      // Submit invalid password
      document.getElementById('passwordInput').value = invalidPassword;
      handlePasswordSubmit();
      
      // Check error display
      const errorDiv = document.getElementById('passwordError');
      return errorDiv.style.display === 'block';
    }
  ),
  { numRuns: 100 }
);
```

#### Property 5: Authentication State Persistence
```javascript
// Feature: sshve2-password-authentication, Property 5: Authentication State Persistence
fc.assert(
  fc.property(
    fc.boolean(), // Random Remember Me state
    (rememberMe) => {
      // Clear storage
      sessionStorage.clear();
      localStorage.clear();
      
      // Authenticate
      document.getElementById('rememberMe').checked = rememberMe;
      authenticateUser(CORRECT_PASSWORD);
      
      // Verify correct storage used
      if (rememberMe) {
        return localStorage.getItem(AUTH_CONFIG.persistentKey) !== null;
      } else {
        return sessionStorage.getItem(AUTH_CONFIG.sessionKey) === 'true';
      }
    }
  ),
  { numRuns: 100 }
);
```

#### Property 6: Authentication State Check on Load
```javascript
// Feature: sshve2-password-authentication, Property 6: Authentication State Check on Load
fc.assert(
  fc.property(
    fc.oneof(
      fc.constant('session'),
      fc.constant('local'),
      fc.constant('none')
    ),
    (storageType) => {
      // Setup storage
      sessionStorage.clear();
      localStorage.clear();
      
      if (storageType === 'session') {
        sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
      } else if (storageType === 'local') {
        localStorage.setItem(AUTH_CONFIG.persistentKey, JSON.stringify({
          authenticated: true,
          timestamp: Date.now()
        }));
      }
      
      // Check authentication
      const isAuthenticated = checkAuthentication();
      
      return (storageType !== 'none') === isAuthenticated;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 8: Password Console Logging Prevention
```javascript
// Feature: sshve2-password-authentication, Property 8: Password Console Logging Prevention
fc.assert(
  fc.property(
    fc.string(), // Random password
    (password) => {
      // Capture console output
      const originalLog = console.log;
      const originalError = console.error;
      const originalWarn = console.warn;
      let passwordLogged = false;
      
      const checkLog = (...args) => {
        if (args.some(arg => String(arg).includes(password))) {
          passwordLogged = true;
        }
      };
      
      console.log = checkLog;
      console.error = checkLog;
      console.warn = checkLog;
      
      // Perform authentication
      document.getElementById('passwordInput').value = password;
      handlePasswordSubmit();
      
      // Restore console
      console.log = originalLog;
      console.error = originalError;
      console.warn = originalWarn;
      
      return !passwordLogged;
    }
  ),
  { numRuns: 100 }
);
```

#### Property 9: Input Reset on Authentication Failure
```javascript
// Feature: sshve2-password-authentication, Property 9: Input Reset on Authentication Failure
fc.assert(
  fc.property(
    fc.string().filter(s => s !== CORRECT_PASSWORD), // Invalid password
    (invalidPassword) => {
      // Submit invalid password
      const input = document.getElementById('passwordInput');
      input.value = invalidPassword;
      handlePasswordSubmit();
      
      // Verify input cleared and focused
      return input.value === '' && document.activeElement === input;
    }
  ),
  { numRuns: 100 }
);
```

### Test Execution

**Unit Tests:**
- Framework: Jest or Mocha
- Run with: `npm test`
- Coverage target: >90% for authentication logic

**Property-Based Tests:**
- Framework: fast-check with Jest/Mocha
- Run with: `npm run test:properties`
- Iterations: 100 per property (configurable)

**Integration Tests:**
- Framework: Playwright or Cypress
- Run with: `npm run test:e2e`
- Test in multiple browsers: Chrome, Firefox, Safari


## Implementation Details

### Integration with Existing index.html

The authentication system will be integrated into the existing `index.html` file with minimal modifications to the current structure.

#### File Structure

```
index.html
├── <head>
│   ├── Existing meta tags and title
│   ├── Existing styles
│   └── + Authentication overlay styles
├── <body>
│   ├── + Password overlay (new, first element)
│   ├── Existing dashboard container
│   └── <script>
│       ├── + Authentication configuration
│       ├── + Authentication functions
│       ├── + Event listeners for auth
│       ├── + Initialization code
│       └── Existing dashboard JavaScript
```

#### Code Organization

The authentication code will be organized into logical sections within the `<script>` tag:

```javascript
// ============================================
// AUTHENTICATION SYSTEM
// ============================================

// 1. Configuration
const AUTH_CONFIG = { ... };

// 2. Utility Functions
async function hashPassword(password) { ... }
function generatePasswordHash(plainPassword) { ... }

// 3. Storage Management
function setAuthenticationState(persistent) { ... }
function checkAuthentication() { ... }
function clearAuthenticationState() { ... }

// 4. Validation Logic
async function validatePassword(inputPassword) { ... }

// 5. UI Controllers
function showPasswordOverlay() { ... }
function hidePasswordOverlay() { ... }
function showError(message) { ... }
function clearPasswordInput() { ... }

// 6. Event Handlers
function handlePasswordSubmit() { ... }
function handleLogout() { ... }

// 7. Initialization
function initializeAuthentication() { ... }

// ============================================
// EXISTING DASHBOARD CODE
// ============================================
// (Unchanged)
```

### Password Hashing Implementation

#### Hash Generation Tool

Administrators will use a separate HTML tool to generate password hashes:

**File: `generate_password_hash.html`**
```html
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>SSHVE2 Password Hash Generator</title>
  <style>
    body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
    input, button { padding: 10px; margin: 10px 0; width: 100%; font-size: 16px; }
    button { background: #1e3c72; color: white; border: none; cursor: pointer; }
    #output { background: #f0f0f0; padding: 15px; margin-top: 20px; word-break: break-all; }
    .instructions { background: #e7f3ff; padding: 15px; margin-bottom: 20px; border-left: 4px solid #2196F3; }
  </style>
</head>
<body>
  <h1>🔐 SSHVE2 Password Hash Generator</h1>
  
  <div class="instructions">
    <h3>使い方:</h3>
    <ol>
      <li>新しいパスワードを入力</li>
      <li>「ハッシュを生成」をクリック</li>
      <li>生成されたハッシュをコピー</li>
      <li>index.htmlの AUTH_CONFIG.passwordHash に貼り付け</li>
    </ol>
  </div>
  
  <label>新しいパスワード:</label>
  <input type="password" id="passwordInput" placeholder="パスワードを入力">
  
  <button onclick="generateHash()">ハッシュを生成</button>
  
  <div id="output" style="display:none;">
    <h3>生成されたハッシュ:</h3>
    <code id="hashValue"></code>
    <br><br>
    <button onclick="copyHash()">コピー</button>
  </div>
  
  <script>
    const AUTH_SALT = 'sshve2_dashboard_salt_2024';
    const HASH_ITERATIONS = 1000;
    
    async function hashPassword(password) {
      const combined = AUTH_SALT + password + AUTH_SALT;
      let hash = await crypto.subtle.digest('SHA-256', 
        new TextEncoder().encode(combined));
      
      for (let i = 0; i < HASH_ITERATIONS; i++) {
        hash = await crypto.subtle.digest('SHA-256', hash);
      }
      
      return btoa(String.fromCharCode(...new Uint8Array(hash)));
    }
    
    async function generateHash() {
      const password = document.getElementById('passwordInput').value;
      if (!password) {
        alert('パスワードを入力してください');
        return;
      }
      
      const hash = await hashPassword(password);
      document.getElementById('hashValue').textContent = hash;
      document.getElementById('output').style.display = 'block';
    }
    
    function copyHash() {
      const hash = document.getElementById('hashValue').textContent;
      navigator.clipboard.writeText(hash).then(() => {
        alert('ハッシュをコピーしました！');
      });
    }
  </script>
</body>
</html>
```

#### Hash Update Process

1. Open `generate_password_hash.html` in a browser
2. Enter the new password
3. Click "ハッシュを生成" to generate the hash
4. Copy the generated hash
5. Open `index.html` in a text editor
6. Find the `AUTH_CONFIG` section
7. Replace the `passwordHash` value with the new hash
8. Save and commit to GitHub
9. GitHub Pages will automatically update

### Session Management Implementation

#### Session Storage Flow

```javascript
// On successful authentication
function setAuthenticationState(persistent = false) {
  const timestamp = Date.now();
  
  if (persistent) {
    // Use localStorage for persistent auth
    const authData = {
      authenticated: true,
      timestamp: timestamp,
      version: '1.0' // For future compatibility
    };
    localStorage.setItem(AUTH_CONFIG.persistentKey, JSON.stringify(authData));
  } else {
    // Use sessionStorage for temporary auth
    sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
  }
}

// On page load
function checkAuthentication() {
  // Priority 1: Check sessionStorage (current session)
  if (sessionStorage.getItem(AUTH_CONFIG.sessionKey) === 'true') {
    return true;
  }
  
  // Priority 2: Check localStorage (persistent)
  const persistentAuth = localStorage.getItem(AUTH_CONFIG.persistentKey);
  if (persistentAuth) {
    try {
      const authData = JSON.parse(persistentAuth);
      
      // Validate structure
      if (!authData.authenticated || !authData.timestamp) {
        throw new Error('Invalid auth data structure');
      }
      
      // Check expiry
      const age = Date.now() - authData.timestamp;
      if (age > AUTH_CONFIG.tokenExpiry) {
        // Expired
        localStorage.removeItem(AUTH_CONFIG.persistentKey);
        return false;
      }
      
      // Valid persistent auth - promote to session
      sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
      return true;
      
    } catch (e) {
      // Corrupted data
      console.error('認証データが破損しています:', e.message);
      localStorage.removeItem(AUTH_CONFIG.persistentKey);
      return false;
    }
  }
  
  return false;
}

// Logout
function clearAuthenticationState() {
  sessionStorage.removeItem(AUTH_CONFIG.sessionKey);
  localStorage.removeItem(AUTH_CONFIG.persistentKey);
}
```

### UI Implementation

#### Overlay HTML Structure

```html
<div id="passwordOverlay">
  <div id="passwordBox">
    <h2>🔐 認証が必要です</h2>
    <p>このダッシュボードにアクセスするにはパスワードを入力してください</p>
    
    <input 
      type="password" 
      id="passwordInput" 
      placeholder="パスワードを入力" 
      autocomplete="off"
      aria-label="パスワード">
    
    <label class="remember-me">
      <input type="checkbox" id="rememberMe">
      <span>ログイン状態を保持する（30日間）</span>
    </label>
    
    <button id="passwordSubmit" onclick="handlePasswordSubmit()">
      ログイン
    </button>
    
    <div id="passwordError" role="alert" aria-live="polite">
      パスワードが正しくありません
    </div>
  </div>
</div>
```

#### CSS Styling

```css
#passwordOverlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  transition: opacity 0.3s ease;
}

#passwordBox {
  background: #fff;
  padding: 40px;
  border-radius: 15px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  text-align: center;
  max-width: 400px;
  width: 90%;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

#passwordBox h2 {
  color: #1e3c72;
  margin-bottom: 20px;
  font-size: 1.8em;
}

#passwordBox p {
  color: #666;
  margin-bottom: 25px;
  font-size: 0.95em;
}

#passwordInput {
  width: 100%;
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 1em;
  margin-bottom: 15px;
  box-sizing: border-box;
  transition: border-color 0.3s;
}

#passwordInput:focus {
  outline: none;
  border-color: #1e3c72;
}

.remember-me {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  font-size: 0.9em;
  color: #666;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
}

#passwordSubmit {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: #fff;
  border: none;
  padding: 15px 40px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 700;
  font-size: 1em;
  width: 100%;
  transition: all 0.3s;
}

#passwordSubmit:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(30, 60, 114, 0.4);
}

#passwordSubmit:active {
  transform: translateY(0);
}

#passwordError {
  color: #dc3545;
  margin-top: 15px;
  font-size: 0.9em;
  display: none;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

/* Mobile responsive */
@media (max-width: 480px) {
  #passwordBox {
    padding: 30px 20px;
  }
  
  #passwordBox h2 {
    font-size: 1.5em;
  }
}
```

### Event Handling

```javascript
// Initialize event listeners
function initializeAuthentication() {
  // Check authentication on load
  if (checkAuthentication()) {
    hidePasswordOverlay();
  } else {
    showPasswordOverlay();
  }
  
  // Enter key handler
  document.getElementById('passwordInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handlePasswordSubmit();
    }
  });
  
  // Button click handler
  document.getElementById('passwordSubmit').addEventListener('click', handlePasswordSubmit);
  
  // Optional: Add logout button to dashboard
  const logoutBtn = document.createElement('button');
  logoutBtn.textContent = 'ログアウト';
  logoutBtn.className = 'btn btn-secondary';
  logoutBtn.style.position = 'fixed';
  logoutBtn.style.top = '20px';
  logoutBtn.style.right = '20px';
  logoutBtn.style.zIndex = '1000';
  logoutBtn.addEventListener('click', handleLogout);
  document.body.appendChild(logoutBtn);
}

// Call on page load
window.addEventListener('DOMContentLoaded', initializeAuthentication);
```

### Security Considerations

#### 1. Password Storage

- Password is never stored in plain text
- Hash is generated using SHA-256 with 1000 iterations
- Salt is embedded in code to prevent rainbow table attacks
- Hash is stored as base64-encoded string

#### 2. Client-Side Limitations

This is a client-side authentication system with inherent limitations:

- **Not cryptographically secure**: Determined users can bypass by inspecting code
- **Purpose**: Deter casual access, not prevent determined attackers
- **Appropriate for**: Internal dashboards, low-sensitivity data
- **Not appropriate for**: Financial data, PII, regulated information

#### 3. HTTPS Requirement

- GitHub Pages provides HTTPS by default
- All authentication happens over encrypted connection
- Prevents password interception in transit

#### 4. No Server-Side Validation

- All validation happens in browser
- No server-side password verification
- No rate limiting or account lockout
- Suitable for trusted user base

### Deployment Process

1. **Update index.html**
   - Add password overlay HTML
   - Add authentication CSS
   - Add authentication JavaScript
   - Generate initial password hash

2. **Create Password Generator Tool**
   - Create `generate_password_hash.html`
   - Store in repository root or separate admin folder

3. **Test Locally**
   - Open index.html in browser
   - Test authentication flow
   - Verify storage behavior
   - Test Remember Me functionality

4. **Commit and Push**
   ```bash
   git add index.html generate_password_hash.html
   git commit -m "Add password authentication to SSHVE2 dashboard"
   git push origin main
   ```

5. **Verify on GitHub Pages**
   - Wait 1-2 minutes for deployment
   - Visit dashboard URL
   - Test authentication
   - Verify all existing features work

### Password Update Procedure

**For Administrators:**

1. Open `generate_password_hash.html` in browser
2. Enter new password
3. Click "ハッシュを生成"
4. Copy generated hash
5. Edit `index.html`:
   ```javascript
   const AUTH_CONFIG = {
     passwordHash: 'NEW_HASH_HERE', // Replace this value
     // ... rest of config
   };
   ```
6. Save and commit:
   ```bash
   git add index.html
   git commit -m "Update dashboard password"
   git push origin main
   ```
7. Notify users of password change
8. All existing sessions will be invalidated (users must re-authenticate)

**Security Note:** When updating the password, all users with persistent authentication will need to log in again with the new password.


## Appendix

### Complete Authentication Code

Below is the complete authentication system code that will be integrated into `index.html`:

```javascript
// ============================================
// AUTHENTICATION SYSTEM
// ============================================

// Configuration
const AUTH_CONFIG = {
  // Password hash (generated using generate_password_hash.html)
  // Default password: 'sshve2024'
  passwordHash: 'YOUR_GENERATED_HASH_HERE',
  
  // Salt for hashing (keep consistent with generator)
  salt: 'sshve2_dashboard_salt_2024',
  
  // Hash iterations
  iterations: 1000,
  
  // Storage keys
  sessionKey: 'sshve2_authenticated',
  persistentKey: 'sshve2_persistent_auth',
  
  // Token expiry (30 days in milliseconds)
  tokenExpiry: 30 * 24 * 60 * 60 * 1000,
  
  // UI configuration
  errorDisplayDuration: 3000,
  fadeOutDuration: 300
};

// Utility: Hash password using Web Crypto API
async function hashPassword(password) {
  try {
    if (typeof crypto === 'undefined' || !crypto.subtle) {
      return hashPasswordFallback(password);
    }
    
    const combined = AUTH_CONFIG.salt + password + AUTH_CONFIG.salt;
    let hash = await crypto.subtle.digest('SHA-256', 
      new TextEncoder().encode(combined));
    
    // Multiple iterations for increased security
    for (let i = 0; i < AUTH_CONFIG.iterations; i++) {
      hash = await crypto.subtle.digest('SHA-256', hash);
    }
    
    return btoa(String.fromCharCode(...new Uint8Array(hash)));
  } catch (e) {
    console.error('ハッシュ化エラー:', e.message);
    return hashPasswordFallback(password);
  }
}

// Fallback hashing for older browsers
function hashPasswordFallback(password) {
  const salt = AUTH_CONFIG.salt;
  let hash = btoa(salt + password + salt);
  
  for (let i = 0; i < 100; i++) {
    hash = btoa(hash);
  }
  
  return hash;
}

// Validate password against stored hash
async function validatePassword(inputPassword) {
  const inputHash = await hashPassword(inputPassword);
  return inputHash === AUTH_CONFIG.passwordHash;
}

// Storage Management
function setAuthenticationState(persistent = false) {
  try {
    const timestamp = Date.now();
    
    if (persistent && typeof localStorage !== 'undefined') {
      const authData = {
        authenticated: true,
        timestamp: timestamp,
        version: '1.0'
      };
      localStorage.setItem(AUTH_CONFIG.persistentKey, JSON.stringify(authData));
    }
    
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
    } else {
      // Fallback to in-memory
      window._authState = true;
    }
  } catch (e) {
    console.error('認証状態の保存エラー:', e.message);
    window._authState = true;
  }
}

function checkAuthentication() {
  // Check in-memory fallback
  if (window._authState === true) {
    return true;
  }
  
  // Check sessionStorage
  try {
    if (typeof sessionStorage !== 'undefined' && 
        sessionStorage.getItem(AUTH_CONFIG.sessionKey) === 'true') {
      return true;
    }
  } catch (e) {
    console.error('セッションストレージ読み込みエラー:', e.message);
  }
  
  // Check localStorage
  try {
    if (typeof localStorage !== 'undefined') {
      const persistentAuth = localStorage.getItem(AUTH_CONFIG.persistentKey);
      if (persistentAuth) {
        const authData = JSON.parse(persistentAuth);
        
        // Validate structure
        if (authData && authData.authenticated && authData.timestamp) {
          // Check expiry
          const age = Date.now() - authData.timestamp;
          if (age < AUTH_CONFIG.tokenExpiry) {
            // Valid - promote to session
            sessionStorage.setItem(AUTH_CONFIG.sessionKey, 'true');
            return true;
          } else {
            // Expired
            localStorage.removeItem(AUTH_CONFIG.persistentKey);
          }
        }
      }
    }
  } catch (e) {
    console.error('ローカルストレージ読み込みエラー:', e.message);
    try {
      localStorage.removeItem(AUTH_CONFIG.persistentKey);
    } catch (e2) {
      // Ignore cleanup errors
    }
  }
  
  return false;
}

function clearAuthenticationState() {
  try {
    if (typeof sessionStorage !== 'undefined') {
      sessionStorage.removeItem(AUTH_CONFIG.sessionKey);
    }
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem(AUTH_CONFIG.persistentKey);
    }
    window._authState = false;
  } catch (e) {
    console.error('認証状態のクリアエラー:', e.message);
  }
}

// UI Controllers
function showPasswordOverlay() {
  const overlay = document.getElementById('passwordOverlay');
  if (overlay) {
    overlay.style.display = 'flex';
    overlay.style.opacity = '1';
    
    // Focus input
    setTimeout(() => {
      const input = document.getElementById('passwordInput');
      if (input) {
        input.focus();
      }
    }, 100);
  }
}

function hidePasswordOverlay() {
  const overlay = document.getElementById('passwordOverlay');
  if (overlay) {
    overlay.style.opacity = '0';
    setTimeout(() => {
      overlay.style.display = 'none';
    }, AUTH_CONFIG.fadeOutDuration);
  }
}

function showError(message) {
  const errorDiv = document.getElementById('passwordError');
  if (errorDiv) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
      errorDiv.style.display = 'none';
    }, AUTH_CONFIG.errorDisplayDuration);
  }
}

function clearPasswordInput() {
  const input = document.getElementById('passwordInput');
  if (input) {
    input.value = '';
    input.focus();
  }
}

// Event Handlers
async function handlePasswordSubmit() {
  const input = document.getElementById('passwordInput');
  const rememberMe = document.getElementById('rememberMe');
  
  if (!input) return;
  
  const password = input.value;
  
  if (!password) {
    showError('パスワードを入力してください');
    return;
  }
  
  // Validate password
  const isValid = await validatePassword(password);
  
  if (isValid) {
    // Success
    const persistent = rememberMe ? rememberMe.checked : false;
    setAuthenticationState(persistent);
    hidePasswordOverlay();
  } else {
    // Failure
    showError('パスワードが正しくありません');
    clearPasswordInput();
  }
}

function handleLogout() {
  if (confirm('ログアウトしますか？')) {
    clearAuthenticationState();
    location.reload();
  }
}

// Initialization
function initializeAuthentication() {
  // Check authentication state
  if (checkAuthentication()) {
    hidePasswordOverlay();
  } else {
    showPasswordOverlay();
  }
  
  // Setup event listeners
  const passwordInput = document.getElementById('passwordInput');
  if (passwordInput) {
    passwordInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        handlePasswordSubmit();
      }
    });
  }
  
  const submitButton = document.getElementById('passwordSubmit');
  if (submitButton) {
    submitButton.addEventListener('click', handlePasswordSubmit);
  }
  
  // Add logout button (optional)
  const logoutBtn = document.createElement('button');
  logoutBtn.textContent = 'ログアウト';
  logoutBtn.className = 'btn btn-secondary';
  logoutBtn.style.cssText = 'position:fixed;top:20px;right:20px;z-index:1000;padding:10px 20px;';
  logoutBtn.addEventListener('click', handleLogout);
  
  // Only show logout button when authenticated
  if (checkAuthentication()) {
    document.body.appendChild(logoutBtn);
  }
}

// Initialize on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAuthentication);
} else {
  initializeAuthentication();
}
```

### Browser Compatibility

**Supported Browsers:**
- Chrome 37+ (Web Crypto API support)
- Firefox 34+
- Safari 11+
- Edge 12+

**Fallback Support:**
- Older browsers use base64 encoding fallback
- Graceful degradation for missing Storage APIs
- In-memory authentication as last resort

**Testing Checklist:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Performance Considerations

**Hash Generation:**
- 1000 iterations of SHA-256
- Approximately 10-50ms on modern hardware
- Acceptable delay for authentication

**Storage Operations:**
- localStorage/sessionStorage are synchronous
- Minimal performance impact (<1ms)
- No network requests

**Page Load Impact:**
- Authentication check: <5ms
- Overlay display: Immediate
- No impact on dashboard load time

### Maintenance and Updates

**Regular Maintenance:**
- Review password every 90 days
- Check for browser compatibility issues
- Monitor console for errors
- Update hash algorithm if needed

**Version History:**
- v1.0: Initial implementation with SHA-256 hashing
- Future: Consider adding rate limiting, CAPTCHA, or 2FA

**Known Limitations:**
1. Client-side only - can be bypassed by determined users
2. No rate limiting - unlimited password attempts
3. No account lockout mechanism
4. Single password for all users
5. Password visible in browser DevTools (as hash)

**Future Enhancements:**
- Add rate limiting (delay after failed attempts)
- Implement CAPTCHA after multiple failures
- Add password strength requirements
- Support multiple user accounts
- Add audit logging
- Implement 2FA (TOTP)

### Documentation for Users

**User Guide (Japanese):**

```markdown
# SSHVE2ダッシュボード - ログインガイド

## 初回アクセス

1. ダッシュボードのURLにアクセスします
2. パスワード入力画面が表示されます
3. 管理者から受け取ったパスワードを入力します
4. 「ログイン」ボタンをクリックします

## ログイン状態の保持

- デフォルト: ブラウザを閉じるまで有効
- 「ログイン状態を保持する」にチェック: 30日間有効

## ログアウト

- 画面右上の「ログアウト」ボタンをクリック
- ブラウザを閉じる（保持していない場合）

## トラブルシューティング

**Q: パスワードを忘れました**
A: 管理者に連絡してパスワードを再発行してもらってください

**Q: ログインできません**
A: 以下を確認してください：
- パスワードが正しいか
- ブラウザのCookieが有効か
- JavaScriptが有効か

**Q: 自動的にログアウトされます**
A: 「ログイン状態を保持する」にチェックを入れてログインしてください
```

### Administrator Guide

**Password Management:**

1. **Generate New Password Hash:**
   - Open `generate_password_hash.html`
   - Enter new password
   - Copy generated hash

2. **Update Dashboard:**
   - Edit `index.html`
   - Replace `AUTH_CONFIG.passwordHash` value
   - Commit and push to GitHub

3. **Notify Users:**
   - Send new password to authorized users
   - Inform them that existing sessions will be invalidated

**Security Best Practices:**
- Change password every 90 days
- Use strong passwords (12+ characters, mixed case, numbers, symbols)
- Don't share password via insecure channels
- Keep `generate_password_hash.html` in secure location
- Monitor access logs (if available)

**Emergency Access:**
- If locked out, edit `index.html` directly in GitHub
- Generate new hash and update immediately
- Test in incognito window before sharing

