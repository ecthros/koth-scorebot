import http.server
import socketserver
import json
import signal
import sys
import threading
import time
from urllib.parse import parse_qs, urlparse

# Define the port for the server
PORT = 8000

# Global array for scores
scores = [["Team A", 0], ["Team B", 0]]

# List of IP addresses for machines
machines = ["192.168.0.4", "192.168.0.5"]

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Handle GET requests
        if self.path.startswith('/details'):
            self.handle_details_page()  # Handle details page request
        elif self.path == '/scores':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # Send scores as JSON
            self.wfile.write(json.dumps(scores).encode())
        else:
            # Serve the main scoreboard HTML
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())

    def get_html(self):
        # Generate HTML for the scoreboard page
        machines_html = ''.join(
            f'<p><i class="fas fa-desktop"></i> <a href="/details?IP={ip}" class="machine-link">{ip}</a></p>' for ip in machines
        )
        
        # Return complete HTML structure for the page
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Live Scoreboard</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4; /* Light mode background */
                    color: #333; /* Light mode text color */
                    margin: 0;
                    padding: 20px;
                    transition: background-color 0.3s, color 0.3s; /* Smooth transition */
                }}
                h1 {{
                    color: #4CAF50; 
                }}
                body.dark {{
                    background-color: #181818; /* Dark mode background */
                    color: #f4f4f4; /* Dark mode text color */
                }}
                #scoreboard {{
                    background: #fff; /* Light mode scoreboard background */
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    transition: background-color 0.3s; /* Smooth transition for background */
                }}
                body.dark #scoreboard {{
                    background: #2c2c2c; /* Dark mode scoreboard background */
                }}
                #machines {{
                    margin-top: 20px;
                }}
                .machine-link {{
                    text-decoration: none; 
                    color: #007BFF; 
                    font-weight: bold; 
                    border-bottom: 1px dotted;
                }}
                .machine-link:hover {{
                    color: darkblue;
                }}
                button {{
                    background-color: transparent; 
                    color: #333; /* Light mode button text */
                    border: 2px solid #333; /* Light mode button border */
                    padding: 10px 15px; 
                    border-radius: 5px; 
                    cursor: pointer; 
                    position: absolute;
                    top: 20px;
                    right: 20px; /* Position for the Toggle Dark Mode button */
                    transition: background-color 0.3s, color 0.3s;
                }}
                body.dark button {{
                    color: white; /* Dark mode button text */
                    border-color: white; /* Dark mode button border */
                }}
                button:hover {{
                    background-color: #4CAF50; 
                    color: white; 
                }}
            </style>
            <script>
                // Function to fetch scores from the server
                function fetchScores() {{
                    fetch('/scores')
                        .then(response => response.json())
                        .then(data => {{
                            data.sort((a, b) => b[1] - a[1]); // Sort scores in descending order
                            const scoreboard = document.getElementById('scoreboard');
                            scoreboard.innerHTML = ''; // Clear existing scores
                            data.forEach(([team, score]) => {{
                                scoreboard.innerHTML += `<p>${{team}}: ${{score}}</p>`; // Display scores
                            }});
                        }});
                }}

                // Function to toggle dark mode
                function toggleDarkMode() {{
                    document.body.classList.toggle('dark'); // Toggle dark class
                    const isDark = document.body.classList.contains('dark');
                    localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled'); // Save user preference
                }}

                // Load user preference on page load
                window.onload = () => {{
                    const savedMode = localStorage.getItem('darkMode');
                    if (savedMode === 'enabled') {{
                        toggleDarkMode(); // Activate dark mode if previously set
                    }}
                    fetchScores(); // Fetch and display scores
                }};
            </script>
        </head>
        <body>
            <h1>Live Scoreboard</h1>
            <div id="scoreboard"></div> <!-- Container for scores -->
            <h2>Machines</h2>
            <div id="machines">{machines_html}</div> <!-- List of machines -->
            <button id="darkModeToggle" onclick="toggleDarkMode()">Toggle Dark Mode</button> <!-- Dark mode toggle button -->
        </body>
        </html>
        """

    def handle_details_page(self):
        # Parse the URL to extract the IP address parameter
        parsed_path = urlparse(self.path)
        ip_address = parse_qs(parsed_path.query).get('IP', [None])[0]
        
        if ip_address in machines:
            # Simulate machine's online status and port status
            online = "yes" if ip_address in machines else "no"
            port_80_status = "open" if ip_address == "192.168.0.4" else "closed"
            port_443_status = "open" if ip_address == "192.168.0.5" else "closed"

            # Set CSS classes based on the machine's status
            online_class = "online" if online == "yes" else "offline"
            port_80_class = "online" if port_80_status == "open" else "offline"
            port_443_class = "online" if port_443_status == "open" else "offline"

            # Generate the HTML response for the details page
            response = f"""
            <html>
            <head>
                <link rel="stylesheet" href="all.min.css">  <!-- Local version -->
                <style>
                    body {{
                        font-family: Arial, sans-serif; 
                        background-color: #f4f4f4; 
                        padding: 20px;
                        transition: background-color 0.3s, color 0.3s; /* Smooth transition */
                    }}
                    body.dark {{
                        background-color: #181818;
                        color: #f4f4f4; /* Dark mode text color */
                    }}
                    h1 {{
                        color: #4CAF50; 
                    }}
                    #details {{
                        background: #fff; 
                        border-radius: 8px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                        transition: background-color 0.3s; 
                    }}
                    body.dark #details {{
                        background: #2c2c2c; 
                    }}
                    .status {{
                        font-weight: bold;
                        font-size: 18px;
                        margin: 10px 0;
                    }}
                    .online {{ color: green; }}
                    .offline {{ color: red; }}
                    button {{
                        background-color: transparent; 
                        color: #333; 
                        border: 2px solid #333; 
                        padding: 10px 15px; 
                        border-radius: 5px; 
                        cursor: pointer; 
                        position: absolute;
                        top: 20px;
                        transition: background-color 0.3s, color 0.3s;
                    }}
                    button.back {{
                        right: 170px; /* Adjusted space for the Back button */
                    }}
                    button.toggle {{
                        right: 20px; /* Position for the Toggle Dark Mode button */
                    }}
                    body.dark button {{
                        color: white; 
                        border-color: white; 
                    }}
                </style>
                <script>
                    // Function to toggle dark mode
                    function toggleDarkMode() {{
                        document.body.classList.toggle('dark');
                        const isDark = document.body.classList.contains('dark');
                        localStorage.setItem('darkMode', isDark ? 'enabled' : 'disabled');
                    }}

                    // Load user preference on page load
                    window.onload = () => {{
                        const savedMode = localStorage.getItem('darkMode');
                        if (savedMode === 'enabled') {{
                            toggleDarkMode(); // Activate dark mode if previously set
                        }}
                    }};
                </script>
            </head>
            <body>
                <h1>Details for {ip_address}</h1>
                <div id="details">
                    <p class="status {online_class}">Online: {online}</p>
                    <p class="status {port_80_class}">Port 80: {port_80_status}</p>
                    <p class="status {port_443_class}">Port 443: {port_443_status}</p>
                </div>
                <button class="back" onclick="window.location.href='/'">Back to Scoreboard</button> <!-- Back button -->
                <button class="toggle" onclick="toggleDarkMode()">Toggle Dark Mode</button> <!-- Dark mode toggle button -->
            </body>
            </html>
            """
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(response.encode())
        else:
            self.send_response(400)  # Invalid IP address
            self.end_headers()
            self.wfile.write(b"Invalid IP address.")

def signal_handler(sig, frame):
    # Handle server shutdown signal
    print("\nShutting down the server...")
    shutdown_event.set()

def run_server():
    # Start the TCP server
    with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
        print(f"Serving at port {PORT}")
        while not shutdown_event.is_set():
            httpd.handle_request()  # Handle requests
        print("Server has been shut down.")

def main():
    global shutdown_event
    shutdown_event = threading.Event()  # Event for signaling shutdown

    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start the server in a separate thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    try:
        while not shutdown_event.is_set():
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        pass  # Graceful exit on Ctrl+C

    server_thread.join()  # Wait for server thread to finish
    print("Main program terminated.")

if __name__ == "__main__":
    main()  # Start the application
