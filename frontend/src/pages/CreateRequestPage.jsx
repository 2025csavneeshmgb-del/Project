import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import apiClient from "../api/client";

function CreateRequestPage() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState([]);
  const [locations, setLocations] = useState([]);
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    category_id: "",
    location_id: "",
    created_by: "",
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    apiClient.get("/categories").then((res) => setCategories(res.data));
    apiClient.get("/locations").then((res) => setLocations(res.data));
    apiClient.get("/users").then((res) => setUsers(res.data));
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    apiClient
      .post("/service-requests", form)
      .then(() => navigate("/"))
      .catch((err) => setError(err.message));
  };

  return (
    <div>
      <h1>New Facility Request</h1>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label>Title</label>
          <input name="title" value={form.title} onChange={handleChange} required />
        </div>
        <div>
          <label>Description</label>
          <textarea name="description" value={form.description} onChange={handleChange} required />
        </div>
        <div>
          <label>Category</label>
          <select name="category_id" value={form.category_id} onChange={handleChange} required>
            <option value="">-- Select Category --</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label>Location</label>
          <select name="location_id" value={form.location_id} onChange={handleChange} required>
            <option value="">-- Select Location --</option>
            {locations.map((l) => (
              <option key={l.id} value={l.id}>
                {l.building} - Floor {l.floor} - Room {l.room}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label>Reported By</label>
          <select name="created_by" value={form.created_by} onChange={handleChange} required>
            <option value="">-- Select User --</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>
        </div>
        <button type="submit">Submit Request</button>
      </form>
    </div>
  );
}

export default CreateRequestPage;