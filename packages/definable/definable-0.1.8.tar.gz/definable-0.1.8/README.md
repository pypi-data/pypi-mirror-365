# Definable

Infrastructure for building and deploying AI agents with a simple YAML configuration and base class extension pattern.

## Features

- **Simple Base Class**: Extend `AgentBox` to create your agent
- **YAML Configuration**: Configure builds with declarative YAML files
- **Docker Packaging**: Build Docker images with a single command
- **FastAPI Integration**: Automatic REST API generation
- **CLI Tools**: Build and serve commands for development

## Quick Start

### 1. Install Definable

```bash
pip install definable
```

### 2. Create Your Agent

```python
# main.py
from definable import AgentBox, AgentInput, AgentOutput, AgentInfo
from pydantic import Field

class SampleAgentInput(AgentInput):
    message: str = Field(description="Input message to process")

class SampleAgentOutput(AgentOutput):
    response_message: str = Field(description="Processed response message")

class DemoAgent(AgentBox):
    def setup(self):
        self.name = 'demo-agent'
        self.version = '1.0.0'
        print("Demo agent initialized!")
    
    def invoke(self, agent_input: SampleAgentInput) -> SampleAgentOutput:
        processed_message = f"Processed: {agent_input.message.upper()}"
        return SampleAgentOutput(response_message=processed_message)
    
    def info(self) -> AgentInfo:
        return AgentInfo(
            name=self.name,
            description="A simple demo agent that processes messages",
            version=self.version,
            input_schema=SampleAgentInput.model_json_schema(),
            output_schema=SampleAgentOutput.model_json_schema()
        )
```

### 3. Create Configuration

```yaml
# agent.yaml
build:
  python_version: "3.11"
  dependencies:
    - "requests>=2.28.0"
  system_packages:
    - "curl"
  environment_variables:
    - API_KEY

agent: "main.py:DemoAgent"

platform:
  name: "demo-agent"
  description: "A simple demo agent for testing"
  version: "1.0.0"

concurrency:
  max_concurrent_requests: 50
  request_timeout: 300
```

### 4. Build and Serve

```bash
# Build Docker image
definable build -t my-agent

# Serve locally for development
definable serve -p 8000
```

## Documentation

Visit our [documentation](https://definable.dev/docs) for detailed guides and API reference.

## License

MIT License - see LICENSE file for details.