# Architecture

## Overview

``` text
SvelteKit Frontend
        │
        ▼
 FastAPI REST API
        │
        ▼
   Service Layer
        │
        ▼
     Database
```

## Frontend

Suggested structure:

-   routes/
-   lib/components/
-   lib/api/
-   lib/stores/
-   lib/utils/

Keep components focused and reusable.

## Backend

Suggested structure:

-   api/
-   services/
-   models/
-   schemas/
-   dependencies/
-   database/

Keep route handlers thin. Business logic belongs in services.

## Design Principles

-   Validate input at the API boundary.
-   Use Pydantic models for request/response schemas.
-   Keep frontend and backend API contracts in sync.
-   Favor composition over deep inheritance.
-   Separate presentation, business logic, and persistence.
