# Mission Control Dashboard

**Beautiful web UI for managing RunPod jobs - because terminals are sad.** 🎨

---

## What This Is

A local web dashboard that runs on your Mac and gives you a visual interface for:
- 📊 Viewing job status in real-time
- ➕ Submitting new jobs (no terminal!)
- 📥 Downloading results with one click
- 🖼️ Previewing rendered images
- 🤖 Monitoring pod agent health
- 📋 Viewing live logs

**No more staring at terminal output!**

---

## Quick Start

```bash
# First time setup
cd dashboard
doppler run -- python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the dashboard (subsequent runs)
cd dashboard
source venv/bin/activate
doppler run -- python3 app.py

# Browser auto-opens to: http://localhost:5001
```

## Testing

```bash
# Run all tests
cd dashboard
source venv/bin/activate
./run_tests.sh

# Or run specific test file
doppler run -- python -m pytest tests/test_cost_calculator.py -v
```

**Current Test Coverage:**
- ✅ Cost Calculator (19 tests) - 100% passing
- 🚧 API Endpoints (coming soon)
- 🚧 Frontend Integration (coming soon)

---

## Features

### ✅ Phase 1 (MVP)
- [x] Job listing from R2
- [x] Job submission form
- [x] Basic status display

### 🚧 Phase 2 (In Progress)
- [ ] Real-time status updates
- [ ] One-click downloads
- [ ] Thumbnail previews

### 🎨 Phase 3 (Polish)
- [ ] Pod agent monitoring
- [ ] Live logs viewer
- [ ] Dark mode
- [ ] Animations & UX polish

---

## Tech Stack

- **Backend:** Python Flask (simple, fast, no overkill)
- **Frontend:** HTML + JavaScript (vanilla, no build tools)
- **Styling:** Tailwind CSS (via CDN, no setup)
- **Real-time:** Server-Sent Events (SSE) for live updates
- **Storage:** R2 (same as Mission Control CLI)

---

## Project Structure

```bash
dashboard/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css      # Custom styles
│   └── js/
│       └── dashboard.js   # Frontend logic
├── templates/
│   └── index.html         # Main dashboard UI
└── README.md              # This file
```

---

## Development

### Run in Dev Mode
```bash
doppler run -- python3 app.py
```

Dashboard runs on `http://localhost:5000`

### Run in Production
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/api/jobs` | GET | List all jobs |
| `/api/jobs` | POST | Submit new job |
| `/api/jobs/<id>` | GET | Get job details |
| `/api/jobs/<id>/download` | GET | Download job results |
| `/api/pod/status` | GET | Get pod agent status |
| `/api/logs` | GET | Stream pod logs (SSE) |

---

## Screenshots

*Coming soon after Phase 1 is complete!*

---

**Built with ❤️ by a UX designer who believes terminals should have feelings too.**

## Related Documentation

- [Doppler Secrets Management](Documents/reference/DOPPLER_SECRETS_MANAGEMENT.md) - secrets management
- [Cost Management](Documents/reference/MODEL_COST_COMPARISON.md) - cost management
