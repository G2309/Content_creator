import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../auth.jsx";

export default function Layout() {
  const { user, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <small>Espacio privado</small>
          Generador
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end>
            Generador
          </NavLink>
          <NavLink to="/ajustes">Contexto del negocio</NavLink>
        </nav>

        <div className="sidebar-footer">
          {user && <span>{user.email}</span>}
          <button className="btn btn-ghost" onClick={logout}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="main">
        <Outlet />
      </main>
    </div>
  );
}
