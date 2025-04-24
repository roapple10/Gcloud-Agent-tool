"""
GCP tool module for handling various GCP-related queries and commands.
This module processes both natural language queries and direct gcloud commands.
"""

import re
import json
import subprocess
from typing import Dict, Any, List, Callable
from .command_executor import execute_gcloud_command

def _format_list_response(items: List[Dict[str, Any]], title: str, item_formatter: Callable) -> str:
    """Format a list of items into a readable response.
    
    Args:
        items: List of item dictionaries.
        title: Title for the list.
        item_formatter: Function to format each item.
        
    Returns:
        str: Formatted response text.
    """
    if not items:
        return f"No {title.lower()} found."
        
    item_list = "\n".join([item_formatter(item) for item in items])
    return f"{title}:\n{item_list}"

def get_suggested_commands(query: str) -> str:
    """
    Provides suggested gcloud commands when the agent doesn't understand a query.
    
    Args:
        query: The user's query that wasn't understood.
        
    Returns:
        str: A string with suggested gcloud commands.
    """
    suggestions = []
    
    # Check for keywords and suggest appropriate commands
    if re.search(r'project', query, re.IGNORECASE):
        if re.search(r'list|show|all', query, re.IGNORECASE):
            suggestions.append("gcloud projects list")
        if re.search(r'describe|detail|info', query, re.IGNORECASE):
            suggestions.append("gcloud projects describe [PROJECT_ID]")
    
    if re.search(r'instance|vm|compute', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
        suggestions.append("gcloud compute instances list")
    
    if re.search(r'storage|bucket', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
        suggestions.append("gcloud storage ls")
    
    if re.search(r'region', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
        suggestions.append("gcloud compute regions list")
    
    if re.search(r'zone', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
        suggestions.append("gcloud compute zones list")
    
    if re.search(r'service', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
        suggestions.append("gcloud services list")
        suggestions.append("gcloud services list --project=[PROJECT_ID]")
    
    if re.search(r'billing|account', query, re.IGNORECASE):
        if re.search(r'list|show|all', query, re.IGNORECASE):
            suggestions.append("gcloud billing accounts list")
        if re.search(r'link|connect|set', query, re.IGNORECASE):
            suggestions.append("gcloud billing projects link [PROJECT_ID] --billing-account=[ACCOUNT_ID]")
    
    if re.search(r'bigquery|bq|dataset', query, re.IGNORECASE):
        if re.search(r'dataset', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
            suggestions.append("bq ls")
            suggestions.append("bq ls --format=json")
            suggestions.append("bq ls --project=[PROJECT_ID]")
        if re.search(r'table', query, re.IGNORECASE) and re.search(r'list|show|all', query, re.IGNORECASE):
            suggestions.append("bq ls [DATASET_ID]")
            suggestions.append("bq ls --project=[PROJECT_ID] [DATASET_ID]")
    
    # Add logging commands
    if re.search(r'log|logs|logging', query, re.IGNORECASE):
        if re.search(r'read|view|show|get', query, re.IGNORECASE):
            suggestions.append('gcloud logging read "resource.type=gce_instance" --limit=10')
            suggestions.append('gcloud logging read "severity>=ERROR" --project=[PROJECT_ID] --limit=10')
        if re.search(r'list', query, re.IGNORECASE):
            suggestions.append('gcloud logging logs list')
            suggestions.append('gcloud logging logs list --project=[PROJECT_ID]')
    
    # If no specific suggestions, provide general commands
    if not suggestions:
        suggestions = [
            "gcloud projects list",
            "gcloud compute instances list",
            "gcloud storage ls",
            "gcloud compute regions list",
            "gcloud compute zones list",
            "gcloud services list",
            "gcloud billing accounts list",
            "gcloud logging read --limit=10",
            "bq ls"
        ]
    
    return "You can try these commands (type the full command to execute directly):\n" + "\n".join(suggestions)

def gcp_tool(query: str) -> Dict[str, Any]:
    """
    Process GCP-related queries using gcloud CLI.
    
    Args:
        query: The user's GCP-related query.
        
    Returns:
        dict: A dictionary containing the response with a 'status' key ('success' or 'error')
              and a 'result' or 'error_message' key.
    """
    # Handle direct gcloud commands (only those directly entered, not natural language)
    if query.startswith("gcloud ") or query.startswith("bq "):
        # Direct execution of gcloud or bq command
        result = execute_gcloud_command(query)
        
        # Format the response
        if result["status"] == "success":
            # For successful command execution
            if isinstance(result["result"], (list, dict)):
                return {
                    "status": "success",
                    "report": f"Command executed successfully:\n{json.dumps(result['result'], indent=2)}"
                }
            else:
                return {
                    "status": "success", 
                    "report": f"Command executed successfully:\n{result['result']}"
                }
        else:
            # For command execution errors
            return {
                "status": "error",
                "error_message": f"Error executing command: {result['error_message']}",
                "suggested_commands": get_suggested_commands(query)
            }
    
    # Handle natural language queries
    if re.search(r"list\s+(?:all\s+)?(?:gcp\s+)?projects", query, re.IGNORECASE):
        result = execute_gcloud_command("gcloud projects list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            projects = result["result"]
            project_formatter = lambda p: f"- {p.get('name', 'Unknown')} (ID: {p.get('projectId', 'Unknown')})"
            return {
                "status": "success",
                "report": _format_list_response(projects, "Available GCP projects", project_formatter)
            }
        return result
        
    elif re.search(r"list\s+(?:all\s+)?(?:gcp\s+)?instances", query, re.IGNORECASE):
        result = execute_gcloud_command("gcloud compute instances list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            instances = result["result"]
            instance_formatter = lambda i: f"- {i.get('name', 'Unknown')} ({i.get('zone', 'Unknown')}, {i.get('status', 'Unknown')})"
            return {
                "status": "success",
                "report": _format_list_response(instances, "Available compute instances", instance_formatter)
            }
        return result
        
    elif re.search(r"list\s+(?:all\s+)?(?:gcp\s+)?buckets", query, re.IGNORECASE):
        # Use gsutil format for storage ls command
        import os
        gcloud_path = os.environ.get('GCLOUD_PATH', r"C:\Users\roapp\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd")
        args = [gcloud_path, "storage", "ls", "--format=gsutil"]
        
        try:
            # Execute the command directly with the correct format
            result = subprocess.run(
                args,
                check=True,
                capture_output=True,
                text=True
            )
            
            return {
                "status": "success",
                "report": f"Here are the available storage buckets:\n{result.stdout.strip()}"
            }
        except subprocess.CalledProcessError as e:
            return {
                "status": "error",
                "error_message": e.stderr.strip() if e.stderr else str(e),
                "exit_code": e.returncode
            }
        
    elif re.search(r"describe\s+project\s+(.+)", query, re.IGNORECASE):
        match = re.search(r"describe\s+project\s+(.+)", query, re.IGNORECASE)
        if match:
            project_id = match.group(1).strip()
            return execute_gcloud_command(f"gcloud projects describe {project_id}")
    
    elif re.search(r"list\s+(?:all\s+)?services", query, re.IGNORECASE):
        # Extract project ID if specified
        project_match = re.search(r"in\s+project\s+(\S+)", query, re.IGNORECASE)
        if project_match:
            project_id = project_match.group(1)
            result = execute_gcloud_command(f"gcloud services list --project={project_id}")
        else:
            result = execute_gcloud_command("gcloud services list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            services = result["result"]
            service_formatter = lambda s: f"- {s.get('name', 'Unknown')}"
            
            project_info = f" in project {project_match.group(1)}" if project_match else ""
            return {
                "status": "success",
                "report": _format_list_response(services, f"Available services{project_info}", service_formatter)
            }
        return result
        
    elif re.search(r"list\s+(?:all\s+)?(?:gcp\s+)?regions", query, re.IGNORECASE):
        result = execute_gcloud_command("gcloud compute regions list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            regions = result["result"]
            region_formatter = lambda r: f"- {r.get('name', 'Unknown')} ({r.get('status', 'Unknown')})"
            return {
                "status": "success",
                "report": _format_list_response(regions, "Available GCP regions", region_formatter)
            }
        return result
        
    elif re.search(r"list\s+(?:all\s+)?(?:gcp\s+)?zones", query, re.IGNORECASE):
        result = execute_gcloud_command("gcloud compute zones list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            zones = result["result"]
            zone_formatter = lambda z: f"- {z.get('name', 'Unknown')} ({z.get('region', 'Unknown')}, {z.get('status', 'Unknown')})"
            return {
                "status": "success",
                "report": _format_list_response(zones, "Available GCP zones", zone_formatter)
            }
        return result
    
    elif re.search(r"list\s+(?:all\s+)?billing\s+accounts", query, re.IGNORECASE):
        result = execute_gcloud_command("gcloud billing accounts list")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            accounts = result["result"]
            account_formatter = lambda a: (f"- {a.get('displayName', 'Unknown')} "
                                          f"(ID: {a.get('name', 'Unknown').split('/')[-1]}, "
                                          f"Open: {a.get('open', False)})")
            return {
                "status": "success",
                "report": _format_list_response(accounts, "Available billing accounts", account_formatter)
            }
        return result
    
    elif re.search(r"link\s+billing\s+account\s+(.+?)\s+to\s+project\s+(.+)", query, re.IGNORECASE) or \
         re.search(r"set\s+billing\s+account\s+(.+?)\s+for\s+project\s+(.+)", query, re.IGNORECASE) or \
         re.search(r"connect\s+billing\s+account\s+(.+?)\s+to\s+project\s+(.+)", query, re.IGNORECASE):
        
        # Extract billing account ID and project ID from the query
        match = re.search(r"(?:link|set|connect)\s+billing\s+account\s+(.+?)\s+(?:to|for)\s+project\s+(.+)", query, re.IGNORECASE)
        
        if match:
            billing_account_id = match.group(1).strip()
            project_id = match.group(2).strip()
            
            # Format IDs properly - remove any 'billingAccounts/' prefix if present
            if billing_account_id.startswith('billingAccounts/'):
                billing_account_id = billing_account_id.split('/')[-1]
            
            result = execute_gcloud_command(f"gcloud billing projects link {project_id} --billing-account={billing_account_id}")
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "report": f"Successfully linked billing account '{billing_account_id}' to project '{project_id}'."
                }
            return result
    
    # Handle 'gcloud billing' command format
    elif query.startswith("gcloud billing "):
        command_parts = query[15:].split()
        
        # Handle 'gcloud billing accounts list'
        if len(command_parts) >= 2 and command_parts[0] == "accounts" and command_parts[1] == "list":
            return gcp_tool("list billing accounts")
            
        # Handle 'gcloud billing projects link'
        elif len(command_parts) >= 4 and command_parts[0] == "projects" and command_parts[1] == "link":
            project_id = command_parts[2]
            billing_flag = next((part for part in command_parts if part.startswith("--billing-account=")), None)
            
            if billing_flag:
                billing_account_id = billing_flag.split("=")[1]
                return gcp_tool(f"link billing account {billing_account_id} to project {project_id}")
    
    # Handle BigQuery related queries
    elif re.search(r"(?:show|list)\s+(?:all\s+)?(?:bigquery|bq)\s+datasets", query, re.IGNORECASE):
        # List all datasets in the default project
        project_match = re.search(r"in\s+project\s+(\S+)", query, re.IGNORECASE)
        
        if project_match:
            project_id = project_match.group(1)
            result = execute_gcloud_command(f"bq ls --project={project_id}")
        else:
            result = execute_gcloud_command("bq ls")
        
        if result["status"] == "success" and isinstance(result["result"], list):
            datasets = result["result"]
            project_info = f" in project {project_match.group(1)}" if project_match else ""
            
            if not datasets:
                return {
                    "status": "success",
                    "report": f"No BigQuery datasets found{project_info}."
                }
                
            dataset_formatter = lambda d: f"- {d.get('id', 'Unknown')} ({d.get('location', 'Unknown')})"
            return {
                "status": "success",
                "report": _format_list_response(datasets, f"BigQuery datasets{project_info}", dataset_formatter)
            }
        return result
        
    elif re.search(r"(?:show|list)\s+(?:all\s+)?(?:bigquery|bq)\s+tables", query, re.IGNORECASE):
        # Extract dataset ID if specified
        dataset_match = re.search(r"in\s+dataset\s+(\S+)", query, re.IGNORECASE)
        project_match = re.search(r"in\s+project\s+(\S+)", query, re.IGNORECASE)
        
        if dataset_match:
            dataset_id = dataset_match.group(1)
            
            # Build the bq command
            if project_match:
                project_id = project_match.group(1)
                result = execute_gcloud_command(f"bq ls --project={project_id} {dataset_id}")
            else:
                result = execute_gcloud_command(f"bq ls {dataset_id}")
            
            if result["status"] == "success" and isinstance(result["result"], list):
                tables = result["result"]
                project_info = f" in project {project_match.group(1)}" if project_match else ""
                
                if not tables:
                    return {
                        "status": "success",
                        "report": f"No tables found in dataset {dataset_id}{project_info}."
                    }
                    
                table_formatter = lambda t: f"- {t.get('tableId', 'Unknown')} ({t.get('type', 'TABLE')})"
                return {
                    "status": "success",
                    "report": _format_list_response(tables, f"Tables in dataset {dataset_id}{project_info}", table_formatter)
                }
            return result
        else:
            return {
                "status": "error",
                "error_message": "Please specify a dataset. For example: 'Show BigQuery tables in dataset my_dataset'.",
                "suggested_commands": "You might want to try these commands:\nbq ls [DATASET_ID]\nbq ls --project=[PROJECT_ID] [DATASET_ID]"
            }
    
    # For queries that don't match any specific pattern, provide a helpful response
    return {
        "status": "error",
        "error_message": f"I'm not sure how to process your query: '{query}'. Try asking about listing projects, instances, buckets, regions, zones, services, billing accounts, or BigQuery datasets and tables.",
        "suggested_commands": get_suggested_commands(query)
    } 