# Implementation Plan: Multi-Agent Research Assistant

## Overview

This implementation plan breaks down the Multi-Agent Research Assistant into discrete coding tasks. The system coordinates three specialized AI agents (Researcher, Analyst, Writer) through a sequential pipeline architecture. Implementation follows a bottom-up approach: core infrastructure first, then individual agents, orchestration logic, error handling, and finally integration with CLI interface.

## Tasks

- [ ] 1. Set up project structure and core infrastructure
  - Create directory structure (agents/, tests/unit/, tests/property/, tests/integration/)
  - Create .env.example file with ANTHROPIC_API_KEY placeholder
  - Create requirements.txt with dependencies: anthropic, python-dotenv, hypothesis, pytest
  - Create empty __init__.py files in agents/ directory
  - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ] 2. Implement exception hierarchy and error models
  - [ ] 2.1 Create exceptions.py with all exception classes
    - Implement PipelineError base class
    - Implement ValidationError, AgentExecutionError with agent_name and original_error attributes
    - Implement APIError, AuthenticationError, RateLimitError, TimeoutError, NetworkError
    - _Requirements: 5.3, 5.5_
  
  - [ ] 2.2 Create error_messages.py with ERROR_MESSAGES dictionary
    - Define all error message templates from design specification
    - _Requirements: 5.3, 5.5, 7.1, 7.2, 7.3_

- [ ] 3. Implement data models
  - [ ] 3.1 Create models.py with input and output dataclasses
    - Implement Topic dataclass with validation in __post_init__
    - Implement ResearchNotes dataclass with from_agent_output classmethod and PLACEHOLDER constant
    - Implement Insights dataclass with from_agent_output, _is_valid_format, and PLACEHOLDER constant
    - Implement FinalReport dataclass with from_agent_output
    - Implement PipelineResult dataclass with execution_status, errors, is_complete_success property, and failed_agents property
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 2.3, 3.3, 4.3, 5.4, 11.1_
  
  - [ ]* 3.2 Write property tests for Topic validation
    - **Property 11: Whitespace-Only Topic Rejection**
    - **Property 12: Valid Topic Acceptance**
    - **Property 13: Topic Whitespace Trimming**
    - **Validates: Requirements 7.2, 7.4, 7.5**
  
  - [ ]* 3.3 Write property tests for output model placeholder logic
    - **Property 6: Placeholder Propagation on Agent Failure**
    - **Validates: Requirements 5.4, 11.3**

- [ ] 4. Implement API client
  - [ ] 4.1 Create api_client.py with APIClient class
    - Implement __init__ to load API key from .env using python-dotenv
    - Implement call_claude method with system_prompt, user_message, max_tokens parameters
    - Use Anthropic SDK to make API calls with model "claude-3-5-sonnet-20241022"
    - Extract text content from API response structure
    - Raise appropriate exceptions for different error types (AuthenticationError, RateLimitError, TimeoutError, NetworkError)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 5.3_
  
  - [ ]* 4.2 Write unit tests for API client error handling
    - Test AuthenticationError raised for missing/invalid API key
    - Test RateLimitError raised for rate limit response
    - Test TimeoutError raised for timeout
    - Test NetworkError raised for connection failure
    - Test successful text extraction from response structure
    - _Requirements: 5.3, 6.5_
  
  - [ ]* 4.3 Write property test for API response text extraction
    - **Property 10: API Response Text Extraction**
    - **Validates: Requirements 6.5**

- [ ] 5. Implement retry logic utility
  - [ ] 5.1 Create retry_logic.py with call_with_retry function
    - Implement retry function with max_retries=1 and backoff_seconds=2 parameters
    - Implement loop with attempt counter
    - Catch AuthenticationError and re-raise immediately without retry
    - Implement exponential backoff with time.sleep between retries
    - Log retry attempts with reason
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  
  - [ ]* 5.2 Write unit tests for retry logic
    - Test exactly 1 retry on failure
    - Test no retry for AuthenticationError
    - Test successful retry recovery
    - Test logging of retry attempts
    - _Requirements: 12.1, 12.3, 12.4, 12.5_
  
  - [ ]* 5.3 Write property test for retry limit enforcement
    - **Property 20: Retry Limit Enforcement**
    - **Property 21: Successful Retry Recovery**
    - **Property 22: Retry Logging**
    - **Validates: Requirements 12.1, 12.3, 12.4, 12.5**

