<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Curl Requester</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #ecf0f1;
      color: #2c3e50;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 2rem;
    }
    .container {
      max-width: 800px;
      width: 100%;
      background: white;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 2rem;
    }
    input, select, button, textarea {
      width: 100%;
      margin-bottom: 1rem;
      padding: 0.75rem;
      border: 1px solid #ccc;
      border-radius: 8px;
      font-size: 1rem;
    }
    button {
      background-color: #1abc9c;
      color: white;
      cursor: pointer;
      border: none;
      transition: background 0.3s ease;
    }
    button:hover {
      background-color: #16a085;
    }
    .response {
      white-space: pre-wrap;
      background: #f4f4f4;
      border-radius: 8px;
      padding: 1rem;
      font-family: monospace;
      font-size: 0.9rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Curl Requester</h1>
    <input type="text" id="urlInput" placeholder="Enter URL"/>
    <button id="sendBtn">Send Request</button>
    <div class="response" id="responseArea">Response will appear here</div>
  </div>

  <script>
    document.getElementById('sendBtn').addEventListener('click', async () => {
    const url = document.getElementById('urlInput').value;
    const responseArea = document.getElementById('responseArea');

    if (!url) {
      responseArea.textContent = 'Please enter a URL.';
      return;
    }

    responseArea.textContent = 'Sending request...';

    try {
      const res = await fetch('/curl.php', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `url=${encodeURIComponent(url)}`
      });

      const contentType = res.headers.get("Content-Type");
      if (contentType && contentType.includes("application/json")) {
        const data = await res.json();

        responseArea.textContent =
          (data.status ? `Status: ${data.status}\n` : '') +
          (data.headers ? `Headers: ${data.headers}\n\n` : '') +
          (data.response || data.error || 'No response');
      } else {
        const text = await res.text();
        responseArea.textContent = `Unexpected response:\n\n${text}`;
      }
    } catch (err) {
      responseArea.textContent = 'Request failed: ' + err.message;
    }
  });

  </script>
</body>
</html>
