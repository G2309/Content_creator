import { useEffect, useState } from "react";
import { api } from "../api";
import { useAuth } from "../auth.jsx";

export default function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [email, setEmail] = useState("");
  const [tempPwd, setTempPwd] = useState("");
  const [isAdminFlag, setIsAdminFlag] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createdBanner, setCreatedBanner] = useState(null);

  const load = async () => {
    setError("");
    try {
      const list = await api.listUsers();
      setUsers(list);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const generateRandomPassword = () => {
    const chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789";
    const buf = new Uint32Array(16);
    crypto.getRandomValues(buf);
    let out = "";
    for (let i = 0; i < buf.length; i++) {
      out += chars[buf[i] % chars.length];
    }
    setTempPwd(out);
  };

  const onCreate = async (e) => {
    e.preventDefault();
    if (tempPwd.length < 8) {
      setError("La contraseña temporal debe tener al menos 8 caracteres.");
      return;
    }

    setCreating(true);
    setError("");
    setCreatedBanner(null);
    try {
      const created = await api.createUser(email.trim().toLowerCase(), tempPwd, isAdminFlag);
      setCreatedBanner({ email: created.email, tempPwd });
      setEmail("");
      setTempPwd("");
      setIsAdminFlag(false);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  const onDelete = async (user) => {
    if (user.id === me.id) return;
    const ok = window.confirm(
      `¿Eliminar al usuario ${user.email}? Esta acción no se puede deshacer.`
    );
    if (!ok) return;
    try {
      await api.deleteUser(user.id);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Administración</div>
        <h1 className="page-title">Usuarios</h1>
        <p className="page-subtitle">
          Crea cuentas para personas que necesitan acceso. Se las pasas por canal
          seguro y la app las obliga a cambiar la contraseña al primer inicio de sesión.
        </p>
      </header>

      {error && <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>{error}</div>}

      {createdBanner && (
        <div className="banner banner-success" style={{ marginBottom: "1.5rem", flexDirection: "column", alignItems: "flex-start", gap: "0.5rem" }}>
          <div><strong>Usuario creado.</strong> Comparte estas credenciales por un canal seguro:</div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.875rem", background: "rgba(255,255,255,0.6)", padding: "0.5rem 0.75rem", borderRadius: "4px" }}>
            <div>Correo: {createdBanner.email}</div>
            <div>Contraseña temporal: {createdBanner.tempPwd}</div>
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: "0.25rem 0.5rem" }}
            onClick={() => setCreatedBanner(null)}
          >
            Entendido, cerrar
          </button>
        </div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 360px)", gap: "1.5rem", alignItems: "start" }}>
        {/* Lista */}
        <section className="card">
          <div className="card-title">Usuarios existentes</div>
          {loading ? (
            <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
          ) : users.length === 0 ? (
            <div style={{ color: "var(--color-text-subtle)" }}>Sin usuarios todavía.</div>
          ) : (
            <table className="users-table">
              <thead>
                <tr>
                  <th>Correo</th>
                  <th>Rol</th>
                  <th>Estado</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.email}{u.id === me.id && <span className="badge"> · tú</span>}</td>
                    <td>{u.is_admin ? "Admin" : "Usuario"}</td>
                    <td>
                      {u.must_change_password
                        ? <span style={{ color: "var(--color-text-muted)" }}>Pendiente cambio</span>
                        : <span style={{ color: "var(--color-success)" }}>Activo</span>}
                    </td>
                    <td style={{ textAlign: "right" }}>
                      {u.id !== me.id && (
                        <button
                          className="btn btn-ghost"
                          style={{ padding: "0.25rem 0.5rem", color: "var(--color-danger)" }}
                          onClick={() => onDelete(u)}
                        >
                          Eliminar
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        {/* Crear usuario */}
        <section className="card">
          <div className="card-title">Crear nuevo usuario</div>
          <form onSubmit={onCreate}>
            <div className="auth-fields">
              <div className="field">
                <label className="field-label" htmlFor="new_email">Correo</label>
                <input
                  id="new_email"
                  type="email"
                  className="input"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>

              <div className="field">
                <label className="field-label" htmlFor="new_temp_pwd">Contraseña temporal</label>
                <input
                  id="new_temp_pwd"
                  type="text"
                  className="input"
                  required
                  minLength={8}
                  value={tempPwd}
                  onChange={(e) => setTempPwd(e.target.value)}
                  style={{ fontFamily: "var(--font-mono)" }}
                />
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={generateRandomPassword}
                  style={{ padding: "0.25rem 0", justifyContent: "flex-start" }}
                >
                  Generar aleatoria
                </button>
              </div>

              <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.875rem", cursor: "pointer" }}>
                <input
                  type="checkbox"
                  checked={isAdminFlag}
                  onChange={(e) => setIsAdminFlag(e.target.checked)}
                />
                Es administrador (puede gestionar otros usuarios)
              </label>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-block"
              disabled={creating || !email || !tempPwd}
            >
              {creating ? <span className="spinner" /> : null}
              {creating ? "Creando…" : "Crear usuario"}
            </button>
          </form>
        </section>
      </div>
    </>
  );
}
