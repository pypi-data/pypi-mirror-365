#!/usr/bin/env python3
"""
Comprehensive tests for the ClaudeLogProcessor to ensure optimizations don't break functionality.
Uses actual test data from tests/mock-data directory.
"""

import json
import os
import shutil

# Add parent directory to path for imports
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sniffly.core.processor import ClaudeLogProcessor, Interaction


class TestClaudeLogProcessor(unittest.TestCase):
    """Test suite for ClaudeLogProcessor using actual test data"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data directory"""
        cls.test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mock-data', '-Users-chip-dev-ai-music')
        
        # Pre-process once to get expected values for comparison
        processor = ClaudeLogProcessor(cls.test_data_dir)
        cls.baseline_messages, cls.baseline_stats = processor.process_logs()
        
        # Store some baseline values for verification
        cls.expected_sessions = ['ba79134d-b6e9-4867-af0c-6941038c9e4b', 
                                'd3ad4cdc-5657-435d-98fa-0035d53e383d',
                                'fed8ce56-bc79-401f-a83e-af084253362f',
                                'ff71dbed-a4f2-4284-a4fc-fe2fb90de929']
        
    def setUp(self):
        """Set up for each test"""
        # Create a temporary directory for modified test data
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_basic_processing(self):
        """Test basic log processing functionality with actual data"""
        processor = ClaudeLogProcessor(self.test_data_dir)
        messages, statistics = processor.process_logs()
        
        # Verify we got messages
        self.assertGreater(len(messages), 0, "Should have processed some messages")
        self.assertEqual(len(messages), len(self.baseline_messages), 
                        f"Should have exactly {len(self.baseline_messages)} messages")
        
        # Verify statistics structure
        self.assertIn('overview', statistics)
        self.assertIn('message_types', statistics['overview'])
        self.assertIn('total_tokens', statistics['overview'])
        self.assertIn('sessions', statistics['overview'])
        
        # Verify session count
        self.assertEqual(statistics['overview']['sessions'], 4, 
                        "Should have 4 sessions from test data")
        self.assertIn('message_types', statistics['overview'])
        self.assertIn('total_tokens', statistics['overview'])
        
    def test_message_extraction(self):
        """Test that messages are extracted correctly"""
        processor = ClaudeLogProcessor(self.test_data_dir)
        messages, _ = processor.process_logs()
        
        # Check message structure
        for msg in messages:
            self.assertIn('type', msg)
            self.assertIn('content', msg)
            self.assertIn('timestamp', msg)
            self.assertIn('session_id', msg)
            self.assertIn('tokens', msg)
            self.assertIn('tools', msg)
            
    def test_deduplication(self):
        """Test that deduplication works correctly"""
        # Create test data with duplicates
        test_messages = [
            {
                "type": "user",
                "message": {"role": "user", "content": "Test message 1"},
                "uuid": "uuid1",
                "timestamp": "2025-06-08T11:00:00.000Z",
                "sessionId": "session1"
            },
            {
                "type": "user", 
                "message": {"role": "user", "content": "Test message 1"},
                "uuid": "uuid1",
                "timestamp": "2025-06-08T11:00:00.000Z",
                "sessionId": "session2"  # Different session, same content
            }
        ]
        
        # Write test data
        test_file = os.path.join(self.temp_dir, "test.jsonl")
        with open(test_file, 'w') as f:
            for msg in test_messages:
                f.write(json.dumps(msg) + '\n')
        
        processor = ClaudeLogProcessor(self.temp_dir)
        messages, _ = processor.process_logs()
        
        # Should have deduplicated to 1 message
        self.assertEqual(len(messages), 1, "Duplicate messages should be removed")
        
    def test_tool_extraction(self):
        """Test that tools are extracted correctly from actual data"""
        processor = ClaudeLogProcessor(self.test_data_dir)
        messages, statistics = processor.process_logs()
        
        # Find messages with tools
        tool_messages = [msg for msg in messages if msg.get('tools')]
        
        # We know the test data contains TodoWrite tools
        self.assertGreater(len(tool_messages), 0, "Should have messages with tools")
        
        # Verify tool structure
        tool_names_found = set()
        for msg in tool_messages:
            for tool in msg['tools']:
                self.assertIn('name', tool)
                self.assertIn('input', tool)
                tool_names_found.add(tool['name'])
        
        # Verify we found TodoWrite tool which is in the test data
        self.assertIn('TodoWrite', tool_names_found, "Should find TodoWrite tool in test data")
        
        # Verify tool statistics
        if 'tools' in statistics:
            tool_usage = statistics['tools'].get('usage_counts', {})
            self.assertIn('TodoWrite', tool_usage, "TodoWrite should be in tool usage stats")
                    
    def test_streaming_message_merge(self):
        """Test that streaming messages are merged correctly"""
        # Create test data with streaming messages matching actual log format
        test_messages = [
            {
                "type": "user",
                "parentUuid": None,
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test",
                "sessionId": "test-session",
                "version": "1.0.17",
                "message": {
                    "role": "user",
                    "content": [{"type": "text", "text": "Test question"}]
                },
                "uuid": "user1",
                "timestamp": "2025-06-08T10:59:59.000Z"
            },
            {
                "type": "assistant",
                "parentUuid": "user1",
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test",
                "sessionId": "test-session",
                "version": "1.0.17",
                "message": {
                    "id": "msg_123",
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-3-sonnet",
                    "content": [{"type": "text", "text": "Part 1"}],
                    "usage": {"input_tokens": 10, "output_tokens": 5}
                },
                "uuid": "assistant1",
                "timestamp": "2025-06-08T11:00:00.000Z"
            },
            {
                "type": "assistant",
                "parentUuid": "user1",
                "isSidechain": False,
                "userType": "external",
                "cwd": "/test",
                "sessionId": "test-session",
                "version": "1.0.17",
                "message": {
                    "id": "msg_123",  # Same ID, streaming continuation
                    "type": "message",
                    "role": "assistant",
                    "model": "claude-3-sonnet",
                    "content": [{"type": "text", "text": "Part 2"}],
                    "usage": {"input_tokens": 0, "output_tokens": 5}
                },
                "uuid": "assistant2",
                "timestamp": "2025-06-08T11:00:01.000Z"
            }
        ]
        
        # Write test data
        test_file = os.path.join(self.temp_dir, "test-session.jsonl")
        with open(test_file, 'w') as f:
            for msg in test_messages:
                f.write(json.dumps(msg) + '\n')
        
        processor = ClaudeLogProcessor(self.temp_dir)
        messages, _ = processor.process_logs()
        
        # Should have total of 2 messages (1 user + 1 merged assistant)
        self.assertEqual(len(messages), 2, "Should have 2 messages total")
        
        # Should have merged to 1 assistant message
        assistant_messages = [m for m in messages if m['type'] == 'assistant']
        self.assertEqual(len(assistant_messages), 1, "Streaming messages should be merged")
        
        # Check content was merged
        merged = assistant_messages[0]
        self.assertIn("Part 1", merged['content'])
        self.assertIn("Part 2", merged['content'])
        
        # Check tokens were summed
        self.assertEqual(merged['tokens']['input'], 10)
        self.assertEqual(merged['tokens']['output'], 10)  # 5 + 5
        
    def test_session_continuation(self):
        """Test session continuation detection"""
        # This would require multiple session files with continuation patterns
        processor = ClaudeLogProcessor(self.test_data_dir)
        
        # Just verify the processor handles multiple sessions correctly
        messages, statistics = processor.process_logs()
        sessions = set(m['session_id'] for m in messages)
        
        # We know our test data has 4 sessions
        self.assertEqual(len(sessions), 4, "Should have 4 sessions")
            
    def test_summary_handling(self):
        """Test handling of summary messages"""
        processor = ClaudeLogProcessor(self.test_data_dir)
        messages, _ = processor.process_logs()
        
        # Check for summary messages
        summaries = [m for m in messages if m['type'] == 'summary']
        compact_summaries = [m for m in messages if m['type'] == 'compact_summary']
        
        # Verify summary structure if any exist
        for summary in summaries + compact_summaries:
            self.assertIn('content', summary)
            self.assertIn('timestamp', summary)
            
    def test_empty_directory(self):
        """Test handling of empty directory"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)
        
        processor = ClaudeLogProcessor(empty_dir)
        messages, statistics = processor.process_logs()
        
        self.assertEqual(len(messages), 0, "Empty directory should return no messages")
        self.assertIsNotNone(statistics, "Statistics should still be returned")
        
    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        # Create test file with malformed JSON
        test_file = os.path.join(self.temp_dir, "malformed.jsonl")
        with open(test_file, 'w') as f:
            f.write('{"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": "test1"}]}, "sessionId": "test", "timestamp": "2025-06-08T10:00:00.000Z"}\n')
            f.write('invalid json\n')  # This should be skipped
            f.write('{"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "test2"}]}, "sessionId": "test", "timestamp": "2025-06-08T10:00:01.000Z"}\n')
        
        processor = ClaudeLogProcessor(self.temp_dir)
        messages, _ = processor.process_logs()
        
        # Should process valid lines and skip invalid
        self.assertGreaterEqual(len(messages), 1, "Should process at least one valid JSON line")


class TestProcessorHelpers(unittest.TestCase):
    """Test helper methods of the processor"""
    
    def test_interaction_class(self):
        """Test the Interaction class"""
        user_msg = {
            'type': 'user',
            'content': 'Test message',
            'timestamp': '2025-06-08T11:00:00.000Z',
            'session_id': 'test-session'
        }
        
        interaction = Interaction(user_msg)
        
        self.assertEqual(interaction.session_id, 'test-session')
        self.assertEqual(interaction.start_time, '2025-06-08T11:00:00.000Z')
        self.assertFalse(interaction.is_complete)
        
        # Add assistant message
        assistant_msg = {
            'type': 'assistant',
            'content': 'Response',
            'timestamp': '2025-06-08T11:00:01.000Z',
            'model': 'claude-3-sonnet'
        }
        
        interaction.add_assistant_message(assistant_msg)
        self.assertEqual(interaction.model, 'claude-3-sonnet')
        self.assertEqual(len(interaction.assistant_messages), 1)
        
    def test_completeness_score(self):
        """Test interaction completeness scoring"""
        user_msg = {'type': 'user', 'content': 'Test', 'session_id': 'test'}
        interaction = Interaction(user_msg)
        
        # Empty interaction should have low score
        score1 = interaction.completeness_score()
        
        # Add assistant message
        interaction.add_assistant_message({
            'type': 'assistant',
            'content': 'Response',
            'message': {'usage': {'output_tokens': 100}}
        })
        
        score2 = interaction.completeness_score()
        self.assertGreater(score2, score1, "Score should increase with assistant message")
        
        # Add tools
        interaction.tools_used = [{'name': 'Read', 'id': '123'}]
        score3 = interaction.completeness_score()
        self.assertGreater(score3, score2, "Score should increase with tools")


class TestProcessorConsistency(unittest.TestCase):
    """Test that processor produces consistent results"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data directory"""
        cls.test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mock-data', '-Users-chip-dev-ai-music')
    
    def test_deterministic_processing(self):
        """Test that processing the same data produces the same results"""
        processor1 = ClaudeLogProcessor(self.test_data_dir)
        messages1, stats1 = processor1.process_logs()
        
        processor2 = ClaudeLogProcessor(self.test_data_dir)
        messages2, stats2 = processor2.process_logs()
        
        # Messages should be identical
        self.assertEqual(len(messages1), len(messages2), 
                        "Should produce same number of messages")
        
        # Statistics should be identical
        self.assertEqual(stats1['overview']['total_messages'], 
                        stats2['overview']['total_messages'],
                        "Total message count should be consistent")
        
        # Token counts should be identical
        self.assertEqual(stats1['overview']['total_tokens'],
                        stats2['overview']['total_tokens'],
                        "Token counts should be consistent")


