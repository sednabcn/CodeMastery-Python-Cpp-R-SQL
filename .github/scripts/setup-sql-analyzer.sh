#!/bin/bash
# Setup Script for SQL Analyzer
# Run this once to set up the SQL quality analysis in your repository

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SQL Analyzer Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Create necessary directories
echo -e "${BLUE}📁 Creating directory structure...${NC}"

mkdir -p .github/workflows
mkdir -p scripts

echo -e "${GREEN}✓${NC} Directories created"

# Create .gitignore entries if not present
echo ""
echo -e "${BLUE}📝 Updating .gitignore...${NC}"

GITIGNORE_ENTRIES="
# SQL Analyzer artifacts
sql-analysis-report.json
sql-analysis-report.html
node_modules/
package-lock.json
*.log

# Temporary SQL files
*.tmp.sql
*.temp.sql
*.bak.sql
"

if [ -f .gitignore ]; then
    if ! grep -q "SQL Analyzer artifacts" .gitignore; then
        echo "$GITIGNORE_ENTRIES" >> .gitignore
        echo -e "${GREEN}✓${NC} Added SQL analyzer entries to .gitignore"
    else
        echo -e "${YELLOW}⚠${NC}  .gitignore already contains SQL analyzer entries"
    fi
else
    echo "$GITIGNORE_ENTRIES" > .gitignore
    echo -e "${GREEN}✓${NC} Created .gitignore with SQL analyzer entries"
fi

# Make scripts executable
echo ""
echo -e "${BLUE}🔧 Setting permissions...${NC}"

if [ -f scripts/analyze-local.sh ]; then
    chmod +x scripts/analyze-local.sh
    echo -e "${GREEN}✓${NC} Made scripts/analyze-local.sh executable"
fi

if [ -f scripts/setup-sql-analyzer.sh ]; then
    chmod +x scripts/setup-sql-analyzer.sh
    echo -e "${GREEN}✓${NC} Made scripts/setup-sql-analyzer.sh executable"
fi

# Initialize npm if package.json doesn't exist
echo ""
echo -e "${BLUE}📦 Checking Node.js setup...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
else
    echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"
    
    if [ ! -f package.json ]; then
        echo -e "${YELLOW}⚠${NC}  package.json not found. Please create it with the provided content."
    else
        echo -e "${GREEN}✓${NC} package.json exists"
        
        echo ""
        echo -e "${BLUE}📦 Installing dependencies...${NC}"
        npm install
        echo -e "${GREEN}✓${NC} Dependencies installed"
    fi
fi

# Check for SQL directories
echo ""
echo -e "${BLUE}🔍 Checking SQL directories...${NC}"

DIRS_FOUND=0

for dir in sql queries migrations; do
    if [ -d "$dir" ]; then
        SQL_COUNT=$(find "$dir" -name "*.sql" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "${GREEN}✓${NC} Found $dir/ directory with $SQL_COUNT SQL files"
        DIRS_FOUND=$((DIRS_FOUND + 1))
    else
        echo -e "${YELLOW}⚠${NC}  Directory $dir/ not found"
    fi
done

if [ $DIRS_FOUND -eq 0 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  No SQL directories found!${NC}"
    echo "Please ensure you have at least one of: sql/, queries/, or migrations/"
fi

# Test the analyzer
echo ""
echo -e "${BLUE}🧪 Testing analyzer setup...${NC}"

if [ -f analyze-sql.js ] && [ -d node_modules ]; then
    if node -e "require('./analyze-sql.js')" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Analyzer script is valid"
    fi
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Review the configuration:"
echo "   • .github/sql-analysis-config.yml"
echo ""
echo "2. Test locally before committing:"
echo "   ${GREEN}./scripts/analyze-local.sh${NC}"
echo ""
echo "3. Commit and push to trigger CI:"
echo "   ${GREEN}git add .${NC}"
echo "   ${GREEN}git commit -m 'Add SQL quality analysis'${NC}"
echo "   ${GREEN}git push${NC}"
echo ""
echo "4. Create a pull request to see the analyzer in action!"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "   • Check README for rule descriptions"
echo "   • Adjust thresholds in sql-analysis-config.yml"
echo "   • View reports in GitHub Actions artifacts"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
