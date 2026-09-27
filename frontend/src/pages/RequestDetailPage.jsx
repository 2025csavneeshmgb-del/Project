import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import apiClient from "../api/client";

const nextStatuses = {
  new: ["assigned"],
  assigned: ["in_progress"],
  in_progress: ["on_hold", "resolved"],
  on_hold: ["in_progress"],
  resolved: ["closed"],
  closed: [],
};

function formatStatus(status) {
  return status.replace(/_/g, " ");
}

function formatDate(value) {
  return new Date(value).toLocaleString();
}

function RequestDetailPage() {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [locations, setLocations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [users, setUsers] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [message, setMessage] = useState("");
  const [selectedUser, setSelectedUser] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [saving, setSaving] = useState(false);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;

    const loadRequest = async () => {
      setLoading(true);
      setError(null);

      try {
        const [requestResponse, locationsResponse, categoriesResponse, usersResponse, auditResponse] = await Promise.all([
          apiClient.get(`/service-requests/${id}`),
          apiClient.get("/locations"),
          apiClient.get("/categories"),
          apiClient.get("/users"),
          apiClient.get(`/service-requests/${id}/audit-logs`),
        ]);

        if (!active) return;
        const requestData = requestResponse.data;
        setRequest(requestData);
        setLocations(locationsResponse.data);
        setCategories(categoriesResponse.data);
        setUsers(usersResponse.data);
        setAuditLogs(auditResponse.data);
        setSelectedUser(requestData.assigned_to || "");
        setSelectedStatus((nextStatuses[requestData.status] || [])[0] || requestData.status);
      } catch (err) {
        if (active) setError(err.response?.data?.detail || err.message);
      } finally {
        if (active) setLoading(false);
      }
    };

    loadRequest();
    return () => {
      active = false;
    };
  }, [id, reloadKey]);

  const handleAssign = async (event) => {
    event.preventDefault();
    setSaving(true);
    setActionError(null);
    setMessage("");

    try {
      await apiClient.patch(`/service-requests/${id}/assign`, { assigned_to: selectedUser });
      setMessage("Request assignment updated.");
      setReloadKey((value) => value + 1);
    } catch (err) {
      setActionError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleStatusChange = async (event) => {
    event.preventDefault();
    setSaving(true);
    setActionError(null);
    setMessage("");

    try {
      await apiClient.patch(`/service-requests/${id}/status`, { status: selectedStatus });
      setMessage("Request status updated.");
      setReloadKey((value) => value + 1);
    } catch (err) {
      setActionError(err.response?.data?.detail || err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Loading request...</p>;
  if (error) return <p role="alert">Error: {error}</p>;
  if (!request) return <p>Request not found.</p>;

  const location = locations.find((item) => item.id === request.location_id);
  const category = categories.find((item) => item.id === request.category_id);
  const reporter = users.find((user) => user.id === request.created_by);
  const assignee = users.find((user) => user.id === request.assigned_to);
  const availableStatuses = nextStatuses[request.status] || [];

  return (
    <div className="request-detail">
      <Link to="/" className="back-link">Back to requests</Link>
      <header className="request-detail-header">
        <div>
          <h1>{request.title}</h1>
          <span className={`status-badge status-${request.status}`}>{formatStatus(request.status)}</span>
        </div>
      </header>

      <section className="request-detail-section">
        <h2>Request details</h2>
        <p className="request-description">{request.description}</p>
        <dl className="request-meta">
          <div>
            <dt>Category</dt>
            <dd>{category?.name || "Unknown category"}</dd>
          </div>
          <div>
            <dt>Location</dt>
            <dd>
              {location
                ? `${location.building}, Floor ${location.floor}${location.room ? `, Room ${location.room}` : ""}`
                : "Unknown location"}
            </dd>
          </div>
          <div>
            <dt>Location ID</dt>
            <dd><code>{request.location_id}</code></dd>
          </div>
          <div>
            <dt>Reported by</dt>
            <dd>{reporter?.name || "Unknown user"}</dd>
          </div>
          <div>
            <dt>Assigned to</dt>
            <dd>{assignee?.name || "Unassigned"}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{formatDate(request.created_at)}</dd>
          </div>
          <div>
            <dt>Last updated</dt>
            <dd>{formatDate(request.updated_at)}</dd>
          </div>
        </dl>
      </section>

      <section className="request-detail-section">
        <h2>Actions</h2>
        <div className="request-actions-grid">
          <form onSubmit={handleAssign}>
            <div>
              <label htmlFor="request-assignee">Assign to member</label>
              <select
                id="request-assignee"
                value={selectedUser}
                onChange={(event) => setSelectedUser(event.target.value)}
                required
              >
                <option value="">Select a member</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>{user.name} ({user.role.replace(/_/g, " ")})</option>
                ))}
              </select>
            </div>
            <button type="submit" disabled={saving || !selectedUser}>
              {saving ? "Saving..." : request.assigned_to ? "Reassign request" : "Assign request"}
            </button>
          </form>

          <form onSubmit={handleStatusChange}>
            <div>
              <label htmlFor="request-status">Move to status</label>
              <select
                id="request-status"
                value={selectedStatus}
                onChange={(event) => setSelectedStatus(event.target.value)}
                disabled={availableStatuses.length === 0}
                required
              >
                {availableStatuses.length === 0 ? (
                  <option value={request.status}>No further status changes</option>
                ) : availableStatuses.map((status) => (
                  <option key={status} value={status}>{formatStatus(status)}</option>
                ))}
              </select>
            </div>
            <button type="submit" disabled={saving || availableStatuses.length === 0}>
              Update status
            </button>
          </form>
        </div>
        {actionError && <p role="alert" className="request-action-error">{actionError}</p>}
        {message && <p role="status" className="request-action-success">{message}</p>}
      </section>

      <section className="request-detail-section">
        <h2>Activity</h2>
        {auditLogs.length === 0 ? (
          <p>No activity recorded.</p>
        ) : (
          <ol className="audit-list">
            {auditLogs.map((entry) => {
              const actor = users.find((user) => user.id === entry.performed_by);
              return (
                <li key={entry.id}>
                  <div className="audit-entry-heading">
                    <strong>{entry.action.replace(/_/g, " ")}</strong>
                    <time>{formatDate(entry.created_at)}</time>
                  </div>
                  <p>{entry.details}</p>
                  <small>By {actor?.name || entry.performed_by}</small>
                </li>
              );
            })}
          </ol>
        )}
      </section>
    </div>
  );
}

export default RequestDetailPage;