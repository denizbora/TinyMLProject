import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = 'http://localhost:5000/api';

function App() {
  const [stats, setStats] = useState({
    total_requests: 0,
    blocked_requests: 0,
    allowed_requests: 0,
    block_rate: 0,
    last_updated: null
  });
  const [events, setEvents] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch stats
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_URL}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  // Fetch events
  const fetchEvents = async () => {
    try {
      const response = await fetch(`${API_URL}/events?limit=50`);
      const data = await response.json();
      setEvents(data.events);
    } catch (error) {
      console.error('Error fetching events:', error);
    }
  };

  // Clear all events
  const clearEvents = async () => {
    if (window.confirm('Tüm event\'leri temizlemek istediğinize emin misiniz?')) {
      try {
        await fetch(`${API_URL}/clear`, { method: 'POST' });
        fetchStats();
        fetchEvents();
      } catch (error) {
        console.error('Error clearing events:', error);
      }
    }
  };

  // Auto-refresh
  useEffect(() => {
    fetchStats();
    fetchEvents();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchStats();
        fetchEvents();
      }, 2000); // Her 2 saniyede bir güncelle

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🛡️ ESP8266 TinyML WAF Dashboard</h1>
        <p>Real-time Web Application Firewall Monitoring</p>
      </header>

      <div className="controls">
        <button onClick={() => setAutoRefresh(!autoRefresh)}>
          {autoRefresh ? '⏸️ Pause' : '▶️ Resume'} Auto-Refresh
        </button>
        <button onClick={() => { fetchStats(); fetchEvents(); }}>
          🔄 Refresh Now
        </button>
        <button onClick={clearEvents} className="danger">
          🗑️ Clear All
        </button>
      </div>

      <div className="stats-container">
        <div className="stat-card">
          <h3>📊 Total Requests</h3>
          <div className="stat-value">{stats.total_requests}</div>
        </div>
        <div className="stat-card allowed">
          <h3>✅ Allowed</h3>
          <div className="stat-value">{stats.allowed_requests}</div>
        </div>
        <div className="stat-card blocked">
          <h3>🚫 Blocked</h3>
          <div className="stat-value">{stats.blocked_requests}</div>
        </div>
        <div className="stat-card rate">
          <h3>📈 Block Rate</h3>
          <div className="stat-value">{stats.block_rate.toFixed(1)}%</div>
        </div>
      </div>

      {stats.last_updated && (
        <div className="last-updated">
          Last updated: {new Date(stats.last_updated).toLocaleString()}
        </div>
      )}

      <div className="events-container">
        <h2>📋 Recent Events</h2>
        {events.length === 0 ? (
          <div className="no-events">No events yet. Waiting for ESP8266...</div>
        ) : (
          <div className="events-list">
            {events.map((event) => (
              <div
                key={event.id}
                className={`event-card ${event.action.toLowerCase()}`}
              >
                <div className="event-header">
                  <span className="event-id">#{event.id}</span>
                  <span className={`event-action ${event.action.toLowerCase()}`}>
                    {event.action === 'BLOCKED' ? '🚫 BLOCKED' : '✅ ALLOWED'}
                  </span>
                  <span className="event-time">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="event-details">
                  <div className="event-row">
                    <strong>Method:</strong> {event.method}
                    <strong>Path:</strong> {event.path}
                    {event.query && <><strong>Query:</strong> {event.query}</>}
                  </div>
                  <div className="event-row">
                    <strong>Client IP:</strong> {event.client_ip}
                    <strong>ESP IP:</strong> {event.esp_ip}
                  </div>
                  <div className="event-row">
                    <strong>User-Agent:</strong> {event.user_agent || 'N/A'}
                  </div>
                  <div className="event-row">
                    <strong>Probability:</strong>
                    <span className={`probability ${event.classification.toLowerCase()}`}>
                      {(event.probability * 100).toFixed(2)}%
                    </span>
                    <strong>Classification:</strong>
                    <span className={`classification ${event.classification.toLowerCase()}`}>
                      {event.classification}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
