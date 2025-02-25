# Language Learning Portal - Frontend

A React-based frontend for the Language Learning Portal, built with Vite, TypeScript, and Material-UI.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running (FastAPI)

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd lang-portal/frontend-react
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Environment Setup**
   Create a `.env` file in the frontend-react directory:
   ```env
   VITE_API_BASE_URL=http://127.0.0.1:8000
   ```

4. **Start Development Server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   The application will be available at `http://localhost:5173`

## Project Structure

```
frontend-react/
├── public/              # Static files
├── src/
│   ├── components/     # Reusable components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── contexts/      # React contexts
│   ├── types/         # TypeScript types
│   └── App.tsx        # Root component
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run test` - Run tests

## Dependencies

- React
- React Router
- Material-UI
- Axios
- TypeScript

## Development Notes

1. **API Integration**
   - Backend API is expected at `http://127.0.0.1:8000`
   - API services are in `src/services/api.ts`

2. **Styling**
   - Using Material-UI (MUI) for components
   - Theme customization in `src/contexts/ThemeContext.tsx`

3. **State Management**
   - Using React Context for theme
   - Local state with useState for component state

4. **Routing**
   - React Router v6 for navigation
   - Route definitions in `App.tsx`

## Common Issues & Solutions

1. **Backend Connection**
   - Ensure backend server is running
   - Check CORS settings if API calls fail
   - Verify API base URL in `.env`

2. **Build Issues**
   - Clear `node_modules` and reinstall if build fails
   - Check Node.js version compatibility
   - Verify all dependencies are installed

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests and lint checks
4. Submit pull request

## License

[Your License Here]
