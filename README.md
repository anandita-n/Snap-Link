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

---

## Jenkins CI/CD Pipeline & AI Triage (Portfolio Showcase)

This project features a fully automated, intelligent CI/CD pipeline built on Jenkins. When tests or linting fail on either the frontend or backend, the pipeline dynamically extracts the failure logs, calls the Google Gemini API to analyze the logs, and generates a structured triage report.

### Jenkins Job Setup
*   **Job Type**: Pipeline (Declarative)
*   **SCM Source**: Configured to track this repository's `main` branch.
*   **Script Path**: `Jenkinsfile` in the project root.
*   **Credentials**:
    *   A Jenkins "Secret text" credential named `gemini-api-key` contains the Google Gemini API Key.
    *   The `Jenkinsfile` binds this key to the `GEMINI_API_KEY` environment variable using `withCredentials` strictly within the `AI Analysis` stage to keep the credential secure.

### How to Trigger Passing vs. Failing Builds
*   **Passing Build**: By default, `TOGGLE_TEST_FAILURE` and `VITE_TOGGLE_TEST_FAILURE` are set to `false` in the `environment` block of the `Jenkinsfile`. Triggering the build will run all tests, pass successfully, and skip the AI analysis stage.
*   **Failing Backend Build**: Set `TOGGLE_TEST_FAILURE = 'true'` in the `environment` block of the `Jenkinsfile` and push.
*   **Failing Frontend Build**: Set `VITE_TOGGLE_TEST_FAILURE = 'true'` in the `environment` block of the `Jenkinsfile` and push.
*   **Failing Both**: Set both env variables to `'true'` in the `Jenkinsfile` environment block and push.

### AI Triage Stage & Script Details
If either parallel test/lint stage fails, the pipeline transitions to the **AI Analysis** stage:
1.  Jenkins collects the failure info (e.g. `backend:test` or `frontend:test` / `frontend:lint`) and local log file paths (`backend/backend_test.log`, `frontend/frontend_lint.log`, `frontend/frontend_test.log`).
2.  Jenkins triggers `scripts/analyze_failure.py` passing the failure paths.
3.  The script extracts the log, queries Gemini, and writes a validated schema to `triage_report.json` which is archived as a build artifact and printed to the console.

### Cost & Guardrails Considerations (Built-In)
*   **Token Cap / Truncation**: To control API costs and stay within context limits, the script automatically truncates the logs, sending only the **last 200 lines** (approx. 6,000 characters).
*   **Cost Visibility**: The script prints log metrics (line counts and character counts) before making calls to keep API usage transparent and measurable.
*   **Timeout Protection**: The Gemini API request is configured with a **30-second timeout**.
*   **Graceful Fallback**: If the Gemini API fails, times out, or returns a malformed response, the script catches the error and writes a default fallback report matching the required JSON schema. The pipeline **does not crash** and the build's original failure state is preserved.
*   **Advisory-Only**: The AI stage never changes the build status; it is strictly advisory.

### Structured Output and JSON Schema Design Decision (For Interviews)
When explaining this project in interviews, you can highlight the following architectural decisions regarding the JSON schema:
1.  **Consistency**: Using a strict JSON schema via Pydantic (`TriageReport`) guarantees that the triage report matches a fixed model. This means automated tools, internal dashboards, or email alerts can reliably parse the report fields (`summary`, `likely_root_cause`, `severity`, `suggested_fix`, `affected_files`) without dealing with erratic plain-text formats.
2.  **LLM Constraint (Structured Outputs)**: By using Gemini's native `response_schema` configuration, the model is constrained at the decoding stage to output valid JSON matching our exact schema. This drastically reduces parsing errors compared to asking the LLM to write JSON in the prompt and attempting to parse the result.
3.  **Robust Fallbacks**: Combining Pydantic validation with a structural fallback ensures the pipeline remains deterministic even if the LLM's response is missing fields or fails constraints.

