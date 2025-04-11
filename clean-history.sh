#!/bin/bash

# Create a new orphan branch
git checkout --orphan temp_branch

# Add all files
git add .

# Commit
git commit -m "Initial commit - Clean history"

# Delete the old branch
git branch -D main

# Rename temp branch to main
git branch -m main

# Force push to remote
git push -f origin main

# Remove old refs and garbage collect
git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin
git reflog expire --expire=now --all
git gc --prune=now --aggressive