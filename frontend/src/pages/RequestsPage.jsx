import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";

function RequestsPage() {
  const [requests, setRequests] = useState([]);
  const [locations, setLocations] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      apiClient.get("/service-requests"),
      apiClient.get("/locations"),
      apiClient.get("/users"),
    ])
      .then(([requestsResponse, locationsResponse, usersResponse]) => {
        setRequests(requestsResponse.data);
        setLocations(locationsResponse.data);
        setUsers(usersResponse.data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.response?.data?.detail || err.message);
        setLoading(false);
      });
  }, []);

  const locationsById = new Map(locations.map((location) => [location.id, location]));
  const usersById = new Map(users.map((user) => [user.id, user]));

  return (
    <div>
      <h1>Facility Requests</h1>
      <div className="page-actions">
        <Link to="/new-request" className="btn-link">+ New Request</Link>
      </div>
      {loading && <p>Loading requests...</p>}
      {error && <p role="alert">Error: {error}</p>}
      {!loading && !error && requests.length === 0 ? (
        <p>No requests found.</p>
      ) : !loading && !error ? (
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Location</th>
              <th>Assigned to</th>
            </tr>
          </thead>
          <tbody>
            {requests.map((req) => (
              <tr key={req.id}>
                <td>
                  <Link to={`/requests/${req.id}`}>{req.title}</Link>
                </td>
                <td>
                  <span className={`status-badge status-${req.status}`}>
                    {req.status.replace(/_/g, " ")}
                  </span>
                </td>
                <td>
                  {locationsById.has(req.location_id)
                    ? `${locationsById.get(req.location_id).building}, Floor ${locationsById.get(req.location_id).floor}${locationsById.get(req.location_id).room ? `, Room ${locationsById.get(req.location_id).room}` : ""}`
                    : "Unknown location"}
                  <small className="request-reference">ID: {req.location_id}</small>
                </td>
                <td>{usersById.get(req.assigned_to)?.name || "Unassigned"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}
    </div>
  );
}

export default RequestsPage;