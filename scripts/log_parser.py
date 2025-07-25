import pandas as pd
import re
import ast
from datetime import datetime
from typing import Dict, Any, Optional, List


class LogParser:
    def __init__(self):
        # Regex pattern to parse the log structure
        self.log_pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3}\|(\w+)\|User context: ([^|]+)\|Model: ([^|]+)\|Summariser: ([^|]+)\|Chat Class: ([^|]+)\|Messages:(.*)$'

    def parse_user_context(self, context_str: str) -> Dict[str, Optional[str]]:
        """Parse the user context string into individual components."""
        context_dict = {
            'participant_code': None,
            'role': None,
            'affiliation': None
        }

        # Handle 'None' case
        if context_str.strip() == 'None':
            return context_dict

        try:
            # Use ast.literal_eval to safely parse the dictionary string
            parsed_context = ast.literal_eval(context_str.strip())
            if isinstance(parsed_context, dict):
                context_dict.update({
                    'participant_code': parsed_context.get('participant_code'),
                    'role': parsed_context.get('role'),
                    'affiliation': parsed_context.get('affiliation')
                })
        except (ValueError, SyntaxError):
            # If parsing fails, try to extract manually
            print(f"Warning: Could not parse user context: {context_str}")

        return context_dict

    def parse_messages(self, messages_str: str) -> str:
        """Parse message history and format it for better readability."""
        if not messages_str or messages_str.strip() == '':
            return None

        # Split messages by the delimiter and join with newlines
        messages = messages_str.strip().split(' ~~~ ')
        # Filter out empty messages
        messages = [msg.strip() for msg in messages if msg.strip()]

        if not messages:
            return None

        # Join messages with newlines for better display in Tableau
        return '\n'.join([f"Message {i+1}: {msg}" for i, msg in enumerate(messages)])

    def parse_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse a single log line into structured data."""
        match = re.match(self.log_pattern, line.strip())

        if not match:
            print(f"Warning: Could not parse line: {line[:100]}...")
            return None

        timestamp_str, log_level, user_context_str, model, summariser, chat_class, messages_str = match.groups()

        # Parse timestamp (remove milliseconds)
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"Warning: Could not parse timestamp: {timestamp_str}")
            timestamp = None

        # Parse user context
        user_context = self.parse_user_context(user_context_str)

        # Parse messages
        parsed_messages = self.parse_messages(messages_str)

        # Count number of messages
        message_count = 0
        if messages_str and messages_str.strip():
            message_count = len(
                [msg for msg in messages_str.strip().split(' ~~~ ') if msg.strip()])

        return {
            'timestamp': timestamp,
            'log_level': log_level,
            'participant_code': user_context['participant_code'],
            'role': user_context['role'],
            'affiliation': user_context['affiliation'],
            'model': model,
            'summariser': summariser.lower() == 'true',  # Convert to boolean
            'chat_class': chat_class,
            'message_history': parsed_messages,
            'message_count': message_count
        }

    def parse_log_file(self, file_path: str) -> pd.DataFrame:
        """Parse entire log file and return as DataFrame."""
        parsed_data = []

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():  # Skip empty lines
                        parsed_line = self.parse_log_line(line)
                        if parsed_line:
                            parsed_line['line_number'] = line_num
                            parsed_data.append(parsed_line)

        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading file: {e}")
            return pd.DataFrame()

        if not parsed_data:
            print("Warning: No valid log entries found.")
            return pd.DataFrame()

        df = pd.DataFrame(parsed_data)

        # Reorder columns for better analysis
        column_order = [
            'line_number', 'timestamp', 'participant_code', 'role', 'affiliation',
            'model', 'summariser', 'chat_class', 'message_count', 'message_history'
        ]

        df = df[column_order]

        return df

    def export_for_tableau(self, df: pd.DataFrame, output_path: str, format: str = 'csv'):
        """Export DataFrame in format suitable for Tableau."""
        try:
            if format.lower() == 'csv':
                df.to_csv(output_path, index=False, encoding='utf-8')
            elif format.lower() == 'excel':
                df.to_excel(output_path, index=False, engine='openpyxl')
            else:
                raise ValueError("Format must be 'csv' or 'excel'")

            print(f"Data exported successfully to {output_path}")

        except Exception as e:
            print(f"Error exporting data: {e}")

# Example usage


def main():
    parser = LogParser()

    # Example with sample data
    sample_logs = [
        "2025-07-25 15:47:50,154|INFO|User context: None|Model: gpt-4.1|Summariser: True|Chat Class: QueryRewriterRAG|Messages:",
        "2025-07-25 15:35:02,743|INFO|User context: {'participant_code': 'ABC', 'role': 'GTA', 'affiliation': 'Economics Department'}|Model: gpt-4.1|Summariser: True|Chat Class: QueryRewriterRAG|Messages: hello ~~~ hello ~~~ Hello. How can I assist you today? ~~~ am I allowed to have a part-time job outside of LSE?"
    ]

    # Parse sample data
    parsed_data = []
    for i, log_line in enumerate(sample_logs, 1):
        parsed_line = parser.parse_log_line(log_line)
        if parsed_line:
            parsed_line['line_number'] = i
            parsed_data.append(parsed_line)

    # Create DataFrame
    df = pd.DataFrame(parsed_data)
    column_order = [
        'line_number', 'timestamp', 'participant_code', 'role', 'affiliation',
        'model', 'summariser', 'chat_class', 'message_count', 'message_history'
    ]
    df = df[column_order]

    print("Sample parsed data:")
    print(df.to_string(max_colwidth=50))

    # To use with actual file:
    df = parser.parse_log_file(
        '/Users/steve/chat-lse/logs/app_log_2025-07-25.log')
    parser.export_for_tableau(
        df, '/Users/steve/chat-lse/logs/parsed_logs.csv', 'csv')
    # parser.export_for_tableau(df, 'parsed_logs.xlsx', 'excel')


if __name__ == "__main__":
    main()
