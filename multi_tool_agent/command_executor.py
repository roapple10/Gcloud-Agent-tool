"""
Command executor module for handling GCP command execution.
This module contains utilities for executing gcloud and BigQuery commands.
"""

import json
import subprocess
import re
import shlex
import os
from typing import Dict, Any, List

# Constants
DEBUG = True  # Set to False in production

def debug_log(message: str) -> None:
    """Print debug messages when DEBUG is enabled."""
    if DEBUG:
        print(f"[DEBUG] {message}")

def execute_subprocess(args: List[str]) -> Dict[str, Any]:
    """Execute a subprocess command and handle the results.
    
    Args:
        args: List of command arguments to execute.
        
    Returns:
        dict: A dictionary with status and result/error information.
    """
    debug_log(f"Executing command: {' '.join(args)}")
    
    try:
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True
        )
        
        if DEBUG:
            debug_log(f"Command stdout: {result.stdout}")
            debug_log(f"Command stderr: {result.stderr}")
        
        # Parse JSON output if possible
        try:
            output = json.loads(result.stdout)
            return {
                "status": "success",
                "result": output
            }
        except json.JSONDecodeError:
            # Return plain text if not JSON
            return {
                "status": "success",
                "result": result.stdout.strip()
            }
    except subprocess.CalledProcessError as e:
        debug_log(f"Command failed: {e.stderr.strip() if e.stderr else str(e)}")
        return {
            "status": "error",
            "error_message": e.stderr.strip() if e.stderr else str(e),
            "exit_code": e.returncode
        }

def handle_bigquery_query(command: str, bq_path: str) -> Dict[str, Any]:
    """Handle BigQuery query commands with special attention to SQL syntax.
    
    Args:
        command: The BigQuery command string.
        bq_path: Path to the BigQuery executable.
        
    Returns:
        dict: Result of command execution.
    """
    # For bq query commands, we need special handling to preserve quotes, backticks, and whitespace
    cmd_parts = command.split(maxsplit=2)  # Split into ['bq', 'query', 'rest of command']
    
    if len(cmd_parts) < 3:
        return {
            "status": "error",
            "error_message": "Invalid BigQuery query command. Missing SQL query."
        }
    
    # The rest contains flags and SQL
    rest = cmd_parts[2]
    
    # Initialize args with bq and query
    args = [bq_path, "query"]
    
    # Find where the SQL query starts - it's either after all flags or enclosed in quotes
    flags = []
    sql = ""
    
    # Try to find SQL enclosed in quotes first
    sql_match = re.search(r'"([^"]*)"', rest)
    if sql_match:
        # We have quoted SQL
        sql = sql_match.group(0)  # Include the quotes
        # Get all flags before the SQL
        before_sql = rest[:rest.find(sql)].strip()
        if before_sql:
            flags = shlex.split(before_sql)
    else:
        # No quoted SQL, try to find based on flags
        parts = shlex.split(rest)
        flag_end_idx = -1
        
        for i, part in enumerate(parts):
            if not part.startswith("--") and (i == 0 or "=" in parts[i-1] or not parts[i-1].startswith("--")):
                flag_end_idx = i
                break
        
        if flag_end_idx >= 0:
            flags = parts[:flag_end_idx]
            sql = " ".join(parts[flag_end_idx:])
        else:
            # No clear flag/SQL boundary, use the entire string as SQL
            sql = rest
    
    # Add flags
    args.extend(flags)
    
    # Add format flag if not already specified
    if not any(arg.startswith("--format") for arg in args):
        args.append("--format=json")
    
    # Add the SQL query - if quoted, remove the quotes as subprocess adds them back
    if sql.startswith('"') and sql.endswith('"'):
        sql = sql[1:-1]
    
    # Special handling to ensure backticks in table references are preserved
    # Look for patterns like project.dataset.table or `project.dataset.table`
    if '`' not in sql and re.search(r'FROM\s+\w+[-\w]*\.\w+\.\w+', sql, re.IGNORECASE):
        # Add backticks around the table reference
        sql = re.sub(
            r'(FROM\s+)(\w+[-\w]*\.\w+\.\w+)',
            r'\1`\2`',
            sql,
            flags=re.IGNORECASE
        )
    
    args.append(sql)
    
    debug_log(f"Processed BigQuery command args: {args}")
    debug_log(f"Final SQL query: {sql}")
    
    return execute_subprocess(args)

def handle_bigquery_command(command: str, bq_path: str) -> Dict[str, Any]:
    """Handle general BigQuery commands.
    
    Args:
        command: The BigQuery command string.
        bq_path: Path to the BigQuery executable.
        
    Returns:
        dict: Result of command execution.
    """
    # Remove the "bq " prefix
    bq_command = command[3:]
    
    args = [bq_path]
    command_args = shlex.split(bq_command)
    
    # Check if format is already specified
    if not any(arg.startswith("--format") for arg in command_args):
        args.extend(command_args + ["--format=json"])
    else:
        # Keep the user's specified format
        args.extend(command_args)
    
    return execute_subprocess(args)

def handle_gcloud_command(command: str, gcloud_path: str) -> Dict[str, Any]:
    """Handle general gcloud commands.
    
    Args:
        command: The gcloud command string.
        gcloud_path: Path to the gcloud executable.
        
    Returns:
        dict: Result of command execution.
    """
    # Remove the "gcloud " prefix
    gcloud_command = command[7:]
    
    args = [gcloud_path]
    command_args = shlex.split(gcloud_command)
    
    # Check if format is already specified
    if not any(arg.startswith("--format") for arg in command_args):
        args.extend(command_args + ["--format=json"])
    else:
        # Keep the user's specified format
        args.extend(command_args)
        
    return execute_subprocess(args)

def execute_gcloud_command(command: str) -> Dict[str, Any]:
    """
    Execute a gcloud CLI command and return the result.
    
    Args:
        command: The full gcloud/bq command to execute.
        
    Returns:
        dict: A dictionary with status and result/error information.
    """
    # Get the gcloud path from environment variable or use default
    gcloud_path = os.environ.get('GCLOUD_PATH')
    bq_path = os.environ.get('BQ_PATH')
    
    debug_log(f"Executing command: {command}")
    
    # Dispatch to the appropriate handler based on command type
    if command.startswith("bq query "):
        return handle_bigquery_query(command, bq_path)
    elif command.startswith("bq "):
        return handle_bigquery_command(command, bq_path)
    elif command.startswith("gcloud "):
        return handle_gcloud_command(command, gcloud_path)
    else:
        return {
            "status": "error",
            "error_message": f"Unsupported command format: {command}"
        } 