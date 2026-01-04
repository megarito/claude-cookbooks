# Claude Cookbooks

A collection of Jupyter notebooks and Python examples for building with the Claude API.

## Quick Start

```bash
# Install dependencies
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Development Commands

```bash
make format        # Format code with ruff
make lint          # Run linting
make check         # Run format-check + lint
make fix           # Auto-fix issues + format
make test          # Run pytest
```

Or directly with uv:

```bash
uv run ruff format .           # Format
uv run ruff check .            # Lint
uv run ruff check --fix .      # Auto-fix
uv run pre-commit run --all-files
```

## Code Style

- **Line length:** 100 characters
- **Quotes:** Double quotes
- **Formatter:** Ruff

Notebooks have relaxed rules for mid-file imports (E402), redefinitions (F811), and variable naming (N803, N806).

## Git Workflow

**Branch naming:** `<username>/<feature-description>`

**Commit format (conventional commits):**
```
feat(scope): add new feature
fix(scope): fix bug
docs(scope): update documentation
style: lint/format
```

## Key Rules

1. **API Keys:** Never commit `.env` files. Always use `os.environ.get("ANTHROPIC_API_KEY")`

2. **Dependencies:** Use `uv add <package>` or `uv add --dev <package>`. Never edit pyproject.toml directly.

3. **Models:** Use current Claude models. Check docs.anthropic.com for latest versions.
   - Sonnet: `claude-sonnet-4-5-20250929`
   - Haiku: `claude-haiku-4-5-20251001`
   - Opus: `claude-opus-4-5-20251101`

4. **Notebooks:**
   - Keep outputs in notebooks (intentional for demonstration)
   - One concept per notebook
   - Test that notebooks run top-to-bottom without errors

5. **Quality checks:** Run `make check` before committing. Pre-commit hooks validate formatting and notebook structure.

## Slash Commands

These commands are available in Claude Code and CI:

- `/notebook-review` - Review notebook quality
- `/model-check` - Validate Claude model references
- `/link-review` - Check links in changed files

## Project Structure

### Directory Organization

Each directory serves a specific purpose. Follow these guidelines when adding new cookbooks:

#### **`capabilities/`** - Core Claude Capabilities
Business-focused use cases demonstrating Claude's core capabilities. Each subdirectory focuses on a specific capability.

**Structure template:**
```
capabilities/
  <capability-name>/
    guide.ipynb          # Main tutorial notebook
    README.md            # Overview and contents
    data/                # Example datasets
    evaluation/          # Evaluation scripts (optional)
    <support-files>      # Additional Python modules if needed
```

**Examples:**
- `classification/` - Classifying insurance tickets with RAG
- `retrieval_augmented_generation/` - Building RAG systems
- `summarization/` - Summarizing legal documents
- `text_to_sql/` - Converting natural language to SQL
- `contextual-embeddings/` - Improving RAG with contextual retrieval

**Notes:**
- Focus on end-to-end business workflows
- Include evaluation/testing when applicable
- Provide sample data for reproducibility

#### **`skills/`** - Claude Skills Framework
Advanced notebooks demonstrating Claude's pre-built skills (Excel, PowerPoint, PDF) and custom skill development.

**Structure:**
```
skills/
  notebooks/           # Tutorial notebooks (numbered)
  custom_skills/       # Custom skill implementations
  sample_data/         # Sample files for demonstrations
  assets/              # Images, templates
  skill_utils.py       # Shared utilities
  file_utils.py        # File handling helpers
```

**Examples:**
- `01_skills_introduction.ipynb` - Getting started with Claude Skills
- `02_skills_financial_applications.ipynb` - Financial use cases
- `03_skills_custom_development.ipynb` - Building custom skills

**Notes:**
- Number notebooks sequentially (01_, 02_, etc.)
- Include working examples with sample data
- Custom skills should be self-contained in subdirectories

#### **`tool_use/`** - Tool Use Patterns
Demonstrations of Claude's tool calling capabilities, including basic and advanced patterns.

**Contents:**
- Individual notebooks showing specific tool use patterns
- `utils/` - Shared tool utilities
- `tests/` - Tool validation tests
- `.env.example` - Template for API keys if needed

**Examples:**
- `calculator_tool.ipynb` - Simple arithmetic tools
- `customer_service_agent.ipynb` - Multi-tool agent patterns
- `extracting_structured_json.ipynb` - Using tools for JSON extraction
- `memory_cookbook.ipynb` - Persistent memory with tools
- `programmatic_tool_calling_ptc.ipynb` - PTC for reduced latency
- `tool_search_with_embeddings.ipynb` - Scaling to thousands of tools

**Notes:**
- Keep tool definitions close to usage examples
- Include error handling patterns
- Show both single and parallel tool use

#### **`multimodal/`** - Vision & Image Processing
Notebooks demonstrating Claude's vision capabilities for analyzing images, documents, charts, and more.

**Contents:**
- Vision tutorial notebooks
- `documents/` - Sample PDFs, images for examples

**Examples:**
- `getting_started_with_vision.ipynb` - Basic image input
- `best_practices_for_vision.ipynb` - Optimization tips
- `how_to_transcribe_text.ipynb` - OCR and document extraction
- `reading_charts_graphs_powerpoints.ipynb` - Chart analysis
- `crop_tool.ipynb` - Image cropping for detailed analysis

**Notes:**
- Include image samples in the notebook or documents/
- Show both single-image and multi-image patterns
- Demonstrate vision + tools combinations

#### **`third_party/`** - External Service Integrations
Integration examples with third-party services and platforms. Each service gets its own subdirectory.

**Structure template:**
```
third_party/
  <ServiceName>/       # Use official capitalization
    <cookbook>.ipynb   # Integration notebook(s)
    README.md          # Setup instructions (optional)
