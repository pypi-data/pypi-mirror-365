"""Main CLI application for AI Bootstrap - Phase 3 with AI Planner."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print
import copier
import asyncio
import sys
import threading
import concurrent.futures
import json
from importlib.resources import files   # std-lib ≥3.9

from .ai_planner import AIPlanner, PlannerError

app = typer.Typer(
    name="ai-bootstrap",
    help="A CLI tool for scaffolding AI/ML projects with AI-powered requirement analysis",
    rich_markup_mode="rich"
)

console = Console()

# Blueprint definitions
BLUEPRINTS = {
    "rag": {
        "name": "RAG System",
        "description": "Retrieval-Augmented Generation system",
        "frameworks": ["langchain", "llamaindex"],
        "features": ["Document processing", "Vector storage", "LLM integration"]
    },
    "multi-agent": {
        "name": "Multi-Agent System",
        "description": "LangGraph-based multi-agent system with supervisor pattern",
        "frameworks": ["langgraph"],
        "features": ["Agent orchestration", "State management", "Tool integration"]
    },
    "multimodal-chatbot": {
        "name": "Multimodal Chatbot",
        "description": "Chatbot with image, audio, and text processing capabilities",
        "frameworks": ["langchain", "chainlit"],
        "features": ["Image processing", "Audio processing", "Web interface"]
    },
    "core-langchain": {
        "name": "Core LangChain Application",
        "description": "Modular LangChain application with chains, prompts, and tools",
        "frameworks": ["langchain"],
        "features": ["Custom chains", "Prompt management", "Tool integration"]
    }
}

# Template directory mapping for project types
TEMPLATE_DIR_MAP = {
    "multi-agent": "multi_agent_system",
    "core-langchain": "core_langchain",
    "multimodal-chatbot": "multimodal_chatbot",
    "rag": "rag_system",
}

def get_templates_dir() -> Path:
    """Get the templates directory path that works both in development and installed package."""
    # Use importlib.resources to locate the templates directory inside the installed package
    return Path(files("ai_bootstrap")) / "templates"

def run_async_safely(coro):
    """Run async function safely, handling existing event loops."""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()
    except RuntimeError:
        return asyncio.run(coro)

@app.command(
    help="Create a new AI/ML project from a blueprint, either interactively or with AI-powered planning.",
    rich_help_panel="Project Commands"
)
def create(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Name of the project to create."),
    project_type: Optional[str] = typer.Option(None, "--type", "-t", help="Type of project blueprint to use."),
    llm_provider: Optional[str] = typer.Option(None, "--llm", help="Default LLM provider (e.g., openai, mistral)."),
    framework: Optional[str] = typer.Option(None, "--framework", help="Default framework (e.g., langchain, llamaindex)."),
    vector_store: Optional[str] = typer.Option(None, "--vector-store", help="Vector store"),
    ui_framework: Optional[str] = typer.Option(None, "--ui-framework", help="UI framework"),
    python_version: Optional[str] = typer.Option("3.11", "--python", help="Python version for the project."),
    ai_planner: bool = typer.Option(False, "--chat", help="Enable AI-powered requirement analysis."),
    planner_provider: Optional[str] = typer.Option("mistral", "--planner-provider", help="AI provider for analysis."),
):
    """Create a new AI/ML project."""
    
    console.print("\n🚀 [bold blue]Bootstrap your AI project[/bold blue]")
    
    if ai_planner:
        console.print("🧠 [bold green]AI Analysis Mode Activated[/bold green]\n")
        _handle_ai_planner_mode_sync(planner_provider, python_version)
    else:
        console.print("🎯 [bold cyan]Interactive Mode[/bold cyan]\n")
        _handle_interactive_mode(name, project_type, llm_provider, framework, python_version, vector_store, ui_framework)

def _handle_ai_planner_mode_sync(planner_provider: str, python_version: str):
    """Handle AI requirement analysis mode synchronously."""
    try:
        console.print("💭 [bold]Describe your ideal AI/ML project:[/bold]")
        console.print("Describe the features you want, the type of application, and any specific requirements from the ones specified below.")
        console.print()
        
        # print all the technologies that are supported by the blueprints
        # console.print("[bold cyan]Available technologies:[/bold cyan]")
        # console.print(f"Supported blueprints: [[bold yellow]{', '.join(BLUEPRINTS.keys())}[/bold yellow]]")
        # console.print("LLM providers: [[bold yellow]openai, ollama, [underline]mistral[/underline], anthropic[/bold yellow]]")
        # console.print("frameworks: [[bold yellow][underline]langchain[/underline], llamaindex, langgraph, chainlit[/bold yellow]]")
        # console.print("vector stores: [[bold yellow][underline]chroma[/underline], faiss[/bold yellow]]")
        # console.print("UI frameworks: [[bold yellow][underline]streamlit[/underline], chainlit, fastapi, cli[/bold yellow]]")
        # console.print("Python versions: [[bold yellow][underline]3.11[/underline], 3.12[/bold yellow]]")
        # console.print("memory backends: [[bold yellow][underline]in_memory[/underline], redis, postgres[/bold yellow]]")

        # Build a table to showcase available technologies
        tech_table = Table(show_header=True, header_style="bold magenta")
        # merge columns one and two
        tech_table.add_column("Tech", style="cyan" , justify="center")
        tech_table.add_column("Available Option", style="white", justify="center")
        tech_table.add_column("Flag", style="yellow", justify="center")

        tech_table.add_row("Blueprints", ", ".join(BLUEPRINTS.keys()), "--type")
        tech_table.add_row("LLM Providers", "openai, ollama, [underline]mistral[/underline], anthropic", "--llm")
        tech_table.add_row("Frameworks", "[underline]langchain[/underline], llamaindex, langgraph, chainlit", "--framework")
        tech_table.add_row("Vector Stores", "[underline]chroma[/underline], faiss", "--vector-store")
        tech_table.add_row("UI Frameworks", "[underline]streamlit[/underline], chainlit, fastapi, cli", "--ui-framework")
        tech_table.add_row("Python Versions", "[underline]3.11[/underline], 3.12", "--python")
        tech_table.add_row("Memory Backends", "[underline]in_memory[/underline], redis, postgres", "(multi-agent only)")

        console.print(tech_table)


        description = ""
        if sys.stdin.isatty():
            description = Prompt.ask(
                "\n[bold cyan]Project description\n" \
                "Describe project & specific requirements from above and let the Agent plan out the application.\nIf none is specified, the AI will choose the [underline]Default Options[/underline] for you.[/bold cyan]",
                default=description
            )
        
        console.print(f"\n🤖 [yellow]AI Analyst is analyzing your requirements...[/yellow]")
        
        # Generate project plan using the safe async runner
        async def get_plan():
            planner = AIPlanner(provider=planner_provider)
            return await planner.generate_enhanced_project_plan(
                description=description,
                available_blueprints=BLUEPRINTS,
                python_version=python_version
            )
        
        with console.status("[bold green]Analyzing..."):
            plan_result = run_async_safely(get_plan())
        
        if not plan_result.success:
            console.print(f"❌ [red]AI Analysis failed: {plan_result.error}[/red]")
            console.print("💡 [yellow]Falling back to interactive mode...[/yellow]")
            _handle_interactive_mode(None, None, None, None, python_version)
            return
        
        # Display the analyzed plan
        _display_ai_generated_plan(plan_result)
        
        # Confirm with user
        if sys.stdin.isatty():
            if not Confirm.ask("\n✅ Proceed with this AI-analyzed project plan?", default=True):
                console.print("❌ Project generation cancelled.")
                console.print("💡 You can run without --chat for manual configuration.")
                return
        
        # Generate project using AI plan
        _generate_project_from_ai_plan_sync(plan_result)
        
    except PlannerError as e:
        console.print(f"❌ [red]AI Analysis Error: {e}[/red]")
        console.print("💡 [yellow]Try running without --chat or check your API configuration.[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Unexpected error: {e}[/red]")
        console.print("💡 [yellow]Falling back to interactive mode...[/yellow]")
        _handle_interactive_mode(None, None, None, None, python_version)

def _display_ai_generated_plan(plan_result):
    """Display the AI-analyzed project plan."""
    plan = plan_result.plan
    
    console.print("\n🎯 [bold blue]AI-Analyzed Project Plan:[/bold blue]")
    
    # Create a rich table for the plan
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")
    table.add_column("Reasoning", style="dim")
    
    # Add plan details to table
    table.add_row("Project Name", plan.project_name, "Based on your description")
    table.add_row("Project Type", plan.project_type, f"Best fit: {BLUEPRINTS.get(plan.project_type, {}).get('name', 'Unknown')}")
    table.add_row("LLM Provider", plan.llm_provider, plan.reasoning.get('llm_provider', 'Recommended choice'))
    
    # Add type-specific configurations
    for key, value in plan.type_specific_config.items():
        if isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                value_str = str(value)
            else:
                value_str = ", ".join(str(v) for v in value)
        else:
            value_str = str(value)
        
        reasoning = plan.reasoning.get(key, "AI recommendation")
        table.add_row(key.replace('_', ' ').title(), value_str, reasoning)
    
    console.print(table)
    
    # Display AI's explanation
    if plan.explanation:
        console.print(f"\n🤖 [bold]AI Analyst's Explanation:[/bold]")
        console.print(f"[italic]{plan.explanation}[/italic]")

def _generate_project_from_ai_plan_sync(plan_result):
    """Generate project using the AI-analyzed plan - fully synchronous."""
    plan = plan_result.plan

    # Use the mapping to get the correct template directory
    template_key = plan.project_type
    template_subdir = TEMPLATE_DIR_MAP.get(template_key, template_key.replace("-", "_"))
    
    # 🔑 KEY FIX: Use the new template path function
    templates_base = get_templates_dir()
    template_dir = templates_base / template_subdir

    if not template_dir.exists():
        console.print(f"❌ [red]Template directory not found: {template_dir}[/red]")
        console.print(f"Available templates: {list(templates_base.glob('*'))}")
        return

    # Prepare answers for Copier using AI plan
    answers = {
        "project_name": plan.project_name,
        "project_type": plan.project_type,
        "llm_provider": plan.llm_provider,
        "python_version": plan.python_version,
        "include_notebooks": True,
        "include_tests": True,
        "include_docker": False,
        **plan.type_specific_config,
    }

    # Generate project
    destination = Path.cwd() / plan.project_name

    try:
        console.print(f"\n🔄 Generating AI-analyzed project: [cyan]{plan.project_name}[/cyan]")
        copier.run_copy(
            src_path=str(template_dir),
            dst_path=str(destination),
            data=answers,
            answers_file=None,
            quiet=False,
            unsafe=True,
        )

        console.print(f"\n✅ [bold green]AI-analyzed project '{plan.project_name}' created successfully![/bold green]")
        console.print(f"📁 Location: [cyan]{destination}[/cyan]")
        console.print("\n🚀 [bold]Next Steps:[/bold]")
        console.print(f"   1. cd {plan.project_name}")
        console.print("   2. Create a new GitHub repository")
        console.print("   3. Push the code to GitHub")
        console.print("   4. Open in GitHub Codespaces")
        console.print("   5. Set up environment variables (.env)")
        console.print("\n🤖 [dim]This project was intelligently analyzed by AI based on your requirements![/dim]")

    except Exception as e:
        console.print(f"❌ [red]Error generating project: {e}[/red]")
        import traceback
        console.print(f"[dim]Debug info: {traceback.format_exc()}[/dim]")

def _handle_interactive_mode(name, project_type, llm_provider, framework, python_version, vector_store, ui_framework):
    """Handle traditional interactive mode."""
    
    # Step 1: Choose project type first
    if not project_type:
        console.print("📋 [bold]Available Project Types:[/bold]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Key", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="white")

        for key, blueprint in BLUEPRINTS.items():
            table.add_row(key, blueprint["name"], blueprint["description"])

        console.print(table)
        console.print()

        project_type = Prompt.ask(
            "🎯 Choose project type", 
            choices=list(BLUEPRINTS.keys()),
            default="rag"
        )

    if project_type not in BLUEPRINTS:
        console.print(f"❌ [red]Invalid project type: {project_type}[/red]")
        raise typer.Exit(1)

    blueprint = BLUEPRINTS[project_type]
    console.print(f"✅ Selected: [cyan]{blueprint['name']}[/cyan]")

    # Use the same mapping for interactive mode
    template_subdir = TEMPLATE_DIR_MAP.get(project_type, project_type.replace("-", "_"))
    
    # 🔑 KEY FIX: Use the new template path function
    templates_base = get_templates_dir()
    template_dir = templates_base / template_subdir

    if not template_dir.exists():
        console.print(f"❌ [red]Template directory not found: {template_dir}[/red]")
        raise typer.Exit(1)

    # Step 2: Get project name
    if not name:
        default_name = f"my-{project_type.replace('_', '-')}-project"
        name = Prompt.ask("📝 Enter project name", default=default_name)

    # Step 3: Framework-specific questions
    answers = {
        "project_name": name,
        "project_type": project_type,
        "python_version": python_version,
        "include_notebooks": True,
        "include_tests": True,
        "include_docker": False,
    }

    # Blueprint-specific configuration
    if project_type == "rag":
        answers.update(_configure_rag_system(llm_provider, framework, vector_store, ui_framework))
    elif project_type == "multi-agent":
        answers.update(_configure_multi_agent_system(llm_provider))
    elif project_type == "multimodal-chatbot":
        answers.update(_configure_multimodal_chatbot(llm_provider, framework))
    elif project_type == "core-langchain":
        answers.update(_configure_core_langchain(llm_provider))

    # Show configuration summary
    _show_configuration_summary(answers)

    # Confirm before generation
    if not Confirm.ask("\n✅ Proceed with project generation?", default=True):
        console.print("❌ Project generation cancelled.")
        raise typer.Exit(0)

    # Generate project
    _generate_project(template_dir, name, answers)

# [Keep all the _configure_* functions unchanged]
def _configure_rag_system(llm_provider: Optional[str], framework: Optional[str], vector_store: Optional[str], ui_framework: Optional[str]) -> dict:
    """Configure RAG system specific options."""
    config = {}
    
    if not llm_provider:
        llm_provider = Prompt.ask(
            "🤖 Choose LLM provider", 
            choices=["openai", "ollama", "mistral"], 
            default="mistral"
        )
    config["llm_provider"] = llm_provider
    
    if not framework:
        framework = Prompt.ask(
            "🔧 Choose framework", 
            choices=["langchain", "llamaindex"], 
            default="langchain"
        )
    config["framework"] = framework
    
    if not vector_store:
        vector_store = Prompt.ask(
            "🗄️ Choose vector store",
            choices=["chroma", "faiss"],
            default="chroma"
        )
    config["vector_store"] = vector_store
    
    if not ui_framework:
        ui_framework = Prompt.ask(
            "🖥️ Choose UI framework",
            choices=["streamlit", "chainlit", "fastapi", "cli"],
            default="streamlit"
        )
    config["ui_framework"] = ui_framework
    
    return config

def _configure_multi_agent_system(llm_provider: Optional[str]) -> dict:
    """Configure Multi-Agent system specific options."""
    config = {}
    
    if not llm_provider:
        llm_provider = Prompt.ask(
            "🤖 Choose LLM provider", 
            choices=["openai", "anthropic", "ollama", "mistral"], 
            default="mistral"
        )
    config["llm_provider"] = llm_provider
    
    # Agent configuration
    num_agents = int(Prompt.ask("👥 Number of specialized agents", default="3"))
    config["num_agents"] = num_agents
    
    agent_types = []
    console.print("\n🎭 Configure your agents:")
    for i in range(num_agents):
        agent_name = Prompt.ask(f"Agent {i+1} name", default=f"agent_{i+1}")
        agent_role = Prompt.ask(f"Agent {i+1} role/specialty", default="general")
        agent_types.append({"name": agent_name, "role": agent_role})
    
    config["agents"] = agent_types
    
    memory_backend = Prompt.ask(
        "💾 Choose memory backend", 
        choices=["in_memory", "redis", "postgres"], 
        default="in_memory"
    )
    config["memory_backend"] = memory_backend
    
    ui_framework = Prompt.ask(
        "🖥️ Choose UI framework", 
        choices=["streamlit", "chainlit", "cli"], 
        default="streamlit"
    )
    config["ui_framework"] = ui_framework
    
    return config

def _configure_multimodal_chatbot(llm_provider: Optional[str], framework: Optional[str]) -> dict:
    """Configure Multimodal Chatbot specific options."""
    config = {}
    
    if not llm_provider:
        llm_provider = Prompt.ask(
            "🤖 Choose LLM provider", 
            choices=["openai", "anthropic", "ollama", "mistral"], 
            default="mistral"
        )
    config["llm_provider"] = llm_provider
    
    # Modality support
    modalities = []
    if Confirm.ask("🖼️ Enable image processing?", default=True):
        modalities.append("image")
        
        image_features = []
        if Confirm.ask("  • Image analysis/description?", default=True):
            image_features.append("analysis")
        if Confirm.ask("  • Image generation?", default=False):
            image_features.append("generation")
        config["image_features"] = image_features
    
    if Confirm.ask("🎵 Enable audio processing?", default=False):
        modalities.append("audio")
        
        audio_features = []
        if Confirm.ask("  • Speech-to-text?", default=True):
            audio_features.append("stt")
        if Confirm.ask("  • Text-to-speech?", default=True):
            audio_features.append("tts")
        config["audio_features"] = audio_features
    
    config["modalities"] = modalities
    
    ui_framework = Prompt.ask(
        "🖥️ Choose UI framework", 
        choices=["chainlit", "streamlit", "flask"], 
        default="chainlit"
    )
    config["ui_framework"] = ui_framework
    
    return config

def _configure_core_langchain(llm_provider: Optional[str]) -> dict:
    """Configure Core LangChain application specific options."""
    config = {}
    
    if not llm_provider:
        llm_provider = Prompt.ask(
            "🤖 Choose LLM provider", 
            choices=["openai", "anthropic", "ollama", "mistral"], 
            default="mistral"
        )
    config["llm_provider"] = llm_provider
    
    # Application type
    app_type = Prompt.ask(
        "🎯 Choose application type", 
        choices=["qa_system", "text_processor", "api_service", "custom"], 
        default="qa_system"
    )
    config["app_type"] = app_type
    
    # Chain types
    chain_types = []
    if Confirm.ask("🔗 Include LLM chains?", default=True):
        chain_types.append("llm")
    if Confirm.ask("🔗 Include sequential chains?", default=False):
        chain_types.append("sequential")
    if Confirm.ask("🔗 Include retrieval chains?", default=app_type == "qa_system"):
        chain_types.append("retrieval")
    
    config["chain_types"] = chain_types
    
    # Tool integration
    include_tools = Confirm.ask("🛠️ Include custom tools?", default=True)
    config["include_tools"] = include_tools
    
    ui_framework = Prompt.ask(
        "🖥️ Choose UI framework", 
        choices=["streamlit", "fastapi", "cli"], 
        default="streamlit"
    )
    config["ui_framework"] = ui_framework
    
    return config

def _show_configuration_summary(answers: dict):
    """Display configuration summary."""
    console.print("\n📋 [bold]Project Configuration:[/bold]")
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")
    
    for key, value in answers.items():
        if isinstance(value, list):
            value_str = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            value_str = str(value)
        else:
            value_str = str(value)
        table.add_row(f"• {key}", value_str)
    
    console.print(table)

def _generate_project(template_dir: Path, name: str, answers: dict):
    """Generate the project using Copier."""
    destination = Path.cwd() / name

    try:
        # Validate choices before running Copier
        if "llm_provider" in answers and answers["llm_provider"] not in ["openai", "ollama", "mistral", "anthropic"]:
            raise ValueError(f"Invalid LLM provider: {answers['llm_provider']}")

        console.print(f"\n🔄 Generating project in: [cyan]{destination}[/cyan]")
        copier.run_copy(
            src_path=str(template_dir),
            dst_path=str(destination),
            data=answers,
            answers_file=None,
            quiet=False,
        )
        console.print(f"\n✅ [bold green]Project '{name}' created successfully![/bold green]")
        console.print(f"📁 Location: [cyan]{destination}[/cyan]")
        console.print("\n🚀 [bold]Next Steps:[/bold]")
        console.print(f"   1. cd {name}")
        console.print("   2. Create a new GitHub repository")
        console.print("   3. Push the code to GitHub")
        console.print("   4. Open in GitHub Codespaces")
        console.print("   5. Set up environment variables (.env)")
    except ValueError as e:
        console.print(f"❌ [red]Configuration Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ [red]Error generating project: {e}[/red]")
        import traceback
        console.print(f"[dim]Debug info: {traceback.format_exc()}[/dim]")
        raise typer.Exit(1)

@app.command(
    help="Update an existing project with the latest template changes.",
    rich_help_panel="Project Commands"
)
def update():
    """Update an existing project with the latest template changes."""
    current_dir = Path.cwd()
    
    # Check if we're in a copier-generated project
    copier_answers_file = current_dir / ".copier-answers.yml"
    
    if not copier_answers_file.exists():
        console.print("❌ [red]This doesn't appear to be a Copier-generated project.[/red]")
        console.print("💡 The update command only works in directories created with ai-bootstrap.")
        raise typer.Exit(1)
    
    console.print("🔄 [bold blue]Updating project with latest template changes...[/bold blue]\n")
    
    try:
        # Run copier update
        copier.run_update(
            dst_path=str(current_dir),
            answers_file=str(copier_answers_file),
            conflict="rej",  # Create .rej files for conflicts
        )
        
        console.print("✅ [bold green]Project updated successfully![/bold green]")
        console.print("\n📝 [bold]What to do next:[/bold]")
        console.print("   • Review any .rej files for merge conflicts")
        console.print("   • Test your application to ensure everything works")
        console.print("   • Commit the updated files to your repository")
        
    except Exception as e:
        console.print(f"❌ [red]Error updating project: {e}[/red]")
        console.print("\n💡 [yellow]Tips:[/yellow]")
        console.print("   • Make sure you've committed your local changes first")
        console.print("   • Check that your internet connection is working")
        console.print("   • Ensure the original template repository is accessible")
        raise typer.Exit(1)

@app.command(
    "list-blueprints",
    help="List available project blueprints and their features.",
    rich_help_panel="Discovery"
)
def list_blueprints():
    """List available project blueprints."""
    console.print("\n📋 [bold blue]Available Project Blueprints:[/bold blue]\n")

    for key, blueprint in BLUEPRINTS.items():
        console.print(f"🎯 [bold cyan]{key}[/bold cyan] - {blueprint['name']}")
        console.print(f"   📝 {blueprint['description']}")
        console.print(f"   🔧 Frameworks: {', '.join(blueprint['frameworks'])}")
        console.print(f"   ✨ Features: {', '.join(blueprint['features'])}")
        console.print()

    console.print("💡 [bold]Usage:[/bold]")
    console.print("   ai-bootstrap create --type <blueprint-key>")
    console.print("   ai-bootstrap create --chat  # Use AI to analyze requirements")
    console.print("   ai-bootstrap create  # Interactive mode")

@app.command(
    "help-table",
    help="Show all commands and their arguments in a table.",
    rich_help_panel="Discovery"
)
def help_table():
    """Display all commands and their arguments in a table format."""
    from rich.table import Table

    commands = [
        {
            "command": "create",
            "description": "Create a new AI/ML project from a blueprint, interactively or with AI-powered planning.",
            "args": [
                "--name/-n", "--type/-t", "--llm", "--framework", "--vector-store",
                "--ui-framework", "--python", "--chat", "--planner-provider"
            ]
        },
        {
            "command": "update",
            "description": "Update an existing project with the latest template changes.",
            "args": []
        },
        {
            "command": "list-blueprints",
            "description": "List available project blueprints and their features.",
            "args": []
        },
        {
            "command": "help-table",
            "description": "Show all commands and their arguments in a table.",
            "args": []
        }
    ]

    table = Table(title="AI Bootstrap CLI Commands", show_lines=True)
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Arguments", style="magenta")
    table.add_column("Description", style="white")

    for cmd in commands:
        args = "\n".join(cmd["args"]) if cmd["args"] else "-"
        table.add_row(cmd["command"], args, cmd["description"])

    console.print(table)
    console.print("\n💡 For detailed help on a command, run: [bold]ai-bootstrap  --help[/bold]")


if __name__ == "__main__":
    app()
