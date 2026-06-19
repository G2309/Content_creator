import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth.jsx";
import Layout from "./components/Layout.jsx";
import Login from "./pages/Login.jsx";
import Generator from "./pages/Generator.jsx";
import Settings from "./pages/Settings.jsx";
import Users from "./pages/Users.jsx";
import ChangePassword from "./pages/ChangePassword.jsx";
import Library from "./pages/Library.jsx";
import Pains from "./pages/Pains.jsx";

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (user.must_change_password) return <Navigate to="/cambiar-password" replace />;
  return children;
}

function PasswordChangeRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.must_change_password) return <Navigate to="/" replace />;
  return children;
}

function PublicOnly({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  if (user) {
    return user.must_change_password
      ? <Navigate to="/cambiar-password" replace />
      : <Navigate to="/" replace />;
  }
  return children;
}

function AdminOnly({ children }) {
  const { user } = useAuth();
  if (!user?.is_admin) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route
        path="/login"
        element={<PublicOnly><Login /></PublicOnly>}
      />
      <Route
        path="/cambiar-password"
        element={<PasswordChangeRoute><ChangePassword forced /></PasswordChangeRoute>}
      />
      <Route
        path="/"
        element={<ProtectedRoute><Layout /></ProtectedRoute>}
      >
        <Route index element={<Generator />} />
        <Route path="biblioteca" element={<Library />} />
        <Route path="ajustes" element={<Settings />} />
        <Route path="ajustes/dolores" element={<Pains />} />
        <Route path="cuenta/password" element={<ChangePassword />} />
        <Route path="usuarios" element={<AdminOnly><Users /></AdminOnly>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