class TestActualDataCharacteristics(unittest.TestCase):
    """Test specific characteristics of the actual test data"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data directory and process once"""
        cls.test_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'mock-data', '-Users-chip-dev-ai-music')
        processor = ClaudeLogProcessor(cls.test_data_dir)
        cls.messages, cls.statistics = processor.process_logs()
    
    def test_ai_music_project_content(self):
        """Test that we correctly process the AI music project data"""
        # The test data is from an AI music project
        summaries = [m for m in self.messages if m['type'] == 'summary']
        
        # Should have at least one summary mentioning AI Music
        ai_music_summaries = [s for s in summaries 
                             if 'AI Music' in s.get('content', '') or 
                                'ai_music' in s.get('content', '').lower()]
        self.assertGreater(len(ai_music_summaries), 0, 
                          "Should find AI Music related summaries")
    
    def test_jupyter_notebook_creation(self):
        """Test that we capture the jupyter notebook creation request"""
        # Look for user messages about jupyter notebook
        user_messages = [m for m in self.messages if m['type'] == 'user']
        jupyter_messages = [m for m in user_messages 
                           if 'jupyter' in m.get('content', '').lower() or
                              'notebook' in m.get('content', '').lower()]
        
        self.assertGreater(len(jupyter_messages), 0,
                          "Should find messages about jupyter notebook")
    
    def test_session_continuity(self):
        """Test that all expected sessions are processed"""
        sessions = set(m['session_id'] for m in self.messages)
        expected_sessions = {
            'ba79134d-b6e9-4867-af0c-6941038c9e4b',
            'd3ad4cdc-5657-435d-98fa-0035d53e383d',
            'fed8ce56-bc79-401f-a83e-af084253362f',
            'ff71dbed-a4f2-4284-a4fc-fe2fb90de929'
        }
        
        self.assertEqual(sessions, expected_sessions,
                        "Should process all expected sessions")
    
    def test_timestamp_ordering(self):
        """Test that messages are properly ordered by timestamp (newest first)"""
        # Messages should be sorted in reverse chronological order
        timestamps = [msg['timestamp'] for msg in self.messages if msg.get('timestamp')]
        sorted_timestamps = sorted(timestamps, reverse=True)
        
        # Compare first 10 to avoid issues with messages that have same timestamp
        self.assertEqual(timestamps[:10], sorted_timestamps[:10],
                        "Messages should be ordered by timestamp (newest first)")


