# Requirements Document

## Introduction

The Multi-Agent Research Assistant is a learning and portfolio project that demonstrates agent orchestration by coordinating three specialized AI agents (Researcher, Analyst, Writer) to research topics and produce comprehensive reports. The system uses a sequential pipeline where each agent performs a specific role: gathering information, analyzing insights, and writing reports. This project showcases modern "agentic AI" architectural patterns in a runnable Python application that will evolve from CLI to a web-based interface.

## Glossary

- **Orchestrator**: The central coordination component that manages agent execution order, data flow between agents, and error handling
- **Researcher_Agent**: The first agent in the pipeline responsible for gathering raw information about a given topic
- **Analyst_Agent**: The second agent that synthesizes research notes into key insights and patterns
- **Writer_Agent**: The third agent that produces a polished report from insights
- **Pipeline**: The sequential execution flow from user input through all three agents to final output
- **System**: The complete Multi-Agent Research Assistant application
- **API_Provider**: The Claude API service from Anthropic used for LLM calls
- **Research_Notes**: Bullet-point list of facts, trends, and data points output by Researcher_Agent
- **Insights**: Numbered list of 3 most important patterns or implications output by Analyst_Agent
- **Final_Report**: 3-4 paragraph report for non-expert readers output by Writer_Agent
- **Topic**: User-provided string describing the subject to research

## Requirements

### Requirement 1: Pipeline Orchestration

**User Story:** As a user, I want the system to coordinate all three agents in sequence, so that I receive a complete research report without manual intervention.

#### Acceptance Criteria

1. WHEN a user provides a topic THEN THE Orchestrator SHALL execute Researcher_Agent, Analyst_Agent, and Writer_Agent in that exact order
2. WHEN Researcher_Agent completes THEN THE Orchestrator SHALL pass the Research_Notes to Analyst_Agent
3. WHEN Analyst_Agent completes THEN THE Orchestrator SHALL pass both the Topic and Insights to Writer_Agent
4. WHEN Writer_Agent completes THEN THE Orchestrator SHALL present the Final_Report to the user
5. WHEN the Pipeline executes THEN THE System SHALL display all intermediate outputs (Research_Notes, Insights, Final_Report) to the user

### Requirement 2: Researcher Agent Functionality

**User Story:** As a user, I want the Researcher agent to gather comprehensive information about my topic, so that subsequent analysis is based on solid factual foundations.

#### Acceptance Criteria

1. WHEN Researcher_Agent receives a Topic THEN THE Researcher_Agent SHALL generate Research_Notes as a bullet-point list
2. THE Researcher_Agent SHALL use the system prompt "You are a Research Agent. Given a topic, list the key facts, trends, and data points relevant to it. Be factual and concise. Output as a bullet list."
3. WHEN Researcher_Agent produces an empty or very short response (less than 50 characters) THEN THE System SHALL retry once with an enhanced prompt requesting "at least 5 distinct points"
4. WHEN Researcher_Agent completes successfully THEN THE Research_Notes SHALL contain factual and concise information relevant to the Topic
5. WHEN Researcher_Agent fails after retry THEN THE System SHALL pass a placeholder "Research data unavailable" to maintain Pipeline continuity

### Requirement 3: Analyst Agent Functionality

**User Story:** As a user, I want the Analyst agent to identify the most important insights from research notes, so that I can understand key patterns without reading raw data.

#### Acceptance Criteria

1. WHEN Analyst_Agent receives Research_Notes THEN THE Analyst_Agent SHALL generate exactly 3 Insights as a numbered list
2. THE Analyst_Agent SHALL use the system prompt "You are an Analyst Agent. You receive raw research notes. Identify the 3 most important insights, patterns, or implications. Output as a numbered list."
3. WHEN Analyst_Agent receives empty or placeholder Research_Notes THEN THE Analyst_Agent SHALL generate Insights indicating "No data available" without crashing the Pipeline
4. WHEN Analyst_Agent completes successfully THEN THE Insights SHALL identify patterns, implications, or key points from the Research_Notes
5. WHEN Analyst_Agent output is malformed or empty THEN THE System SHALL pass a placeholder "Analysis unavailable" to Writer_Agent

### Requirement 4: Writer Agent Functionality

**User Story:** As a user, I want the Writer agent to produce a clear, readable report, so that I can understand the research findings without technical expertise.

#### Acceptance Criteria

1. WHEN Writer_Agent receives Topic and Insights THEN THE Writer_Agent SHALL generate a Final_Report consisting of 3-4 paragraphs
2. THE Writer_Agent SHALL use the system prompt "You are a Writer Agent. You receive a topic and key insights. Write a short, clear report (3-4 paragraphs) for a non-expert reader, based ONLY on the given insights."
3. WHEN Writer_Agent receives placeholder or empty Insights THEN THE Writer_Agent SHALL produce a Final_Report noting "insufficient data" rather than inventing content
4. WHEN Writer_Agent completes successfully THEN THE Final_Report SHALL be coherent, grounded in the provided Insights, and contain no contradictions with Research_Notes
5. THE Writer_Agent SHALL write for a non-expert audience using clear, accessible language

### Requirement 5: Error Handling and Resilience

**User Story:** As a user, I want the system to handle errors gracefully, so that I receive useful feedback instead of system crashes.

