import { defineRailway, github, project, service } from "railway/iac";

export default defineRailway(() => {
  const backend = service("backend", {
    source: github("TerryMinal/treasury-take-home", {
      branch: "main",
      rootDirectory: "backend",
    }),
    healthcheck: "/health",
    env: {
      RAILWAY_DOCKERFILE_PATH: "/backend/Dockerfile",
    },
  });

  const frontend = service("frontend", {
    source: github("TerryMinal/treasury-take-home", {
      branch: "main",
      rootDirectory: "frontend",
    }),
    build: "pnpm build",
    start: "pnpm start",
    env: {
      NODE_ENV: "production",
      BACKEND_PRIVATE_BASE_URL: "http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}",
    },
  });

  return project("treasury-take-home", {
    resources: [backend, frontend],
  });
});