- [ ] 6. Checkpoint - Verify core infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement Researcher Agent
  - [ ] 7.1 Create agents/researcher.py with execute function
    - Implement execute(topic: str, api_client: APIClient) -> str function
    - Use system prompt: "You are a Research Agent. Given a topic, list the key facts, trends, and data points relevant to it. Be factual and concise. Output as a bullet list."
    - Call api_client.call_claude with system prompt and topic
    - Validate response length (≥50 characters)
    - If response too short, retry with enhanced prompt: "List at least 5 distinct points about: {topic}"
    - Wrap API call in call_with_retry for error handling
    - Raise AgentExecutionError if API call fails after retry
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 12.2_
  
  - [ ]* 7.2 Write unit tests for Researcher Agent
    - Test successful execution returns bullet-point list
    - Test short response triggers enhanced prompt retry
    - Test AgentExecutionError raised on failure after retry
    - Test correct system prompt used
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  
  - [ ]* 7.3 Write property test for Researcher output format
    - **Property 3: Researcher Output Format**
    - **Property 8: Agent-Specific System Prompt Application** (Researcher)
    - **Property 9: Agent Input Data Inclusion** (Researcher)
    - **Validates: Requirements 2.1, 6.3, 6.4**

- [ ] 8. Implement Analyst Agent
  - [ ] 8.1 Create agents/analyst.py with execute function
    - Implement execute(research_notes: str, api_client: APIClient) -> str function
    - Use system prompt: "You are an Analyst Agent. You receive raw research notes. Identify the 3 most important insights, patterns, or implications. Output as a numbered list."
    - Handle empty/placeholder research notes gracefully
    - Call api_client.call_claude with system prompt and research_notes
    - Wrap API call in call_with_retry for error handling
    - Raise AgentExecutionError if API call fails after retry
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 8.2 Write unit tests for Analyst Agent
    - Test successful execution returns numbered list
    - Test handles empty research notes without crashing
    - Test handles placeholder research notes without crashing
    - Test AgentExecutionError raised on failure after retry
    - Test correct system prompt used
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  
  - [ ]* 8.3 Write property test for Analyst output format
    - **Property 4: Analyst Output Format**
    - **Property 8: Agent-Specific System Prompt Application** (Analyst)
    - **Property 9: Agent Input Data Inclusion** (Analyst)
    - **Validates: Requirements 3.1, 6.3, 6.4**

- [ ] 9. Implement Writer Agent
  - [ ] 9.1 Create agents/writer.py with execute function
    - Implement execute(topic: str, insights: str, api_client: APIClient) -> str function
    - Use system prompt: "You are a Writer Agent. You receive a topic and key insights. Write a short, clear report (3-4 paragraphs) for a non-expert reader, based ONLY on the given insights."
    - Accept both topic and insights as input parameters
    - Handle placeholder insights appropriately (note "insufficient data")
    - Call api_client.call_claude with system prompt, topic, and insights
    - Wrap API call in call_with_retry for error handling
    - Raise AgentExecutionError if API call fails after retry
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 9.2 Write unit tests for Writer Agent
    - Test successful execution returns 3-4 paragraph report
    - Test handles placeholder insights appropriately
    - Test AgentExecutionError raised on failure after retry
    - Test correct system prompt used
    - Test both topic and insights included in API call
    - _Requirements: 4.1, 4.2, 4.3, 4.5_
  
  - [ ]* 9.3 Write property test for Writer output format
    - **Property 5: Writer Output Format**
    - **Property 8: Agent-Specific System Prompt Application** (Writer)
    - **Property 9: Agent Input Data Inclusion** (Writer)
    - **Validates: Requirements 4.1, 6.3, 6.4**

- [ ] 10. Checkpoint - Verify all agents implemented
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 11. Implement orchestrator pipeline logic
  - [ ] 11.1 Create orchestrator.py with run_pipeline function
    - Implement run_pipeline(topic: str) -> PipelineResult function
    - Validate topic by creating Topic dataclass instance (raises ValueError if invalid)
    - Initialize APIClient with API key from environment
    - Initialize execution_status dict and errors list
    - Execute Researcher Agent and store research_notes
    - Validate Researcher output is not None before proceeding
    - If Researcher fails, use ResearchNotes.PLACEHOLDER and mark in execution_status
    - Create ResearchNotes object using from_agent_output classmethod
    - Execute Analyst Agent with research_notes and store insights
    - Validate Analyst output is not None before proceeding
    - If Analyst fails, use Insights.PLACEHOLDER and mark in execution_status
    - Create Insights object using from_agent_output classmethod
    - Execute Writer Agent with topic and insights and store final_report
    - If Writer fails, mark in execution_status
    - Create FinalReport object using from_agent_output classmethod
    - Return PipelineResult with all outputs, execution_status, and errors
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.4, 5.6, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 11.2 Write unit tests for orchestrator
    - Test successful end-to-end execution with all agents succeeding
    - Test Researcher failure propagates placeholder to Analyst
    - Test Analyst failure propagates placeholder to Writer
    - Test Writer failure returns partial results
    - Test execution_status tracks success/failure correctly
    - Test state cleanup after completion
    - _Requirements: 1.1, 1.2, 1.3, 5.4, 5.6, 11.2, 11.3, 11.5_
  
  - [ ]* 11.3 Write property tests for orchestrator pipeline
    - **Property 1: Pipeline Sequential Execution and Data Flow**
    - **Property 17: State Storage During Execution**
    - **Property 18: Output Validation Before Proceeding**
    - **Property 19: State Cleanup on Termination**
    - **Validates: Requirements 1.1, 1.2, 1.3, 11.1, 11.2, 11.5**

