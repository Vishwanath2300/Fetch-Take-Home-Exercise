### Endpoint Monitoring Service (Python)

This application monitors the availability of HTTP endpoints defined in a YAML configuration file. It periodically checks each endpoint and reports on their availability by domain.

## Installation

# Prerequisites

- Python 3.6 or later
- pip (Python package manager)

# Steps to Install

1. Clone the repository:

   ```
   git clone https://github.com/Vishwanath2300/Fetch-Take-Home-Exercise.git
   cd fetch
   ```

2. Install below dependencies:
   ```
   pip install requests pyyaml
   ```

## Running the Application

1. Create a YAML file with your endpoints configuration (see sample format below)
   **2** Run the application:
   ```
   python monitor.py sample.yaml
   ```

## Below is th e Sample YAML file

```yaml
- name: sample index up
  url: https://example.com/
  method: GET

- name: sample post endpoint
  url: https://example.com/api
  method: POST
  headers:
    content-type: application/json
  body: '{"key":"value"}'
```

# Issues Identified and Fixes Implemented

1.  Domain Extraction Issues
    Issue: The original code used string splitting to extract domains, which is error-prone and didn't handle port numbers correctly.
    Fix: Used Python's `urllib.parse` library to properly parse URLs and extract domains, while ignoring port numbers.

2.  Body Handling
    Issue: The code wasn't properly handling request bodies based on content type.
    Fix: Added logic to process the body correctly based on content type headers, ensuring JSON is sent as JSON and other data as raw.

3.  Response Time Requirement
    Issue: The original code didn't measure response time and didn't enforce the 500ms response time requirement.
    Fix: Added request timing and enforced the requirement that endpoints must respond in 500ms or less to be considered available.

4.  Thread Safety Issues
    Issue: The stats dictionary was accessed concurrently without proper synchronization.
    Fix: Implemented thread-safe counters using threading.Lock to ensure data integrity during concurrent operations.

5.  Concurrent Endpoint Checking
    Issue: Endpoints were checked sequentially, which could cause delays in the check cycle.
    Fix: Used Python's `concurrent.futures` to check endpoints in parallel, improving efficiency.

6.  Regular Checking Cycles
    Issue: The original implementation didn't guarantee that checks would happen every 15 seconds regardless of endpoint response times.
    Fix: Restructured the monitoring loop to maintain a consistent 15-second interval between check cycles.

7.  Timeout Handling
    Issue: No request timeouts were set, which could cause the application to hang on slow endpoints.
    Fix: Added a 500ms timeout parameter to requests to ensure they don't exceed the required response time.

8.  Error Handling
    Issue: Limited error handling and logging throughout the application.
    Fix: Added comprehensive error handling with try/except blocks and improved logging for better debugging.

9.  Default HTTP Method
    Issue: If no method was specified in the YAML, the code would still try to make a request with an empty method.
    Fix: Set a default method (GET) when none is specified.

10. Initial Check Delay
    Issue: The original code would wait 15 seconds before performing the first check.
    Fix: The application now performs an immediate check on startup, followed by regular 15-second intervals.

11. Empty Stats Handling
    Issue: Potential division by zero if no checks had been performed yet.
    Fix: Added safeguards to handle cases where total count is zero.

12. Reporting Enhancement
    Issue: Basic availability reports lacked detail and timestamp information.
    Fix: Enhanced reporting to include timestamps and actual success/total counts for better monitoring.

# Technical Decisions

1. URL Parsing: Used Python's built-in `urllib.parse` library for more robust URL handling rather than custom string splitting.

2. Concurrency Model: Chose `ThreadPoolExecutor` for concurrent endpoint checking since the operations are I/O bound.

3. Thread Safety: Used fine-grained locks within the DomainStats class to allow concurrent updates while preventing race conditions.

4. Error Handling: Implemented comprehensive exception handling to ensure the application continues running even when individual endpoint checks fail.

5. Data Structuring: Used a class-based approach for better organization and encapsulation of the monitoring logic.

6. Content Type Handling: Added smart handling of request bodies based on content-type headers to ensure proper API interactions.

# Future Improvements

1. Add configurable timeout and interval settings via command line arguments
2. Implement persistent storage for historical availability data
3. Add a web interface or dashboard for monitoringa
4. Include more detailed error categorization and reporting
5. Create alerting mechanisms for extended downtime
6. Add support for authentication methods like OAuth or API keys
7. Implement retries for failed requests with exponential backoff
