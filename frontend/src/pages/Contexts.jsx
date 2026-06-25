import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" });
}

export default function Contexts() {
  const [contexts, setContexts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [working, setWorking] = useState(null);

  const load = async () => {
    setError("");
    try {
      const list = await api.getContexts();
      setContexts(list);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onSetPrimary = async (ctx) => {
    setWorking(ctx.id);
    setError("");
    try {
      await api.setPrimaryContext(ctx.id);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setWorking(null);
    }
  };

  const onDelete = async (ctx) => {
    const ok = window.confirm(
      `¿Eliminar el contexto "${ctx.name}"? Esta acción no se puede deshacer.`
    );
    if (!ok) return;
    setWorking(ctx.id);
    setError("");
    try {
      await api.deleteContext(ctx.id);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setWorking(null);
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Configuración</div>
        <h1 className="page-title">Contextos del negocio</h1>
        <p className="page-subtitle">
          Guarda múltiples contextos: tu negocio, tus competidores u otras marcas. El marcado como
          <strong> Principal</strong> es el que la IA usa por defecto para generar contenido.
          Los demás puedes incluirlos como referencia en el Generador para comparaciones o
          análisis de competencia.
        </p>
      </header>

      {error && <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>{error}</div>}

      <div style={{ marginBottom: "1.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <Link to="/ajustes/nuevo" className="btn btn-primary">
          + Nuevo contexto
        </Link>
      </div>

      {loading ? (
        <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
      ) : contexts.length === 0 ? (
        <div className="empty-state">
          <p style={{ marginBottom: "1rem" }}>No tienes contextos todavía.</p>
          <p style={{ fontSize: "0.875rem" }}>
            <Link to="/ajustes/nuevo" style={{ color: "var(--color-accent)", textDecoration: "underline" }}>
              Crea el primero
            </Link>{" "}
            — puedes empezar pegando la URL de un sitio web o llenarlo a mano.
          </p>
        </div>
      ) : (
        <div className="pains-list">
          {contexts.map((c) => (
            <div key={c.id} className="pain-row">
              <div className="pain-row-header">
                <div className="pain-row-text">
                  <div className="pain-row-label">
                    {c.name}
                    {c.is_primary && (
                      <span className="chip" style={{ marginLeft: "0.5rem" }}>Principal</span>
                    )}
                  </div>
                  {c.business_name && (
                    <div className="pain-row-desc">{c.business_name}</div>
                  )}
                  <div style={{ fontSize: "0.75rem", color: "var(--color-text-subtle)", marginTop: "0.25rem" }}>
                    Actualizado el {formatDate(c.updated_at)}
                  </div>
                </div>
                <div className="pain-row-actions">
                  <Link
                    to={`/ajustes/contexto/${c.id}`}
                    className="btn btn-ghost"
                    style={{ padding: "0.25rem 0.75rem" }}
                  >
                    Editar
                  </Link>
                  {!c.is_primary && (
                    <button
                      className="btn btn-ghost"
                      onClick={() => onSetPrimary(c)}
                      disabled={working === c.id}
                      style={{ padding: "0.25rem 0.75rem" }}
                    >
                      Marcar principal
                    </button>
                  )}
                  <button
                    className="btn btn-ghost"
                    onClick={() => onDelete(c)}
                    disabled={working === c.id}
                    style={{ padding: "0.25rem 0.75rem", color: "var(--color-danger)" }}
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