```

**Current integrations:**
- `Pinecone/` - Vector database for RAG
- `VoyageAI/` - Embedding services
- `MongoDB/` - Database integration
- `LlamaIndex/` - LLM framework integration
- `Deepgram/` - Audio transcription
- `ElevenLabs/` - Text-to-speech and speech-to-text
- `Wikipedia/` - Search and retrieval
- `WolframAlpha/` - Computational queries

**Notes:**
- Use service's official name/capitalization
- Include setup instructions and API key requirements
- Show realistic integration patterns

#### **`claude_agent_sdk/`** - Claude Agent SDK Tutorials
Tutorials for building agents with the Claude Agent SDK, from simple to complex patterns.

**Structure:**
```
claude_agent_sdk/
  00_*.ipynb                    # Numbered tutorials
  01_*.ipynb
  02_*.ipynb
  <agent-name>_agent/           # Agent implementation folders
    main.py                     # Agent entry point
    .claude/                    # Agent configuration
  utils/                        # Shared utilities
```

**Examples:**
- `00_The_one_liner_research_agent.ipynb` - Simple research agent
- `01_The_chief_of_staff_agent.ipynb` - Multi-agent orchestration
- `02_The_observability_agent.ipynb` - MCP server integration

**Notes:**
- Number notebooks in learning progression
- Include working agent implementations
- Show both simple and advanced patterns

#### **`extended_thinking/`** - Extended Reasoning
Notebooks demonstrating Claude's extended thinking capability for complex reasoning tasks.

**Contents:**
- Standalone notebooks showing extended thinking patterns
- Examples with and without tool use

**Examples:**
- `extended_thinking.ipynb` - Basic extended thinking
- `extended_thinking_with_tool_use.ipynb` - Combining thinking with tools

**Notes:**
- Show budget management
- Demonstrate when to use vs. regular prompting

#### **`misc/`** - Utilities & Cross-Cutting Features
Notebooks covering API features that don't fit into other categories: caching, batching, evals, etc.

**Contents:**
- Individual feature notebooks
- `data/` - Sample datasets

**Examples:**
- `prompt_caching.ipynb` - Reducing costs with caching
- `batch_processing.ipynb` - Message Batches API
- `building_evals.ipynb` - Evaluation systems
- `how_to_enable_json_mode.ipynb` - Reliable JSON output
- `metaprompt.ipynb` - Prompt engineering tool

**Notes:**
- Focus on API features and patterns
- Include cost/performance comparisons
- Show practical applications

#### **`patterns/`** - Agent & Workflow Patterns
Reusable architectural patterns for multi-agent systems and workflows.

**Structure:**
```
patterns/
  agents/              # Agent collaboration patterns
    <pattern>.ipynb    # Individual pattern notebooks
```

**Examples:**
- `basic_workflows.ipynb` - Simple multi-LLM patterns
- `evaluator_optimizer.ipynb` - Generation + evaluation loop
- `orchestrator_workers.ipynb` - Central orchestrator pattern

**Notes:**
- Focus on architecture, not specific use cases
- Show pattern variations and trade-offs
- Include performance/cost considerations

#### **`coding/`** - Code Generation & Development
Notebooks focused on using Claude for software development tasks.

**Examples:**
- `prompting_for_frontend_aesthetics.ipynb` - Frontend design guidance

**Notes:**
- Include before/after examples
- Show prompt engineering for code quality

#### **`finetuning/`** - Model Customization
Guides for finetuning Claude models on custom data.

**Structure:**
```
finetuning/
  <finetuning-guide>.ipynb
  datasets/            # Example training datasets
```

**Notes:**
- Include dataset preparation guidance
- Show evaluation of finetuned models

#### **`observability/`** - Monitoring & Analytics
Tools and patterns for monitoring Claude API usage and performance.

**Examples:**
- `usage_cost_api.ipynb` - Admin API for usage tracking

#### **`tool_evaluation/`** - Tool Testing Framework
Framework for evaluating agent tool use independently from tasks.

**Notes:**
- Separate tool evaluation from task evaluation
- Support parallel evaluation runs

#### **`.claude/`** - Claude Code Configuration
Configuration for Claude Code CLI features.

**Structure:**
```
.claude/
  commands/            # Slash command definitions
  skills/              # Custom skill definitions
  agents/              # Agent configurations
```

**Notes:**
- Not for user-facing cookbooks
- Configuration for development tools only

#### **`scripts/`** - Automation & Validation
Helper scripts for CI/CD, validation, and automation.

**Examples:**
- `detect-secrets/` - Secret detection
- Validation scripts for notebooks

**Notes:**
- Not for user-facing cookbooks
- Focus on repository maintenance

## Adding a New Cookbook

1. Create notebook in the appropriate directory
2. Add entry to `registry.yaml` with title, description, path, authors, categories
3. Add author info to `authors.yaml` if new contributor
4. Run quality checks and submit PR
