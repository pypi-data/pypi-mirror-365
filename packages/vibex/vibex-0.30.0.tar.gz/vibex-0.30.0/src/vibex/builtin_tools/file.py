"""
File operations for VibeX.
"""

import os
import mimetypes
from pathlib import Path
from typing import Annotated, Optional, Dict, Any
from vibex.core.tool import tool, Tool, ToolResult
from vibex.storage.project import ProjectStorage
from vibex.storage.factory import ProjectStorageFactory
from vibex.utils.logger import get_logger

logger = get_logger(__name__)


class FileTool(Tool):
    """File tool that works with project artifacts and provides simple file operations."""

    def __init__(self, project_storage: ProjectStorage):
        super().__init__()

        # Validate required parameter
        if project_storage is None:
            raise TypeError("FileTool requires a ProjectStorage instance, got None")

        if not hasattr(project_storage, 'get_project_path'):
            raise TypeError(f"FileTool requires a ProjectStorage instance, got {type(project_storage)}")

        self.project_storage = project_storage
        logger.debug(f"FileTool initialized with project storage: {self.project_storage.get_project_path()}")

    @tool(description="Write content to a file")
    async def write_file(
        self,
        filename: Annotated[str, "Name of the file (e.g., 'report.html', 'requirements.md')"],
        content: Annotated[str, "Content to write to the file"]
    ) -> ToolResult:
        """Write content to file as a project artifact with versioning."""
        try:
            # Store as artifact with metadata
            metadata = {
                "filename": filename,
                "content_type": self._get_content_type(filename),
                "tool": "file_tool"
            }

            result = await self.project_storage.store_artifact(
                name=filename,
                content=content,
                content_type=metadata["content_type"],
                metadata=metadata,
                commit_message=f"Updated {filename}"
            )

            if result.success:
                version = result.data.get("version", "unknown") if result.data else "unknown"
                logger.info(f"Wrote file artifact: {filename} (version: {version})")

                # Return ToolResult with user-friendly content for LLM + structured data
                return ToolResult(
                    success=True,
                    result={
                        "path": filename,
                        "size": len(content),
                        "message": f"Successfully wrote {len(content)} characters to {filename}"
                    },
                    metadata={
                        "filename": filename,
                        "size": len(content),
                        "version": version,
                        "content_type": metadata["content_type"]
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    result={"error": f"Failed to write file: {result.error}"},
                    error=result.error
                )

        except Exception as e:
            logger.error(f"Error writing file {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Failed to write file: {str(e)}"},
                error=str(e)
            )

    @tool(description="Append content to an existing file. WARNING: Do not use for structured files like HTML, XML, or JSON as it will corrupt their structure.")
    async def append_file(
        self,
        filename: Annotated[str, "Name of the file to append to"],
        content: Annotated[str, "Content to append to the file"],
        separator: Annotated[str, "Separator between existing and new content (default: newline)"] = "\n"
    ) -> ToolResult:
        """Append content to an existing file. Creates the file if it doesn't exist.
        
        WARNING: This tool should NOT be used for structured files like:
        - HTML files (will add content after closing tags)
        - XML files (will break document structure)
        - JSON files (will create invalid JSON)
        
        For structured files, read the entire content, modify it, and use write_file instead.
        """
        try:
            # Check if file exists and get current content
            existing_content = ""
            file_exists = False

            try:
                read_result = await self.read_file(filename)
                if read_result.success:
                    # Extract content from the result
                    content_str = read_result.result
                    # Extract content directly from result
                    existing_content = read_result.result
                    file_exists = True
            except:
                # File doesn't exist, that's fine
                pass

            # Combine content
            if file_exists and existing_content:
                new_content = existing_content + separator + content
            else:
                new_content = content

            # Write the combined content
            result = await self.write_file(filename, new_content)

            if result.success:
                action = "appended to" if file_exists else "created"
                logger.info(f"Successfully {action} file: {filename}")
                return ToolResult(
                    success=True,
                    result={
                        "message": f"Successfully {action} {filename}",
                        "filename": filename,
                        "action": action,
                        "appended_size": len(content),
                        "total_size": len(new_content)
                    },
                    metadata={
                        "filename": filename,
                        "action": action,
                        "appended_size": len(content),
                        "total_size": len(new_content)
                    }
                )
            else:
                return result

        except Exception as e:
            logger.error(f"Error appending to file {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error appending to file: {str(e)}"},
                error=str(e)
            )

    @tool(description="Read the contents of a file")
    async def read_file(
        self,
        filename: Annotated[str, "Name of the file to read"],
        version: Annotated[Optional[str], "Specific version to read (optional, defaults to latest)"] = None
    ) -> ToolResult:
        """Read file contents from project artifacts."""
        try:
            content = await self.project_storage.get_artifact(filename, version)

            if content is None:
                return ToolResult(
                    success=False,
                    result={"error": f"File not found: {filename}"},
                    error=f"File not found: {filename}"
                )

            logger.info(f"Read file artifact: {filename}")
            return ToolResult(
                success=True,
                result=content,
                metadata={
                    "filename": filename,
                    "size": len(content),
                    "version": version,
                    "content": content  # Include raw content for programmatic access
                }
            )

        except Exception as e:
            logger.error(f"Error reading file {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error reading file: {str(e)}"},
                error=str(e)
            )

    @tool(description="List all files in the project")
    async def list_files(self) -> ToolResult:
        """List all file artifacts in the project."""
        try:
            artifacts = await self.project_storage.list_artifacts()

            if not artifacts:
                return ToolResult(
                    success=True,
                    result={"files": [], "count": 0, "message": "No files found in project"},
                    metadata={"files": [], "count": 0}
                )

            # Group by filename (artifacts can have multiple versions)
            files_by_name = {}
            for artifact in artifacts:
                name = artifact["name"]
                if name not in files_by_name:
                    files_by_name[name] = []
                files_by_name[name].append(artifact)

            files_metadata = []
            for name, versions in files_by_name.items():
                latest_version = sorted(versions, key=lambda x: x.get("created_at", ""))[-1]
                size = latest_version.get("size", 0)
                version_count = len(versions)
                created_at = latest_version.get("created_at", "unknown")

                # Add structured data for programmatic access
                files_metadata.append({
                    "name": name,
                    "size": size,
                    "version_count": version_count,
                    "created_at": created_at,
                    "latest_version": latest_version.get("version", "unknown")
                })

            logger.info(f"Listed {len(files_by_name)} file artifacts")
            return ToolResult(
                success=True,
                result={"files": files_metadata, "count": len(files_by_name)},
                metadata={
                    "files": files_metadata,
                    "count": len(files_by_name)
                }
            )

        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error listing files: {str(e)}"},
                error=str(e)
            )

    @tool(description="Check if a file exists in the project")
    async def file_exists(
        self,
        filename: Annotated[str, "Name of the file to check"]
    ) -> ToolResult:
        """Check if a file artifact exists in the project."""
        try:
            content = await self.project_storage.get_artifact(filename)

            if content is not None:
                # Get artifact metadata
                artifacts = await self.project_storage.list_artifacts()
                file_artifacts = [a for a in artifacts if a["name"] == filename]

                if file_artifacts:
                    latest = sorted(file_artifacts, key=lambda x: x.get("created_at", ""))[-1]
                    size = latest.get("size", 0)
                    created_at = latest.get("created_at", "unknown")
                    version_count = len(file_artifacts)

                    info = {"exists": True, "filename": filename, "size": size, "created_at": created_at, "version_count": version_count}

                    logger.info(f"File exists: {filename}")
                    return ToolResult(
                        success=True,
                        result=info,
                        metadata={
                            "filename": filename,
                            "exists": True,
                            "size": size,
                            "created_at": created_at,
                            "version_count": version_count
                        }
                    )
                else:
                    return ToolResult(
                        success=True,
                        result={"exists": True, "filename": filename},
                        metadata={"filename": filename, "exists": True}
                    )
            else:
                return ToolResult(
                    success=True,
                    result={"exists": False, "filename": filename},
                    metadata={"filename": filename, "exists": False}
                )

        except Exception as e:
            logger.error(f"Error checking file {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error checking file: {str(e)}"},
                error=str(e)
            )

    @tool(description="Delete a file from the project")
    async def delete_file(
        self,
        filename: Annotated[str, "Name of the file to delete"],
        version: Annotated[Optional[str], "Specific version to delete (optional, deletes all versions if not specified)"] = None
    ) -> ToolResult:
        """Delete a file artifact from the project."""
        try:
            result = await self.project_storage.delete_artifact(filename, version)

            if result.success:
                if version:
                    logger.info(f"Deleted file artifact version: {filename} (version: {version})")
                    return ToolResult(
                        success=True,
                        result={"deleted": True, "filename": filename, "version": version},
                        metadata={"filename": filename, "version": version}
                    )
                else:
                    logger.info(f"Deleted file artifact: {filename}")
                    return ToolResult(
                        success=True,
                        result={"deleted": True, "filename": filename},
                        metadata={"filename": filename}
                    )
            else:
                return ToolResult(
                    success=False,
                    result={"error": f"Failed to delete file: {result.error}"},
                    error=result.error
                )

        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error deleting file: {str(e)}"},
                error=str(e)
            )

    @tool(description="Get version history of a file")
    async def get_file_versions(
        self,
        filename: Annotated[str, "Name of the file to get versions for"]
    ) -> ToolResult:
        """Get version history of a file artifact."""
        try:
            versions = await self.project_storage.get_artifact_versions(filename)

            if not versions:
                return ToolResult(
                    success=False,
                    result={"error": f"No versions found for file: {filename}"},
                    error=f"No versions found for file: {filename}"
                )

            # Get detailed info for each version
            artifacts = await self.project_storage.list_artifacts()
            file_artifacts = [a for a in artifacts if a["name"] == filename]

            if not file_artifacts:
                return ToolResult(
                    success=False,
                    result={"error": f"No artifact metadata found for file: {filename}"},
                    error=f"No artifact metadata found for file: {filename}"
                )

            # Sort by creation time
            file_artifacts.sort(key=lambda x: x.get("created_at", ""))

            version_list = []
            versions_metadata = []
            for i, artifact in enumerate(file_artifacts):
                version = artifact.get("version", f"v{i+1}")
                size = artifact.get("size", 0)
                created_at = artifact.get("created_at", "unknown")

                version_list.append(f"  {version} - {size} bytes, created: {created_at}")
                versions_metadata.append({
                    "version": version,
                    "size": size,
                    "created_at": created_at
                })

            logger.info(f"Retrieved {len(versions)} versions for {filename}")
            return ToolResult(
                success=True,
                result={"filename": filename, "versions": versions_metadata, "count": len(versions)},
                metadata={
                    "filename": filename,
                    "versions": versions_metadata,
                    "count": len(versions)
                }
            )

        except Exception as e:
            logger.error(f"Error getting versions for {filename}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error getting versions: {str(e)}"},
                error=str(e)
            )

    @tool(description="Get project summary with file statistics")
    async def get_project_summary(self) -> ToolResult:
        """Get a summary of the project contents."""
        try:
            summary = await self.project_storage.get_project_summary()

            if isinstance(summary, dict) and "error" in summary:
                return ToolResult(
                    success=False,
                    result={"error": f"Error getting project summary: {summary['error']}"},
                    error=summary['error']
                )

            # Format the summary nicely
            if isinstance(summary, dict):
                result_text = summary
            else:
                result_text = {"summary": summary}

            logger.info("Retrieved project summary")
            return ToolResult(
                success=True,
                result=result_text,
                metadata=summary if isinstance(summary, dict) else {"summary": summary}
            )

        except Exception as e:
            logger.error(f"Error getting project summary: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error getting project summary: {str(e)}"},
                error=str(e)
            )

    @tool(description="Create a directory in the project")
    async def create_directory(
        self,
        path: Annotated[str, "Directory path to create (e.g., 'reports', 'data/sources')"]
    ) -> ToolResult:
        """Create a directory in the project using the underlying file storage."""
        try:
            result = await self.project_storage.file_storage.create_directory(path)

            if result.success:
                if result.metadata and result.metadata.get("already_exists"):
                    logger.info(f"Directory already exists: {path}")
                    return ToolResult(
                        success=True,
                        result={"exists": True, "path": path},
                        metadata={"path": path, "already_exists": True}
                    )
                else:
                    logger.info(f"Created directory: {path}")
                    return ToolResult(
                        success=True,
                        result={"created": True, "path": path},
                        metadata={"path": path, "created": True}
                    )
            else:
                return ToolResult(
                    success=False,
                    result={"error": f"Failed to create directory: {result.error}"},
                    error=result.error
                )

        except Exception as e:
            logger.error(f"Error creating directory {path}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error creating directory: {str(e)}"},
                error=str(e)
            )

    @tool(description="List contents of a directory in the project")
    async def list_directory(
        self,
        path: Annotated[str, "Directory path to list (defaults to project root)"] = ""
    ) -> ToolResult:
        """List the contents of a directory in the project."""
        try:
            # Use empty string for root, or the specified path
            directory_path = path if path else ""

            files = await self.project_storage.file_storage.list_directory(directory_path)

            if not files:
                display_path = directory_path if directory_path else "project root"
                return ToolResult(
                    success=True,
                    result={"path": directory_path, "items": [], "count": 0},
                    metadata={"path": directory_path, "items": [], "count": 0}
                )

            items_metadata = []
            for file_info in files:
                # Check if it's a directory (ends with /) or file
                if file_info.path.endswith('/'):
                    items_metadata.append({
                        "name": file_info.path,
                        "type": "directory",
                        "size": 0
                    })
                else:
                    items_metadata.append({
                        "name": file_info.path,
                        "type": "file",
                        "size": file_info.size
                    })

            display_path = directory_path if directory_path else "project root"
            logger.info(f"Listed directory: {display_path}")
            return ToolResult(
                success=True,
                result={"path": directory_path, "items": items_metadata, "count": len(items)},
                metadata={
                    "path": directory_path,
                    "items": items_metadata,
                    "count": len(items)
                }
            )

        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return ToolResult(
                success=False,
                result={"error": f"Error listing directory: {str(e)}"},
                error=str(e)
            )

    def _get_content_type(self, filename: str) -> str:
        """Determine content type from filename."""
        if filename.endswith('.html'):
            return 'text/html'
        elif filename.endswith('.md'):
            return 'text/markdown'
        elif filename.endswith('.json'):
            return 'application/json'
        elif filename.endswith('.txt'):
            return 'text/plain'
        elif filename.endswith('.py'):
            return 'text/x-python'
        elif filename.endswith('.js'):
            return 'text/javascript'
        elif filename.endswith('.css'):
            return 'text/css'
        else:
            return 'text/plain'


