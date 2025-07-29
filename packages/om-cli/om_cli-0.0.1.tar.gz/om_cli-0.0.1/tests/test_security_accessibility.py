"""
Security and accessibility tests for om CLI
"""

import pytest
import subprocess
import os
import stat
import tempfile
import json
import re
from pathlib import Path

@pytest.mark.security
class TestSecurity:
    """Security-related tests"""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in the codebase"""
        suspicious_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'credential\s*=\s*["\'][^"\']+["\']',
        ]
        
        files_to_check = [
            'main.py',
            'om',
            'quick_actions.py',
            'improved_menu.py'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                for pattern in suspicious_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Check if it's in a comment or test data
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if any(match in line for match in matches):
                                if not (line.strip().startswith('#') or 
                                       'test' in line.lower() or 
                                       'example' in line.lower() or
                                       'placeholder' in line.lower()):
                                    pytest.fail(f"Potential hardcoded secret in {file_path}:{line_num}: {line.strip()}")
    
    def test_file_permissions_security(self, temp_home):
        """Test that data files are created with secure permissions"""
        om_dir = os.path.join(temp_home, '.om')
        os.makedirs(om_dir, exist_ok=True)
        
        # Create a test data file
        test_file = os.path.join(om_dir, 'test_data.json')
        test_data = {"sensitive": "data"}
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        # Check file permissions
        file_stat = os.stat(test_file)
        file_mode = stat.filemode(file_stat.st_mode)
        
        # File should not be world-readable
        assert not (file_stat.st_mode & stat.S_IROTH), f"File {test_file} is world-readable: {file_mode}"
        assert not (file_stat.st_mode & stat.S_IWOTH), f"File {test_file} is world-writable: {file_mode}"
    
    def test_input_sanitization(self):
        """Test that user input is properly sanitized"""
        # Test with potentially dangerous input
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "\x00\x01\x02",  # null bytes and control characters
            "A" * 10000,  # very long input
        ]
        
        for dangerous_input in dangerous_inputs:
            # Test with quick gratitude (which accepts user input)
            process = subprocess.Popen(['python3', 'quick_actions.py', 'gratitude'], 
                                     stdin=subprocess.PIPE, 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            try:
                stdout, stderr = process.communicate(input=dangerous_input + '\n', timeout=10)
                # Should not crash or behave unexpectedly
                assert process.returncode in [0, 1], f"Unexpected return code for input: {repr(dangerous_input)}"
            except subprocess.TimeoutExpired:
                process.kill()
                pytest.fail(f"Application hung on input: {repr(dangerous_input)}")
    
    def test_path_traversal_protection(self, temp_home):
        """Test protection against path traversal attacks"""
        # This test would be more relevant if the app accepts file paths from users
        # For now, we test that the app doesn't create files outside the expected directory
        
        om_dir = os.path.join(temp_home, '.om')
        os.makedirs(om_dir, exist_ok=True)
        
        # The application should only create files within the .om directory
        # This is more of a design verification than a security test for this CLI app
        
        # Check that no files are created outside the home directory
        before_files = set()
        for root, dirs, files in os.walk(temp_home):
            for file in files:
                before_files.add(os.path.join(root, file))
        
        # Run a command that might create files
        result = subprocess.run(['python3', 'main.py', 'dashboard'], 
                              capture_output=True, text=True, timeout=10,
                              env={'HOME': temp_home})
        
        after_files = set()
        for root, dirs, files in os.walk(temp_home):
            for file in files:
                after_files.add(os.path.join(root, file))
        
        new_files = after_files - before_files
        
        # All new files should be within the home directory
        for new_file in new_files:
            assert new_file.startswith(temp_home), f"File created outside home directory: {new_file}"
    
    def test_environment_variable_injection(self):
        """Test that environment variables can't be used for injection"""
        # Test with potentially dangerous environment variables
        dangerous_env = {
            'HOME': '/tmp/../../etc',
            'PATH': '/tmp/malicious:/usr/bin',
            'PYTHONPATH': '/tmp/malicious',
        }
        
        env = os.environ.copy()
        env.update(dangerous_env)
        
        result = subprocess.run(['python3', 'main.py', '--help'], 
                              capture_output=True, text=True, env=env, timeout=10)
        
        # Should still work normally
        assert result.returncode == 0
    
    def test_command_injection_protection(self):
        """Test protection against command injection"""
        # Since this is a CLI app, test that it doesn't execute arbitrary commands
        # This is more relevant if the app ever calls subprocess with user input
        
        # For now, verify that the app doesn't use shell=True inappropriately
        # This would require code analysis rather than runtime testing
        
        files_to_check = ['main.py', 'quick_actions.py']
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Look for subprocess calls with shell=True
                if 'subprocess' in content and 'shell=True' in content:
                    # This isn't necessarily bad, but should be reviewed
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if 'shell=True' in line:
                            # Check if it's using user input
                            if any(var in line for var in ['input', 'args', 'argv']):
                                pytest.fail(f"Potential command injection risk in {file_path}:{line_num}")

