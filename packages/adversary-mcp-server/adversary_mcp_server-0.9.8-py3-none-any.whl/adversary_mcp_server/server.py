"""Adversary MCP Server - Security vulnerability scanning and exploit generation."""

import asyncio
import json
import json as json_lib
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server  # Add this import
from mcp.types import ServerCapabilities, Tool, ToolsCapability
from pydantic import BaseModel

from . import get_version
from .credentials import CredentialManager

# Set up centralized logging
from .logger import get_logger
from .scanner.diff_scanner import GitDiffScanner
from .scanner.exploit_generator import ExploitGenerator
from .scanner.false_positive_manager import FalsePositiveManager
from .scanner.scan_engine import EnhancedScanResult, ScanEngine
from .scanner.types import Category, Language, LanguageSupport, Severity, ThreatMatch
from .threat_modeling import DiagramGenerator, ThreatModelBuilder
from .threat_modeling.models import Severity as ThreatSeverity

logger = get_logger("server")


class AdversaryToolError(Exception):
    """Exception raised when a tool operation fails."""

    pass


class ScanRequest(BaseModel):
    """Request for scanning code or files."""

    content: str | None = None
    file_path: str | None = None
    language: str | None = None
    severity_threshold: str | None = "medium"
    include_exploits: bool = True
    use_llm: bool = False


class ScanResult(BaseModel):
    """Result of a security scan."""

    threats: list[dict[str, Any]]
    summary: dict[str, Any]
    metadata: dict[str, Any]


