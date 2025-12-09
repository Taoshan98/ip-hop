# Frontend Documentation

Modern Next.js dashboard for IP-HOP Dynamic DNS management.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Pages](#pages)
- [Components](#components)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [Testing](#testing)
- [Development](#development)

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── app/                    # Next.js 14 App Router
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx           # Landing page
│   │   ├── login/             # Login page
│   │   ├── setup/             # Initial setup
│   │   └── dashboard/         # Protected dashboard
│   │       ├── layout.tsx     # Dashboard layout
│   │       ├── page.tsx       # Dashboard home
│   │       ├── providers/     # Providers management
│   │       └── domains/       # Domains management
│   │
│   ├── components/            # React components
│   │   ├── ui/               # Shadcn UI primitives
│   │   ├── confirm-dialog.tsx # Confirmation dialogs
│   │   ├── history-modal.tsx  # Update history viewer
│   │   └── providers.tsx      # Query client wrapper
│   │
│   ├── context/              # React Context
│   │   └── AuthContext.tsx   # Authentication state
│   │
│   └── lib/                  # Utilities
│       ├── api.ts           # Axios instance
│       ├── errors.ts        # Error handling
│       └── utils.ts         # Helper functions
│
└── __tests__/               # 68 comprehensive tests
```

## 📄 Pages

### Authentication Flow

#### 1. Landing Page (`/`)
**Purpose**: Entry point, redirects based on auth state

**Behavior**:
- If unauthenticated → redirect to `/login`
- If authenticated → redirect to `/dashboard`
- If no admin exists → redirect to `/setup`

---

#### 2. Setup Page (`/setup`)
**Purpose**: First-time admin account creation

**Features**:
- Admin username input
- Password with strength validation
- Auto-login after setup
- One-time only (disabled after first admin)

**Validation**:
- Username: 3-100 characters
- Password: Strong password requirements (see backend docs)

---

#### 3. Login Page (`/login`)
**Purpose**: User authentication

**Features**:
- Username/password form
- Remember session (HttpOnly cookie)
- Error handling
- Auto-redirect to dashboard on success

---

### Dashboard Pages

#### 4. Dashboard Home (`/dashboard`)
**Purpose**: Overview and quick actions

**Features**:
- Total providers count
- Total domains count
- Recent activity overview
- Quick navigation cards

---

#### 5. Providers Page (`/dashboard/providers`)
**Purpose**: DNS provider management

**Features**:
- Provider list with status
- Add new provider (Cloudflare, Dynu, DuckDNS, No-IP)
- Edit provider settings
- Enable/disable providers
- Delete providers (with confirmation)

**Provider Card Display**:
- Provider name
- Type badge (Cloudflare/Dynu)
- Status indicator (enabled/disabled)
- Actions: Edit, Delete

---

#### 6. Domains Page (`/dashboard/domains`)
**Purpose**: Domain/subdomain management

**Features**:
- Domain list with current IP
- Add new domain
- Edit domain configuration
- Update now (force IP update)
- View update history
- Clear history
- Enable/disable domains
- Delete domains

**Domain Table Columns**:
- Domain name
- Provider
- Current IP
- Last update time
- Schedule (cron expression)
- Status (enabled/disabled)
- Actions

---

## 🧩 Components

### UI Components (`components/ui/`)

Built with Radix UI and Tailwind CSS.

#### Button
**Usage**:
```tsx
import { Button } from '@/components/ui/button';

<Button variant="destructive" size="lg">Delete</Button>
```

**Variants**: `default`, `destructive`, `outline`, `secondary`, `ghost`, `link`  
**Sizes**: `default`, `sm`, `lg`, `icon`

---

#### Input
**Usage**:
```tsx
import { Input } from '@/components/ui/input';

<Input type="email" placeholder="Email" />
```

**Types**: All HTML input types supported

---

#### Label
**Usage**:
```tsx
import { Label } from '@/components/ui/label';

<Label htmlFor="email">Email Address</Label>
```

---

#### Card
**Usage**:
```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
} from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content here</CardContent>
  <CardFooter>Footer content</CardFooter>
</Card>
```

---

#### Table
**Usage**:
```tsx
import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell
} from '@/components/ui/table';

<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Name</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

---

#### Dialog
**Usage**:
```tsx
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription
} from '@/components/ui/dialog';

<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
    {/* Content */}
  </DialogContent>
</Dialog>
```

---

#### Alert Dialog
**Usage**:
```tsx
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogAction,
  AlertDialogCancel
} from '@/components/ui/alert-dialog';

<AlertDialog>
  <AlertDialogTrigger>Delete</AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>Are you sure?</AlertDialogTitle>
      <AlertDialogDescription>
        This action cannot be undone.
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>Cancel</AlertDialogCancel>
      <AlertDialogAction>Continue</AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

---

### Custom Components

#### ConfirmDialog Provider
**Global confirmation dialog system**

**Setup** (in layout):
```tsx
import { ConfirmDialogProvider } from '@/components/confirm-dialog';

<ConfirmDialogProvider>
  {children}
</ConfirmDialogProvider>
```

**Usage**:
```tsx
import { useConfirmDialog } from '@/components/confirm-dialog';

function MyComponent() {
  const { confirm } = useConfirmDialog();
  
  const handleDelete = () => {
    confirm({
      title: 'Delete Item',
      description: 'Are you sure? This cannot be undone.',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      variant: 'destructive',
      onConfirm: async () => {
        await deleteItem();
      },
      onCancel: () => {
        console.log('Cancelled');
      }
    });
  };
  
  return <button onClick={handleDelete}>Delete</button>;
}
```

---

#### HistoryModal
**View domain update history**

**Usage**:
```tsx
import { HistoryModal } from '@/components/history-modal';

<HistoryModal
  domainId={1}
  domainName="example.com"
  isOpen={showHistory}
  onClose={() => setShowHistory(false)}
/>
```

**Features**:
- Displays update history in  timeline
- Shows old IP → new IP transitions
- Update timestamps
- Success/failure indicators
- Clear history action

---

#### Providers Wrapper
**React Query client provider**

**Purpose**: Wraps app with TanStack Query for server state

```tsx
import Providers from '@/components/providers';

<Providers>
  {children}
</Providers>
```

---

## 🔄 State Management

### Authentication Context

**Setup**:
```tsx
import { AuthProvider, useAuth } from '@/context/AuthContext';

// In root layout
<AuthProvider>
  {children}
</AuthProvider>
```

**Usage**:
```tsx
function MyComponent() {
  const { isAuthenticated, isLoading, login, logout } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <div>
      {isAuthenticated ? (
        <button onClick={logout}>Logout</button>
      ) : (
        <button onClick={login}>Login</button>
      )}
    </div>
  );
}
```

**Features**:
- Automatic authentication check on mount
- Redirect to login if unauthenticated
- HttpOnly cookie management
- Loading states

---

### Server State (React Query)

**Configuration**:
```tsx
// In components/providers.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});
```

**Usage Example**:
```tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';

