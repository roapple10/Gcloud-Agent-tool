# GCP Agent

A powerful agent that can answer questions about weather, time, and Google Cloud Platform resources using the gcloud CLI.

<<<<<<< HEAD
## Prerequisites

- Python 3.8 or higher
- Google Cloud SDK installed and configured
- ADK (Agent Development Kit) installed

## Installing Google Cloud SDK (gcloud CLI)

The GCP Agent relies on the Google Cloud SDK to interact with Google Cloud resources. Follow these steps to install and configure it:

### Installation

1. Download the Google Cloud SDK installer:

   - **Windows**: Download the [installer](https://cloud.google.com/sdk/docs/install-sdk#windows)
   - **macOS**: Download the [installer](https://cloud.google.com/sdk/docs/install-sdk#mac)
   - **Linux**: Download the [installer](https://cloud.google.com/sdk/docs/install-sdk#linux)

2. Run the installer and follow the on-screen instructions.

3. Verify the installation by opening a new terminal window and running:

```bash
gcloud --version
```

You should see output showing the installed version of the Google Cloud SDK.

### Authentication and Configuration

1. Log in to your Google Cloud account:

```bash
gcloud auth login
```

This will open a browser window where you can log in with your Google account.

2. Set your default project:

```bash
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with the ID of your Google Cloud project.

3. Verify your configuration:

```bash
gcloud config list
```

This will show your active configuration, including the account and project.

For detailed instructions, refer to the [official Google Cloud SDK documentation](https://cloud.google.com/sdk/docs).

## Setup and Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd gcp_agent
```

2. Create and activate a virtual environment (optional but recommended):

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Configure the `.env` file:

An example configuration file is provided as `.env.example`. Copy this file to create your own `.env` file:

```bash
# On Windows
copy multi_tool_agent\.env.example multi_tool_agent\.env

# On macOS/Linux
cp multi_tool_agent/.env.example multi_tool_agent/.env
```

Then edit the `.env` file and replace the placeholder values with your actual Google API key:

```
GOOGLE_API_KEY=your_google_api_key_here
MODEL_NAME=gemini-2.0-flash
GCLOUD_PATH=path_to_your_gcloud_executable
```

For the `GCLOUD_PATH`, you need to provide the full path to your gcloud executable:
- On Windows: `C:\Users\YOUR_USERNAME\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`
- On macOS/Linux: `/usr/local/bin/gcloud` (or the path from `which gcloud`)

## Running the Agent

1. Activate the environment variables:

```bash
# On Windows (PowerShell)
cd multi_tool_agent
$env:GOOGLE_API_KEY="your_google_api_key_here"  # Replace with your actual Google API key
$env:MODEL_NAME="gemini-2.0-flash"

# On macOS/Linux
cd multi_tool_agent
export GOOGLE_API_KEY=your_google_api_key_here  # Replace with your actual Google API key
export MODEL_NAME=gemini-2.0-flash
```

2. Start the ADK web interface:

```bash
adk web
```

This will start a local web server, typically at http://localhost:8080. Open this URL in your browser to interact with the agent.

## Features

The GCP Agent provides information about:

1. **Weather Information**: Get current weather for specific cities (currently only supports New York).
2. **Time Information**: Get current time for specific cities (currently only supports New York).
3. **GCP Resources**: Interact with Google Cloud Platform using natural language or gcloud-style commands.

### GCP Tool Functionality

The `gcp_tool` function allows you to query GCP resources using either natural language or gcloud CLI syntax:

- List GCP projects
- List compute instances
- List storage buckets
- Describe projects
- List GCP regions
- List GCP zones
- List GCP services
- List billing accounts
- Link billing accounts to projects
- List BigQuery datasets
- List BigQuery tables in a dataset

## Example Questions

### Weather and Time

- "What's the weather in New York?"
- "What time is it in New York?"

### GCP Resources (Natural Language Format)

- "List all GCP projects"
- "Show me my compute instances"
- "List all storage buckets"
- "Describe project PROJECT_ID"
- "List all GCP regions"
- "List all zones"
- "List services in project PROJECT_ID"
- "List billing accounts"
- "Link billing account BILLING_ACCOUNT_ID to project PROJECT_ID"
- "Set billing account BILLING_ACCOUNT_ID for project PROJECT_ID"
- "Connect billing account BILLING_ACCOUNT_ID to project PROJECT_ID"
- "Show BigQuery datasets"
- "List BigQuery datasets in project PROJECT_ID"
- "Show BigQuery tables in dataset DATASET_NAME"
- "Show BigQuery tables in dataset DATASET_NAME in project PROJECT_ID"

### GCP Resources (gcloud CLI Format)

- "gcloud projects list"
- "gcloud compute instances list"
- "gcloud storage ls"
- "gcloud projects describe PROJECT_ID"
- "gcloud compute regions list"
- "gcloud compute zones list"
- "gcloud services list --project=PROJECT_ID"
- "gcloud billing accounts list"
- "gcloud billing projects link PROJECT_ID --billing-account=BILLING_ACCOUNT_ID"
- "bq ls"
- "bq ls --format=json"
- "bq ls DATASET_NAME"
- "bq ls --project=PROJECT_ID DATASET_NAME"

## Testing

You can test the GCP tool directly using the test scripts:

```bash
# Test natural language and gcloud CLI formats
python test/test_gcp_formats.py

# Test various GCP queries
python test/test_gcp.py
```

## Customization

The agent can be extended to support additional GCP commands by modifying the `gcp_tool` function in `agent.py`.

## Troubleshooting

- Make sure Google Cloud SDK is installed and in your PATH
- Ensure you are authenticated with gcloud (`gcloud auth login`)
- Check that the correct project is selected (`gcloud config set project PROJECT_ID`)
- Make sure the `GCLOUD_PATH` in your `.env` file points to the correct location of your gcloud executable:

```bash
# To find your gcloud path:
# On Windows:
where gcloud

# On macOS/Linux:
which gcloud
```

- If you don't set the `GCLOUD_PATH` environment variable, the agent will fall back to a default path, which may not work on your system

=======
[... rest of README content ...]
>>>>>>> fbb49d5424923038e9a283c41b3687d9d2cae89b
