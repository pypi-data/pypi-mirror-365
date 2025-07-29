#!/bin/bash

# Om Mental Health Platform - Quick Test Script
# Tests essential commands for basic functionality verification
# Author: Alexander Straub (frism)

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
TOTAL=0

echo -e "${BLUE}🧘‍♀️ Om Quick Test - Essential Commands${NC}"
echo "========================================"

# Test function
quick_test() {
    local cmd="$1"
    local desc="$2"
    ((TOTAL++))
    
    echo -n "Testing $cmd ... "
    
    if timeout 3s ./om $cmd > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
}

# Check if om exists
if [ ! -f "./om" ]; then
    echo -e "${RED}❌ Error: ./om not found!${NC}"
    exit 1
fi

chmod +x ./om

# Essential command tests
echo -e "\n${YELLOW}🔧 Testing Core Commands:${NC}"
quick_test "help" "Help system"
quick_test "status" "System status"
quick_test "version" "Version info"

echo -e "\n${YELLOW}⚡ Testing Quick Actions:${NC}"
quick_test "qm" "Quick mood"
quick_test "qb" "Quick breathing"
quick_test "qg" "Quick gratitude"

echo -e "\n${YELLOW}🆘 Testing Crisis Support:${NC}"
quick_test "crisis" "Crisis support"
quick_test "rescue" "Rescue sessions"
quick_test "emergency" "Emergency support"

echo -e "\n${YELLOW}🤖 Testing AI Features:${NC}"
quick_test "coach" "AI coach"
quick_test "dashboard" "Dashboard"
quick_test "gamify" "Gamification"

echo -e "\n${YELLOW}🧠 Testing Mental Health:${NC}"
quick_test "mood" "Mood tracking"
quick_test "anxiety" "Anxiety support"
quick_test "breathing" "Breathing exercises"

echo -e "\n${YELLOW}📊 Results:${NC}"
echo "Total: $TOTAL"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All essential commands working!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some commands failed. Run ./test_all_commands.sh for details.${NC}"
    exit 1
fi
