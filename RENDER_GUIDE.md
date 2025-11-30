# How to Deploy "Kallanum Policum" on Render

## Prerequisites
1.  **GitHub Account**: You need to push your code to a GitHub repository.
2.  **Render Account**: Sign up at [render.com](https://render.com).

## Step 1: Push Code to GitHub
1.  Create a new repository on GitHub.
2.  Open your terminal in the project folder (`d:\game kallan\kallanum_policum`).
3.  Run these commands:
    ```bash
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
    git branch -M main
    git remote add origin <YOUR_GITHUB_REPO_URL>
    git push -u origin main
    ```

## Step 2: Create a Blueprint on Render
1.  Go to your [Render Dashboard](https://dashboard.render.com/).
2.  Click **"New +"** and select **"Blueprint"**.
3.  Connect your GitHub account and select the repository you just created.
4.  Render will automatically detect the `render.yaml` file.
5.  Click **"Apply"**.

## Step 3: Wait for Deployment
- Render will:
    - Create a database (PostgreSQL).
    - Build your Python app.
    - Run the migrations.
    - Start the server using `daphne`.
- This process usually takes 2-3 minutes.

## Step 4: Play!
- Once deployed, Render will give you a URL (e.g., `https://kallanum-policum.onrender.com`).
- Share this link with your friends to play!

## Troubleshooting
- **"Server Error (500)"**: Check the logs in the Render dashboard.
- **"WebSocket Error"**: Ensure you are using `wss://` (secure WebSocket) if your site is `https://`. The code automatically handles this, but some networks block WebSockets.
