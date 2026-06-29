import { useEffect, useMemo, useState } from "react";
import { api } from "../api";

const CATEGORIES = [
  { id: "pain", label: "Dolores", help: "Frustraciones o problemas concretos del cliente." },
  { id: "desire", label: "Deseos", help: "Lo que el cliente quiere lograr o cómo quiere sentirse." },
  { id: "fear", label: "Miedos", help: "Lo que el cliente teme que pase si toma una mala decisión." },
  { id: "story", label: "Historias", help: "Anécdotas reales del negocio: éxitos, errores asumidos, momentos clave." },
];

const EMPTY_FORM = { label: "", description: "", category: "pain" };

function categoryLabel(id) {
  return CATEGORIES.find((c) => c.id === id)?.label || id;
}

export default function CustomerData() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("pain");

  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const [importOpen, setImportOpen] = useState(false);

  const load = async () => {
    setError("");
    try {
      const list = await api.getPains();
      setItems(list);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = useMemo(
    () => items.filter((i) => i.category === activeTab),
    [items, activeTab]
  );

  const countsByCategory = useMemo(() => {
    const counts = { pain: 0, desire: 0, fear: 0, story: 0 };
    items.forEach((i) => {
      if (counts[i.category] !== undefined) counts[i.category] += 1;
    });
    return counts;
  }, [items]);

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      label: item.label,
      description: item.description,
      category: item.category,
    });
    setActiveTab(item.category);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setForm({ ...EMPTY_FORM, category: activeTab });
  };

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!form.label.trim()) return;
    setSubmitting(true);
    setError("");
    try {
      if (editingId) {
        await api.updatePain(editingId, {
          label: form.label.trim(),
          description: form.description.trim(),
          category: form.category,
        });
      } else {
        await api.createPain(form.label.trim(), form.description.trim(), form.category);
      }
      setForm({ ...EMPTY_FORM, category: activeTab });
      setEditingId(null);
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const onDelete = async (item) => {
    if (!window.confirm(`¿Eliminar "${item.label}"?`)) return;
    try {
      await api.deletePain(item.id);
      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const onTabChange = (catId) => {
    setActiveTab(catId);
    if (!editingId) {
      setForm({ ...EMPTY_FORM, category: catId });
    }
  };

  const activeCategoryInfo = CATEGORIES.find((c) => c.id === activeTab);

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Configuración</div>
        <h1 className="page-title">Datos del cliente</h1>
        <p className="page-subtitle">
          Información sobre tu cliente que la IA usa para generar contenido. Organízala por
          categoría: <strong>dolores</strong> (lo que le duele), <strong>deseos</strong> (lo que
          quiere), <strong>miedos</strong> (lo que teme) y <strong>historias</strong> reales del
          negocio. Mientras más material tengas, más variado será el contenido generado.
        </p>
      </header>

      {error && (
        <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      <div style={{ marginBottom: "1.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button className="btn btn-secondary" onClick={() => setImportOpen(true)}>
          + Importar desde biblioteca sugerida
        </button>
      </div>

      <div className="tabs" style={{ marginBottom: "1.5rem", display: "flex", gap: "0.25rem", flexWrap: "wrap", borderBottom: "1px solid var(--color-border)" }}>
        {CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            className={`tab-btn ${activeTab === cat.id ? "tab-btn-active" : ""}`}
            onClick={() => onTabChange(cat.id)}
            style={{
              background: "transparent",
              border: "none",
              borderBottom: activeTab === cat.id ? "2px solid var(--color-accent)" : "2px solid transparent",
              padding: "0.75rem 1.25rem",
              cursor: "pointer",
              fontFamily: "var(--font-sans)",
              fontWeight: activeTab === cat.id ? 600 : 500,
              color: activeTab === cat.id ? "var(--color-accent)" : "var(--color-text-muted)",
              fontSize: "0.9375rem",
            }}
          >
            {cat.label}
            <span style={{ marginLeft: "0.4rem", opacity: 0.7, fontSize: "0.8125rem" }}>
              ({countsByCategory[cat.id]})
            </span>
          </button>
        ))}
      </div>

      <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginBottom: "1.25rem" }}>
        {activeCategoryInfo?.help}
      </p>

      <form onSubmit={onSubmit} className="card" style={{ marginBottom: "2rem" }}>
        <div className="card-title">
          {editingId ? "Editar elemento" : `Agregar nuevo (${categoryLabel(form.category).toLowerCase()})`}
        </div>

        <div className="field">
          <label className="field-label">Categoría</label>
          <select
            className="input"
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
          >
            {CATEGORIES.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
        </div>

        <div className="field">
          <label className="field-label">Título corto</label>
          <input
            type="text"
            className="input"
            value={form.label}
            onChange={(e) => setForm({ ...form, label: e.target.value })}
            maxLength={255}
            placeholder={
              form.category === "pain" ? "Ej. Cargos sorpresa al final del envío" :
              form.category === "desire" ? "Ej. Recibir todo en México sin complicaciones" :
              form.category === "fear" ? "Ej. Que el paquete nunca llegue" :
              "Ej. Asumimos un error de cotización con un cliente"
            }
            required
          />
        </div>

        <div className="field">
          <label className="field-label">Descripción / detalle</label>
          <textarea
            className="textarea"
            rows={3}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            maxLength={2000}
            placeholder="Da contexto a la IA: cómo se vive, qué impacto tiene, qué ejemplo concreto sirve."
          />
        </div>

        <div style={{ display: "flex", gap: "0.5rem", marginTop: "1rem" }}>
          <button type="submit" className="btn btn-primary" disabled={submitting || !form.label.trim()}>
            {submitting ? <span className="spinner" /> : null}
            {submitting ? "Guardando…" : (editingId ? "Guardar cambios" : "Agregar")}
          </button>
          {editingId && (
            <button type="button" className="btn btn-ghost" onClick={cancelEdit}>
              Cancelar
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <p style={{ marginBottom: "0.75rem" }}>No hay {categoryLabel(activeTab).toLowerCase()} todavía.</p>
          <p style={{ fontSize: "0.875rem" }}>
            Agrega uno con el formulario de arriba, o importa de la biblioteca sugerida.
          </p>
        </div>
      ) : (
        <div className="pains-list">
          {filtered.map((item) => (
            <div key={item.id} className="pain-row">
              <div className="pain-row-header">
                <div className="pain-row-text">
                  <div className="pain-row-label">{item.label}</div>
                  {item.description && (
                    <div className="pain-row-desc">{item.description}</div>
                  )}
                </div>
                <div className="pain-row-actions">
                  <button
                    className="btn btn-ghost"
                    onClick={() => startEdit(item)}
                    style={{ padding: "0.25rem 0.75rem" }}
                  >
                    Editar
                  </button>
                  <button
                    className="btn btn-ghost"
                    onClick={() => onDelete(item)}
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

      {importOpen && (
        <ImportModal
          onClose={() => setImportOpen(false)}
          onImported={async () => {
            setImportOpen(false);
            await load();
          }}
        />
      )}
    </>
  );
}

function ImportModal({ onClose, onImported }) {
  const [suggested, setSuggested] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(new Set());
  const [filterCat, setFilterCat] = useState("all");
  const [importing, setImporting] = useState(false);

  useEffect(() => {
    api
      .getSuggestedInsights()
      .then((list) => setSuggested(list))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const toggle = (idx) => {
    const next = new Set(selected);
    if (next.has(idx)) next.delete(idx);
    else next.add(idx);
    setSelected(next);
  };

  const selectAllVisible = () => {
    const next = new Set(selected);
    suggested.forEach((item, idx) => {
      if (filterCat === "all" || item.category === filterCat) {
        next.add(idx);
      }
    });
    setSelected(next);
  };

  const clearSelection = () => setSelected(new Set());

  const doImport = async () => {
    if (selected.size === 0) return;
    setImporting(true);
    setError("");
    try {
      const items = Array.from(selected).map((idx) => suggested[idx]);
      await api.importInsights(items);
      onImported();
    } catch (e) {
      setError(e.message);
      setImporting(false);
    }
  };

  const visible = suggested.filter(
    (item) => filterCat === "all" || item.category === filterCat
  );

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(9, 36, 81, 0.55)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "1rem",
        zIndex: 100,
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          background: "var(--color-surface)",
          borderRadius: "12px",
          width: "100%",
          maxWidth: "780px",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          boxShadow: "0 20px 60px rgba(0,0,0,0.25)",
        }}
      >
        <div style={{ padding: "1.5rem 1.5rem 1rem", borderBottom: "1px solid var(--color-border)" }}>
          <h2 style={{ fontFamily: "var(--font-serif)", fontSize: "1.5rem", margin: 0, color: "var(--color-text)" }}>
            Biblioteca sugerida
          </h2>
          <p style={{ fontSize: "0.875rem", color: "var(--color-text-muted)", marginTop: "0.5rem", marginBottom: 0 }}>
            Catálogo de dolores, deseos, miedos e historias del nicho de paquetería USA → México.
            Selecciona los que quieras agregar a tu lista. Los repetidos se ignoran.
          </p>
        </div>

        <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid var(--color-border)", display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
          <select
            className="input"
            value={filterCat}
            onChange={(e) => setFilterCat(e.target.value)}
            style={{ width: "auto" }}
          >
            <option value="all">Todas las categorías</option>
            {CATEGORIES.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>

          <button type="button" className="btn btn-ghost" onClick={selectAllVisible} style={{ padding: "0.4rem 0.75rem" }}>
            Seleccionar todos
          </button>
          <button type="button" className="btn btn-ghost" onClick={clearSelection} style={{ padding: "0.4rem 0.75rem" }}>
            Limpiar
          </button>
          <span style={{ marginLeft: "auto", fontSize: "0.875rem", color: "var(--color-text-muted)" }}>
            {selected.size} seleccionados
          </span>
        </div>

        <div style={{ overflowY: "auto", flex: 1, padding: "1rem 1.5rem" }}>
          {error && <div className="banner banner-error" style={{ marginBottom: "1rem" }}>{error}</div>}
          {loading ? (
            <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {visible.map((item, visIdx) => {
                const origIdx = suggested.indexOf(item);
                const isSelected = selected.has(origIdx);
                return (
                  <label
                    key={origIdx}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "0.75rem",
                      padding: "0.75rem",
                      borderRadius: "8px",
                      cursor: "pointer",
                      border: `1px solid ${isSelected ? "var(--color-accent)" : "var(--color-border)"}`,
                      background: isSelected ? "rgba(9,36,81,0.04)" : "var(--color-surface)",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggle(origIdx)}
                      style={{ marginTop: "0.25rem" }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.25rem" }}>
                        <span style={{ fontWeight: 600, color: "var(--color-text)" }}>{item.label}</span>
                        <span className="chip chip-neutral" style={{ fontSize: "0.6875rem" }}>
                          {categoryLabel(item.category)}
                        </span>
                      </div>
                      <div style={{ fontSize: "0.8125rem", color: "var(--color-text-muted)" }}>
                        {item.description}
                      </div>
                    </div>
                  </label>
                );
              })}
            </div>
          )}
        </div>

        <div style={{ padding: "1rem 1.5rem", borderTop: "1px solid var(--color-border)", display: "flex", gap: "0.5rem", justifyContent: "flex-end" }}>
          <button type="button" className="btn btn-ghost" onClick={onClose} disabled={importing}>
            Cancelar
          </button>
          <button type="button" className="btn btn-primary" onClick={doImport} disabled={importing || selected.size === 0}>
            {importing ? <span className="spinner" /> : null}
            {importing ? "Importando…" : `Importar ${selected.size} elemento${selected.size === 1 ? "" : "s"}`}
          </button>
        </div>
      </div>
    </div>
  );
}
