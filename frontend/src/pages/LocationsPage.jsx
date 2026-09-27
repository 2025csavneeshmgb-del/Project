import { useEffect, useState } from "react";
import apiClient from "../api/client";

function LocationsPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ building: "", floor: "", room: "" });
  const [success, setSuccess] = useState("");

  useEffect(() => {
    apiClient
      .get("/locations")
      .then((res) => {
        setLocations(res.data);
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
      const response = await apiClient.post("/locations", form);
      setLocations((current) => [...current, response.data]);
      setForm({ building: "", floor: "", room: "" });
      setSuccess("Location created.");
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading locations...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div>
      <h1>Locations</h1>
      <h2>Add location</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="location-building">Building</label>
          <input id="location-building" name="building" value={form.building} onChange={handleChange} maxLength={100} required />
        </div>
        <div>
          <label htmlFor="location-floor">Floor</label>
          <input id="location-floor" name="floor" value={form.floor} onChange={handleChange} maxLength={50} required />
        </div>
        <div>
          <label htmlFor="location-room">Room</label>
          <input id="location-room" name="room" value={form.room} onChange={handleChange} maxLength={50} />
        </div>
        {error && <p role="alert" style={{ color: "#b91c1c" }}>{error}</p>}
        {success && <p role="status" style={{ color: "#047857" }}>{success}</p>}
        <button type="submit" disabled={saving}>{saving ? "Adding..." : "Add location"}</button>
      </form>
      {locations.length === 0 ? (
        <p>No locations found.</p>
      ) : (
        <ul>
          {locations.map((l) => (
            <li key={l.id}>
              Building {l.building}, Floor {l.floor}, Room {l.room}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default LocationsPage;