#### Acceptance Criteria

1. WHEN an API call fails with a network error THEN THE System SHALL retry once before reporting failure to the user
2. WHEN an API call times out THEN THE System SHALL log the timeout and stop the Pipeline with a clear error message
3. WHEN the API key is missing or invalid THEN THE System SHALL display a clear error message indicating authentication failure
4. WHEN an agent produces malformed output THEN THE System SHALL pass placeholder data to the next agent to maintain Pipeline continuity
5. WHEN rate limiting occurs THEN THE System SHALL display a clear message indicating the API rate limit was reached
6. WHEN any agent fails after retry THEN THE System SHALL display all successfully completed outputs and indicate which agent failed

### Requirement 6: API Integration

**User Story:** As a developer, I want the system to integrate with Claude API properly, so that all agent calls execute reliably.

#### Acceptance Criteria

1. THE System SHALL use the Anthropic SDK to make API calls to Claude
2. WHEN making API calls THEN THE System SHALL load the API key from a .env file
3. WHEN making API calls THEN THE System SHALL apply the agent-specific system prompt for each agent (Researcher, Analyst, Writer)
4. WHEN making API calls THEN THE System SHALL include the appropriate input data (Topic for Researcher, Research_Notes for Analyst, Topic and Insights for Writer)
5. WHEN an API call succeeds THEN THE System SHALL extract and return the text response from the API

### Requirement 7: Input Validation

**User Story:** As a user, I want the system to validate my input, so that I receive useful feedback for invalid requests.

#### Acceptance Criteria

1. WHEN a user provides an empty Topic string THEN THE System SHALL reject the input and display an error message
2. WHEN a user provides a Topic with only whitespace characters THEN THE System SHALL reject the input and display an error message
3. WHEN a user provides a Topic exceeding 500 characters THEN THE System SHALL reject the input and display an error message
4. WHEN a user provides a valid Topic THEN THE System SHALL accept it and begin Pipeline execution
5. THE System SHALL trim leading and trailing whitespace from Topic before processing

### Requirement 8: Output Display

**User Story:** As a user, I want to see all intermediate outputs, so that I can understand how the system arrived at the final report.

#### Acceptance Criteria

1. WHEN Researcher_Agent completes THEN THE System SHALL display the Research_Notes to the user
2. WHEN Analyst_Agent completes THEN THE System SHALL display the Insights to the user
3. WHEN Writer_Agent completes THEN THE System SHALL display the Final_Report to the user
4. WHEN displaying outputs THEN THE System SHALL clearly label each section (Research Notes, Key Insights, Final Report)
5. WHEN the Pipeline completes successfully THEN THE System SHALL display all three outputs in execution order

### Requirement 9: Project Structure and Configuration

**User Story:** As a developer, I want the project to follow a clear structure, so that I can easily navigate and maintain the codebase.

#### Acceptance Criteria

1. THE System SHALL organize agent implementations in an agents/ directory containing researcher.py, analyst.py, and writer.py
2. THE System SHALL organize future tool implementations in a tools/ directory
3. THE System SHALL implement the Orchestrator logic in main.py as the entry point
4. THE System SHALL store the API key in a .env file that is excluded from version control
5. THE System SHALL define all dependencies in requirements.txt including anthropic, python-dotenv, and streamlit (for Phase 2)

### Requirement 10: CLI Interface (Phase 1)

**User Story:** As a user, I want to interact with the system through a command-line interface, so that I can test functionality without a web UI.

#### Acceptance Criteria

1. WHEN the user runs main.py THEN THE System SHALL prompt for a Topic via terminal input
2. WHEN the user enters a Topic THEN THE System SHALL execute the full Pipeline
3. WHEN the Pipeline completes THEN THE System SHALL display all outputs to the terminal
4. WHEN an error occurs THEN THE System SHALL display the error message to the terminal
5. THE System SHALL support running from the command line with `python main.py`

### Requirement 11: State Management

**User Story:** As a developer, I want the system to maintain state throughout pipeline execution, so that data flows correctly between agents.

#### Acceptance Criteria

1. WHEN the Pipeline executes THEN THE Orchestrator SHALL store Topic, Research_Notes, Insights, and Final_Report in memory
2. WHEN an agent completes THEN THE Orchestrator SHALL validate that the output is not None before proceeding
3. WHEN an agent output is None or empty THEN THE Orchestrator SHALL use appropriate placeholder data for the next agent
4. THE Orchestrator SHALL maintain state using Python variables for Phase 1 (no database required)
5. WHEN the Pipeline completes or fails THEN THE Orchestrator SHALL release all state from memory

### Requirement 12: Retry Logic

**User Story:** As a user, I want the system to automatically retry failed operations, so that transient issues don't prevent successful execution.

#### Acceptance Criteria

1. WHEN an agent API call fails THEN THE System SHALL attempt exactly 1 retry before failing
2. WHEN Researcher_Agent returns insufficient output THEN THE System SHALL retry with an enhanced prompt requesting "at least 5 distinct points"
3. WHEN an API call fails on retry THEN THE System SHALL not attempt further retries for that agent
4. WHEN a retry succeeds THEN THE System SHALL proceed with the Pipeline as if the first call succeeded
5. THE System SHALL log each retry attempt with the reason for retrying