function Providers() {
  const queryClient = useQueryClient();
  
  // Fetch data
  const { data: providers, isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: async () => {
      const response = await api.get('/providers');
      return response.data;
    },
  });
  
  // Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/providers/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['providers'] });
    },
  });
  
  return (
    <div>
      {providers?.map(provider => (
        <div key={provider.id}>
          {provider.name}
          <button onClick={() => deleteMutation.mutate(provider.id)}>
            Delete
          </button>
        </div>
      ))}
    </div>
  );
}
```

---

## 🌐 API Integration

### API Client (`lib/api.ts`)

**Base Configuration**:
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8001/api/v1',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Features**:
- Automatic cookie handling
- Base URL configuration
- Request/response interceptors
- Error handling

---

### Error Handling (`lib/errors.ts`)

**Utilities**:
```typescript
import { getErrorMessage, isAxiosError } from '@/lib/errors';

try {
  await api.post('/endpoint');
} catch (error) {
  const message = getErrorMessage(error);
  console.error(message);
  
  if (isAxiosError(error)) {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
  }
}
```

**Functions**:
- `isAxiosError(error)`: Type guard for Axios errors
- `getErrorMessage(error)`: Extract user-friendly message

---

### Toast Notifications

**Setup** (using sonner):
```tsx
import { Toaster } from 'sonner';

<Toaster position="top-right" richColors />
```

**Usage**:
```tsx
import { toast } from 'sonner';

// Success
toast.success('Provider added successfully!');

// Error
toast.error('Failed to delete domain');

// Info
toast.info('Updating IP address...');

// Promise
toast.promise(
  api.post('/domains'),
  {
    loading: 'Creating domain...',
    success: 'Domain created!',
    error: 'Failed to create domain',
  }
);
```

---

## 🧪 Testing

### Test Suite
```bash
cd frontend
npm test
```

**Coverage**:
- 68 tests
- 8 test suites
- 100% pass rate
- ~45% code coverage

### Test Categories

**Utils** (17 tests):
- `cn()` className merging
- Error message extraction

**UI Components** (28 tests):
- Button variants and interactions
- Input types and validation
- Label rendering
- Card composition

**Context** (6 tests):
- Auth state management
- Login/logout flows
- Route protection

**Components** (4 tests):
- Dialog confirmations
- Provider wrappers

### Run Tests

```bash
# All tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

---

## 🛠️ Development

### Setup

```bash
cd frontend
npm install
```

### Run Development Server

```bash
npm run dev
# Open http://localhost:3000
```

### Build for Production

```bash
npm run build
npm start
```

### Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
```

---

## 🎨 Styling

### Tailwind CSS

**Configuration** (`tailwind.config.ts`):
- Custom color palette
- Extended spacing
- Custom animations
- HSL color system

**Usage**:
```tsx
<div className="bg-primary text-primary-foreground rounded-lg p-4">
  Styled component
</div>
```

### CSS Variables

**Light/Dark Mode** (`app/globals.css`):
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  /* ... */
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... */
}
```

---

## 📦 Dependencies

### Core
- **Next.js 14** - React framework
- **React 19** - UI library
- **TypeScript** - Type safety

### UI
- **Tailwind CSS** - Styling
- **Radix UI** - Headless components
- **Lucide React** - Icons
- **Sonner** - Toast notifications

### State & Data
- **TanStack Query** - Server state
- **Axios** - HTTP client

### Testing
- **Jest** - Test framework
- **React Testing Library** - Component testing
- **@testing-library/user-event** - User interactions

---

## 🔒 Security

### Authentication
- HttpOnly cookies (no localStorage)
- Automatic token refresh
- Protected routes with middleware

### XSS Protection
- React auto-escapes content
- Content Security Policy headers
- No `dangerouslySetInnerHTML`

---

## 📱 Responsive Design

All pages and components are fully responsive:
- Mobile-first approach
- Tailwind breakpoints: `sm`, `md`, `lg`, `xl`, `2xl`
- Touch-friendly interactive elements

---

## 🚀 Performance

### Optimizations
- Server components (where possible)
- Dynamic imports for heavy components
- Image optimization with Next.js Image
- Code splitting automatic

---

**For backend integration, see:** [Backend Documentation](../backend/README.md)
