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
      BODY_SIZE_LIMIT: "10M",
      BACKEND_PRIVATE_BASE_URL: `http://${backend.env.RAILWAY_PRIVATE_DOMAIN}:${backend.env.PORT}`,
    },
  });

  return project("treasury-take-home", {
    resources: [backend, frontend],
  });
});
