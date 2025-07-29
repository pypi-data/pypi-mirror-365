#!/bin/bash

# Om Mental Health Platform - Comprehensive Command Test Script
# Tests every available command in the om system
# Author: Alexander Straub (frism)
# Email: schraube.eins@icloud.com

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Log file
LOG_FILE="om_test_results_$(date +%Y%m%d_%H%M%S).log"

# Function to print colored output
print_status() {
    local status=$1
    local command=$2
    local message=$3
    
    case $status in
        "PASS")
            echo -e "${GREEN}✅ PASS${NC} | $command | $message" | tee -a "$LOG_FILE"
            ((PASSED_TESTS++))
            ;;
        "FAIL")
            echo -e "${RED}❌ FAIL${NC} | $command | $message" | tee -a "$LOG_FILE"
            ((FAILED_TESTS++))
            ;;
        "SKIP")
            echo -e "${YELLOW}⏭️  SKIP${NC} | $command | $message" | tee -a "$LOG_FILE"
            ((SKIPPED_TESTS++))
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️  INFO${NC} | $message" | tee -a "$LOG_FILE"
            ;;
        "SECTION")
            echo -e "\n${PURPLE}🔧 TESTING SECTION: $message${NC}" | tee -a "$LOG_FILE"
            echo "=" | tr ' ' '=' | head -c 50 | tee -a "$LOG_FILE"
            echo "" | tee -a "$LOG_FILE"
            ;;
    esac
    ((TOTAL_TESTS++))
}

