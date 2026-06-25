import { defineRailway, github, project, service } from "railway/iac";

export default defineRailway(() => {
  const backend = service("backend", {
    source: github("TerryMinal/treasury-take-home", {
      branch: "main",
    }),
    healthcheck: "/health",
    env: {
      RAILWAY_DOCKERFILE_PATH: "/backend/Dockerfile",
    },
  });

  const frontend = service("frontend", {
    source: github("TerryMinal/treasury-take-home", { branch: "main" }),
    build: "pnpm --dir frontend build",
    start: "pnpm --dir frontend start",
    env: {
      NODE_ENV: "production",
      BACKEND_PRIVATE_BASE_URL: "http://${{backend.RAILWAY_PRIVATE_DOMAIN}}:${{backend.PORT}}",
    },
  });

  return project("treasury-take-home", {
    resources: [backend, frontend],
  });
});