def create_baseline_results():
    """Create baseline results file for future comparison"""
    test_data_dir = os.path.join(os.path.dirname(__file__), 'mock-data', '-Users-chip-dev-ai-music')
    processor = ClaudeLogProcessor(test_data_dir)
    messages, statistics = processor.process_logs()
    
    # Collect detailed baseline data
    baseline = {
        'message_count': len(messages),
        'total_tokens': statistics['overview']['total_tokens'],
        'message_types': statistics['overview']['message_types'],
        'user_interactions': statistics.get('user_interactions', {}),
        'cache_stats': statistics.get('cache', {}),
        'error_count': statistics.get('errors', {}).get('total_errors', 0),
        'sessions': statistics['overview']['sessions'],
        'date_range': statistics['overview']['date_range'],
        'tool_usage': statistics.get('tools', {}).get('usage_counts', {}),
        'models': statistics.get('models', {}).get('usage_counts', {}),
        # Store message details for verification
        'message_details': {
            'user_count': len([m for m in messages if m['type'] == 'user']),
            'assistant_count': len([m for m in messages if m['type'] == 'assistant']),
            'summary_count': len([m for m in messages if m['type'] == 'summary']),
            'tool_result_count': len([m for m in messages if m.get('has_tool_result', False)]),
        }
    }
    
    # Save baseline
    baseline_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'baseline_results.json')
    with open(baseline_file, 'w') as f:
        json.dump(baseline, f, indent=2)
    
    print(f"Baseline results saved to {baseline_file}")
    print(f"Total messages: {baseline['message_count']}")
    print(f"Message types: {baseline['message_types']}")
    print(f"Total tokens: {baseline['total_tokens']}")
    return baseline


if __name__ == '__main__':
    # Optionally create baseline on first run
    import sys
    if '--create-baseline' in sys.argv:
        create_baseline_results()
        sys.exit(0)
    
    # Run tests
    unittest.main()