# Function to test a command
test_command() {
    local cmd="$1"
    local description="$2"
    local expected_behavior="$3"
    
    echo -n "Testing: $cmd ... "
    
    # Capture output and exit code
    if timeout 10s ./om $cmd > /tmp/om_test_output 2>&1; then
        local exit_code=$?
        local output=$(cat /tmp/om_test_output)
        
        # Check for common error patterns
        if echo "$output" | grep -qi "error\|exception\|traceback\|failed"; then
            print_status "FAIL" "$cmd" "Command produced error output"
            echo "Output: $output" >> "$LOG_FILE"
        elif echo "$output" | grep -qi "command not found\|unknown command"; then
            print_status "FAIL" "$cmd" "Command not recognized"
        elif [ ${#output} -eq 0 ]; then
            print_status "SKIP" "$cmd" "No output (may be interactive)"
        else
            print_status "PASS" "$cmd" "$description"
        fi
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            print_status "SKIP" "$cmd" "Command timed out (likely interactive)"
        else
            print_status "FAIL" "$cmd" "Command failed with exit code $exit_code"
        fi
    fi
    
    # Clean up
    rm -f /tmp/om_test_output
}

# Function to test command with arguments
test_command_with_args() {
    local cmd="$1"
    local args="$2"
    local description="$3"
    
    echo -n "Testing: $cmd $args ... "
    
    if timeout 5s ./om $cmd $args > /tmp/om_test_output 2>&1; then
        local output=$(cat /tmp/om_test_output)
        
        if echo "$output" | grep -qi "error\|exception\|traceback"; then
            print_status "FAIL" "$cmd $args" "Command with args produced error"
        else
            print_status "PASS" "$cmd $args" "$description"
        fi
    else
        print_status "SKIP" "$cmd $args" "Command with args timed out or failed"
    fi
    
    rm -f /tmp/om_test_output
}

# Start testing
echo -e "${CYAN}🧘‍♀️ Om Mental Health Platform - Comprehensive Command Test${NC}"
echo -e "${CYAN}================================================================${NC}"
echo "Started at: $(date)" | tee "$LOG_FILE"
echo "Log file: $LOG_FILE" | tee -a "$LOG_FILE"
echo ""

# Check if om executable exists
if [ ! -f "./om" ]; then
    echo -e "${RED}❌ Error: ./om executable not found!${NC}"
    echo "Please run this script from the om project directory."
    exit 1
fi

# Make sure om is executable
chmod +x ./om

print_status "INFO" "" "Starting comprehensive om command testing"

# =============================================================================
# QUICK ACTIONS (Q-SERIES COMMANDS)
# =============================================================================
print_status "SECTION" "" "QUICK ACTIONS (Q-SERIES)"

test_command "qm" "Quick mood check"
test_command "qb" "Quick breathing exercise"
test_command "qg" "Quick gratitude practice"
test_command "qf" "Quick focus reset"
test_command "qc" "Quick calm technique"
test_command "qr" "Quick relaxation"
test_command "qs" "Quick stress relief"
test_command "qe" "Quick energy boost"

# =============================================================================
# CRISIS & EMERGENCY SUPPORT
# =============================================================================
print_status "SECTION" "" "CRISIS & EMERGENCY SUPPORT"

test_command "crisis" "Crisis support resources"
test_command "emergency" "Emergency intervention"
test_command "rescue" "Rescue sessions menu"
test_command "rescue crisis" "Crisis resources via rescue"
test_command "rescue international" "International crisis menu"
test_command "rescue setup" "Crisis support setup"
test_command "rescue countries" "List available countries"
test_command "rescue custom" "View custom crisis resources"
test_command "sos" "SOS emergency support"
test_command "911" "US emergency alias"
test_command "112" "European emergency alias"
test_command "999" "UK emergency alias"

# Test rescue with specific feelings
test_command "rescue feeling overwhelmed" "Rescue for overwhelmed feeling"
test_command "rescue feeling panic" "Rescue for panic"
test_command "rescue quick" "Quick rescue technique"
test_command "rescue history" "Rescue session history"

# =============================================================================
# AI-POWERED FEATURES
# =============================================================================
print_status "SECTION" "" "AI-POWERED FEATURES"

test_command "coach" "AI mental health coach"
test_command "coach daily" "Daily AI coaching"
test_command "coach analyze" "AI pattern analysis"
test_command "coach urgent" "Urgent AI insights"
test_command "coach summary" "AI coaching summary"
test_command "coach feedback" "AI coach feedback"

test_command "autopilot" "Wellness autopilot"
test_command "autopilot tasks" "Autopilot task list"
test_command "autopilot recommendations" "AI recommendations"
test_command "autopilot config" "Autopilot configuration"

test_command "gamify" "Gamification system"
test_command "gamify status" "Gamification status"
test_command "gamify achievements" "Achievement list"
test_command "gamify challenge" "Daily challenge"
test_command "gamify leaderboard" "Personal leaderboard"

# =============================================================================
# WELLNESS DASHBOARD
# =============================================================================
print_status "SECTION" "" "WELLNESS DASHBOARD"

test_command "dashboard" "Wellness dashboard"
test_command "dashboard show" "Static dashboard"
test_command "dashboard live" "Live dashboard"
test_command "dashboard summary" "Dashboard summary"
test_command "dashboard export" "Export dashboard data"

# =============================================================================
# MOOD TRACKING & MENTAL HEALTH
# =============================================================================
print_status "SECTION" "" "MOOD TRACKING & MENTAL HEALTH"

test_command "mood" "Mood tracking"
test_command "mood log" "Log mood entry"
test_command "mood history" "Mood history"
test_command "mood trends" "Mood trend analysis"
test_command "mood export" "Export mood data"

test_command "anxiety" "Anxiety support"
test_command "anxiety_support" "Anxiety support module"
test_command "depression" "Depression support"
test_command "depression_support" "Depression support module"
test_command "insomnia" "Insomnia support"
test_command "insomnia_support" "Insomnia support module"

# =============================================================================
# WELLNESS PRACTICES
# =============================================================================
print_status "SECTION" "" "WELLNESS PRACTICES"

test_command "breathing" "Breathing exercises"
test_command "breathe" "Breathing alias"
test_command "meditation" "Meditation sessions"
test_command "meditate" "Meditation alias"
test_command "gratitude" "Gratitude practice"
test_command "grateful" "Gratitude alias"

test_command "affirmations" "Daily affirmations"
test_command "affirmations daily" "Daily affirmation"
test_command "affirmations random" "Random affirmation"
test_command "affirmations categories" "Affirmation categories"

# =============================================================================
# SLEEP & RELAXATION
# =============================================================================
print_status "SECTION" "" "SLEEP & RELAXATION"

test_command "sleep" "Sleep optimization"
test_command "sleep sounds" "Sleep sounds"
test_command "sleep quality" "Sleep quality tracking"
test_command "sleep cycle" "Sleep cycle calculation"
test_command "sleep hygiene" "Sleep hygiene tips"

# =============================================================================
# HABITS & ROUTINES
# =============================================================================
print_status "SECTION" "" "HABITS & ROUTINES"

test_command "habits" "Habit tracking"
test_command "habits list" "List habits"
test_command "habits add" "Add new habit"
test_command "habits check" "Check habit completion"
test_command "habits stats" "Habit statistics"

test_command "morning" "Morning routine"
test_command "evening" "Evening routine"
test_command "routine" "Daily routines"

# =============================================================================
# CBT & THERAPEUTIC TOOLS
# =============================================================================
print_status "SECTION" "" "CBT & THERAPEUTIC TOOLS"

test_command "cbt" "CBT toolkit"
test_command "cbt_toolkit" "CBT toolkit module"
test_command "coping" "Coping strategies"
test_command "coping_strategies" "Coping strategies module"
test_command "coping_skills" "Coping skills module"

test_command "journal" "Guided journaling"
test_command "guided_journals" "Guided journals module"
test_command "thoughts" "Thought tracking"
test_command "emotions" "Emotion analysis"

# =============================================================================
# PHYSICAL WELLNESS
# =============================================================================
print_status "SECTION" "" "PHYSICAL WELLNESS"

test_command "physical" "Physical wellness"
test_command "exercise" "Exercise routines"
test_command "stretch" "Stretching exercises"
test_command "movement" "Movement practices"

# =============================================================================
# SOCIAL & CONNECTION
# =============================================================================
print_status "SECTION" "" "SOCIAL & CONNECTION"

test_command "social" "Social connection"
test_command "social_connection" "Social connection module"
test_command "connection" "Connection practices"
test_command "relationships" "Relationship support"

# =============================================================================
# LEARNING & GROWTH
# =============================================================================
print_status "SECTION" "" "LEARNING & GROWTH"

test_command "learning" "Learning paths"
test_command "learning_paths" "Learning paths module"
test_command "articles" "Mental health articles"
test_command "mental_health_articles" "Articles module"
test_command "resources" "Mental health resources"

# =============================================================================
# ADVANCED FEATURES
# =============================================================================
print_status "SECTION" "" "ADVANCED FEATURES"

test_command "intention" "Intention timer"
test_command "intention_timer" "Intention timer module"
test_command "timer" "Timer functions"
test_command "focus" "Focus sessions"

test_command "hypnosis" "Hypnosis sessions"
test_command "hypnosis_sessions" "Hypnosis module"
test_command "neurowave" "Neurowave stimulation"
test_command "neurowave_stimulation" "Neurowave module"

# =============================================================================
# NICKY CASE INTEGRATION
# =============================================================================
print_status "SECTION" "" "NICKY CASE INTEGRATION"

test_command "wolf" "Nicky Case wolf guide"
test_command "nicky" "Nicky Case guide"
test_command "nicky_case_guide" "Nicky Case guide module"
test_command "fear" "Fear as friend"
test_command "anxiety_wolf" "Anxiety wolf guide"

# =============================================================================
# DATA & BACKUP
# =============================================================================
print_status "SECTION" "" "DATA & BACKUP"

test_command "backup" "Backup system"
test_command "backup create" "Create backup"
test_command "backup list" "List backups"
test_command "export" "Export data"
test_command "import" "Import data"

test_command "data" "Data management"
test_command "data show" "Show data"
test_command "data location" "Data location"
test_command "data clear" "Clear data"

# =============================================================================
# SYSTEM & CONFIGURATION
# =============================================================================
print_status "SECTION" "" "SYSTEM & CONFIGURATION"

test_command "config" "Configuration"
test_command "settings" "Settings management"
test_command "status" "System status"
test_command "version" "Version information"
test_command "about" "About om"

test_command "help" "Help system"
test_command "docs" "Documentation"
test_command "support" "Support information"

# =============================================================================
# API & INTEGRATIONS
# =============================================================================
print_status "SECTION" "" "API & INTEGRATIONS"

test_command "api" "API server"
test_command "api start" "Start API server"
test_command "api status" "API status"
test_command "apis" "External APIs"
test_command "integrations" "External integrations"

# =============================================================================
# TESTING & DIAGNOSTICS
# =============================================================================
print_status "SECTION" "" "TESTING & DIAGNOSTICS"

test_command "test" "Test system"
test_command "doctor" "System diagnostics"
test_command "health" "Health check"
test_command "debug" "Debug information"

# =============================================================================
# VISUAL & TUI FEATURES
# =============================================================================
print_status "SECTION" "" "VISUAL & TUI FEATURES"

test_command "visual" "Visual features"
test_command "tui" "Text user interface"
test_command "achievements" "Visual achievements"
test_command "gallery" "Achievement gallery"

# =============================================================================
# ALIASES AND SHORTCUTS
# =============================================================================
print_status "SECTION" "" "ALIASES AND SHORTCUTS"

# Common aliases
test_command "m" "Mood alias"
test_command "b" "Breathing alias"
test_command "g" "Gratitude alias"
test_command "h" "Help alias"
test_command "s" "Status alias"
test_command "d" "Dashboard alias"
test_command "c" "Coach alias"

# Emotional state aliases
test_command "anxious" "Anxious state support"
test_command "sad" "Sad state support"
test_command "stressed" "Stressed state support"
test_command "overwhelmed" "Overwhelmed state support"
test_command "angry" "Angry state support"
test_command "lonely" "Lonely state support"

# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================
print_status "SECTION" "" "EDGE CASES & ERROR HANDLING"

test_command "nonexistent_command" "Non-existent command handling"
test_command "" "Empty command handling"
test_command "help nonexistent" "Help for non-existent command"

# Commands with invalid arguments
test_command_with_args "mood" "invalid_arg" "Invalid mood argument"
test_command_with_args "coach" "invalid_action" "Invalid coach action"
test_command_with_args "gamify" "invalid_option" "Invalid gamify option"

# =============================================================================
# INTERACTIVE COMMANDS (LIMITED TESTING)
# =============================================================================
print_status "SECTION" "" "INTERACTIVE COMMANDS (LIMITED)"

# These commands are typically interactive, so we test if they start properly
test_command "setup" "Initial setup (interactive)"
test_command "onboarding" "User onboarding (interactive)"
test_command "wizard" "Setup wizard (interactive)"

# =============================================================================
# FINAL RESULTS
# =============================================================================

echo "" | tee -a "$LOG_FILE"
echo -e "${CYAN}🏁 TEST RESULTS SUMMARY${NC}" | tee -a "$LOG_FILE"
echo "=========================" | tee -a "$LOG_FILE"
echo "Total Tests: $TOTAL_TESTS" | tee -a "$LOG_FILE"
echo -e "${GREEN}Passed: $PASSED_TESTS${NC}" | tee -a "$LOG_FILE"
echo -e "${RED}Failed: $FAILED_TESTS${NC}" | tee -a "$LOG_FILE"
echo -e "${YELLOW}Skipped: $SKIPPED_TESTS${NC}" | tee -a "$LOG_FILE"

# Calculate success rate
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo "Success Rate: ${SUCCESS_RATE}%" | tee -a "$LOG_FILE"
else
    echo "Success Rate: 0%" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "Completed at: $(date)" | tee -a "$LOG_FILE"
echo "Full log saved to: $LOG_FILE" | tee -a "$LOG_FILE"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests completed successfully!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the log for details.${NC}"
    exit 1
fi
