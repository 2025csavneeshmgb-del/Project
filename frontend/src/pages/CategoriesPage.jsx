import { useEffect, useState } from "react";
import apiClient from "../api/client";

function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });
  const [success, setSuccess] = useState("");

  useEffect(() => {
    apiClient
      .get("/categories")
      .then((res) => {
        setCategories(res.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const handleChange = (event) => {
    setForm({ ...form, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess("");

    try {
      const response = await apiClient.post("/categories", form);
      setCategories((current) => [...current, response.data]);
      setForm({ name: "", description: "" });
      setSuccess("Category created.");
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading categories...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>Categories</h1>
      <h2>Add category</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="category-name">Name</label>
          <input id="category-name" name="name" value={form.name} onChange={handleChange} minLength={2} maxLength={100} required />
        </div>
        <div>
          <label htmlFor="category-description">Description</label>
          <textarea id="category-description" name="description" value={form.description} onChange={handleChange} maxLength={300} />
        </div>
        {error && <p role="alert" style={{ color: "#b91c1c" }}>{error}</p>}
        {success && <p role="status" style={{ color: "#047857" }}>{success}</p>}
        <button type="submit" disabled={saving}>{saving ? "Adding..." : "Add category"}</button>
      </form>
      {categories.length === 0 ? (
        <p>No categories found.</p>
      ) : (
        <ul>
          {categories.map((c) => (
            <li key={c.id}>
              <strong>{c.name}</strong> — {c.description}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default CategoriesPage;