#!/bin/bash
# Push with GitHub token - enter your token when prompted

echo "Enter your GitHub Personal Access Token:"
read -s TOKEN

git remote set-url origin https://${TOKEN}@github.com/ruthlessmallard/mining-by-the-numbers.git

git push -u origin master

echo "Push complete!"