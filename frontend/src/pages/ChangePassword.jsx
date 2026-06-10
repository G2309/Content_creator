import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../auth.jsx";

export default function ChangePassword({ forced = false }) {
  const { refresh, logout } = useAuth();
  const navigate = useNavigate();

  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (newPwd.length < 8) return "La nueva contraseña debe tener al menos 8 caracteres.";
    if (newPwd !== confirmPwd) return "La confirmación no coincide.";
    if (newPwd === currentPwd) return "La nueva contraseña debe ser distinta a la actual.";
    return null;
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    const localErr = validate();
    if (localErr) {
      setError(localErr);
      return;
    }

    setLoading(true);
    try {
      await api.changePassword(currentPwd, newPwd);
      setSuccess(true);
      setCurrentPwd("");
      setNewPwd("");
      setConfirmPwd("");

      await refresh();

      if (forced) {
        setTimeout(() => navigate("/", { replace: true }), 700);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formMarkup = (
    <form onSubmit={onSubmit} noValidate>
      {error && <div className="banner banner-error" style={{ marginBottom: "1rem" }}>{error}</div>}
      {success && (
        <div className="banner banner-success" style={{ marginBottom: "1rem" }}>
          Contraseña actualizada correctamente.
        </div>
      )}

      <div className="auth-fields">
        <div className="field">
          <label className="field-label" htmlFor="current_password">
            {forced ? "Contraseña temporal" : "Contraseña actual"}
          </label>
          <input
            id="current_password"
            type="password"
            className="input"
            autoComplete="current-password"
            required
            value={currentPwd}
            onChange={(e) => setCurrentPwd(e.target.value)}
          />
        </div>

        <div className="field">
          <label className="field-label" htmlFor="new_password">Nueva contraseña</label>
          <input
            id="new_password"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            minLength={8}
            value={newPwd}
            onChange={(e) => setNewPwd(e.target.value)}
          />
          <span className="field-hint">Mínimo 8 caracteres.</span>
        </div>

        <div className="field">
          <label className="field-label" htmlFor="confirm_password">Confirmar nueva contraseña</label>
          <input
            id="confirm_password"
            type="password"
            className="input"
            autoComplete="new-password"
            required
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
          />
        </div>
      </div>

      <button
        type="submit"
        className="btn btn-primary btn-block"
        disabled={loading || !currentPwd || !newPwd || !confirmPwd}
      >
        {loading ? <span className="spinner" /> : null}
        {loading ? "Actualizando…" : "Cambiar contraseña"}
      </button>

      {forced && (
        <button
          type="button"
          className="btn btn-ghost btn-block"
          onClick={logout}
          style={{ marginTop: "0.75rem" }}
        >
          Cancelar y cerrar sesión
        </button>
      )}
    </form>
  );

  if (forced) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <div className="auth-brand">Define tu contraseña</div>
          <p className="auth-sub">
            Por seguridad, debes reemplazar la contraseña temporal antes de continuar.
          </p>
          {formMarkup}
        </div>
      </div>
    );
  }

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Cuenta</div>
        <h1 className="page-title">Cambiar contraseña</h1>
      </header>
      <div style={{ maxWidth: "480px" }}>
        <div className="card">{formMarkup}</div>
      </div>
    </>
  );
}
