def parse_git_diff(patch: str) -> dict:
    """
    Parses a file's git patch and returns a mapping of 
    actual line numbers in the new file to patch position numbers.
    GitHub API requires the `position` index within the patch to post inline comments.
    """
    if not patch:
        return {}
        
    line_to_position = {}
    current_line = 0
    
    # GitHub's patch position is 1-indexed and counts all lines in the patch
    for position, line in enumerate(patch.split('\n'), start=1):
        if line.startswith('@@'):
            # Parse the @@ -start,count +start,count @@ header
            # Extract the new file start line
            parts = line.split(' ')
            if len(parts) >= 3:
                new_file_range = parts[2]  # +start,count
                current_line = int(new_file_range.strip('+').split(',')[0]) - 1
        elif line.startswith('+') and not line.startswith('+++'):
            current_line += 1
            line_to_position[current_line] = position
        elif line.startswith('-') and not line.startswith('---'):
            pass  # Deleted lines don't increment the new file line number
        elif line.startswith(' '):
            current_line += 1
        elif line == '\\ No newline at end of file':
            pass
            
    return line_to_position