- [ ] 12. Implement CLI interface
  - [ ] 12.1 Create main.py with CLI entry point
    - Implement main() function as entry point
    - Prompt user for topic input using input()
    - Handle KeyboardInterrupt gracefully
    - Call run_pipeline with user topic
    - Catch ValidationError and display appropriate error message
    - Display Research Notes section with label
    - Display Key Insights section with label
    - Display Final Report section with label
    - Display all three outputs in execution order
    - If any agent failed, display which agent failed and show partial results
    - Display all errors from PipelineResult.errors list
    - Add if __name__ == "__main__": block to call main()
    - _Requirements: 1.5, 7.1, 7.2, 7.3, 7.4, 8.1, 8.2, 8.3, 8.4, 8.5, 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [ ]* 12.2 Write unit tests for CLI display logic
    - Test empty topic rejected with error message
    - Test whitespace-only topic rejected with error message
    - Test topic exceeding 500 characters rejected with error message
    - Test valid topic accepted and pipeline executed
    - Test all three outputs displayed with correct labels
    - Test partial results displayed when agent fails
    - Test error messages displayed correctly
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 8.4, 10.3, 10.4_
  
  - [ ]* 12.3 Write property tests for output display
    - **Property 2: Complete Output Display**
    - **Property 7: Partial Success Display**
    - **Property 14: Output Section Labeling**
    - **Property 15: Pipeline Execution Triggers from Valid Input**
    - **Property 16: Terminal Output Display**
    - **Validates: Requirements 1.5, 5.6, 8.1, 8.2, 8.3, 8.4, 8.5, 10.2, 10.3, 10.4**

- [ ] 13. Checkpoint - Verify end-to-end integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Write integration tests
  - [ ]* 14.1 Create tests/integration/test_end_to_end.py
    - Test happy path: valid topic → all agents succeed → complete output
    - Test Researcher fails → placeholder → Analyst and Writer continue
    - Test Analyst fails → Researcher succeeds → Writer gets placeholder
    - Test Writer fails → Researcher and Analyst outputs displayed
    - Use mocked Anthropic SDK for all API calls
    - Verify all outputs formatted correctly
    - Verify execution_status tracks all agents
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.4, 5.6_

- [ ] 15. Create project documentation files
  - [ ] 15.1 Create README.md
    - Add project overview and purpose
    - Add setup instructions (clone, install dependencies, add API key to .env)
    - Add usage instructions (run python main.py)
    - Add example output showing all three agent outputs
    - Add requirements section listing Python 3.8+ and Anthropic API key
    - _Requirements: 9.4, 10.5_
  
  - [ ] 15.2 Create .gitignore
    - Add .env to exclude API keys from version control
    - Add __pycache__/, *.pyc, .pytest_cache/
    - Add .hypothesis/ for property test cache
    - _Requirements: 9.4_

- [ ] 16. Final checkpoint - Full system validation
  - Run full test suite (unit, property, integration tests)
  - Manually test CLI with valid topic to verify end-to-end flow
  - Verify .env.example exists and README documents setup
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Implementation follows bottom-up approach: infrastructure → agents → orchestration → CLI
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and error handling
- Integration tests validate end-to-end workflows with mocked API
- Checkpoints ensure incremental validation at major milestones
- All agent implementations use the exact system prompts specified in requirements
- Retry logic is centralized in retry_logic.py for consistency
- Error handling follows the exception hierarchy defined in design
- Placeholder data strategy ensures graceful degradation on agent failures
- State management is handled entirely in-memory (no database required for Phase 1)

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["3.1", "4.1", "5.1"] },
    { "id": 3, "tasks": ["3.2", "3.3", "4.2", "4.3", "5.2", "5.3"] },
    { "id": 4, "tasks": ["7.1", "8.1", "9.1"] },
    { "id": 5, "tasks": ["7.2", "7.3", "8.2", "8.3", "9.2", "9.3"] },
    { "id": 6, "tasks": ["11.1"] },
    { "id": 7, "tasks": ["11.2", "11.3"] },
    { "id": 8, "tasks": ["12.1"] },
    { "id": 9, "tasks": ["12.2", "12.3", "14.1"] },
    { "id": 10, "tasks": ["15.1", "15.2"] }
  ]
}
```
