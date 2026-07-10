# SnapLink - Minimal URL Shortener

A minimal, clean, and testable URL shortener portfolio project featuring a Python (FastAPI) backend and a React (Vite) frontend.

This application is designed with modularity and testability as top priorities. It features isolated business logic and storage interfaces to demonstrate clean architecture, and includes toggleable unit test failure modes designed to simulate CI/CD pipeline breaks.

---

## Repository Structure

```
project-2/
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI routes, CORS, and request schemas
│   │   ├── storage.py      # Encapsulated in-memory storage layer
│   │   └── logic.py        # Core pure business logic (URL & custom alias validation)
│   ├── tests/
│   │   └── test_logic.py   # Pytest unit tests (with toggleable failure)
│   ├── requirements.txt    # Python package dependencies
│   └── pytest.ini          # Pytest path and execution configuration
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UrlForm.jsx # URL shortener form submission component
│   │   │   └── UrlList.jsx # Shortened links and clicks display table
│   │   ├── App.jsx         # App orchestration and state controller
│   │   ├── App.css         # Local CSS styles (plain cards, clear margins)
│   │   └── index.css       # Core styling & neutral design variables
│   ├── tests/
│   │   └── App.test.jsx    # Vitest component test suite (with toggleable failure)
│   ├── package.json
│   ├── vite.config.js      # Vite and Vitest configuration
│   └── index.html
└── README.md               # Setup and running instructions
```

---

## Architectural Highlights (For Interviews)

*   **Isolated Storage Module**: The database logic lives entirely inside [storage.py](file:///c:/Users/adi/Desktop/project-2/backend/app/storage.py). It operates via a clean interface (`save_link`, `get_link_by_code`, `get_link_by_url`, etc.), making it trivial to swap out the in-memory dictionary for Redis, PostgreSQL, or MongoDB without changing the rest of the application.
*   **Pure Core Logic**: Core business validation and generation live in [logic.py](file:///c:/Users/adi/Desktop/project-2/backend/app/logic.py) as pure functions. They do not rely on FastAPI context, request objects, or database state, allowing them to be fully unit tested in complete isolation.
*   **Collision Avoidance Policy**: When shortening a link without a custom alias, the application generates a random 6-character alphanumeric short code. If a duplicate short code is randomly generated, the router automatically catches the collision and retries generation up to 10 times before reporting an error.

---

## Backend (`backend/`)

### Setup and Running

1.  **Navigate to backend directory**:
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment (optional but recommended)**:
    ```bash
    python -m venv venv
    # On Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Uvicorn local server**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    The API documentation will be available at `http://localhost:8000/docs`.

### Running Tests

Run the pytest unit tests inside the `backend/` folder:

*   **Run normally (all pass)**:
    ```bash
    pytest
    ```

*   **Simulate a CI/CD Test Failure**:
    Set the `TOGGLE_TEST_FAILURE` environment variable to `true` to force a test to fail (useful for testing pipeline rules):
    ```powershell
    # Windows (PowerShell)
    $env:TOGGLE_TEST_FAILURE="true"; pytest
    
    # macOS/Linux/Bash
    TOGGLE_TEST_FAILURE=true pytest
    ```

---

## Frontend (`frontend/`)

The frontend is a single-page React app built on Vite, styled with plain CSS. The UI is designed with simplicity in mind: clean margins, plain border cards, neutral background, and a single indigo accent color.

### Setup and Running

1.  **Navigate to frontend directory**:
    ```bash
    cd frontend
    ```

2.  **Install node dependencies**:
    ```bash
    npm install
    ```

3.  **Run the Vite local development server**:
    ```bash
    npm run dev
    ```
    The React application will run locally at `http://localhost:5173/`.

### Running Tests

We use Vitest and React Testing Library for frontend component verification.

*   **Run normally (all pass)**:
    ```bash
    npm run test
    ```

*   **Simulate a CI/CD Test Failure**:
    Set the `VITE_TOGGLE_TEST_FAILURE` environment variable to `true` to force a component test to fail:
    ```powershell
    # Windows (PowerShell)
    $env:VITE_TOGGLE_TEST_FAILURE="true"; npm run test
    
    # macOS/Linux/Bash
    VITE_TOGGLE_TEST_FAILURE=true npm run test
    ```
