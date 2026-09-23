# Cloud Deployment

## Recommended free setup

Deploy the repository with `render.yaml` in Render:

1. Push this repository to GitHub.
2. In Render, choose **New -> Blueprint** and select the repository.
3. Deploy both services.
4. Copy the frontend URL into the API service `CORS_ORIGINS` value.
5. Copy the API URL, including `/api`, into the frontend `VITE_API_URL` value.
6. Redeploy the frontend.

The frontend URL can then be opened from any phone or computer.

## Important free-tier limits

Render's free web service sleeps after inactivity and has monthly usage limits. It is free, but it is not guaranteed to run continuously. The SQLite database on a free service is also not durable across every redeploy or service restart, so this setup is suitable for testing and light personal use, not production history retention.

For genuinely continuous operation, use an always-on VM such as Oracle Cloud Always Free or a low-cost VPS, attach persistent storage, and run the same `backend/Dockerfile`. No free hosted option can promise unlimited uptime, storage, and outbound data fetching.

## Required production settings

Set a long random `SECRET_KEY` on the API service. Keep `DATA_PROVIDER=betpawa` and set `CORS_ORIGINS` to the exact frontend origin, without a trailing slash.