# Sherlock Assistant

![Sherlock Assistant Logo](sherlock_logo.png)

Sherlock Assistant is a Retrieval-Augmented Generation (RAG) application designed to process, manage, and analyze investigative case files. The system fhas a modular architecture comprising a FastAPI backend, an interactive Streamlit frontend, and an integrated RAG engine leveraging ChromaDB and OpenAI models.

## Project Architecture

The application is structured into isolated modules to maintain a clean separation of concerns:

- **src/backend**: Contains the FastAPI REST API engine responsible for handling document submission, tracking session metadata, and managing case deletions.
- **src/frontend**: Houses the Streamlit dashboard, providing an interactive UI for document upload, inventory verification, and an interactive chat feed interface.
- **src/rag**: Implements text extraction via PyPDF, embedding generation, and contextual semantic search execution with ChromaDB.

## Directory Layout

```text
sherlock_assistant/
│
├── requirements.txt
├── docker-compose.yml
├── sherlock_logo.png
├── .env
│
└── src/
    ├── backend/
    │   ├── Dockerfile
    │   └── main.py
    ├── frontend/
    │   ├── Dockerfile
    │   └── app.py
    └── rag/
        └── rag_engine.py
```

## Prerequisites

Ensure the following environments and accounts are set up before starting installation:

1. **Docker Desktop**: Download and install Docker Desktop for your operating system. Ensure the engine is fully running before executing build commands.
2. **OpenAI API Platform**: An active OpenAI API account with sufficient credits to access structural text embedding models and completion endpoints.

## Configuration

The application utilizes environment variables to securely pass sensitive API credentials to the decoupled services.

1. Navigate to the root directory of the project (`sherlock_assistant/`).
2. Create a file named `.env` in this directory.
3. Define your OpenAI configuration key within the file exactly as follows:

```env
OPENAI_API_KEY=your_actual_openai_api_key_here
```

## Installation and Execution

You will first need to clone this repository:

```powershell
git clone https://github.com/sntsaax/sherlock_assistant.git
```

The entire ecosystem is orchestrated using Docker Compose, combining dependencies, networking, and volume storage into a single build process.

1. Launch your terminal application (e.g., PowerShell, Command Prompt, or Bash) and change directories to the root of the project (That being, wherever you decided to clone it into):

```powershell
cd C:\Users\user\sherlock_assistant
```

2. Execute the unifed compilation and initialization command:

```powershell
docker-compose up --build
```

3. Docker will automatically pull the necessary base Python images, download the shared requirements list, configure internal networking bridges, and start up both service endpoints.

4. To verify that both containers are actively running in the background, open a separate terminal window and execute:

```powershell
docker ps
```

## Accessing the Interfaces

Once the initialization sequence is complete, the individual layers of the application can be accessed via your web browser:

### Interactive Frontend Dashboard
- **URL**: http://localhost:8501
- **Description**: The primary user interface. Allows uploading case documents (.txt and .pdf), viewing uploaded case metadata inventories, deleting obsolete cases, and interacting with specific document contexts through a vertical chat container interface.

### REST API Swagger Documentation
- **URL**: http://localhost:8000/docs
- **Description**: The interactive Swagger UI generated automatically by FastAPI. This interface can be used to manually test endpoints (`POST /documents`, `GET /documents`, `DELETE /documents/{case_id}`, and `POST /query`) with full multi-part binary file streaming support.

## Troubleshooting

### Named Pipe Connection Error
If the terminal yields an error regarding `//./pipe/dockerDesktopLinuxEngine`, Docker Desktop is either suspended or not actively running. Ensure the Docker Desktop application is open and wait for the system tray whale icon to turn solid green before running your commands.

### Missing Dependency Failures
If a service fails due to missing modules, ensure that all third-party libraries ( `pypdf`, ot `watchfiles`) are correctly defined inside the unified `requirements.txt` file located in the root directory before running the build step with the `--build` flag. Though this should not happen, since requirements.txt already has these modules.

### Terminating Docker Process
If you wish to terminate the Docker Containers, you can run the following command:

```powershell
docker-compose down
```

## Observations
- The application does NOT save items in the cloud, so any submitted documents will only be available during the session. If the session is terminated and restarted, the documents will not be available anymore.

- The user MUST select the specific case they want to ask questions about, it is not globalised to handle accessing too many different documents at the same time because of cost and efficiency concerns.

- The chatbot is ONLY available for use once the user has submitted at least ONE case file.

- The application does NOT support reading of files within its UI; if user needs to verify responses, they must manually check the file on their respective local designated program.

- This repository includes two example-files generated with AI in order to test the chatbot, feel free to use your own files.

- The chatbot is configured to ONLY be able to answer questions related to the preselected case, it is NOT a usual chatbot.