"""
Role-Based File Access Control
Determines which files each stakeholder role can edit
"""

from typing import List, Dict
import fnmatch

# Role-based file patterns
ROLE_PERMISSIONS: Dict[str, Dict[str, List[str]]] = {
    "Frontend": {
        "allowed": [
            "app/**/*.tsx",
            "app/**/*.ts",
            "components/**/*.tsx",
            "components/**/*.ts",
            "*.css",
            "*.scss",
            "public/**/*",
            "styles/**/*"
        ],
        "blocked": [
            "app/api/**/*",
            "backend/**/*",
            "server.ts",
            "*.config.js",
            "database/**/*"
        ]
    },
    "Backend": {
        "allowed": [
            "app/api/**/*",
            "backend/**/*",
            "server.ts",
            "*.config.js",
            "database/**/*",
            "prisma/**/*",
            "lib/db/**/*"
        ],
        "blocked": [
            "components/**/*.tsx",
            "app/**/page.tsx",
            "app/**/layout.tsx",
            "*.css",
            "*.scss"
        ]
    },
    "Founder": {
        "allowed": ["**/*"],  # Can edit everything
        "blocked": []
    },
    "Investor": {
        "allowed": [],  # View-only
        "blocked": ["**/*"]
    },
    "Facilitator": {
        "allowed": [],  # View-only
        "blocked": ["**/*"]
    }
}


def can_edit_file(role: str, file_path: str) -> bool:
    """
    Check if a stakeholder with given role can edit a file
    
    Args:
        role: Stakeholder role (Frontend, Backend, etc.)
        file_path: Path to file (e.g., "app/page.tsx")
    
    Returns:
        True if allowed, False otherwise
    """
    permissions = ROLE_PERMISSIONS.get(role)
    if not permissions:
        return False
    
    # Check if explicitly blocked
    for pattern in permissions["blocked"]:
        if fnmatch.fnmatch(file_path, pattern):
            return False
    
    # Check if allowed
    for pattern in permissions["allowed"]:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    
    return False


def get_allowed_files(role: str, all_files: List[str]) -> List[str]:
    """
    Filter files list to only those the role can edit
    
    Args:
        role: Stakeholder role
        all_files: List of all file paths
    
    Returns:
        Filtered list of allowed files
    """
    return [f for f in all_files if can_edit_file(role, f)]


def get_file_restrictions(role: str) -> Dict[str, List[str]]:
    """
    Get the file restriction rules for a role
    
    Returns:
        Dict with 'allowed' and 'blocked' patterns
    """
    return ROLE_PERMISSIONS.get(role, {"allowed": [], "blocked": ["**/*"]})