class AdversaryMCPServer:
    """MCP server for security vulnerability scanning and exploit generation."""

    def __init__(self) -> None:
        """Initialize the Adversary MCP server."""
        logger.info("=== Initializing Adversary MCP Server ===")
        self.server: Server = Server("adversary-mcp-server")
        self.credential_manager = CredentialManager()
        logger.debug("Created credential manager")

        # Get configuration to determine scanner settings
        logger.debug("Loading configuration...")
        config = self.credential_manager.load_config()
        logger.info(
            f"Configuration loaded - LLM analysis: {config.enable_llm_analysis}, Semgrep: {config.enable_semgrep_scanning}"
        )

        logger.info("Initializing scan engine...")
        self.scan_engine = ScanEngine(
            self.credential_manager,
            enable_llm_analysis=config.enable_llm_analysis,
            enable_semgrep_analysis=config.enable_semgrep_scanning,
        )
        logger.debug("Scan engine initialized")

        logger.debug("Initializing exploit generator...")
        self.exploit_generator = ExploitGenerator(self.credential_manager)

        logger.debug("Initializing diff scanner...")
        self.diff_scanner = GitDiffScanner(self.scan_engine)

        logger.debug("Initializing false positive manager...")

        # Set up server handlers
        logger.debug("Setting up server handlers...")
        self._setup_handlers()
        logger.info("=== Adversary MCP Server initialization complete ===")

    def _setup_handlers(self) -> None:
        """Set up server request handlers."""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available adversary analysis tools."""
            return [
                Tool(
                    name="adv_scan_code",
                    description="Scan source code for security vulnerabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "Source code content to scan",
                            },
                            "language": {
                                "type": "string",
                                "description": "Programming language",
                                "enum": LanguageSupport.get_language_enum_values(),
                            },
                            "severity_threshold": {
                                "type": "string",
                                "description": "Minimum severity threshold (low, medium, high, critical)",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium",
                            },
                            "include_exploits": {
                                "type": "boolean",
                                "description": "Whether to include exploit examples",
                                "default": True,
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Whether to include LLM analysis prompts (for use with your client's LLM)",
                                "default": False,
                            },
                            "use_semgrep": {
                                "type": "boolean",
                                "description": "Whether to include Semgrep analysis",
                                "default": True,
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format for results",
                                "enum": ["text", "json"],
                                "default": "text",
                            },
                            "output": {
                                "type": "string",
                                "description": "Path to output file for JSON results (optional, defaults to .adversary.json in project root)",
                            },
                        },
                        "required": ["content", "language"],
                    },
                ),
                Tool(
                    name="adv_scan_file",
                    description="Scan a file for security vulnerabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to the file to scan",
                            },
                            "severity_threshold": {
                                "type": "string",
                                "description": "Minimum severity threshold",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium",
                            },
                            "include_exploits": {
                                "type": "boolean",
                                "description": "Whether to include exploit examples",
                                "default": True,
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Whether to include LLM analysis prompts (for use with your client's LLM)",
                                "default": False,
                            },
                            "use_semgrep": {
                                "type": "boolean",
                                "description": "Whether to include Semgrep analysis",
                                "default": True,
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format for results",
                                "enum": ["text", "json"],
                                "default": "text",
                            },
                            "output": {
                                "type": "string",
                                "description": "Path to output file for JSON results (optional, defaults to .adversary.json in project root)",
                            },
                        },
                        "required": ["file_path"],
                    },
                ),
                Tool(
                    name="adv_scan_folder",
                    description="Scan a folder for security vulnerabilities",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "directory_path": {
                                "type": "string",
                                "description": "Path to the directory to scan",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to scan subdirectories",
                                "default": True,
                            },
                            "severity_threshold": {
                                "type": "string",
                                "description": "Minimum severity threshold",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium",
                            },
                            "include_exploits": {
                                "type": "boolean",
                                "description": "Whether to include exploit examples",
                                "default": True,
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Whether to include LLM analysis prompts (for use with your client's LLM)",
                                "default": False,
                            },
                            "use_semgrep": {
                                "type": "boolean",
                                "description": "Whether to include Semgrep analysis",
                                "default": True,
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format for results",
                                "enum": ["text", "json"],
                                "default": "text",
                            },
                            "output": {
                                "type": "string",
                                "description": "Path to output file for JSON results (optional, defaults to .adversary.json in project root)",
                            },
                        },
                        "required": ["directory_path"],
                    },
                ),
                Tool(
                    name="adv_diff_scan",
                    description="Scan security vulnerabilities in git diff changes between branches",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source_branch": {
                                "type": "string",
                                "description": "Source branch name (e.g., 'feature-branch')",
                            },
                            "target_branch": {
                                "type": "string",
                                "description": "Target branch name (e.g., 'main')",
                            },
                            "working_directory": {
                                "type": "string",
                                "description": "Working directory path for git operations (defaults to current directory)",
                                "default": ".",
                            },
                            "severity_threshold": {
                                "type": "string",
                                "description": "Minimum severity threshold (low, medium, high, critical)",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium",
                            },
                            "include_exploits": {
                                "type": "boolean",
                                "description": "Whether to include exploit examples",
                                "default": True,
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Whether to include LLM analysis prompts (for use with your client's LLM)",
                                "default": False,
                            },
                            "use_semgrep": {
                                "type": "boolean",
                                "description": "Whether to include Semgrep analysis",
                                "default": True,
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format for results",
                                "enum": ["text", "json"],
                                "default": "text",
                            },
                        },
                        "required": ["source_branch", "target_branch"],
                    },
                ),
                Tool(
                    name="adv_generate_exploit",
                    description="Generate exploit for a specific vulnerability",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vulnerability_type": {
                                "type": "string",
                                "description": "Type of vulnerability (sql_injection, xss, etc.)",
                            },
                            "code_context": {
                                "type": "string",
                                "description": "Vulnerable code context",
                            },
                            "target_language": {
                                "type": "string",
                                "description": "Target programming language",
                                "enum": LanguageSupport.get_language_enum_values(),
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Whether to include LLM exploit generation prompts",
                                "default": False,
                            },
                        },
                        "required": [
                            "vulnerability_type",
                            "code_context",
                            "target_language",
                        ],
                    },
                ),
                Tool(
                    name="adv_configure_settings",
                    description="Configure adversary MCP server settings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "severity_threshold": {
                                "type": "string",
                                "description": "Default severity threshold",
                                "enum": ["low", "medium", "high", "critical"],
                            },
                            "exploit_safety_mode": {
                                "type": "boolean",
                                "description": "Enable safety mode for exploit generation",
                            },
                            "enable_llm_analysis": {
                                "type": "boolean",
                                "description": "Enable LLM-based analysis",
                            },
                            "enable_exploit_generation": {
                                "type": "boolean",
                                "description": "Enable exploit generation",
                            },
                        },
                        "required": [],
                    },
                ),
                Tool(
                    name="adv_get_status",
                    description="Get server status and configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="adv_get_version",
                    description="Get version information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                ),
                Tool(
                    name="adv_mark_false_positive",
                    description="Mark a finding as a false positive",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "finding_uuid": {
                                "type": "string",
                                "description": "UUID of the finding to mark as false positive",
                            },
                            "adversary_file_path": {
                                "type": "string",
                                "description": "Path to the .adversary.json file containing the finding",
                            },
                            "reason": {
                                "type": "string",
                                "description": "Reason for marking as false positive",
                            },
                        },
                        "required": ["finding_uuid", "adversary_file_path"],
                    },
                ),
                Tool(
                    name="adv_unmark_false_positive",
                    description="Remove false positive marking from a finding",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "finding_uuid": {
                                "type": "string",
                                "description": "UUID of the finding to unmark",
                            },
                            "adversary_file_path": {
                                "type": "string",
                                "description": "Path to the .adversary.json file containing the finding",
                            },
                        },
                        "required": ["finding_uuid", "adversary_file_path"],
                    },
                ),
                Tool(
                    name="adv_list_false_positives",
                    description="List all findings marked as false positives",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "adversary_file_path": {
                                "type": "string",
                                "description": "Path to the .adversary.json file to list false positives from",
                            },
                        },
                        "required": ["adversary_file_path"],
                    },
                ),
                Tool(
                    name="adv_threat_model",
                    description="Generate STRIDE-based threat model from source code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_name": {
                                "type": "string",
                                "description": "Name of the repository/project to analyze (e.g., 'hello-world', 'my-app')",
                            },
                            "source_path": {
                                "type": "string",
                                "description": "Optional: explicit path to analyze (overrides repo_name discovery)",
                            },
                            "search_depth": {
                                "type": "integer",
                                "description": "Optional: maximum directory depth to search for repositories (default: 3)",
                                "minimum": 1,
                                "maximum": 5,
                                "default": 3,
                            },
                            "output_file": {
                                "type": "string",
                                "description": "Optional: output file path (defaults to threat_model.{format} in project root)",
                            },
                            "include_threats": {
                                "type": "boolean",
                                "description": "Include STRIDE threat analysis in output",
                                "default": True,
                            },
                            "severity_threshold": {
                                "type": "string",
                                "description": "Minimum severity threshold for threats",
                                "enum": ["low", "medium", "high", "critical"],
                                "default": "medium",
                            },
                            "output_format": {
                                "type": "string",
                                "description": "Output format for threat model",
                                "enum": ["json", "markdown"],
                                "default": "markdown",
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Enable LLM-enhanced threat analysis for additional insights",
                                "default": False,
                            },
                        },
                        "anyOf": [
                            {"required": ["repo_name"]},
                            {"required": ["source_path"]},
                        ],
                    },
                ),
                Tool(
                    name="adv_diagram",
                    description="Generate Mermaid.js architecture diagram from threat model",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "repo_name": {
                                "type": "string",
                                "description": "Name of the repository/project to analyze (e.g., 'verisapi', 'my-app')",
                            },
                            "source_path": {
                                "type": "string",
                                "description": "Optional: explicit path to source file/directory OR path to existing threat model JSON file (overrides repo_name discovery)",
                            },
                            "search_depth": {
                                "type": "integer",
                                "description": "Optional: maximum directory depth to search for repositories (default: 3)",
                                "minimum": 1,
                                "maximum": 5,
                                "default": 3,
                            },
                            "output_file": {
                                "type": "string",
                                "description": "Optional: path for Mermaid diagram output file (.mmd extension) (defaults to threat_diagram.mmd in project root)",
                            },
                            "diagram_type": {
                                "type": "string",
                                "description": "Type of Mermaid diagram to generate",
                                "enum": ["flowchart"],
                                "default": "flowchart",
                            },
                            "show_threats": {
                                "type": "boolean",
                                "description": "Highlight components with threats in diagram",
                                "default": True,
                            },
                            "layout_direction": {
                                "type": "string",
                                "description": "Layout direction for diagram",
                                "enum": ["TD", "LR", "BT", "RL"],
                                "default": "TD",
                            },
                            "use_llm": {
                                "type": "boolean",
                                "description": "Enable LLM-enhanced threat analysis when generating new threat models",
                                "default": False,
                            },
                        },
                        "anyOf": [
                            {"required": ["repo_name"]},
                            {"required": ["source_path"]},
                        ],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: dict[str, Any]
        ) -> list[types.TextContent]:
            """Call the specified tool with the given arguments."""
            try:
                logger.info(f"=== TOOL CALL START: {name} ===")
                logger.debug(f"Tool arguments: {arguments}")

                if name == "adv_scan_code":
                    logger.info("Handling scan_code request")
                    return await self._handle_scan_code(arguments)

                elif name == "adv_scan_file":
                    logger.info("Handling scan_file request")
                    return await self._handle_scan_file(arguments)

                elif name == "adv_scan_folder":
                    logger.info("Handling scan_folder request")
                    return await self._handle_scan_directory(arguments)

                elif name == "adv_diff_scan":
                    logger.info("Handling diff_scan request")
                    return await self._handle_diff_scan(arguments)

                elif name == "adv_generate_exploit":
                    logger.info("Handling generate_exploit request")
                    return await self._handle_generate_exploit(arguments)

                elif name == "adv_configure_settings":
                    logger.info("Handling configure_settings request")
                    return await self._handle_configure_settings(arguments)

                elif name == "adv_get_status":
                    logger.info("Handling get_status request")
                    return await self._handle_get_status()

                elif name == "adv_get_version":
                    logger.info("Handling get_version request")
                    return await self._handle_get_version()

                elif name == "adv_mark_false_positive":
                    logger.info("Handling mark_false_positive request")
                    return await self._handle_mark_false_positive(arguments)

                elif name == "adv_unmark_false_positive":
                    logger.info("Handling unmark_false_positive request")
                    return await self._handle_unmark_false_positive(arguments)

                elif name == "adv_list_false_positives":
                    logger.info("Handling list_false_positives request")
                    return await self._handle_list_false_positives(arguments)

                elif name == "adv_threat_model":
                    logger.info("Handling threat_model request")
                    return await self._handle_generate_threat_model(arguments)

                elif name == "adv_diagram":
                    logger.info("Handling diagram request")
                    return await self._handle_generate_diagram(arguments)

                else:
                    logger.error(f"Unknown tool requested: {name}")
                    raise AdversaryToolError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool {name} execution failed: {e}")
                logger.debug("Tool {name} error details", exc_info=True)
                raise AdversaryToolError(f"Tool {name} failed: {str(e)}")

            finally:
                logger.info(f"=== TOOL CALL END: {name} ===")

    async def _handle_scan_code(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle code scanning request."""
        try:
            logger.info("Starting code scan")

            content = arguments["content"]
            language_str = arguments["language"]
            severity_threshold = arguments.get("severity_threshold", "medium")
            include_exploits = arguments.get("include_exploits", True)
            use_llm = arguments.get("use_llm", False)
            use_semgrep = arguments.get("use_semgrep", True)
            output_format = arguments.get("output_format", "text")
            output_path = arguments.get("output")
            # For scan_code operations, use user data directory since there's no specific project context
            default_directory = str(
                Path.home() / ".local" / "share" / "adversary-mcp-server"
            )
            working_directory = arguments.get("working_directory", default_directory)
            # Convert to absolute path for better logging
            working_directory_abs = str(Path(working_directory).resolve())
            logger.info(f"Code scan - working_directory: {working_directory_abs}")

            # Resolve output path if provided
            output_path_resolved = None
            if output_path:
                output_path_resolved = self._resolve_file_path(
                    output_path, "output path"
                )
                logger.info(f"Code scan - output_path resolved: {output_path_resolved}")

            logger.debug(
                f"Code scan parameters - Language: {language_str}, "
                f"Severity: {severity_threshold}, LLM: {use_llm}, "
                f"Semgrep: {use_semgrep}"
            )

            # Convert language string to enum
            language = Language(language_str)
            severity_enum = Severity(severity_threshold)

            logger.info(f"Scanning {len(content)} characters of {language.value} code")

            # Scan the code using enhanced scanner (rules-based)
            logger.debug("Calling scan_engine.scan_code...")
            scan_result = await self.scan_engine.scan_code(
                source_code=content,
                file_path="input.code",
                language=language,
                use_llm=use_llm,
                use_semgrep=use_semgrep,
                severity_threshold=severity_enum,
            )
            logger.info(
                f"Code scan completed - found {len(scan_result.all_threats)} threats"
            )

            # Generate exploits if requested
            if include_exploits:
                logger.info("Generating exploits for discovered threats...")
                exploit_count = 0
                for threat in scan_result.all_threats:
                    try:
                        exploits = self.exploit_generator.generate_exploits(
                            threat, content, False  # Don't use LLM directly
                        )
                        threat.exploit_examples = exploits
                        if exploits:
                            exploit_count += len(exploits)
                    except Exception as e:
                        logger.warning(
                            f"Failed to generate exploits for {threat.rule_id}: {e}"
                        )
                logger.info(f"Generated {exploit_count} total exploit examples")
            else:
                logger.debug("Exploit generation skipped")

            # Format results based on output format
            if output_format == "json":
                logger.debug("Formatting results as JSON")
                result = self._format_json_scan_results(
                    scan_result, "code", working_directory
                )
                # Save JSON results to custom path or default location
                save_path = output_path_resolved if output_path_resolved else "."
                saved_path = self._save_scan_results_json(result, save_path)
                if saved_path:
                    logger.info(f"JSON results saved to: {saved_path}")
                else:
                    logger.warning("Failed to save JSON results")
            else:
                logger.debug("Formatting results as text")
                # Format results with enhanced information
                result = self._format_enhanced_scan_results(scan_result, "code")

                # Add LLM prompts if requested
                if use_llm:
                    logger.debug("Adding LLM analysis prompts to results")
                    result += self._add_llm_analysis_prompts(
                        content, language, "input.code"
                    )

                    # Add LLM exploit prompts for each threat found
                    if include_exploits and scan_result.all_threats:
                        logger.debug("Adding LLM exploit prompts to results")
                        result += self._add_llm_exploit_prompts(
                            scan_result.all_threats, content
                        )

                # Auto-save JSON results (regardless of output format)
                # Use output_path_resolved if provided, otherwise use working_directory (user data directory)
                save_location = (
                    output_path_resolved if output_path_resolved else working_directory
                )
                logger.info(
                    f"🔧 adv_scan_code auto-save: output_path_resolved={output_path_resolved}, working_directory={working_directory_abs}, save_location={save_location}"
                )
                json_result = self._format_json_scan_results(
                    scan_result, "code", working_directory
                )
                self._save_scan_results_json(json_result, save_location)

            logger.info("Code scan completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Code scanning failed: {e}")
            logger.debug("Code scan error details", exc_info=True)
            raise AdversaryToolError(f"Code scanning failed: {e}")

    async def _handle_scan_file(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle file scanning request."""
        try:
            logger.info("Starting file scan")

            # Get initial file path and working directory
            input_file_path = arguments["file_path"]
            working_directory = arguments.get("working_directory", str(Path.cwd()))

            # Resolve file path relative to working directory if it's relative
            file_path = Path(input_file_path)
            if not file_path.is_absolute():
                file_path = Path(working_directory) / file_path
            file_path = file_path.resolve()

            severity_threshold = arguments.get("severity_threshold", "medium")
            include_exploits = arguments.get("include_exploits", True)
            use_llm = arguments.get("use_llm", False)
            use_semgrep = arguments.get("use_semgrep", True)
            output_format = arguments.get("output_format", "text")
            output_path = arguments.get("output")

            # Convert to absolute path for better logging
            working_directory_abs = str(Path(working_directory).resolve())
            logger.info(f"File scan - working_directory: {working_directory_abs}")

            # Resolve output path if provided
            output_path_resolved = None
            if output_path:
                output_path_resolved = self._resolve_file_path(
                    output_path, "output path"
                )
                logger.info(f"File scan - output_path resolved: {output_path_resolved}")

            logger.info(f"Scanning file: {file_path}")
            logger.debug(
                f"File scan parameters - Severity: {severity_threshold}, "
                f"LLM: {use_llm}, Semgrep: {use_semgrep}"
            )

            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                raise AdversaryToolError(f"File not found: {file_path}")

            # Convert severity threshold to enum
            severity_enum = Severity(severity_threshold)

            # Scan the file using enhanced scanner (rules-based)
            logger.debug("Calling scan_engine.scan_file...")
            scan_result = await self.scan_engine.scan_file(
                file_path=file_path,
                use_llm=use_llm,
                use_semgrep=use_semgrep,
                severity_threshold=severity_enum,
            )
            logger.info(
                f"File scan completed - found {len(scan_result.all_threats)} threats"
            )

            # Generate exploits if requested
            if include_exploits:
                logger.info("Generating exploits for discovered threats...")
                file_content = ""
                try:
                    with open(file_path, encoding="utf-8") as f:
                        file_content = f.read()
                    logger.debug(f"Read {len(file_content)} characters from file")
                except Exception as e:
                    logger.warning(f"Could not read file content for exploits: {e}")

                exploit_count = 0
                for threat in scan_result.all_threats:
                    try:
                        exploits = self.exploit_generator.generate_exploits(
                            threat, file_content, False  # Don't use LLM directly
                        )
                        threat.exploit_examples = exploits
                        if exploits:
                            exploit_count += len(exploits)
                    except Exception as e:
                        logger.warning(
                            f"Failed to generate exploits for {threat.rule_id}: {e}"
                        )
                logger.info(f"Generated {exploit_count} total exploit examples")
            else:
                logger.debug("Exploit generation skipped")

            # Format results based on output format
            if output_format == "json":
                logger.debug("Formatting results as JSON")
                result = self._format_json_scan_results(
                    scan_result, str(file_path), working_directory
                )
                # Save JSON results to custom path or default location
                save_path = output_path_resolved if output_path_resolved else "."
                saved_path = self._save_scan_results_json(result, save_path)
                if saved_path:
                    logger.info(f"JSON results saved to: {saved_path}")
                else:
                    logger.warning("Failed to save JSON results")
            else:
                logger.debug("Formatting results as text")
                # Format results with enhanced information
                result = self._format_enhanced_scan_results(scan_result, str(file_path))

                # Add LLM prompts if requested
                if use_llm:
                    logger.debug("Adding LLM analysis prompts to results")
                    # Read file content for LLM analysis
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            file_content = f.read()

                        # Detect language from file extension
                        language = self.scan_engine._detect_language(file_path)

                        result += self._add_llm_analysis_prompts(
                            file_content, language, str(file_path)
                        )

                        # Add LLM exploit prompts for each threat found
                        if include_exploits and scan_result.all_threats:
                            logger.debug("Adding LLM exploit prompts to results")
                            result += self._add_llm_exploit_prompts(
                                scan_result.all_threats, file_content
                            )

                    except Exception as e:
                        logger.warning(f"Could not read file for LLM analysis: {e}")
                        result += f"\n\n⚠️ **LLM Analysis:** Could not read file for LLM analysis: {e}\n"

                # Auto-save JSON results to project root (regardless of output format)
                logger.info(
                    f"🔧 adv_scan_file auto-save: file_path={file_path}, working_directory={working_directory_abs}"
                )
                json_result = self._format_json_scan_results(
                    scan_result, str(file_path), working_directory
                )
                self._save_scan_results_json(json_result, working_directory)

            logger.info("File scan completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"File scanning failed: {e}")
            logger.debug("File scan error details", exc_info=True)
            raise AdversaryToolError(f"File scanning failed: {e}")

    async def _handle_scan_directory(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle directory scanning request."""
        try:
            logger.info("Starting directory scan")
            directory_path = Path(arguments["directory_path"]).resolve()
            recursive = arguments.get("recursive", True)
            severity_threshold = arguments.get("severity_threshold", "medium")
            include_exploits = arguments.get("include_exploits", True)
            use_llm = arguments.get("use_llm", False)
            use_semgrep = arguments.get("use_semgrep", True)
            output_format = arguments.get("output_format", "text")
            output_path = arguments.get("output")

            # Resolve output path if provided
            output_path_resolved = None
            if output_path:
                output_path_resolved = self._resolve_file_path(
                    output_path, "output path"
                )
                logger.info(
                    f"Directory scan - output_path resolved: {output_path_resolved}"
                )

            logger.info(f"Scanning directory: {directory_path}")
            logger.debug(
                f"Directory scan parameters - Recursive: {recursive}, "
                f"Severity: {severity_threshold}, LLM: {use_llm}, "
                f"Semgrep: {use_semgrep}"
            )

            if not directory_path.exists():
                logger.error(f"Directory not found: {directory_path}")
                raise AdversaryToolError(f"Directory not found: {directory_path}")

            # Convert severity threshold to enum
            severity_enum = Severity(severity_threshold)

            # Scan the directory using enhanced scanner (rules-based)
            logger.debug("Calling scan_engine.scan_directory...")
            scan_results = await self.scan_engine.scan_directory(
                directory_path=directory_path,
                recursive=recursive,
                use_llm=use_llm,
                use_semgrep=use_semgrep,
                severity_threshold=severity_enum,
                max_files=50,  # Limit files for performance
            )

            logger.info(
                f"Directory scan completed - processed {len(scan_results)} files"
            )

            # Combine all threats from all files
            all_threats = []
            for scan_result in scan_results:
                all_threats.extend(scan_result.all_threats)

            logger.info(f"Total threats found across all files: {len(all_threats)}")

            # Generate exploits if requested (limited for directory scans)
            if include_exploits:
                logger.info(
                    "Generating exploits for discovered threats (limited to first 10)..."
                )
                exploit_count = 0
                for threat in all_threats[:10]:  # Limit to first 10 threats
                    try:
                        exploits = self.exploit_generator.generate_exploits(
                            threat, "", False  # Don't use LLM directly
                        )
                        threat.exploit_examples = exploits
                        if exploits:
                            exploit_count += len(exploits)
                    except Exception as e:
                        logger.warning(
                            f"Failed to generate exploits for {threat.rule_id}: {e}"
                        )
                logger.info(f"Generated {exploit_count} total exploit examples")
            else:
                logger.debug("Exploit generation skipped")

            # Format results based on output format
            if output_format == "json":
                logger.debug("Formatting results as JSON")
                result = self._format_json_directory_results(
                    scan_results, str(directory_path), str(directory_path)
                )
                # Save JSON results to custom path or default location
                save_path = output_path_resolved if output_path_resolved else "."
                saved_path = self._save_scan_results_json(result, save_path)
                if saved_path:
                    logger.info(f"JSON results saved to: {saved_path}")
                else:
                    logger.warning("Failed to save JSON results")
            else:
                logger.debug("Formatting results as text")
                # Format results with enhanced information
                result = self._format_directory_scan_results(
                    scan_results, str(directory_path)
                )

                # Add LLM prompts if requested (only for files with issues)
                if use_llm and scan_results:
                    logger.debug(
                        "Adding LLM analysis prompts for files with issues (first 3)"
                    )
                    result += "\n\n# 🤖 LLM Analysis Prompts\n\n"
                    result += "For enhanced LLM-based analysis, use the following prompts with your client's LLM:\n\n"
                    result += "**Note:** Directory scans include prompts for the first 3 files with security issues.\n\n"

                    files_with_issues = [sr for sr in scan_results if sr.all_threats][
                        :3
                    ]
                    for i, scan_result in enumerate(files_with_issues, 1):
                        try:
                            with open(scan_result.file_path, encoding="utf-8") as f:
                                file_content = f.read()

                            # Detect language
                            language = self.scan_engine._detect_language(
                                Path(scan_result.file_path)
                            )

                            result += f"## File {i}: {scan_result.file_path}\n\n"
                            result += self._add_llm_analysis_prompts(
                                file_content,
                                language,
                                str(scan_result.file_path),
                                include_header=False,
                            )

                        except Exception as e:
                            logger.warning(
                                f"Could not read {scan_result.file_path} for LLM analysis: {e}"
                            )
                            result += f"⚠️ Could not read {scan_result.file_path} for LLM analysis: {e}\n\n"

                # Auto-save JSON results to project root (regardless of output format)
                logger.info(
                    f"🔧 adv_scan_folder auto-save: directory_path={directory_path}"
                )
                json_result = self._format_json_directory_results(
                    scan_results, str(directory_path), str(directory_path)
                )
                self._save_scan_results_json(json_result, str(directory_path))

            logger.info("Directory scan completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Directory scanning failed: {e}")
            logger.debug("Directory scan error details", exc_info=True)
            raise AdversaryToolError(f"Directory scanning failed: {e}")

    async def _handle_diff_scan(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle git diff scanning request."""
        try:
            source_branch = arguments["source_branch"]
            target_branch = arguments["target_branch"]
            working_directory = arguments.get("working_directory", ".")
            # Convert to absolute path for better logging
            working_directory_abs = str(Path(working_directory).resolve())
            logger.info(f"Diff scan - working_directory: {working_directory_abs}")
            severity_threshold = arguments.get("severity_threshold", "medium")
            include_exploits = arguments.get("include_exploits", True)
            use_llm = arguments.get("use_llm", False)
            use_semgrep = arguments.get("use_semgrep", True)
            output_format = arguments.get("output_format", "text")

            # Convert severity threshold to enum
            severity_enum = Severity(severity_threshold)

            # Convert working directory to Path object
            working_dir_path = Path(working_directory).resolve()

            # Get diff summary first
            diff_summary = self.diff_scanner.get_diff_summary(
                source_branch, target_branch, working_dir_path
            )

            # Check if there's an error in the summary
            if "error" in diff_summary:
                raise AdversaryToolError(
                    f"Git diff operation failed: {diff_summary['error']}"
                )

            # Scan the diff changes
            scan_results = await self.diff_scanner.scan_diff(
                source_branch=source_branch,
                target_branch=target_branch,
                working_dir=working_dir_path,
                use_llm=use_llm,
                use_semgrep=use_semgrep,
                severity_threshold=severity_enum,
            )

            # Collect all threats
            all_threats = []
            for file_path, file_scan_results in scan_results.items():
                for scan_result in file_scan_results:
                    all_threats.extend(scan_result.all_threats)

            # Generate exploits if requested
            if include_exploits:
                logger.info("Generating exploits for discovered threats...")
                exploit_count = 0
                for threat in all_threats[:10]:  # Limit to first 10 threats
                    try:
                        exploits = self.exploit_generator.generate_exploits(
                            threat, "", False  # Don't use LLM directly
                        )
                        threat.exploit_examples = exploits
                        if exploits:
                            exploit_count += len(exploits)
                    except Exception as e:
                        logger.warning(
                            f"Failed to generate exploits for {threat.rule_id}: {e}"
                        )
                logger.info(f"Generated {exploit_count} total exploit examples")
            else:
                logger.debug("Exploit generation skipped")

            # Format results based on output format
            if output_format == "json":
                logger.debug("Formatting results as JSON")
                result = self._format_json_diff_results(
                    scan_results,
                    diff_summary,
                    f"{source_branch}..{target_branch}",
                    working_directory,
                )
                # Auto-save JSON results to project root
                self._save_scan_results_json(result, ".")
            else:
                logger.debug("Formatting results as text")
                # Format results
                result = self._format_diff_scan_results(
                    scan_results, diff_summary, source_branch, target_branch
                )

                # Add LLM prompts if requested
                if use_llm and scan_results:
                    logger.debug("Adding LLM analysis prompts for diff scan")
                    result += "\n\n# 🤖 LLM Analysis Prompts\n\n"
                    result += "For enhanced LLM-based analysis, use the following prompts with your client's LLM:\n\n"
                    result += "**Note:** Diff scans include prompts for changed code in files with security issues.\n\n"

                    files_with_issues = [
                        (path, results)
                        for path, results in scan_results.items()
                        if any(r.all_threats for r in results)
                    ][:3]
                    for i, (file_path, file_scan_results) in enumerate(
                        files_with_issues, 1
                    ):
                        try:
                            # Get the changed code from the diff
                            diff_changes = self.diff_scanner.get_diff_changes(
                                source_branch, target_branch, working_dir_path
                            )
                            if file_path in diff_changes:
                                chunks = diff_changes[file_path]
                                # For LLM analysis, include minimal context for better understanding
                                changed_code = "\n".join(
                                    chunk.get_added_lines_with_minimal_context()
                                    for chunk in chunks
                                )

                                # Detect language
                                language = self.scan_engine._detect_language(
                                    Path(file_path)
                                )

                                result += f"## File {i}: {file_path}\n\n"
                                result += self._add_llm_analysis_prompts(
                                    changed_code,
                                    language,
                                    file_path,
                                    include_header=False,
                                )

                        except Exception as e:
                            result += (
                                f"⚠️ Could not get changed code for {file_path}: {e}\n\n"
                            )

            logger.info("Diff scan completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Diff scanning failed: {e}")
            logger.debug("Diff scan error details", exc_info=True)
            raise AdversaryToolError(f"Diff scanning failed: {e}")

    async def _handle_generate_exploit(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle exploit generation request."""
        try:
            vulnerability_type = arguments["vulnerability_type"]
            code_context = arguments["code_context"]
            target_language = arguments["target_language"]
            use_llm = arguments.get("use_llm", False)

            # Create a mock threat match for exploit generation
            # Map vulnerability type to category
            type_to_category = {
                "sql_injection": Category.INJECTION,
                "command_injection": Category.INJECTION,
                "xss": Category.XSS,
                "deserialization": Category.DESERIALIZATION,
                "path_traversal": Category.LFI,
            }

            category = type_to_category.get(vulnerability_type, Category.INJECTION)

            mock_threat = ThreatMatch(
                rule_id=f"custom_{vulnerability_type}",
                rule_name=vulnerability_type.replace("_", " ").title(),
                description=f"Custom {vulnerability_type} vulnerability",
                category=category,
                severity=Severity.HIGH,
                file_path="custom_scan",
                line_number=1,
                code_snippet=code_context,
            )

            # Generate exploits (template-based only for now)
            exploits = self.exploit_generator.generate_exploits(
                mock_threat, code_context, False  # Don't use LLM directly
            )

            # Format results
            result = f"# {vulnerability_type.replace('_', ' ').title()} Exploit\n\n"
            result += f"**Target Language:** {target_language}\n"
            result += f"**Vulnerability Type:** {vulnerability_type}\n"
            result += "**Severity:** HIGH\n\n"
            result += "**Code Context:**\n"
            result += f"```{target_language}\n{code_context}\n```\n\n"
            result += "**Generated Exploits:**\n\n"

            if exploits:
                for i, exploit in enumerate(exploits, 1):
                    result += f"### Exploit {i}:\n\n"
                    result += f"```\n{exploit}\n```\n\n"
            else:
                result += "No template-based exploits available for this vulnerability type.\n\n"

            # Add LLM exploit prompts if requested
            if use_llm:
                result += "# 🤖 LLM Exploit Generation\n\n"
                result += "For enhanced LLM-based exploit generation, use the following prompts with your client's LLM:\n\n"

                prompt = self.exploit_generator.create_exploit_prompt(
                    mock_threat, code_context
                )

                result += "## System Prompt\n\n"
                result += f"```\n{prompt.system_prompt}\n```\n\n"
                result += "## User Prompt\n\n"
                result += f"```\n{prompt.user_prompt}\n```\n\n"
                result += "**Instructions:** Send both prompts to your LLM for enhanced exploit generation.\n"

            logger.info("Exploit generation completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Exploit generation failed: {e}")
            logger.debug("Exploit generation error details", exc_info=True)
            raise AdversaryToolError(f"Exploit generation failed: {e}")

    async def _handle_configure_settings(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle configuration settings request."""
        try:
            logger.info("Configuring server settings")
            logger.debug(f"Configuration arguments: {arguments}")

            config = self.credential_manager.load_config()
            import dataclasses

            original_config = dataclasses.replace(config)

            # Update configuration
            if "severity_threshold" in arguments:
                old_value = config.severity_threshold
                config.severity_threshold = arguments["severity_threshold"]
                logger.info(
                    f"Severity threshold changed: {old_value} -> {config.severity_threshold}"
                )

            if "exploit_safety_mode" in arguments:
                old_value = config.exploit_safety_mode
                config.exploit_safety_mode = arguments["exploit_safety_mode"]
                logger.info(
                    f"Exploit safety mode changed: {old_value} -> {config.exploit_safety_mode}"
                )

            if "enable_llm_analysis" in arguments:
                old_value = config.enable_llm_analysis
                config.enable_llm_analysis = arguments["enable_llm_analysis"]
                logger.info(
                    f"LLM analysis changed: {old_value} -> {config.enable_llm_analysis}"
                )

            if "enable_exploit_generation" in arguments:
                old_value = config.enable_exploit_generation
                config.enable_exploit_generation = arguments[
                    "enable_exploit_generation"
                ]
                logger.info(
                    f"Exploit generation changed: {old_value} -> {config.enable_exploit_generation}"
                )

            # Save configuration
            logger.debug("Saving updated configuration...")
            self.credential_manager.store_config(config)
            logger.info("Configuration saved successfully")

            # Reinitialize components with new config
            logger.debug("Reinitializing components with new configuration...")
            self.exploit_generator = ExploitGenerator(self.credential_manager)
            self.scan_engine = ScanEngine(
                self.credential_manager,
                enable_llm_analysis=config.enable_llm_analysis,
                enable_semgrep_analysis=config.enable_semgrep_scanning,
            )
            logger.info("Components reinitialized with new configuration")

            result = "✅ Configuration updated successfully!\n\n"
            result += "**Current Settings:**\n"
            result += f"- Severity Threshold: {config.severity_threshold}\n"
            result += f"- Exploit Safety Mode: {'✓ Enabled' if config.exploit_safety_mode else '✗ Disabled'}\n"
            result += f"- LLM Security Analysis: {'✓ Enabled' if config.enable_llm_analysis else '✗ Disabled'}\n"
            result += f"- Exploit Generation: {'✓ Enabled' if config.enable_exploit_generation else '✗ Disabled'}\n"

            logger.info("Server settings updated successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Failed to configure settings: {e}")
            logger.debug("Configuration error details", exc_info=True)
            raise AdversaryToolError(f"Failed to configure settings: {e}")

    async def _handle_get_status(self) -> list[types.TextContent]:
        """Handle get status request."""
        try:
            logger.info("Getting server status")
            config = self.credential_manager.load_config()

            result = "# Adversary MCP Server Status\n\n"
            result += "## Configuration\n"
            result += f"- **Severity Threshold:** {config.severity_threshold}\n"
            result += f"- **Exploit Safety Mode:** {'✓ Enabled' if config.exploit_safety_mode else '✗ Disabled'}\n"
            result += f"- **LLM Analysis:** {'✓ Enabled' if config.enable_llm_analysis else '✗ Disabled'}\n"
            result += f"- **Exploit Generation:** {'✓ Enabled' if config.enable_exploit_generation else '✗ Disabled'}\n\n"

            result += "## Security Scanners\n"

            # Semgrep status
            if self.scan_engine.semgrep_scanner.is_available():
                semgrep_status = self.scan_engine.semgrep_scanner.get_status()
                result += f"- **Semgrep Scanner:** ✓ Available (Version: {semgrep_status.get('version', 'unknown')})\n"
            else:
                result += "- **Semgrep Scanner:** ✗ Not Available\n"

            # LLM status
            if self.scan_engine.enable_llm_analysis:
                result += "- **LLM Scanner:** ✓ Enabled (Client-based)\n"
            else:
                result += "- **LLM Scanner:** ✗ Disabled\n"

            result += "\n## Components\n"
            result += "- **Scan Engine:** ✓ Active\n"
            result += "- **Exploit Generator:** ✓ Active\n"
            result += "- **LLM Integration:** ✓ Client-based (no API key required)\n"
            result += "- **False Positive Manager:** ✓ Active\n"

            logger.info("Status retrieved successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            logger.debug("Status error details", exc_info=True)
            raise AdversaryToolError(f"Failed to get status: {e}")

    async def _handle_get_version(self) -> list[types.TextContent]:
        """Handle get version request."""
        try:
            version = self._get_version()
            result = "# Adversary MCP Server\n\n"
            result += f"**Version:** {version}\n"
            result += "**LLM Integration:** Client-based (no API key required)\n"
            result += "**Supported Languages:** Python, JavaScript, TypeScript\n"

            # Count available scanners instead of rules
            scanner_count = 0
            if self.scan_engine.semgrep_scanner.is_available():
                scanner_count += 1
            if self.scan_engine.enable_llm_analysis:
                scanner_count += 1

            result += f"**Active Scanners:** {scanner_count}\n"

            logger.info("Version information retrieved successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Failed to get version: {e}")
            logger.debug("Version retrieval error details", exc_info=True)
            raise AdversaryToolError(f"Failed to get version: {e}")

    def _get_version(self) -> str:
        """Get the current version."""
        return get_version()

    def _get_current_working_directory(self) -> Path:
        """Get the current working directory.

        This method exists to allow easy mocking in tests.

        Returns:
            Path object representing current working directory
        """
        from pathlib import Path

        return Path.cwd()

    def _resolve_file_path(
        self, file_path: str, path_description: str = "file path"
    ) -> str:
        """Resolve relative file path to absolute path.

        Args:
            file_path: Path to file or directory (may be relative)
            path_description: Description of the path type for error messages

        Returns:
            Absolute path to the file or directory
        """
        from pathlib import Path

        # Handle empty or whitespace-only paths
        if not file_path or not file_path.strip():
            raise AdversaryToolError(f"{path_description} cannot be empty")

        path = Path(file_path.strip())

        # If it's already absolute, return as-is
        if path.is_absolute():
            return str(path)

        # For relative paths, resolve against the current working directory
        # This assumes the MCP client is running from the project directory
        resolved_path = self._get_current_working_directory() / path
        return str(resolved_path.resolve())

    def _resolve_adversary_file_path(self, adversary_file_path: str) -> str:
        """Resolve relative adversary file path to absolute path.

        Args:
            adversary_file_path: Path to .adversary.json file (may be relative)

        Returns:
            Absolute path to the .adversary.json file
        """
        return self._resolve_file_path(adversary_file_path, "adversary_file_path")

    def _filter_threats_by_severity(
        self, threats: list[ThreatMatch], min_severity: Severity
    ) -> list[ThreatMatch]:
        """Filter threats by minimum severity level."""
        severity_order = [
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
            Severity.CRITICAL,
        ]
        min_index = severity_order.index(min_severity)

        return [
            threat
            for threat in threats
            if severity_order.index(threat.severity) >= min_index
        ]

    def _format_scan_results(self, threats: list[ThreatMatch], scan_target: str) -> str:
        """Format scan results for display."""
        result = f"# Security Scan Results for {scan_target}\n\n"

        if not threats:
            result += "🎉 **No security vulnerabilities found!**\n\n"
            return result

        # Summary
        severity_counts = {}
        for threat in threats:
            severity = threat.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        result += "## Summary\n"
        result += f"**Total Threats:** {len(threats)}\n"
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[
                    severity
                ]
                result += f"**{severity.capitalize()}:** {count} {emoji}\n"
        result += "\n"

        # Detailed results
        result += "## Detailed Results\n\n"

        for i, threat in enumerate(threats, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(threat.severity.value, "⚪")

            result += f"### {i}. {threat.rule_name} {severity_emoji}\n"
            result += f"**File:** {threat.file_path}:{threat.line_number}\n"
            result += f"**Severity:** {threat.severity.value.capitalize()}\n"
            result += f"**Category:** {threat.category.value.capitalize()}\n"
            result += f"**Description:** {threat.description}\n\n"

            if threat.code_snippet:
                result += "**Code Context:**\n"
                result += f"```\n{threat.code_snippet}\n```\n\n"

            if threat.exploit_examples:
                result += "**Exploit Examples:**\n"
                for j, exploit in enumerate(threat.exploit_examples, 1):
                    result += f"*Example {j}:*\n"
                    result += f"```\n{exploit}\n```\n\n"

            if threat.remediation:
                result += f"**Remediation:** {threat.remediation}\n\n"

            if threat.references:
                result += "**References:**\n"
                for ref in threat.references:
                    result += f"- {ref}\n"
                result += "\n"

            result += "---\n\n"

        return result

    def _format_enhanced_scan_results(self, scan_result, scan_target: str) -> str:
        """Format enhanced scan results for display.

        Args:
            scan_result: Enhanced scan result object
            scan_target: Target that was scanned

        Returns:
            Formatted scan results string
        """
        result = f"# Enhanced Security Scan Results for {scan_target}\n\n"

        if not scan_result.all_threats:
            result += "🎉 **No security vulnerabilities found!**\n\n"
            # Still show analysis overview
            result += "## Analysis Overview\n\n"
            result += f"**LLM Analysis:** {scan_result.stats['llm_threats']} findings\n"
            result += f"**Language:** {scan_result.language.value}\n\n"
            return result

        # Analysis overview
        result += "## Analysis Overview\n\n"
        result += f"**LLM Analysis:** {scan_result.stats['llm_threats']} findings\n"
        result += f"**Total Unique:** {scan_result.stats['unique_threats']} findings\n"
        result += f"**Language:** {scan_result.language.value}\n\n"

        # Summary by severity
        severity_counts = scan_result.stats["severity_counts"]
        result += "## Summary\n"
        result += f"**Total Threats:** {len(scan_result.all_threats)}\n"
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[
                    severity
                ]
                result += f"**{severity.capitalize()}:** {count} {emoji}\n"
        result += "\n"

        # Scan metadata
        metadata = scan_result.scan_metadata
        if metadata.get("llm_scan_success") is not None:
            result += "## Scan Details\n\n"
            result += f"**LLM Scan:** {'✅ Success' if metadata.get('llm_scan_success') else '❌ Failed'}\n"
            if metadata.get("source_lines"):
                result += f"**Source Lines:** {metadata['source_lines']}\n"
            result += "\n"

        # Detailed findings
        result += "## Detailed Results\n\n"

        for i, threat in enumerate(scan_result.all_threats, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }.get(threat.severity.value, "⚪")

            # Identify source (rules vs LLM)
            source_icon = "🤖" if threat.rule_id.startswith("llm_") else "📋"
            source_text = (
                "LLM Analysis" if threat.rule_id.startswith("llm_") else "Rules Engine"
            )

            result += f"### {i}. {threat.rule_name} {severity_emoji} {source_icon}\n"
            result += f"**Source:** {source_text}\n"
            result += f"**File:** {threat.file_path}:{threat.line_number}\n"
            result += f"**Severity:** {threat.severity.value.capitalize()}\n"
            result += f"**Category:** {threat.category.value.capitalize()}\n"
            result += f"**Confidence:** {threat.confidence:.2f}\n"
            result += f"**Description:** {threat.description}\n\n"

            if threat.code_snippet:
                result += "**Code Context:**\n"
                result += f"```\n{threat.code_snippet}\n```\n\n"

            if threat.exploit_examples:
                result += "**Exploit Examples:**\n"
                for j, exploit in enumerate(threat.exploit_examples, 1):
                    result += f"*Example {j}:*\n"
                    result += f"```\n{exploit}\n```\n\n"

            if threat.remediation:
                result += f"**Remediation:** {threat.remediation}\n\n"

            if threat.references:
                result += "**References:**\n"
                for ref in threat.references:
                    result += f"- {ref}\n"
                result += "\n"

            result += "---\n\n"

        return result

    def _format_directory_scan_results(self, scan_results, scan_target: str) -> str:
        """Format directory scan results for display.

        Args:
            scan_results: List of enhanced scan results
            scan_target: Target directory that was scanned

        Returns:
            Formatted scan results string
        """
        if not scan_results:
            return f"# Directory Scan Results for {scan_target}\n\n❌ No files found to scan\n"

        # Combine statistics
        total_threats = sum(len(result.all_threats) for result in scan_results)
        total_files = len(scan_results)
        files_with_threats = sum(1 for result in scan_results if result.all_threats)

        # Count by severity across all files
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for result in scan_results:
            for severity, count in result.stats["severity_counts"].items():
                severity_counts[severity] += count

        # Build result string
        result = f"# Enhanced Directory Scan Results for {scan_target}\n\n"

        if total_threats == 0:
            result += "🎉 **No security vulnerabilities found in any files!**\n\n"
            result += f"**Files Scanned:** {total_files}\n"
            return result

        result += "## Overview\n\n"
        result += f"**Files Scanned:** {total_files}\n"
        result += f"**Files with Issues:** {files_with_threats}\n"
        result += f"**Total Threats:** {total_threats}\n\n"

        # Add scanner status information
        result += self._format_scanner_status(scan_results)
        result += "\n"

        # Summary by severity
        result += "## Summary\n"
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[
                    severity
                ]
                result += f"**{severity.capitalize()}:** {count} {emoji}\n"
        result += "\n"

        # File-by-file breakdown
        result += "## Files with Security Issues\n\n"

        for scan_result in scan_results:
            if scan_result.all_threats:
                result += f"### {scan_result.file_path}\n"
                result += f"Found {len(scan_result.all_threats)} issue(s)\n\n"

                for threat in scan_result.all_threats:
                    severity_emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🟢",
                    }.get(threat.severity.value, "⚪")

                    source_icon = "🤖" if threat.rule_id.startswith("llm_") else "📋"

                    result += (
                        f"- **{threat.rule_name}** {severity_emoji} {source_icon}\n"
                    )
                    result += f"  Line {threat.line_number}: {threat.description}\n\n"

        return result

    def _format_diff_scan_results(
        self,
        scan_results,
        diff_summary: dict[str, any],
        source_branch: str,
        target_branch: str,
    ) -> str:
        """Format diff scan results for display.

        Args:
            scan_results: Dictionary mapping file paths to lists of scan results
            diff_summary: Summary of the diff changes
            source_branch: Source branch name
            target_branch: Target branch name

        Returns:
            Formatted scan results string
        """
        if not scan_results:
            result = "# Git Diff Scan Results\n\n"
            result += f"**Source Branch:** {source_branch}\n"
            result += f"**Target Branch:** {target_branch}\n\n"

            if diff_summary.get("total_files_changed", 0) == 0:
                result += "🎉 **No changes found between branches!**\n\n"
            else:
                result += (
                    "🎉 **No security vulnerabilities found in diff changes!**\n\n"
                )
                result += (
                    f"**Files Changed:** {diff_summary.get('total_files_changed', 0)}\n"
                )
                result += (
                    f"**Supported Files:** {diff_summary.get('supported_files', 0)}\n"
                )
                result += f"**Lines Added:** {diff_summary.get('lines_added', 0)}\n"
                result += f"**Lines Removed:** {diff_summary.get('lines_removed', 0)}\n"

            return result

        # Combine statistics
        total_threats = sum(
            len(result.all_threats)
            for file_results in scan_results.values()
            for result in file_results
        )
        total_files = len(scan_results)
        files_with_threats = sum(
            1
            for file_results in scan_results.values()
            if any(result.all_threats for result in file_results)
        )

        # Count by severity across all files
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for file_results in scan_results.values():
            for result in file_results:
                for severity, count in result.stats["severity_counts"].items():
                    severity_counts[severity] += count

        # Build result string
        result = "# Git Diff Scan Results\n\n"
        result += f"**Source Branch:** {source_branch}\n"
        result += f"**Target Branch:** {target_branch}\n\n"

        result += "## Diff Summary\n\n"
        result += (
            f"**Total Files Changed:** {diff_summary.get('total_files_changed', 0)}\n"
        )
        result += f"**Supported Files:** {diff_summary.get('supported_files', 0)}\n"
        result += f"**Lines Added:** {diff_summary.get('lines_added', 0)}\n"
        result += f"**Lines Removed:** {diff_summary.get('lines_removed', 0)}\n"
        result += f"**Files with Security Issues:** {files_with_threats}\n"
        result += f"**Total Threats:** {total_threats}\n\n"

        if total_threats == 0:
            result += "🎉 **No security vulnerabilities found in diff changes!**\n\n"
            return result

        # Summary by severity
        result += "## Security Issues Summary\n"
        for severity in ["critical", "high", "medium", "low"]:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[
                    severity
                ]
                result += f"**{severity.capitalize()}:** {count} {emoji}\n"
        result += "\n"

        # File-by-file breakdown
        result += "## Files with Security Issues\n\n"

        for file_path, file_results in scan_results.items():
            for scan_result in file_results:
                if scan_result.all_threats:
                    result += f"### {file_path}\n"
                    result += f"Found {len(scan_result.all_threats)} issue(s) in diff changes\n\n"

                    for threat in scan_result.all_threats:
                        severity_emoji = {
                            "critical": "🔴",
                            "high": "🟠",
                            "medium": "🟡",
                            "low": "🟢",
                        }.get(threat.severity.value, "⚪")

                        source_icon = (
                            "🤖" if threat.rule_id.startswith("llm_") else "📋"
                        )

                        result += (
                            f"- **{threat.rule_name}** {severity_emoji} {source_icon}\n"
                        )
                        result += f"  Line {threat.line_number}: {threat.description}\n"

                        if threat.code_snippet:
                            result += f"  Code: `{threat.code_snippet.strip()}`\n"

                        if threat.exploit_examples:
                            result += f"  Exploit Examples: {len(threat.exploit_examples)} available\n"

                        result += "\n"

        return result

    def _format_json_scan_results(
        self,
        scan_result: EnhancedScanResult,
        scan_target: str,
        working_directory: str = ".",
    ) -> str:
        """Format enhanced scan results as JSON.

        Args:
            scan_result: Enhanced scan result object
            scan_target: Target that was scanned

        Returns:
            JSON formatted scan results
        """
        from datetime import datetime

        # Convert threats to dictionaries with complete false positive metadata
        threats_data = []
        for threat in scan_result.all_threats:
            # Get complete false positive information
            adversary_file_path = str(Path(working_directory) / ".adversary.json")
            project_fp_manager = FalsePositiveManager(
                adversary_file_path=adversary_file_path
            )
            false_positive_data = project_fp_manager.get_false_positive_details(
                threat.uuid
            )

            threat_data = {
                "uuid": threat.uuid,
                "rule_id": threat.rule_id,
                "rule_name": threat.rule_name,
                "description": threat.description,
                "category": threat.category.value,
                "severity": threat.severity.value,
                "file_path": threat.file_path,
                "line_number": threat.line_number,
                "end_line_number": getattr(
                    threat, "end_line_number", threat.line_number
                ),
                "code_snippet": threat.code_snippet,
                "confidence": threat.confidence,
                "source": getattr(threat, "source", "rules"),
                "cwe_id": getattr(threat, "cwe_id", []),
                "owasp_category": getattr(threat, "owasp_category", ""),
                "remediation": getattr(threat, "remediation", ""),
                "references": getattr(threat, "references", []),
                "exploit_examples": getattr(threat, "exploit_examples", []),
                "is_false_positive": false_positive_data is not None,
                "false_positive_metadata": false_positive_data,
            }
            threats_data.append(threat_data)

        # Create comprehensive JSON structure
        result_data = {
            "scan_metadata": {
                "target": scan_target,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "language": scan_result.language.value,
                "file_path": scan_result.file_path,
                "scan_type": "enhanced",
                "total_threats": len(scan_result.all_threats),
            },
            "scan_configuration": {
                "llm_scan_enabled": scan_result.scan_metadata.get(
                    "llm_scan_success", False
                ),
                "semgrep_scan_enabled": scan_result.scan_metadata.get(
                    "semgrep_scan_success", False
                ),
            },
            "statistics": scan_result.stats,
            "threats": threats_data,
            "scanner_execution_status": {
                "llm_scanner": {
                    "executed": scan_result.scan_metadata.get(
                        "llm_scan_success", False
                    ),
                    "reason": scan_result.scan_metadata.get(
                        "llm_scan_reason", "unknown"
                    ),
                    "error": scan_result.scan_metadata.get("llm_scan_error", None),
                    "threats_found": scan_result.stats.get("llm_threats", 0),
                },
                "semgrep_scanner": {
                    "executed": scan_result.scan_metadata.get(
                        "semgrep_scan_success", False
                    ),
                    "reason": scan_result.scan_metadata.get(
                        "semgrep_scan_reason", "unknown"
                    ),
                    "error": scan_result.scan_metadata.get("semgrep_scan_error", None),
                    "threats_found": scan_result.stats.get("semgrep_threats", 0),
                },
            },
            "scan_details": {
                "llm_scan_success": scan_result.scan_metadata.get(
                    "llm_scan_success", False
                ),
                "semgrep_scan_success": scan_result.scan_metadata.get(
                    "semgrep_scan_success", False
                ),
                "source_lines": scan_result.scan_metadata.get("source_lines", 0),
                "source_size": scan_result.scan_metadata.get("source_size", 0),
            },
        }

        return json.dumps(result_data, indent=2)

    def _format_json_directory_results(
        self,
        scan_results: list[EnhancedScanResult],
        scan_target: str,
        working_directory: str = ".",
    ) -> str:
        """Format directory scan results as JSON.

        Args:
            scan_results: List of enhanced scan results
            scan_target: Target directory that was scanned

        Returns:
            JSON formatted directory scan results
        """

        # Combine all threats
        all_threats = []
        files_scanned = []

        for scan_result in scan_results:
            files_scanned.append(
                {
                    "file_path": scan_result.file_path,
                    "language": scan_result.language.value,
                    "threat_count": (
                        len(scan_result.all_threats)
                        if hasattr(scan_result, "all_threats")
                        and isinstance(scan_result.all_threats, list)
                        else 0
                    ),
                    "issues_identified": bool(scan_result.all_threats),
                }
            )

            for threat in scan_result.all_threats:
                # Get complete false positive information
                adversary_file_path = str(Path(working_directory) / ".adversary.json")
                project_fp_manager = FalsePositiveManager(
                    adversary_file_path=adversary_file_path
                )
                false_positive_data = project_fp_manager.get_false_positive_details(
                    threat.uuid
                )

                threat_data = {
                    "uuid": threat.uuid,
                    "rule_id": threat.rule_id,
                    "rule_name": threat.rule_name,
                    "description": threat.description,
                    "category": threat.category.value,
                    "severity": threat.severity.value,
                    "file_path": threat.file_path,
                    "line_number": threat.line_number,
                    "end_line_number": getattr(
                        threat, "end_line_number", threat.line_number
                    ),
                    "code_snippet": threat.code_snippet,
                    "confidence": threat.confidence,
                    "source": getattr(threat, "source", "rules"),
                    "cwe_id": getattr(threat, "cwe_id", []),
                    "owasp_category": getattr(threat, "owasp_category", ""),
                    "remediation": getattr(threat, "remediation", ""),
                    "references": getattr(threat, "references", []),
                    "exploit_examples": getattr(threat, "exploit_examples", []),
                    "is_false_positive": false_positive_data is not None,
                    "false_positive_metadata": false_positive_data,
                }
                all_threats.append(threat_data)

        # Calculate summary statistics
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for threat in all_threats:
            severity_counts[threat["severity"]] += 1

        result_data = {
            "scan_metadata": {
                "target": scan_target,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "scan_type": "directory",
                "total_threats": len(all_threats),
                "files_scanned": len(files_scanned),
            },
            "scanner_execution_summary": {
                "semgrep_scanner": self._get_semgrep_summary(scan_results),
                "llm_scanner": {
                    "files_processed": len(
                        [
                            f
                            for f in scan_results
                            if f.scan_metadata.get("llm_scan_success", False)
                        ]
                    ),
                    "files_failed": len(
                        [
                            f
                            for f in scan_results
                            if not f.scan_metadata.get("llm_scan_success", False)
                            and f.scan_metadata.get("llm_scan_reason")
                            not in ["disabled", "not_available"]
                        ]
                    ),
                    "total_threats": sum(
                        f.stats.get("llm_threats", 0) for f in scan_results
                    ),
                },
            },
            "statistics": {
                "total_threats": len(all_threats),
                "severity_counts": severity_counts,
                "files_with_threats": len(
                    [
                        f
                        for f in files_scanned
                        if isinstance(f.get("threat_count", 0), int)
                        and int(f["threat_count"]) > 0
                    ]
                ),
            },
            "files": files_scanned,
            "threats": all_threats,
        }

        return json.dumps(result_data, indent=2)

    def _get_semgrep_summary(
        self, scan_results: list[EnhancedScanResult]
    ) -> dict[str, Any]:
        """Get enhanced Semgrep scanner summary with detailed status information.

        Args:
            scan_results: List of enhanced scan results

        Returns:
            Dictionary with enhanced Semgrep scanner summary
        """
        semgrep_summary = {
            "files_processed": len(
                [
                    f
                    for f in scan_results
                    if f.scan_metadata.get("semgrep_scan_success", False)
                ]
            ),
            "files_failed": len(
                [
                    f
                    for f in scan_results
                    if not f.scan_metadata.get("semgrep_scan_success", False)
                    and f.scan_metadata.get("semgrep_scan_reason")
                    not in ["disabled", "not_available"]
                ]
            ),
            "total_threats": sum(
                f.stats.get("semgrep_threats", 0) for f in scan_results
            ),
        }

        # Get detailed Semgrep status from the first scan result (they should all be the same)
        if scan_results:
            first_result_metadata = scan_results[0].scan_metadata

            # Add enhanced status information
            semgrep_status = first_result_metadata.get("semgrep_status", {})
            semgrep_summary.update(
                {
                    "installation_status": semgrep_status.get(
                        "installation_status", "unknown"
                    ),
                    "version": semgrep_status.get("version"),
                    "available": semgrep_status.get("available", False),
                    "has_pro_features": semgrep_status.get("has_pro_features", False),
                }
            )

            # Add installation guidance if Semgrep is not available
            if not semgrep_status.get("available", False):
                semgrep_summary.update(
                    {
                        "error": semgrep_status.get("error"),
                        "installation_guidance": semgrep_status.get(
                            "installation_guidance"
                        ),
                    }
                )

            # Add scan-specific information
            scan_reason = first_result_metadata.get("semgrep_scan_reason")
            if scan_reason:
                semgrep_summary["scan_reason"] = scan_reason

            scan_error = first_result_metadata.get("semgrep_scan_error")
            if scan_error:
                semgrep_summary["scan_error"] = scan_error

        return semgrep_summary

    def _format_scanner_status(self, scan_results: list[EnhancedScanResult]) -> str:
        """Format scanner status information for text output.

        Args:
            scan_results: List of enhanced scan results

        Returns:
            Formatted scanner status string
        """
        if not scan_results:
            return ""

        status_lines = ["## Scanner Status\n"]

        # Get Semgrep status from first result
        semgrep_status = scan_results[0].scan_metadata.get("semgrep_status", {})

        # Semgrep status
        if semgrep_status.get("available", False):
            version = semgrep_status.get("version", "unknown")
            pro_features = (
                " (Pro)" if semgrep_status.get("has_pro_features", False) else ""
            )
            status_lines.append(f"**Semgrep:** ✅ Available {version}{pro_features}")
        else:
            error = semgrep_status.get("error", "unknown error")
            guidance = semgrep_status.get("installation_guidance", "")
            status_lines.append(f"**Semgrep:** ❌ Not Available - {error}")
            if guidance:
                status_lines.append(f"  💡 {guidance}")

        # LLM scanner status
        llm_success = any(
            r.scan_metadata.get("llm_scan_success", False) for r in scan_results
        )
        status_lines.append(
            f"**LLM Scanner:** {'✅ Available' if llm_success else '❌ Disabled'}"
        )

        return "\n".join(status_lines)

    def _format_json_diff_results(
        self,
        scan_results: dict[str, list[EnhancedScanResult]],
        diff_summary: dict[str, any],
        scan_target: str,
        working_directory: str = ".",
    ) -> str:
        """Format git diff scan results as JSON.

        Args:
            scan_results: Dictionary mapping file paths to scan results
            diff_summary: Git diff summary information
            scan_target: Target branches for diff scan
            working_directory: Working directory for false positive lookups

        Returns:
            JSON formatted diff scan results
        """

        # Collect all threats from all files
        all_threats = []
        files_changed = []

        for file_path, file_scan_results in scan_results.items():
            file_threat_count = 0
            for scan_result in file_scan_results:
                file_threat_count += len(scan_result.all_threats)
                for threat in scan_result.all_threats:
                    # Get complete false positive information
                    adversary_file_path = str(
                        Path(working_directory) / ".adversary.json"
                    )
                    project_fp_manager = FalsePositiveManager(
                        adversary_file_path=adversary_file_path
                    )
                    false_positive_data = project_fp_manager.get_false_positive_details(
                        threat.uuid
                    )

                    threat_data = {
                        "uuid": threat.uuid,
                        "rule_id": threat.rule_id,
                        "rule_name": threat.rule_name,
                        "description": threat.description,
                        "category": threat.category.value,
                        "severity": threat.severity.value,
                        "file_path": threat.file_path,
                        "line_number": threat.line_number,
                        "end_line_number": getattr(
                            threat, "end_line_number", threat.line_number
                        ),
                        "code_snippet": threat.code_snippet,
                        "confidence": threat.confidence,
                        "source": getattr(threat, "source", "rules"),
                        "cwe_id": getattr(threat, "cwe_id", []),
                        "owasp_category": getattr(threat, "owasp_category", ""),
                        "remediation": getattr(threat, "remediation", ""),
                        "references": getattr(threat, "references", []),
                        "exploit_examples": getattr(threat, "exploit_examples", []),
                        "is_false_positive": false_positive_data is not None,
                        "false_positive_metadata": false_positive_data,
                    }
                    all_threats.append(threat_data)

            files_changed.append(
                {
                    "file_path": file_path,
                    "threat_count": file_threat_count,
                    "lines_added": diff_summary.get("files_changed", {})
                    .get(file_path, {})
                    .get("lines_added", 0),
                    "lines_removed": diff_summary.get("files_changed", {})
                    .get(file_path, {})
                    .get("lines_removed", 0),
                }
            )

        # Calculate summary statistics
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for threat in all_threats:
            severity_counts[threat["severity"]] += 1

        result_data = {
            "scan_metadata": {
                "target": scan_target,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "scan_type": "git_diff",
                "total_threats": len(all_threats),
                "files_changed": len(files_changed),
            },
            "diff_summary": diff_summary,
            "statistics": {
                "total_threats": len(all_threats),
                "severity_counts": severity_counts,
                "files_with_threats": len(
                    [f for f in files_changed if f["threat_count"] > 0]
                ),
            },
            "files": files_changed,
            "threats": all_threats,
        }

        return json.dumps(result_data, indent=2)

    def _preserve_uuids_and_false_positives(
        self, new_threats: list[dict], adversary_file_path: Path
    ) -> list[dict]:
        """Preserve UUIDs and false positive markings from existing scan results.

        Args:
            new_threats: List of new threat dictionaries from current scan
            adversary_file_path: Path to existing .adversary.json file

        Returns:
            List of threats with preserved UUIDs and false positive markings
        """

        if not adversary_file_path.exists():
            logger.debug("No existing .adversary.json found, using new UUIDs")
            return new_threats

        try:
            # Load existing threats with their UUIDs and false positive markings
            with open(adversary_file_path, encoding="utf-8") as f:
                existing_data = json.load(f)

            existing_threats = existing_data.get("threats", [])
            logger.info(
                f"Loaded {len(existing_threats)} existing threats for UUID preservation"
            )

            # Create fingerprint-to-threat mapping from existing data
            existing_fingerprints = {}
            for threat in existing_threats:
                # Reconstruct fingerprint from existing threat data
                rule_id = threat.get("rule_id", "")
                file_path = threat.get("file_path", "")
                line_number = threat.get("line_number", 0)

                if rule_id and file_path:
                    # Normalize path like in ThreatMatch.get_fingerprint()
                    normalized_path = str(Path(file_path).resolve())
                    fingerprint = f"{rule_id}:{normalized_path}:{line_number}"
                    existing_fingerprints[fingerprint] = {
                        "uuid": threat.get("uuid"),
                        "is_false_positive": threat.get("is_false_positive", False),
                        "false_positive_reason": threat.get("false_positive_reason"),
                        "false_positive_marked_date": threat.get(
                            "false_positive_marked_date"
                        ),
                        "false_positive_last_updated": threat.get(
                            "false_positive_last_updated"
                        ),
                        "false_positive_marked_by": threat.get(
                            "false_positive_marked_by"
                        ),
                    }

            logger.debug(
                f"Built fingerprint map with {len(existing_fingerprints)} entries"
            )

            # Process new threats and preserve UUIDs where possible
            preserved_count = 0
            new_count = 0

            for threat in new_threats:
                rule_id = threat.get("rule_id", "")
                file_path = threat.get("file_path", "")
                line_number = threat.get("line_number", 0)

                if rule_id and file_path:
                    # Generate fingerprint for this new threat
                    normalized_path = str(Path(file_path).resolve())
                    fingerprint = f"{rule_id}:{normalized_path}:{line_number}"

                    if fingerprint in existing_fingerprints:
                        # Preserve existing UUID and false positive data
                        existing_data = existing_fingerprints[fingerprint]
                        threat["uuid"] = existing_data["uuid"]
                        threat["is_false_positive"] = existing_data["is_false_positive"]

                        # Preserve false positive metadata if marked
                        if existing_data["is_false_positive"]:
                            threat["false_positive_reason"] = existing_data[
                                "false_positive_reason"
                            ]
                            threat["false_positive_marked_date"] = existing_data[
                                "false_positive_marked_date"
                            ]
                            threat["false_positive_last_updated"] = existing_data[
                                "false_positive_last_updated"
                            ]
                            threat["false_positive_marked_by"] = existing_data[
                                "false_positive_marked_by"
                            ]

                        preserved_count += 1
                        logger.debug(
                            f"Preserved UUID for {fingerprint}: {existing_data['uuid']}"
                        )
                    else:
                        # New finding, keep the generated UUID
                        new_count += 1
                        logger.debug(f"New finding with UUID: {threat.get('uuid')}")

            logger.info(
                f"UUID preservation complete: {preserved_count} preserved, {new_count} new"
            )
            return new_threats

        except Exception as e:
            logger.warning(f"Failed to preserve UUIDs from existing file: {e}")
            logger.debug("UUID preservation error details", exc_info=True)
            return new_threats

    def _save_scan_results_json(
        self, json_data: str, output_path: str = "."
    ) -> str | None:
        """Save scan results to JSON file.

        Args:
            json_data: JSON formatted scan results
            output_path: Output file path or directory (defaults to .adversary.json in current dir)

        Returns:
            Path to saved file or None if save failed
        """
        try:
            # Convert to absolute path for logging
            output_path_abs = str(Path(output_path).resolve())
            logger.info(f"💾 Saving scan results - input path: {output_path_abs}")

            path = Path(output_path)
            path_abs = str(path.resolve())
            logger.debug(
                f"Resolved path object: {path_abs} (exists: {path.exists()}, is_dir: {path.is_dir() if path.exists() else 'unknown'})"
            )

            # If output_path is a directory, append the default filename
            if path.is_dir() or (not path.suffix and not path.exists()):
                final_path = path / ".adversary.json"
                logger.info(f"📁 Treating as directory, using: {final_path}")
            else:
                # output_path is a full file path
                final_path = path
                logger.info(f"📄 Treating as file path, using: {final_path}")

            # Ensure parent directory exists
            final_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug(f"📂 Ensured parent directory exists: {final_path.parent}")

            try:
                data = json_lib.loads(json_data)
                threats = data.get("threats", [])

                # Only attempt UUID preservation if we have threats
                if threats and len(threats) > 0:
                    logger.info(
                        f"🔄 Preserving UUIDs for {len(threats)} threats before saving"
                    )
                    preserved_threats = self._preserve_uuids_and_false_positives(
                        threats, final_path
                    )
                    data["threats"] = preserved_threats

                    # Re-serialize with preserved data
                    json_data = json_lib.dumps(data, indent=2)
                    logger.info(
                        f"💾 Writing {len(preserved_threats)} threats with preserved UUIDs to: {final_path}"
                    )
                else:
                    logger.debug(f"💾 Writing data without threats to: {final_path}")

            except Exception as json_error:
                logger.warning(
                    f"Failed to parse JSON for UUID preservation: {json_error}"
                )
                logger.debug("JSON parsing error details", exc_info=True)
                logger.info(f"💾 Writing original JSON data to: {final_path}")

            with open(final_path, "w", encoding="utf-8") as f:
                f.write(json_data)

            logger.info(f"✅ Scan results saved successfully to {final_path}")
            return str(final_path)
        except Exception as e:
            logger.error(f"❌ Failed to save scan results JSON to {output_path}: {e}")
            logger.debug("Save error details", exc_info=True)
            return None

    def _add_llm_analysis_prompts(
        self,
        content: str,
        language: Language,
        file_path: str,
        include_header: bool = True,
    ) -> str:
        """Add LLM analysis prompts to scan results."""
        try:
            analyzer = self.scan_engine.llm_analyzer
            prompt = analyzer.create_analysis_prompt(
                content, file_path, language, max_findings=20
            )

            result = ""
            if include_header:
                result += "\n\n# 🤖 LLM Security Analysis\n\n"
                result += "For enhanced LLM-based analysis, use the following prompts with your client's LLM:\n\n"

            result += "## System Prompt\n\n"
            result += f"```\n{prompt.system_prompt}\n```\n\n"
            result += "## User Prompt\n\n"
            result += f"```\n{prompt.user_prompt}\n```\n\n"
            result += "**Instructions:** Send both prompts to your LLM for enhanced security analysis.\n\n"

            return result
        except Exception as e:
            return f"\n\n⚠️ **LLM Analysis:** Failed to create prompts: {e}\n"

    def _add_llm_exploit_prompts(self, threats: list[ThreatMatch], content: str) -> str:
        """Add LLM exploit prompts for discovered threats."""
        if not threats:
            return ""

        result = "\n\n# 🤖 LLM Exploit Generation\n\n"
        result += "For enhanced LLM-based exploit generation, use the following prompts with your client's LLM:\n\n"
        result += "**Note:** Showing prompts for the first 3 threats found.\n\n"

        for i, threat in enumerate(threats[:3], 1):
            try:
                prompt = self.exploit_generator.create_exploit_prompt(threat, content)

                result += f"## Threat {i}: {threat.rule_name}\n\n"
                result += f"**Type:** {threat.category.value} | **Severity:** {threat.severity.value}\n\n"
                result += "### System Prompt\n\n"
                result += f"```\n{prompt.system_prompt}\n```\n\n"
                result += "### User Prompt\n\n"
                result += f"```\n{prompt.user_prompt}\n```\n\n"
                result += "**Instructions:** Send both prompts to your LLM for enhanced exploit generation.\n\n"
                result += "---\n\n"

            except Exception as e:
                result += (
                    f"⚠️ Failed to create exploit prompt for {threat.rule_name}: {e}\n\n"
                )

        return result

    async def _handle_mark_false_positive(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle mark false positive request."""
        try:
            finding_uuid = arguments.get("finding_uuid")
            adversary_file_path = arguments.get("adversary_file_path")
            reason = arguments.get("reason", "Marked as false positive via MCP")
            marked_by = arguments.get("marked_by", "user")

            if not finding_uuid:
                raise AdversaryToolError("finding_uuid is required")
            if not adversary_file_path:
                raise AdversaryToolError("adversary_file_path is required")

            # Resolve relative path to absolute path
            resolved_path = self._resolve_adversary_file_path(adversary_file_path)

            # Create false positive manager with resolved file path
            fp_manager = FalsePositiveManager(adversary_file_path=resolved_path)

            success = fp_manager.mark_false_positive(finding_uuid, reason, marked_by)

            if success:
                logger.info(
                    f"✅ Successfully marked finding {finding_uuid} as false positive in {resolved_path}"
                )
                result = "✅ **Finding marked as false positive**\n\n"
                result += f"**UUID:** {finding_uuid}\n"
                result += f"**Reason:** {reason}\n"
                result += f"**File:** {resolved_path}\n"
            else:
                logger.warning(
                    f"❌ Failed to mark finding {finding_uuid} as false positive - not found in {resolved_path}"
                )
                result = "⚠️ **Finding not found**\n\n"
                result += f"**UUID:** {finding_uuid}\n"
                result += f"**File checked:** {resolved_path}\n"
                result += "The threat with this UUID was not found in the .adversary.json file.\n"
                result += (
                    "Make sure you've run a scan that generated this finding first.\n"
                )

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error marking false positive: {e}")
            raise AdversaryToolError(f"Failed to mark false positive: {str(e)}")

    async def _handle_unmark_false_positive(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle unmark false positive request."""
        try:
            finding_uuid = arguments.get("finding_uuid")
            adversary_file_path = arguments.get("adversary_file_path")

            if not finding_uuid:
                raise AdversaryToolError("finding_uuid is required")
            if not adversary_file_path:
                raise AdversaryToolError("adversary_file_path is required")

            # Resolve relative path to absolute path
            resolved_path = self._resolve_adversary_file_path(adversary_file_path)

            # Create false positive manager with resolved file path
            fp_manager = FalsePositiveManager(adversary_file_path=resolved_path)
            success = fp_manager.unmark_false_positive(finding_uuid)

            if success:
                logger.info(
                    f"✅ Successfully unmarked finding {finding_uuid} from {resolved_path}"
                )
                result = "✅ **Finding unmarked as false positive**\n\n"
                result += f"**UUID:** {finding_uuid}\n"
                result += f"**File:** {resolved_path}\n"
            else:
                logger.warning(
                    f"❌ Finding {finding_uuid} not found in false positives in {resolved_path}"
                )
                result = "⚠️ **Finding not found in false positives**\n\n"
                result += f"**UUID:** {finding_uuid}\n"
                result += f"**File checked:** {resolved_path}\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error unmarking false positive: {e}")
            raise AdversaryToolError(f"Failed to unmark false positive: {str(e)}")

    async def _handle_list_false_positives(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle list false positives request."""
        try:
            adversary_file_path = arguments.get("adversary_file_path")

            if not adversary_file_path:
                raise AdversaryToolError("adversary_file_path is required")

            # Resolve relative path to absolute path
            resolved_path = self._resolve_adversary_file_path(adversary_file_path)

            # Create false positive manager with resolved file path
            fp_manager = FalsePositiveManager(adversary_file_path=resolved_path)
            false_positives = fp_manager.get_false_positives()

            result = f"# False Positives ({len(false_positives)} found)\n\n"
            result += f"**File:** {resolved_path}\n\n"

            if not false_positives:
                result += "No false positives found.\n"
                return [types.TextContent(type="text", text=result)]

            for fp in false_positives:
                result += f"## {fp['uuid']}\n\n"
                result += f"**Reason:** {fp.get('reason', 'No reason provided')}\n"
                result += f"**Marked:** {fp.get('marked_date', 'Unknown')}\n"
                if fp.get("last_updated") != fp.get("marked_date"):
                    result += f"**Updated:** {fp.get('last_updated', 'Unknown')}\n"
                result += "\n---\n\n"

            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Error listing false positives: {e}")
            raise AdversaryToolError(f"Failed to list false positives: {str(e)}")

    async def _handle_generate_threat_model(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle threat model generation request."""
        try:
            logger.info("Starting threat model generation")

            # Get parameters
            repo_name = arguments.get("repo_name")
            source_path_arg = arguments.get("source_path")
            search_depth = arguments.get("search_depth", 3)
            output_file = arguments.get("output_file")
            include_threats = arguments.get("include_threats", True)
            severity_threshold_str = arguments.get("severity_threshold", "medium")
            output_format = arguments.get("output_format", "markdown")
            use_llm = arguments.get("use_llm", False)

            # Determine source path
            if source_path_arg:
                # Explicit path provided
                source_path = Path(source_path_arg)
                logger.info(f"Using explicit source path: {source_path}")
            elif repo_name:
                # Find repo by name
                source_path = self._find_repo_by_name(repo_name, max_depth=search_depth)
                logger.info(f"Found repository '{repo_name}' at: {source_path}")
            else:
                raise AdversaryToolError(
                    "Either 'repo_name' or 'source_path' must be provided"
                )

            # Set default output file in the project directory
            if output_file is None:
                extension = "json" if output_format == "json" else "md"
                output_file = source_path / f"threat_model.{extension}"
                logger.info(f"Using default output file: {output_file}")
            else:
                output_file = Path(output_file)

            # Convert severity string to enum
            severity_threshold = ThreatSeverity(severity_threshold_str.lower())

            # Resolve paths
            source_path_resolved = source_path.resolve()
            output_file_resolved = output_file.resolve()

            logger.info(f"Analyzing source: {source_path_resolved}")
            logger.info(f"Output file: {output_file_resolved}")

            # Validate source path exists
            if not source_path_resolved.exists():
                raise AdversaryToolError(f"Source path does not exist: {source_path}")

            # Create threat model builder with LLM support
            builder = ThreatModelBuilder(enable_llm=use_llm)

            # Generate threat model
            threat_model = builder.build_threat_model(
                source_path=str(source_path_resolved),
                include_threats=include_threats,
                severity_threshold=severity_threshold,
                use_llm=use_llm,
                llm_options={
                    "severity_threshold": severity_threshold_str,
                    "enable_business_logic": True,
                    "enable_data_flow_analysis": True,
                    "enable_attack_surface": True,
                    "enable_contextual_enhancement": True,
                },
            )

            # Save threat model
            builder.save_threat_model(
                threat_model=threat_model,
                output_path=str(output_file_resolved),
                format=output_format,
            )

            # Generate response
            components = threat_model.components
            result = "# Threat Model Generated\n\n"
            result += f"**Source:** {source_path}\n"
            result += f"**Output:** {output_file}\n"
            result += f"**Format:** {output_format}\n\n"

            result += "## Architecture Summary\n\n"
            result += f"- **Trust Boundaries:** {len(components.boundaries)}\n"
            result += f"- **External Entities:** {len(components.external_entities)}\n"
            result += f"- **Processes:** {len(components.processes)}\n"
            result += f"- **Data Stores:** {len(components.data_stores)}\n"
            result += f"- **Data Flows:** {len(components.data_flows)}\n\n"

            if include_threats:
                result += f"- **Threats Identified:** {len(threat_model.threats)}\n\n"

                # Show threat breakdown by severity
                threat_counts = {}
                for threat in threat_model.threats:
                    severity = threat.severity.value
                    threat_counts[severity] = threat_counts.get(severity, 0) + 1

                if threat_counts:
                    result += "### Threat Breakdown\n\n"
                    for severity in ["critical", "high", "medium", "low"]:
                        count = threat_counts.get(severity, 0)
                        if count > 0:
                            emoji = {
                                "critical": "🔴",
                                "high": "🟠",
                                "medium": "🟡",
                                "low": "🟢",
                            }[severity]
                            result += (
                                f"- **{severity.capitalize()}:** {count} {emoji}\n"
                            )
                    result += "\n"

            # Show component breakdown
            if components.external_entities:
                result += "### External Entities\n"
                for entity in components.external_entities[:5]:  # Show first 5
                    result += f"- {entity}\n"
                if len(components.external_entities) > 5:
                    result += (
                        f"- ... and {len(components.external_entities) - 5} more\n"
                    )
                result += "\n"

            if components.processes:
                result += "### Processes\n"
                for process in components.processes[:5]:  # Show first 5
                    result += f"- {process}\n"
                if len(components.processes) > 5:
                    result += f"- ... and {len(components.processes) - 5} more\n"
                result += "\n"

            if components.data_stores:
                result += "### Data Stores\n"
                for store in components.data_stores[:5]:  # Show first 5
                    result += f"- {store}\n"
                if len(components.data_stores) > 5:
                    result += f"- ... and {len(components.data_stores) - 5} more\n"
                result += "\n"

            result += f"✅ **Threat model saved to:** `{output_file}`\n\n"

            # Add LLM enhancement information if used
            if use_llm and "llm_prompts" in threat_model.metadata:
                result += "🤖 **LLM Analysis Available:**\n"
                prompt_count = threat_model.metadata.get("llm_prompt_count", 0)
                result += (
                    f"- Generated {prompt_count} analysis prompts for client LLM\n"
                )
                result += "- Business logic, data flow, attack surface, and contextual analysis available\n"
                result += "- Prompts stored in threat model metadata for processing\n"
                result += "\n"
            elif use_llm:
                result += "⚠️ **LLM Enhancement:** Requested but not available\n\n"

            result += "**Next Steps:**\n"
            result += "- Use `adv_diagram` to create a visual diagram\n"
            result += f"- Review the {output_format} file for detailed findings\n"
            if not use_llm:
                result += (
                    "- Consider using `use_llm: true` for enhanced threat analysis\n"
                )

            logger.info("Threat model generation completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Threat model generation failed: {e}")
            logger.debug("Threat model error details", exc_info=True)
            raise AdversaryToolError(f"Threat model generation failed: {e}")

    async def _handle_generate_diagram(
        self, arguments: dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle Mermaid diagram generation request."""
        try:
            logger.info("Starting diagram generation")

            # Get parameters
            repo_name = arguments.get("repo_name")
            source_path_arg = arguments.get("source_path")
            search_depth = arguments.get("search_depth", 3)
            output_file = arguments.get("output_file")
            diagram_type = arguments.get("diagram_type", "flowchart")
            show_threats = arguments.get("show_threats", True)
            layout_direction = arguments.get("layout_direction", "TD")
            use_llm = arguments.get("use_llm", False)

            # Determine source path
            if source_path_arg:
                # Explicit path provided
                source_path = Path(source_path_arg)
                logger.info(f"Using explicit source path: {source_path}")
            elif repo_name:
                # Find repo by name
                source_path = self._find_repo_by_name(repo_name, max_depth=search_depth)
                logger.info(f"Found repository '{repo_name}' at: {source_path}")
            else:
                raise AdversaryToolError(
                    "Either 'repo_name' or 'source_path' must be provided"
                )

            # Set default output file in the project directory
            if output_file is None:
                output_file = source_path / "threat_diagram.mmd"
                logger.info(f"Using default output file: {output_file}")
            else:
                output_file = Path(output_file)

            # Resolve paths
            source_path_resolved = source_path.resolve()
            output_file_resolved = output_file.resolve()

            logger.info(f"Source: {source_path_resolved}")
            logger.info(f"Output: {output_file_resolved}")

            # Check if source is an existing threat model JSON file
            if source_path_resolved.suffix.lower() == ".json":
                logger.info("Using existing threat model JSON file")
                try:
                    with open(source_path_resolved, encoding="utf-8") as f:
                        threat_model_data = json.load(f)

                    # Generate diagram from JSON data using proper object model
                    from .threat_modeling.models import (
                        DataFlow,
                        ThreatModel,
                        ThreatModelComponents,
                    )

                    components = ThreatModelComponents(
                        boundaries=threat_model_data.get("boundaries", []),
                        external_entities=threat_model_data.get(
                            "external_entities", []
                        ),
                        processes=threat_model_data.get("processes", []),
                        data_stores=threat_model_data.get("data_stores", []),
                        data_flows=[
                            DataFlow(**flow)
                            for flow in threat_model_data.get("data_flows", [])
                        ],
                    )

                    threat_model = ThreatModel(components=components)
                    generator = DiagramGenerator()
                    diagram_content = generator.generate_diagram(
                        threat_model,
                        show_threats=show_threats,
                        diagram_type=diagram_type,
                        layout_direction=layout_direction,
                    )

                except (json.JSONDecodeError, KeyError) as e:
                    raise AdversaryToolError(f"Invalid threat model JSON file: {e}")

            else:
                # Generate new threat model from source code
                logger.info("Generating new threat model from source code")

                if not source_path_resolved.exists():
                    raise AdversaryToolError(
                        f"Source path does not exist: {source_path}"
                    )

                # Create threat model builder with LLM support
                builder = ThreatModelBuilder(enable_llm=use_llm)

                # Generate threat model (include threats if show_threats is True)
                threat_model = builder.build_threat_model(
                    source_path=str(source_path_resolved),
                    include_threats=show_threats,
                    severity_threshold=ThreatSeverity.MEDIUM,
                    use_llm=use_llm,
                    llm_options={
                        "severity_threshold": "medium",
                        "enable_business_logic": True,
                        "enable_data_flow_analysis": True,
                        "enable_attack_surface": True,
                        "enable_contextual_enhancement": True,
                    },
                )

                # Generate diagram
                generator = DiagramGenerator()
                diagram_content = generator.generate_diagram(
                    threat_model=threat_model,
                    diagram_type=diagram_type,
                    show_threats=show_threats,
                    layout_direction=layout_direction,
                )

            # Save diagram
            with open(output_file_resolved, "w") as f:
                f.write(diagram_content)

            # Generate response
            result = "# Mermaid Diagram Generated\n\n"
            result += f"**Source:** {source_path}\n"
            result += f"**Output:** {output_file}\n"
            result += f"**Diagram Type:** {diagram_type}\n"
            result += f"**Layout:** {layout_direction}\n"
            result += f"**Show Threats:** {show_threats}\n"

            # Add LLM enhancement info if used and generating new threat model
            if use_llm and not str(source_path).endswith(".json"):
                if (
                    hasattr(threat_model, "metadata")
                    and "llm_prompts" in threat_model.metadata
                ):
                    prompt_count = threat_model.metadata.get("llm_prompt_count", 0)
                    result += f"**LLM Enhanced:** Yes ({prompt_count} analysis prompts available)\n"
                else:
                    result += "**LLM Enhanced:** Requested but not available\n"

            result += "\n"

            # Show full diagram for rendering in Cursor
            result += "## Diagram Preview\n\n"
            result += "```mermaid\n"
            result += diagram_content
            result += "\n```\n\n"

            result += f"✅ **Diagram saved to:** `{output_file}`\n\n"
            result += "**Usage:**\n"
            result += "- Copy the `.mmd` file content to visualize in Mermaid-compatible tools\n"
            result += "- Use with GitHub, GitLab, or online Mermaid editors\n"
            result += "- Integrate into documentation or presentations\n"

            logger.info("Diagram generation completed successfully")
            return [types.TextContent(type="text", text=result)]

        except Exception as e:
            logger.error(f"Diagram generation failed: {e}")
            logger.debug("Diagram error details", exc_info=True)
            raise AdversaryToolError(f"Diagram generation failed: {e}")

    async def run(self) -> None:
        """Run the MCP server."""
        logger.info("Starting MCP server...")
        try:
            async with stdio_server() as (read_stream, write_stream):
                logger.info("MCP server running and accepting connections")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="adversary-mcp-server",
                        server_version=self._get_version(),
                        capabilities=ServerCapabilities(
                            tools=ToolsCapability(listChanged=True)
                        ),
                    ),
                )
        except Exception as e:
            logger.error(f"Server runtime error: {e}")
            logger.debug("Server error details", exc_info=True)
            raise

    def _find_repo_by_name(self, repo_name: str, max_depth: int = 3) -> Path:
        """Find a repository by name using recursive search from home directory."""

        home = Path.home()
        found_repos = []

        # Directories to skip for performance and relevance
        skip_dirs = {
            ".git",
            ".svn",
            ".hg",  # Version control internals
            "node_modules",
            "venv",
            ".venv",
            "env",  # Dependencies/virtual envs
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",  # Python cache
            ".idea",
            ".vscode",  # IDE directories
            "target",
            "build",
            "dist",  # Build outputs
            "vendor",
            "bower_components",  # Package managers
            ".npm",
            ".yarn",
            ".cargo",  # Package manager caches
            "Library",
            "Applications",
            "Desktop",
            "Downloads",  # macOS system dirs
            "AppData",
            "LocalAppData",  # Windows system dirs
        }

        def search_directory(current_path: Path, current_depth: int):
            """Recursively search for repositories."""
            if current_depth > max_depth:
                return

            try:
                for item in current_path.iterdir():
                    if not item.is_dir():
                        continue

                    # Skip hidden directories and known non-repo directories
                    if item.name.startswith(".") or item.name in skip_dirs:
                        continue

                    # If directory name matches repo name, check if it's a valid project
                    if item.name == repo_name and self._is_valid_project(item):
                        found_repos.append(item)
                        logger.debug(f"Found potential repo at: {item}")

                    # Recurse into subdirectory if we haven't hit max depth
                    if current_depth < max_depth:
                        search_directory(item, current_depth + 1)

            except (PermissionError, OSError, FileNotFoundError):
                # Skip directories we can't access
                logger.debug(f"Skipping inaccessible directory: {current_path}")
                pass

        logger.info(
            f"Searching for repository '{repo_name}' in home directory (max depth: {max_depth})"
        )
        search_directory(home, 0)

        if not found_repos:
            raise AdversaryToolError(f"Repository '{repo_name}' not found.")

        if len(found_repos) == 1:
            logger.info(f"Found repository '{repo_name}' at: {found_repos[0]}")
            return found_repos[0]

        # Multiple matches - let user know and pick the first one
        logger.warning(f"Multiple repositories named '{repo_name}' found:")
        for repo in found_repos:
            logger.warning(f"  - {repo}")
        logger.info(f"Using first match: {found_repos[0]}")
        return found_repos[0]

    def _is_valid_project(self, path: Path) -> bool:
        """Check if a directory looks like a valid project."""
        project_indicators = [
            ".git",  # Git repository
            "package.json",  # Node.js project
            "pyproject.toml",  # Python project
            "Cargo.toml",  # Rust project
            "pom.xml",  # Maven project
            "build.gradle",  # Gradle project
            "composer.json",  # PHP project
            "go.mod",  # Go project
            "requirements.txt",  # Python requirements
            "yarn.lock",  # Yarn project
            "package-lock.json",  # NPM project
            "Gemfile",  # Ruby project
            ".project",  # Eclipse project
            "README.md",  # Documentation (least specific)
        ]

        return any((path / indicator).exists() for indicator in project_indicators)


async def async_main() -> None:
    """Async main function."""
    server = AdversaryMCPServer()
    await server.run()


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
