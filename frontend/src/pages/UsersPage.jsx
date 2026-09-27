import { useEffect, useState } from "react";
import apiClient from "../api/client";

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "employee" });
  const [success, setSuccess] = useState("");

  useEffect(() => {
    apiClient
      .get("/users")
      .then((res) => {
        setUsers(res.data);
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
      const response = await apiClient.post("/users", form);
      setUsers((current) => [...current, response.data]);
      setForm({ name: "", email: "", password: "", role: "employee" });
      setSuccess("User created.");
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading users...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>Users</h1>
      <h2>Add user</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="user-name">Name</label>
          <input id="user-name" name="name" value={form.name} onChange={handleChange} minLength={2} maxLength={100} required />
        </div>
        <div>
          <label htmlFor="user-email">Email</label>
          <input id="user-email" name="email" type="email" value={form.email} onChange={handleChange} required />
        </div>
        <div>
          <label htmlFor="user-password">Password</label>
          <input id="user-password" name="password" type="password" value={form.password} onChange={handleChange} minLength={8} required />
        </div>
        <div>
          <label htmlFor="user-role">Role</label>
          <select id="user-role" name="role" value={form.role} onChange={handleChange}>
            <option value="employee">Employee</option>
            <option value="support_staff">Support staff</option>
            <option value="facility_manager">Facility manager</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        {error && <p role="alert" style={{ color: "#b91c1c" }}>{error}</p>}
        {success && <p role="status" style={{ color: "#047857" }}>{success}</p>}
        <button type="submit" disabled={saving}>{saving ? "Adding..." : "Add user"}</button>
      </form>
      {users.length === 0 ? (
        <p>No users found.</p>
      ) : (
        <ul>
          {users.map((u) => (
            <li key={u.id}>
              {u.name} — {u.email} ({u.role})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default UsersPage;