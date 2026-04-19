# React TypeScript Project Instructions

## Project Overview
This is a modern React application built with TypeScript, focusing on user experience and maintainable code architecture.

## Technology Stack
- React 18 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- React Router for navigation
- React Query for data fetching and caching
- Jest and React Testing Library for testing
- ESLint and Prettier for code quality

## Coding Standards
- Use functional components with hooks
- Prefer custom hooks for reusable logic
- Use TypeScript interfaces for all data structures
- Follow the single responsibility principle
- Write descriptive, self-documenting code
- Use early returns to reduce nesting
- Handle errors gracefully with proper user feedback

## Component Patterns
- Use named exports for components
- Implement proper TypeScript prop interfaces
- Use React.memo for expensive components when appropriate
- Follow accessibility guidelines (WCAG 2.1 AA)
- Use semantic HTML elements
- Implement proper loading and error states

## State Management
- Use React Query for server state
- Use local component state for UI state
- Avoid prop drilling with appropriate component composition
- Use custom hooks to encapsulate stateful logic

## Testing Guidelines
- Write tests for all user-facing features
- Use React Testing Library for component testing
- Mock external dependencies appropriately
- Test error states and edge cases
- Aim for meaningful test coverage over high percentages

## File Organization
- Group related components in feature directories
- Use index.ts files for clean imports
- Separate custom hooks from components
- Keep utility functions in dedicated modules
- Use consistent naming conventions

## Performance Considerations
- Implement code splitting for large applications
- Use React.lazy for route-based splitting
- Optimize bundle size and loading times
- Use appropriate memoization techniques
- Monitor and optimize re-renders