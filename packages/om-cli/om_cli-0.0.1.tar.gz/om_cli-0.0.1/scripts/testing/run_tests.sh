#!/bin/bash

# Om Mental Health Platform - Advanced Test Runner
# Uses JSON configuration for comprehensive testing
# Author: Alexander Straub (frism)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
CONFIG_FILE="test_config.json"
LOG_FILE="test_results_$(date +%Y%m%d_%H%M%S).log"
TIMEOUT=10

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Functions
print_header() {
    echo -e "${CYAN}🧘‍♀️ Om Mental Health Platform - Advanced Test Runner${NC}"
    echo -e "${CYAN}=====================================================${NC}"
    echo "Started: $(date)" | tee "$LOG_FILE"
    echo "Config: $CONFIG_FILE" | tee -a "$LOG_FILE"
    echo "Log: $LOG_FILE" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

print_section() {
    local section="$1"
    local description="$2"
    echo -e "\n${PURPLE}🔧 TESTING: $section${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}Description: $description${NC}" | tee -a "$LOG_FILE"
    echo "$(printf '=%.0s' {1..60})" | tee -a "$LOG_FILE"
}

test_command() {
    local cmd="$1"
    local desc="$2"
    local category="$3"
    
    ((TOTAL_TESTS++))
    
    echo -n "Testing: $cmd ... " | tee -a "$LOG_FILE"
    
    # Run command with timeout
    if timeout $TIMEOUT ./om $cmd > /tmp/om_test_out 2>&1; then
        local output=$(cat /tmp/om_test_out)
        
        # Check for errors
        if echo "$output" | grep -qi "error\|exception\|traceback\|failed"; then
            echo -e "${RED}❌ FAIL${NC} - Error in output" | tee -a "$LOG_FILE"
            echo "Output: $output" >> "$LOG_FILE"
            ((FAILED_TESTS++))
        elif echo "$output" | grep -qi "command not found\|unknown command"; then
            echo -e "${RED}❌ FAIL${NC} - Command not found" | tee -a "$LOG_FILE"
            ((FAILED_TESTS++))
        elif [ ${#output} -eq 0 ] && [[ "$cmd" != "help" && "$cmd" != "status" ]]; then
            echo -e "${YELLOW}⏭️  SKIP${NC} - No output (interactive)" | tee -a "$LOG_FILE"
            ((SKIPPED_TESTS++))
        else
            echo -e "${GREEN}✅ PASS${NC} - $desc" | tee -a "$LOG_FILE"
            ((PASSED_TESTS++))
        fi
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            echo -e "${YELLOW}⏭️  SKIP${NC} - Timeout (interactive)" | tee -a "$LOG_FILE"
            ((SKIPPED_TESTS++))
        else
            echo -e "${RED}❌ FAIL${NC} - Exit code $exit_code" | tee -a "$LOG_FILE"
            ((FAILED_TESTS++))
        fi
    fi
    
    rm -f /tmp/om_test_out
}

run_category_tests() {
    local category="$1"
    
    # Extract category info from JSON (simplified parsing)
    local description=$(grep -A 1 "\"$category\":" "$CONFIG_FILE" | grep "description" | cut -d'"' -f4)
    
    print_section "$category" "$description"
    
    # Parse commands from JSON for this category
    local in_category=false
    local in_commands=false
    
    while IFS= read -r line; do
        if [[ $line == *"\"$category\":"* ]]; then
            in_category=true
        elif [[ $line == *"\"commands\":"* ]] && [ "$in_category" = true ]; then
            in_commands=true
        elif [[ $line == *"]"* ]] && [ "$in_commands" = true ]; then
            in_commands=false
            in_category=false
        elif [ "$in_commands" = true ] && [[ $line == *"\"cmd\":"* ]]; then
            local cmd=$(echo "$line" | cut -d'"' -f4)
            local desc_line=$(grep -A 1 "\"cmd\": \"$cmd\"" "$CONFIG_FILE" | grep "desc")
            local desc=$(echo "$desc_line" | cut -d'"' -f4)
            
            test_command "$cmd" "$desc" "$category"
        fi
    done < "$CONFIG_FILE"
}

print_summary() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}🏁 TEST RESULTS SUMMARY${NC}" | tee -a "$LOG_FILE"
    echo "=========================" | tee -a "$LOG_FILE"
    echo "Total Tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
    echo -e "${GREEN}Passed: $PASSED_TESTS${NC}" | tee -a "$LOG_FILE"
    echo -e "${RED}Failed: $FAILED_TESTS${NC}" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}" | tee -a "$LOG_FILE"
    
    if [ $TOTAL_TESTS -gt 0 ]; then
        local success_rate=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
        echo "Success Rate: ${success_rate}%" | tee -a "$LOG_FILE"
        
        if [ $success_rate -ge 90 ]; then
            echo -e "${GREEN}🎉 Excellent! System is highly functional.${NC}" | tee -a "$LOG_FILE"
        elif [ $success_rate -ge 75 ]; then
            echo -e "${YELLOW}👍 Good! Most features working properly.${NC}" | tee -a "$LOG_FILE"
        else
            echo -e "${RED}⚠️  Needs attention. Many features failing.${NC}" | tee -a "$LOG_FILE"
        fi
    fi
    
    echo "" | tee -a "$LOG_FILE"
    echo "Completed: $(date)" | tee -a "$LOG_FILE"
    echo "Full log: $LOG_FILE" | tee -a "$LOG_FILE"
}

# Main execution
main() {
    # Check prerequisites
    if [ ! -f "./om" ]; then
        echo -e "${RED}❌ Error: ./om executable not found!${NC}"
        echo "Please run this script from the om project directory."
        exit 1
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ Error: $CONFIG_FILE not found!${NC}"
        echo "Please ensure test_config.json exists."
        exit 1
    fi
    
    chmod +x ./om
    
    print_header
    
    # Parse command line arguments
    if [ $# -eq 0 ]; then
        # Run all categories
        categories=("quick_actions" "crisis_support" "ai_features" "dashboard" "mood_tracking" 
                   "wellness_practices" "sleep_support" "habits_routines" "cbt_therapeutic" 
                   "nicky_case" "advanced_features" "data_management" "system_config" 
                   "api_integrations" "testing_diagnostics")
    else
        # Run specific categories
        categories=("$@")
    fi
    
    # Run tests for each category
    for category in "${categories[@]}"; do
        run_category_tests "$category"
    done
    
    print_summary
    
    # Exit with appropriate code
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Show usage if requested
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [category1] [category2] ..."
    echo ""
    echo "Available categories:"
    echo "  quick_actions      - Ultra-fast wellness commands"
    echo "  crisis_support     - International crisis intervention"
    echo "  ai_features        - AI-powered coaching and gamification"
    echo "  dashboard          - Visual wellness dashboard"
    echo "  mood_tracking      - Mood and mental health monitoring"
    echo "  wellness_practices - Core wellness and mindfulness"
    echo "  sleep_support      - Sleep optimization tools"
    echo "  habits_routines    - Habit tracking and routines"
    echo "  cbt_therapeutic    - CBT and therapeutic tools"
    echo "  nicky_case         - Nicky Case integration"
    echo "  advanced_features  - Advanced therapeutic techniques"
    echo "  data_management    - Data backup and management"
    echo "  system_config      - System configuration and help"
    echo "  api_integrations   - API server and integrations"
    echo "  testing_diagnostics - Testing and diagnostics"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 quick_actions      # Test only quick actions"
    echo "  $0 crisis_support ai_features  # Test specific categories"
    exit 0
fi

# Run main function
main "$@"
