import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

const RESULT_FIELDS = [
  { key: "views", label: "Vistas" },
  { key: "retention_pct", label: "Retención %" },
  { key: "follows", label: "Seguidores" },
  { key: "saves", label: "Guardados" },
  { key: "comments", label: "Comentarios" },
];

const FUNNEL_LABELS = { TOFU: "Descubrimiento", MOFU: "Confianza", BOFU: "Venta" };

function hasResults(t) {
  return RESULT_FIELDS.some((f) => t[f.key] !== null && t[f.key] !== undefined);
}

function InsightList({ title, rows }) {
  if (!rows || rows.length === 0) return null;
  return (
    <div style={{ minWidth: "220px", flex: 1 }}>
      <div style={{ fontSize: "0.8125rem", fontWeight: 600, marginBottom: "0.5rem" }}>{title}</div>
      <ol style={{ margin: 0, paddingLeft: "1.25rem", fontSize: "0.875rem" }}>
        {rows.slice(0, 5).map((r) => (
          <li key={r.key} style={{ marginBottom: "0.25rem" }}>
            {r.label} — <strong>{r.avg_follows}</strong> seguidores promedio
            <span style={{ color: "var(--color-text-subtle)" }}> ({r.posts} publ.)</span>
          </li>
        ))}
      </ol>
    </div>
  );
}

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
  const [filterObjective, setFilterObjective] = useState("");
  const [filterPillar, setFilterPillar] = useState("");
  const [insights, setInsights] = useState(null);

  const [resultsId, setResultsId] = useState(null);
  const [resultsForm, setResultsForm] = useState({});
  const [savingResults, setSavingResults] = useState(false);

  const [editingId, setEditingId] = useState(null);
  const [editContent, setEditContent] = useState("");
  const [savingEdit, setSavingEdit] = useState(false);

  const load = async () => {
    setError("");
    try {
      const [list, ins] = await Promise.all([api.listTemplates(), api.getLibraryInsights()]);
      setTemplates(list);
      setInsights(ins);
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

  const objectiveOptions = useMemo(() => {
    const map = new Map();
    templates.forEach((t) => t.objective_id && map.set(t.objective_id, t.objective_label));
    return Array.from(map.entries());
  }, [templates]);

  const pillarOptions = useMemo(() => {
    const map = new Map();
    templates.forEach((t) => t.pillar_id && map.set(t.pillar_id, t.pillar_label));
    return Array.from(map.entries());
  }, [templates]);

  const filtered = useMemo(() => {
    return templates.filter((t) => {
      if (filterFormat && t.format_id !== filterFormat) return false;
      if (filterPain && t.pain_label !== filterPain) return false;
      if (filterObjective && t.objective_id !== filterObjective) return false;
      if (filterPillar && t.pillar_id !== filterPillar) return false;
      return true;
    });
  }, [templates, filterFormat, filterPain, filterObjective, filterPillar]);

  const openResults = (t) => {
    setResultsId(t.id);
    setResultsForm(Object.fromEntries(RESULT_FIELDS.map((f) => [f.key, t[f.key] ?? ""])));
    setError("");
  };

  const saveResults = async () => {
    setSavingResults(true);
    setError("");
    try {
      const payload = Object.fromEntries(
        RESULT_FIELDS.map((f) => {
          const raw = String(resultsForm[f.key] ?? "").trim();
          return [f.key, raw === "" ? null : Math.max(0, parseInt(raw, 10) || 0)];
        })
      );
      const updated = await api.updateTemplateResults(resultsId, payload);
      setTemplates((prev) => prev.map((t) => (t.id === updated.id ? updated : t)));
      setInsights(await api.getLibraryInsights());
      setResultsId(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingResults(false);
    }
  };

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

  const startEdit = (t) => {
    setEditingId(t.id);
    setEditContent(t.content);
    setExpanded((prev) => ({ ...prev, [t.id]: true }));
    setError("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditContent("");
  };

  const saveEdit = async () => {
    if (!editContent.trim()) {
      setError("La plantilla no puede quedar vacía.");
      return;
    }
    setSavingEdit(true);
    setError("");
    try {
      const updated = await api.updateTemplate(editingId, editContent);
      setTemplates((prev) =>
        prev.map((t) => (t.id === updated.id ? { ...t, content: updated.content } : t))
      );
      cancelEdit();
    } catch (e) {
      setError(e.message);
    } finally {
      setSavingEdit(false);
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Biblioteca</div>
        <h1 className="page-title">Tus plantillas guardadas</h1>
        <p className="page-subtitle">
          Aquí viven los textos que guardaste. Cuando publiques uno, anota sus resultados de
          Instagram: el sistema aprende qué te trae seguidores y lo usa en los guiones nuevos.
        </p>
      </header>

      {error && <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>{error}</div>}

      {insights && templates.length > 0 && (
        <section className="card" style={{ marginBottom: "1.5rem" }}>
          <div className="card-title">Tu mezcla de los últimos {insights.balance.window_days} días</div>
          <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
            {Object.keys(FUNNEL_LABELS).map((k) => (
              <div key={k} style={{ fontSize: "0.875rem" }}>
                <strong>{FUNNEL_LABELS[k]}</strong>: {insights.balance.counts[k]}{" "}
                <span style={{ color: "var(--color-text-subtle)" }}>
                  ({insights.balance.actual_pct[k]}% · meta {insights.balance.target_pct[k]}%)
                </span>
              </div>
            ))}
          </div>
          <div className="banner banner-info">{insights.balance.message}</div>

          <div className="card-title" style={{ marginTop: "1.25rem" }}>Qué te trae seguidores</div>
          {insights.by_hook.length === 0 && insights.by_pillar.length === 0 ? (
            <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", margin: 0 }}>
              Anota los resultados de al menos {insights.min_posts} publicaciones con el mismo gancho
              o pilar para empezar a ver qué funciona. Llevas {insights.posts_with_results} con resultados.
            </p>
          ) : (
            <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
              <InsightList title="Por gancho" rows={insights.by_hook} />
              <InsightList title="Por pilar" rows={insights.by_pillar} />
              <InsightList title="Por objetivo" rows={insights.by_objective} />
            </div>
          )}
        </section>
      )}

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
            {objectiveOptions.length > 1 && (
              <select
                className="input"
                style={{ width: "auto" }}
                value={filterObjective}
                onChange={(e) => setFilterObjective(e.target.value)}
              >
                <option value="">Todos los objetivos</option>
                {objectiveOptions.map(([id, label]) => (
                  <option key={id} value={id}>{label}</option>
                ))}
              </select>
            )}
            {pillarOptions.length > 1 && (
              <select
                className="input"
                style={{ width: "auto" }}
                value={filterPillar}
                onChange={(e) => setFilterPillar(e.target.value)}
              >
                <option value="">Todos los pilares</option>
                {pillarOptions.map(([id, label]) => (
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
                <option value="">Todas las ideas</option>
                {painOptions.map((label) => (
                  <option key={label} value={label}>{label}</option>
                ))}
              </select>
            )}
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {filtered.map((t) => {
              const isExpanded = !!expanded[t.id];
              const isEditing = editingId === t.id;

              return (
                <article key={t.id} className="template-card">
                  <div className="template-card-meta">
                    <div className="template-card-tags">
                      <span className="chip">{t.format_label}</span>
                      <span className="chip chip-neutral">{t.pain_label}</span>
                      {t.objective_label && <span className="chip chip-neutral">{t.objective_label}</span>}
                      {t.pillar_label && <span className="chip chip-neutral">{t.pillar_label}</span>}
                      {t.hook_label && <span className="chip chip-neutral">Gancho: {t.hook_label}</span>}
                      {t.angle_label && <span className="chip chip-neutral">Ángulo: {t.angle_label}</span>}
                    </div>
                    <span className="template-card-date">{formatDate(t.created_at)}</span>
                  </div>

                  {isEditing ? (
                    <textarea
                      className="textarea"
                      rows={12}
                      value={editContent}
                      onChange={(e) => setEditContent(e.target.value)}
                      maxLength={40000}
                      style={{ minHeight: "200px", fontFamily: "inherit", lineHeight: 1.6 }}
                    />
                  ) : (
                    <div className={`template-card-content ${isExpanded ? "expanded" : ""}`}>
                      {t.content}
                    </div>
                  )}

                  {resultsId === t.id ? (
                    <div style={{ marginTop: "1rem" }}>
                      <div style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "0.5rem" }}>
                        Cópialos de Instagram → el reel → Ver estadísticas. Deja vacío lo que no tengas.
                      </div>
                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(110px, 1fr))", gap: "0.5rem" }}>
                        {RESULT_FIELDS.map((f) => (
                          <label key={f.key} className="field" style={{ margin: 0 }}>
                            <span className="field-label">{f.label}</span>
                            <input
                              type="number"
                              min="0"
                              max={f.key === "retention_pct" ? 100 : undefined}
                              className="input"
                              value={resultsForm[f.key]}
                              onChange={(e) => setResultsForm({ ...resultsForm, [f.key]: e.target.value })}
                            />
                          </label>
                        ))}
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.75rem" }}>
                        <button className="btn btn-primary" onClick={saveResults} disabled={savingResults}>
                          {savingResults ? <span className="spinner" /> : null}
                          {savingResults ? "Guardando…" : "Guardar resultados"}
                        </button>
                        <button className="btn btn-ghost" onClick={() => setResultsId(null)} disabled={savingResults}>
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : hasResults(t) && (
                    <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "0.75rem", fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                      {RESULT_FIELDS.filter((f) => t[f.key] !== null && t[f.key] !== undefined).map((f) => (
                        <span key={f.key}>{f.label}: <strong>{t[f.key]}</strong></span>
                      ))}
                    </div>
                  )}

                  <div className="template-card-actions">
                    {isEditing ? (
                      <>
                        <button
                          className="btn btn-primary"
                          onClick={saveEdit}
                          disabled={savingEdit || !editContent.trim()}
                        >
                          {savingEdit ? <span className="spinner" /> : null}
                          {savingEdit ? "Guardando…" : "Guardar cambios"}
                        </button>
                        <button
                          className="btn btn-ghost"
                          onClick={cancelEdit}
                          disabled={savingEdit}
                        >
                          Cancelar
                        </button>
                      </>
                    ) : (
                      <>
                        <button className="btn btn-secondary" onClick={() => copy(t)}>
                          {copiedId === t.id ? "Copiado ✓" : "Copiar"}
                        </button>
                        <button className="btn btn-secondary" onClick={() => startEdit(t)}>
                          Editar
                        </button>
                        <button className="btn btn-secondary" onClick={() => openResults(t)}>
                          {hasResults(t) ? "Editar resultados" : "Anotar resultados"}
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
                      </>
                    )}
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
