import { useEffect, useState } from "react";
import { api } from "../api";

export default function Pains() {
  const [pains, setPains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [creating, setCreating] = useState(false);
  const [newLabel, setNewLabel] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const [editingId, setEditingId] = useState(null);
  const [editLabel, setEditLabel] = useState("");
  const [editDesc, setEditDesc] = useState("");
  const [saving, setSaving] = useState(false);

  const load = async () => {
    setError("");
    try {
      const list = await api.getPains();
      setPains(list);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const onCreate = async (e) => {
    e.preventDefault();
    if (newLabel.trim().length < 2) {
      setError("El nombre del dolor debe tener al menos 2 caracteres.");
      return;
    }
    setCreating(true);
    setError("");
    try {
      const created = await api.createPain(newLabel.trim(), newDesc.trim());
      setPains((prev) => [...prev, created]);
      setNewLabel("");
      setNewDesc("");
    } catch (e) {
      setError(e.message);
    } finally {
      setCreating(false);
    }
  };

  const startEdit = (pain) => {
    setEditingId(pain.id);
    setEditLabel(pain.label);
    setEditDesc(pain.description);
    setError("");
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditLabel("");
    setEditDesc("");
  };

  const saveEdit = async () => {
    if (editLabel.trim().length < 2) {
      setError("El nombre del dolor debe tener al menos 2 caracteres.");
      return;
    }
    setSaving(true);
    setError("");
    try {
      const updated = await api.updatePain(editingId, {
        label: editLabel.trim(),
        description: editDesc.trim(),
      });
      setPains((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      cancelEdit();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (pain) => {
    const ok = window.confirm(
      `¿Eliminar el dolor "${pain.label}"? Las plantillas guardadas con este dolor se mantendrán, pero ya no podrás usarlo para generar nuevo contenido.`
    );
    if (!ok) return;
    setError("");
    try {
      await api.deletePain(pain.id);
      setPains((prev) => prev.filter((p) => p.id !== pain.id));
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <>
      <header className="page-header">
        <div className="page-eyebrow">Configuración</div>
        <h1 className="page-title">Dolores del cliente</h1>
        <p className="page-subtitle">
          Estos son los problemas que tu negocio resuelve. Cada vez que generas contenido,
          eliges uno como punto de partida. Mientras más específicos, mejor los textos.
        </p>
      </header>

      {error && (
        <div className="banner banner-error" style={{ marginBottom: "1.5rem" }}>
          {error}
        </div>
      )}

      <div className="settings-form">
        <section className="card">
          <div className="card-title">Agregar nuevo dolor</div>
          <form onSubmit={onCreate}>
            <div className="auth-fields">
              <div className="field">
                <label className="field-label" htmlFor="new_label">Nombre del dolor</label>
                <input
                  id="new_label"
                  className="input"
                  required
                  minLength={2}
                  maxLength={255}
                  value={newLabel}
                  onChange={(e) => setNewLabel(e.target.value)}
                  placeholder="Ej. Tarifas de envío difíciles de calcular"
                />
              </div>
              <div className="field">
                <label className="field-label" htmlFor="new_desc">Descripción (opcional)</label>
                <textarea
                  id="new_desc"
                  className="textarea"
                  rows={2}
                  maxLength={1000}
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Cuenta brevemente cómo afecta este problema al cliente."
                />
              </div>
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={creating || newLabel.trim().length < 2}
            >
              {creating ? <span className="spinner" /> : null}
              {creating ? "Agregando…" : "Agregar dolor"}
            </button>
          </form>
        </section>

        <section className="card">
          <div className="card-title">Dolores existentes</div>

          {loading ? (
            <div style={{ color: "var(--color-text-subtle)" }}>Cargando…</div>
          ) : pains.length === 0 ? (
            <div className="empty-state">
              <p>No tienes dolores configurados todavía.</p>
              <p style={{ fontSize: "0.875rem", marginTop: "0.5rem" }}>
                Agrega el primero usando el formulario de arriba.
              </p>
            </div>
          ) : (
            <div className="pains-list">
              {pains.map((p) => (
                <div key={p.id} className="pain-row">
                  {editingId === p.id ? (
                    <>
                      <div className="field">
                        <label className="field-label">Nombre</label>
                        <input
                          className="input"
                          value={editLabel}
                          onChange={(e) => setEditLabel(e.target.value)}
                          maxLength={255}
                        />
                      </div>
                      <div className="field">
                        <label className="field-label">Descripción</label>
                        <textarea
                          className="textarea"
                          rows={2}
                          value={editDesc}
                          onChange={(e) => setEditDesc(e.target.value)}
                          maxLength={1000}
                        />
                      </div>
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        <button
                          className="btn btn-primary"
                          onClick={saveEdit}
                          disabled={saving || editLabel.trim().length < 2}
                          style={{ padding: "0.5rem 1rem" }}
                        >
                          {saving ? <span className="spinner" /> : null}
                          {saving ? "Guardando…" : "Guardar"}
                        </button>
                        <button
                          className="btn btn-ghost"
                          onClick={cancelEdit}
                          disabled={saving}
                          style={{ padding: "0.5rem 1rem" }}
                        >
                          Cancelar
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="pain-row-header">
                      <div className="pain-row-text">
                        <div className="pain-row-label">{p.label}</div>
                        {p.description && (
                          <div className="pain-row-desc">{p.description}</div>
                        )}
                      </div>
                      <div className="pain-row-actions">
                        <button
                          className="btn btn-ghost"
                          onClick={() => startEdit(p)}
                          style={{ padding: "0.25rem 0.75rem" }}
                        >
                          Editar
                        </button>
                        <button
                          className="btn btn-ghost"
                          onClick={() => remove(p)}
                          style={{ padding: "0.25rem 0.75rem", color: "var(--color-danger)" }}
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </>
  );
}