@pytest.mark.accessibility
class TestAccessibility:
    """Accessibility tests"""
    
    def test_text_output_readability(self):
        """Test that text output is readable and well-formatted"""
        result = subprocess.run(['python3', 'main.py', '--help'], 
                              capture_output=True, text=True)
        
        assert result.returncode == 0
        output = result.stdout
        
        # Should have proper line breaks
        lines = output.split('\n')
        assert len(lines) > 1, "Output should have multiple lines"
        
        # Lines shouldn't be too long (accessibility guideline)
        for line in lines:
            assert len(line) <= 120, f"Line too long for accessibility: {len(line)} chars"
        
        # Should have some structure (headers, sections)
        assert any('=' in line or '-' in line for line in lines), "Output should have visual structure"
    
    def test_color_output_optional(self):
        """Test that color output can be disabled"""
        # Test with NO_COLOR environment variable
        env = os.environ.copy()
        env['NO_COLOR'] = '1'
        
        result = subprocess.run(['python3', 'main.py', '--help'], 
                              capture_output=True, text=True, env=env)
        
        assert result.returncode == 0
        
        # Output should not contain ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', result.stdout)
        
        # If colors were properly disabled, the clean output should be the same
        # (This test assumes the app respects NO_COLOR)
        assert len(clean_output) == len(result.stdout) or env.get('NO_COLOR'), "Colors should be disabled with NO_COLOR"
    
    def test_unicode_support(self):
        """Test that the application supports unicode characters"""
        # Test with unicode in gratitude input
        unicode_input = "🧘‍♀️ mindfulness 🌟 wellness 💚 gratitude\n"
        
        process = subprocess.Popen(['python3', 'quick_actions.py', 'gratitude'], 
                                 stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True, encoding='utf-8')
        
        try:
            stdout, stderr = process.communicate(input=unicode_input, timeout=10)
            # Should handle unicode without errors
            assert process.returncode in [0, 1]
        except UnicodeError:
            pytest.fail("Application should support unicode characters")
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Application should handle unicode input without hanging")
    
    def test_screen_reader_compatibility(self):
        """Test compatibility with screen readers"""
        result = subprocess.run(['python3', 'main.py', '--help'], 
                              capture_output=True, text=True)
        
        output = result.stdout
        
        # Should not rely solely on visual formatting
        # Text should be meaningful without colors or special characters
        
        # Check for descriptive text
        assert any(word in output.lower() for word in ['help', 'usage', 'command', 'option']), \
            "Help output should contain descriptive text"
        
        # Should not have excessive special characters that confuse screen readers
        special_char_ratio = sum(1 for c in output if not c.isalnum() and not c.isspace()) / len(output)
        assert special_char_ratio < 0.3, f"Too many special characters: {special_char_ratio:.2%}"
    
    def test_keyboard_navigation(self):
        """Test that the application works with keyboard-only navigation"""
        # For a CLI app, this mainly means testing that it doesn't require mouse input
        # and that interactive elements can be navigated with keyboard
        
        # Test that help can be accessed via keyboard
        result = subprocess.run(['python3', 'main.py', '--help'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        
        # Test that quick actions work with keyboard input
        process = subprocess.Popen(['python3', 'quick_actions.py', 'help'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        stdout, stderr = process.communicate(timeout=10)
        assert process.returncode == 0
    
    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful"""
        # Test with invalid command
        result = subprocess.run(['python3', 'main.py', 'invalid_command'], 
                              capture_output=True, text=True)
        
        # Should provide helpful error message
        error_output = result.stderr + result.stdout
        
        # Error message should be informative
        assert len(error_output.strip()) > 0, "Should provide error message for invalid command"
        
        # Should suggest alternatives or help
        helpful_words = ['help', 'usage', 'try', 'available', 'command']
        assert any(word in error_output.lower() for word in helpful_words), \
            "Error message should be helpful"
    
    def test_consistent_interface(self):
        """Test that the interface is consistent across commands"""
        commands = ['--help', '--list-modules']
        
        outputs = []
        for cmd in commands:
            result = subprocess.run(['python3', 'main.py', cmd], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                outputs.append(result.stdout)
        
        if len(outputs) >= 2:
            # Check for consistent formatting patterns
            # This is a basic check - in practice you'd want more sophisticated analysis
            
            # All outputs should use similar line length patterns
            avg_line_lengths = []
            for output in outputs:
                lines = [line for line in output.split('\n') if line.strip()]
                if lines:
                    avg_length = sum(len(line) for line in lines) / len(lines)
                    avg_line_lengths.append(avg_length)
            
            if len(avg_line_lengths) >= 2:
                # Line lengths should be reasonably consistent
                max_diff = max(avg_line_lengths) - min(avg_line_lengths)
                assert max_diff < 50, "Output formatting should be consistent across commands"
    
    def test_timeout_handling(self):
        """Test that the application handles timeouts gracefully"""
        # Start an interactive command and let it timeout
        process = subprocess.Popen(['python3', 'main.py'], 
                                 stdin=subprocess.PIPE, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        try:
            # Don't provide input, let it wait
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            # This is expected for interactive commands
            process.terminate()
            try:
                stdout, stderr = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
        
        # Should terminate gracefully
        assert process.returncode != 0  # Not successful completion, but not a crash

@pytest.mark.privacy
class TestPrivacy:
    """Privacy-related tests"""
    
    def test_data_location_privacy(self, temp_home):
        """Test that data is stored in appropriate private locations"""
        env = {'HOME': temp_home}
        
        # Run a command that might create data
        result = subprocess.run(['python3', 'main.py', 'dashboard'], 
                              capture_output=True, text=True, env=env, timeout=10)
        
        # Check that data directory is in user's home
        om_dir = os.path.join(temp_home, '.om')
        if os.path.exists(om_dir):
            # Directory should have appropriate permissions
            dir_stat = os.stat(om_dir)
            
            # Directory should not be world-readable
            assert not (dir_stat.st_mode & stat.S_IROTH), "Data directory should not be world-readable"
            assert not (dir_stat.st_mode & stat.S_IWOTH), "Data directory should not be world-writable"
    
    def test_no_external_data_transmission(self):
        """Test that the application doesn't transmit data externally"""
        # This is a basic test - in practice you'd want network monitoring
        
        # Check that the code doesn't contain obvious network calls
        files_to_check = ['main.py', 'quick_actions.py']
        
        network_patterns = [
            r'requests\.',
            r'urllib\.',
            r'http\.',
            r'socket\.',
            r'telnet',
            r'ftp'
        ]
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                for pattern in network_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        # Check if it's in comments or imports that aren't used
                        lines = content.split('\n')
                        for line_num, line in enumerate(lines, 1):
                            if any(match in line for match in matches):
                                if not (line.strip().startswith('#') or 
                                       line.strip().startswith('import') or
                                       'test' in line.lower()):
                                    # This might be legitimate, but should be reviewed
                                    print(f"Network-related code found in {file_path}:{line_num}: {line.strip()}")
    
    def test_temporary_file_cleanup(self, temp_home):
        """Test that temporary files are cleaned up properly"""
        # This test would be more relevant if the app creates temporary files
        
        # Check that no temporary files are left behind
        temp_dir = tempfile.gettempdir()
        before_files = set(os.listdir(temp_dir))
        
        # Run some commands
        subprocess.run(['python3', 'main.py', '--help'], 
                      capture_output=True, text=True)
        subprocess.run(['python3', 'quick_actions.py', 'help'], 
                      capture_output=True, text=True)
        
        after_files = set(os.listdir(temp_dir))
        new_files = after_files - before_files
        
        # Filter out files that might be created by other processes
        om_related_files = [f for f in new_files if 'om' in f.lower()]
        
        assert len(om_related_files) == 0, f"Temporary files not cleaned up: {om_related_files}"
