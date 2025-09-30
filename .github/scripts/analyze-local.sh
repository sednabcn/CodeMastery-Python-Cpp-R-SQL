#!/bin/bash
# Local SQL Analysis Script
# Run this before committing to check SQL quality locally

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   SQL Quality Analyzer - Local Mode${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js is not installed${NC}"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Node.js found: $(node --version)"

# Check if we're in the repository root
if [ ! -d ".github" ] && [ ! -d "sql" ] && [ ! -d "queries" ] && [ ! -d "migrations" ]; then
    echo -e "${YELLOW}⚠️  Warning: Not in repository root directory${NC}"
    echo "Please run this script from the repository root"
    exit 1
fi

echo -e "${GREEN}✓${NC} Repository structure detected"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo ""
    echo -e "${BLUE}📦 Installing dependencies...${NC}"
    npm install --silent
    echo -e "${GREEN}✓${NC} Dependencies installed"
fi

# Check if analyzer exists
if [ ! -f "analyze-sql.js" ]; then
    echo ""
    echo -e "${RED}❌ Error: analyze-sql.js not found${NC}"
    echo "Please ensure the analyzer script is in the repository root"
    exit 1
fi

# Count SQL files
SQL_COUNT=$(find sql queries migrations -name "*.sql" 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo -e "${BLUE}🔍 Analysis Configuration:${NC}"
echo "   • SQL files found: $SQL_COUNT"
echo "   • Directories: sql/, queries/, migrations/"
echo "   • Minimum score: 70/100"
echo ""

# Run the analysis
echo -e "${BLUE}Running analysis...${NC}"
echo "─────────────────────────────────────────────────────────"

if node analyze-sql.js; then
    EXIT_CODE=0
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ SQL Quality Check PASSED${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
else
    EXIT_CODE=1
    echo ""
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}❌ SQL Quality Check FAILED${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Please fix the issues above before committing${NC}"
fi

# Check if report was generated
if [ -f "sql-analysis-report.json" ]; then
    echo ""
    echo -e "${BLUE}📄 Detailed report saved to: sql-analysis-report.json${NC}"
    
    # Show quick summary
    if command -v jq &> /dev/null; then
        AVG_SCORE=$(jq -r '.summary.average_score' sql-analysis-report.json)
        TOTAL_FILES=$(jq -r '.summary.total_files' sql-analysis-report.json)
        TOTAL_ISSUES=$(jq -r '.summary.total_issues' sql-analysis-report.json)
        CRITICAL=$(jq -r '.summary.critical_issues' sql-analysis-report.json)
        
        echo ""
        echo -e "${BLUE}Quick Summary:${NC}"
        echo "   • Average Score: $AVG_SCORE/100"
        echo "   • Files Analyzed: $TOTAL_FILES"
        echo "   • Total Issues: $TOTAL_ISSUES"
        echo "   • Critical Issues: $CRITICAL"
    fi
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

exit $EXIT_CODE
