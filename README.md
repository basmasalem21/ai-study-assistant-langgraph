# AI Assistant with LangGraph

An intelligent AI assistant web application built with Streamlit and LangGraph that provides web search, YouTube video retrieval, and mind map generation capabilities.

## Features

- **Chat Interface**: Interactive chat interface with session management
- **Web Search**: Search the web for information using DuckDuckGo
- **YouTube Video Retrieval**: Find relevant YouTube videos based on topics
- **Mind Map Generation**: Create visual mind maps from uploaded text files
- **Session Memory**: Maintains conversation history across sessions
- **Tool Integration**: Uses LangGraph for intelligent tool routing

## Tech Stack

- **Frontend**: Streamlit
- **AI/ML**: 
  - LangGraph (agent orchestration)
  - LangChain (LLM framework)
  - OpenRouter API (GPT model)
  - Weaviate (vector database)
  - Sentence Transformers (embeddings)
- **Tools**:
  - DuckDuckGo Search
  - YouTube Data API
  - Graphviz (mind map visualization)

## Installation

### Prerequisites

- Python 3.14 or higher
- uv package manager (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd web scraping
```

2. Install dependencies using uv:
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root:
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

4. Run the application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Chat Interface

- Type your message in the chat input
- The AI will respond using appropriate tools based on your query
- Conversation history is maintained per session

### Web Search

Simply ask the AI to search for information:
```
"Search for the latest developments in AI"
```

### YouTube Videos

Request videos on a specific topic:
```
"Find videos about machine learning tutorials"
```

### Mind Map Generation

1. Upload a text file using the file uploader
2. Click "Generate Mindmap" button
3. View and download the generated mind map image

## Project Structure

```
.
├── app.py                      # Streamlit web interface
├── main.py                     # LangGraph agent configuration
├── retrieval_tool.py           # YouTube video retrieval
├── embedding_storing_data.py   # Vector database setup
├── DataIngestion.py            # Data ingestion utilities
├── Tools/
│   ├── web_search.py          # Web search tool
│   ├── gen2.py                # Mind map generation
│   ├── mindmap_tool.py        # Mind map utilities
│   └── youtube_videos_search.py # YouTube search
├── Data/                       # Data storage directory
├── output/                     # Generated outputs
└── pyproject.toml             # Project dependencies
```

## Configuration

### Model Settings

The application uses OpenRouter's GPT model by default. You can modify the model in `main.py`:

```python
model = ChatOpenRouter(
    model="openai/gpt-oss-120b:free",
    temperature=0.7,
    api_key=OPENROUTER_API_KEY,
)
```

### Tool Routing

The agent automatically routes to appropriate tools based on user queries:
- Video-related queries → `retrieval_tool`
- Web search queries → `search`
- Mind map requests → `create_mindmap`

## Environment Variables

- `OPENROUTER_API_KEY`: Required for accessing the LLM via OpenRouter

## Development

### Adding New Tools

1. Create a new tool function in `main.py` with the `@tool` decorator
2. Add the tool to the `tools` list
3. Update the system prompt if needed

### Modifying the Agent

The agent logic is defined in `main.py`:
- `AgentNode`: Main agent processing logic
- `should_continue`: Routing logic for tool calls
- `StateGraph`: Graph structure for the agent

## License

This project is provided as-is for educational and research purposes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
