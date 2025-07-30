import os
from typing import Optional, List
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool
from .client import FilesystemClient
from .exceptions import FilesystemError
from dotenv import load_dotenv

load_dotenv()

def _get_client(api_url: str, config: RunnableConfig) -> FilesystemClient:   
    # In dev mode, use a dummy token since server bypasses auth 
    print(os.getenv("DEV_MODE"))
    if os.getenv("DEV_MODE", "false").lower() == "true":
        return FilesystemClient(api_url=api_url, auth_token="dev-token")
    # Production mode - require proper auth
    user_auth = config.get("configurable", {}).get("langgraph_auth_user", {})
    auth_token = user_auth.get("supabase_token")
    if not auth_token:
        raise ValueError(
            "Missing supabase_token in langgraph auth context configuration. "
            "Make sure to set up custom auth in your LangGraph deployment. "
            "Or, you can set DEV_MODE=true for local testing without auth."
        )
    return FilesystemClient(api_url=api_url, auth_token=auth_token)


def get_filesystem_tools(api_url: str) -> List[BaseTool]:
    @tool
    def list_files(
        path: Optional[str] = None,
        config: RunnableConfig = None
    ) -> str:
        """List files in the virtual filesystem.
        
        Args:
            path: Optional directory path to filter by (e.g., '/documents')
            
        Returns:
            Formatted list of files
        """
        try:
            client = _get_client(api_url, config)
            files = client.list_files(path)
            
            if not files:
                return "No files found."
            
            file_list = []
            for file in files:
                file_list.append(
                    f"- {file.path} (v{file.version}, "
                    f"{file.updated_at.strftime('%Y-%m-%d %H:%M')})"
                )
            
            return "Files:\\n" + "\\n".join(file_list)
        except Exception as e:
            return f"Error listing files: {str(e)}"

    @tool
    def read_file(path: str, config: RunnableConfig = None) -> str:
        """Read the contents of a file from the virtual filesystem.
        
        Args:
            path: Path to the file to read (e.g., '/notes.txt')
            
        Returns:
            File contents or error message
        """
        try:
            client = _get_client(api_url, config)
            file_data = client.read_file(path)
            return file_data.content or "[File is empty]"
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @tool
    def create_file(
        path: str,
        content: str,
        config: RunnableConfig = None
    ) -> str:
        """Create a new file in the virtual filesystem.
        
        Args:
            path: Path for the new file (e.g., '/notes.txt')
            content: Initial content for the file
            
        Returns:
            Success message or error
        """
        try:
            client = _get_client(api_url, config)
            file_data = client.create_file(path, content)
            return f"Successfully created file: {file_data.path} (version {file_data.version})"
        except Exception as e:
            import traceback
            return f"Error creating file: {str(e)} - {traceback.format_exc()}"

    @tool
    def edit_file(
        path: str,
        content: str,
        config: RunnableConfig = None
    ) -> str:
        """Replace the entire contents of an existing file. Make sure you've read the file before editing it.
        
        This tool handles version conflicts automatically by retrying once.
        
        Args:
            path: Path to the file to edit
            content: New content for the file, remember this will replace the entire file
            
        Returns:
            Success message or error
        """
        try:
            client = _get_client(api_url, config)
            
            # First, read the current file to get version
            current = client.read_file(path)
            
            try:
                # Try to update with current version
                updated = client.update_file(path, content, current.version)
                return f"Successfully updated {updated.path} to version {updated.version}"
            except FilesystemError as e:
                if "conflict" in str(e).lower():
                    # Retry once if there was a conflict
                    current = client.read_file(path)
                    updated = client.update_file(path, content, current.version)
                    return f"Successfully updated {updated.path} to version {updated.version} (after retry)"
                raise
                
        except Exception as e:
            return f"Error editing file: {str(e)}"

    @tool
    def append_to_file(
        path: str,
        content: str,
        config: RunnableConfig = None
    ) -> str:
        """Append content to the end of an existing file. Make sure you've read the file before appending to it.
        
        Args:
            path: Path to the file to append to
            content: Content to append to the file
            
        Returns:
            Success message or error
        """
        try:
            client = _get_client(api_url, config)
            updated = client.append_to_file(path, content)
            return f"Successfully appended to {updated.path} (now version {updated.version})"
        except Exception as e:
            return f"Error appending to file: {str(e)}"

    return [
        list_files,
        read_file,
        create_file,
        edit_file,
        append_to_file,
    ]