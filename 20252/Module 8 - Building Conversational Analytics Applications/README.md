# Conversational Analytics Application

A multi-agent conversational analytics system that allows users to upload CSV files and ask questions about their data using natural language. The application uses multiple AI agents to provide comprehensive data analysis and insights.

## Features

- **Natural Language Queries**: Ask questions about your data in plain English
- **Speech Input**: Use voice commands to interact with the system
- **Multi-Agent Analysis**: Sophisticated analysis using specialized AI agents
- **Real-time Results**: Get insights immediately
- **Educational**: Learn about data analysis and AI agents
- **Browser-based**: No complex setup required

## AI Agents

The system uses five specialized AI agents:

1. **Manager Agent**: Orchestrates the analysis workflow and coordinates other agents
2. **Data Cleaner Agent**: Identifies and fixes data quality issues
3. **Analyst Agent**: Performs statistical analysis and generates insights
4. **Code Executor Agent**: Generates and executes Python code for analysis
5. **Report Writer Agent**: Creates comprehensive reports and summaries

## Technology Stack

- **Frontend**: Streamlit
- **AI Framework**: CrewAI
- **LLM**: Google Gemini
- **Data Processing**: Pandas, NumPy
- **Speech Recognition**: Browser-based Web Speech API
- **Visualization**: Plotly, Seaborn, Matplotlib

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key (free tier available)
- Modern web browser (Chrome, Edge, Firefox)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd conversational_analytics
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your Gemini API key:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Run the Application

```bash
streamlit run frontend/app.py
```

The application will open in your browser at `http://localhost:8501`.

## Usage Guide

### 1. Upload Data
- Go to the "Upload Data" tab
- Upload a CSV or Excel file
- The system will automatically analyze the data structure

### 2. Ask Questions
- Switch to the "Ask Questions" tab
- Type your question in natural language
- Examples:
  - "What is the average salary by department?"
  - "Show me the correlation between age and salary"
  - "Create a visualization of performance scores"

### 3. Use Speech Input
- Go to the "Speech Input" tab
- Click "Start Recording" and speak your question
- The system will transcribe and process your question

### 4. View Results
- Analysis results are displayed in organized sections
- View executive summaries, insights, and detailed reports
- Access generated Python code and execution results

## Example Data

The application includes sample data in the `examples/` directory:
- `sample_data.csv`: Employee dataset with salary, department, and performance data
- `test_questions.md`: Sample questions to test the system

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `DEBUG` | Enable debug mode | False |
| `DEFAULT_MODEL` | Gemini model to use | gemini-pro |

### Customization

You can customize the application by modifying:
- Agent behavior in `backend/agents/`
- UI components in `frontend/components/`
- Data processing logic in `backend/utils/`

## Educational Value

This application is designed for educational purposes to help students learn about:

- **Multi-Agent AI Systems**: How different AI agents work together
- **Data Analysis Workflows**: End-to-end data analysis processes
- **Natural Language Processing**: Converting questions to analysis tasks
- **Conversational AI**: Building interactive AI interfaces
- **Data Science**: Practical data analysis techniques

## Project Structure

```
conversational_analytics/
├── backend/
│   ├── agents/           # AI agents
│   ├── utils/            # Utility modules
│   └── main.py           # Main backend logic
├── frontend/
│   ├── components/       # UI components
│   ├── utils/           # Frontend utilities
│   └── app.py           # Streamlit app
├── examples/            # Sample data and questions
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is correctly set in the `.env` file
2. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`
3. **File Upload Issues**: Check that your CSV file is properly formatted
4. **Speech Recognition**: Use Chrome or Edge for best speech recognition support

### Debug Mode

Enable debug mode by setting `DEBUG=True` in your `.env` file for detailed logging.

## Contributing

This is an educational project. Contributions are welcome for:
- Additional agent capabilities
- UI improvements
- Documentation enhancements
- Bug fixes

## License

This project is for educational purposes. Please respect the terms of service for all third-party APIs used.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the example data and questions
3. Contact your instructor or course administrator

## Updates

- **v1.0.0**: Initial release with basic multi-agent functionality
- **v1.1.0**: Added speech input capabilities
- **v1.2.0**: Enhanced UI and error handling

---
