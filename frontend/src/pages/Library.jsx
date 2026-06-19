import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

function formatDate(iso) {
  const d = new Date(iso);
  return d.toLocaleDateString("es", { day: "numeric", month: "short", year: "numeric" });
}

export default function Library() {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expanded, setExpanded] = useState({});
  const [copiedId, setCopiedId] = useState(null);
  const [filterFormat, setFilterFormat] = useState("");
  const [filterPain, setFilterPain] = useState("");

  const load = async () => {
    setError("");
    try {
      const list = await api.listTemplates();
      setTemplates(list);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const formatOptions = useMemo(() => {
    const set = new Map();
    templates.forEach((t) => set.set(t.format_id, t.format_label));
    return Array.from(set.entries());
  }, [templates]);

  const painOptions = useMemo(() => {
    const set = new Set();
    templates.forEach((t) => set.add(t.pain_label));
    return Array.from(set);
  }, [templates]);

  const filtered = useMemo(() => {
    return templates.filter((t) => {
      if (filterFormat && t.format_id !== filterFormat) return false;
      if (filterPain && t.pain_label !== filterPain) return false;
      return true;
    });
  }, [templates, filterFormat, filterPain]);

  const toggle = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const copy = async (t) => {
    try {
      await navigator.clipboard.writeText(t.content);
      setCopiedId(t.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      setError("No se pudo copiar al portapapeles.");
    }
  };

  const remove = async (t) => {
    const ok = window.confirm("¿Eliminar esta plantilla? Esta acción no se puede deshacer.");
    if (!ok) return;
    try {
      await api.deleteTemplate(t.id);
      setTemplates((prev) => prev.filter((x) => x.id !== t.id));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Biblioteca</div>
        <h1 className="page-title">Tus plantillas guardadas</h1>
        <p className="page-subtitle">
          Aquí viven los textos que marcaste como buenos. Puedes copiarlos directo o
          eliminar los que ya no sirvan.
        </p>
      </header>

      {error && <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>{error}</div>}

      {loading ? (
        <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
      ) : templates.length === 0 ? (
        <div className="empty-state">
          <p style={{ marginBottom: "1rem" }}>Aún no has guardado ninguna plantilla.</p>
          <p style={{ fontSize: "0.875rem" }}>
            Genera un texto en el{" "}
            <Link to="/" style={{ color: "var(--color-accent)", textDecoration: "underline" }}>Generador</Link>{" "}
            y haz clic en "Guardar en biblioteca" para verlo aquí.
          </p>
        </div>
      ) : (
        <>
          <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1.5rem", flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
              {filtered.length} {filtered.length === 1 ? "plantilla" : "plantillas"}
            </span>
            {formatOptions.length > 1 && (
              <select
                className="input"
                style={{ width: "auto" }}
                value={filterFormat}
                onChange={(e) => setFilterFormat(e.target.value)}
              >
                <option value="">Todos los formatos</option>
                {formatOptions.map(([id, label]) => (
                  <option key={id} value={id}>{label}</option>
                ))}
              </select>
            )}
            {painOptions.length > 1 && (
              <select
                className="input"
                style={{ width: "auto" }}
                value={filterPain}
                onChange={(e) => setFilterPain(e.target.value)}
              >
                <option value="">Todos los dolores</option>
                {painOptions.map((label) => (
                  <option key={label} value={label}>{label}</option>
                ))}
              </select>
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {filtered.map((t) => {
              const isExpanded = !!expanded[t.id];
              return (
                <article key={t.id} className="template-card">
                  <div className="template-card-meta">
                    <div className="template-card-tags">
                      <span className="chip">{t.format_label}</span>
                      <span className="chip chip-neutral">{t.pain_label}</span>
                    </div>
                    <span className="template-card-date">{formatDate(t.created_at)}</span>
                  </div>

                  <div className={`template-card-content ${isExpanded ? "expanded" : ""}`}>
                    {t.content}
                  </div>

                  <div className="template-card-actions">
                    <button className="btn btn-secondary" onClick={() => copy(t)}>
                      {copiedId === t.id ? "Copiado ✓" : "Copiar"}
                    </button>
                    <button className="btn btn-ghost" onClick={() => toggle(t.id)}>
                      {isExpanded ? "Mostrar menos" : "Mostrar completo"}
                    </button>
                    <button
                      className="btn btn-ghost"
                      style={{ color: "var(--color-danger)", marginLeft: "auto" }}
                      onClick={() => remove(t)}
                    >
                      Eliminar
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        </>
      )}
    </>
  );
}
