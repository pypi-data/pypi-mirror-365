

def sz_in_bytes_str(n_bytes: int) -> str:
    """
    Convert integer no of bytes to optimal human-readable format
    """
    # Suffixes for the size
    for x in ["B", "KB", "MB", "GB", "TB", 'PB']:
        if n_bytes < 1024:
            return f"{n_bytes:.2f}{x}"
        n_bytes = n_bytes / 1024