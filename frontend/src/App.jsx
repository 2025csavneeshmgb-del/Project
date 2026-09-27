import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RequestsPage from "./pages/RequestsPage";
import CreateRequestPage from "./pages/CreateRequestPage";
import RequestDetailPage from "./pages/RequestDetailPage";
import CategoriesPage from "./pages/CategoriesPage";
import LocationsPage from "./pages/LocationsPage";
import UsersPage from "./pages/UsersPage";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <header className="navbar">
        <div className="navbar-brand">Facility Desk</div>
        <nav className="navbar-links">
          <Link to="/">Requests</Link>
          <Link to="/categories">Categories</Link>
          <Link to="/locations">Locations</Link>
          <Link to="/users">Users</Link>
        </nav>
      </header>
      <main className="page-container">
        <Routes>
          <Route path="/" element={<RequestsPage />} />
          <Route path="/new-request" element={<CreateRequestPage />} />
          <Route path="/requests/:id" element={<RequestDetailPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/locations" element={<LocationsPage />} />
          <Route path="/users" element={<UsersPage />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default App;