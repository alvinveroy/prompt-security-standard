"""
Basic UPSS Example Application
Demonstrates simple usage of the UPSS loader in a Python application.
"""

from upss_loader import UPSSLoader
import sys


def main():
    """Main application entry point."""
    try:
        # Initialize the UPSS loader
        print("Loading UPSS configuration...")
        loader = UPSSLoader("upss_config.yaml")
        
        # Display available prompts
        print("\n" + "="*50)
        print("Available Prompts:")
        print("="*50)
        for prompt_id in loader.list_prompts():
            metadata = loader.get_prompt_metadata(prompt_id)
            print(f"\nID: {prompt_id}")
            print(f"  Type: {metadata.get('type')}")
            print(f"  Version: {metadata.get('version')}")
            print(f"  Description: {metadata.get('description')}")
        
        # Load and display a specific prompt
        print("\n" + "="*50)
        print("System Assistant Prompt:")
        print("="*50)
        system_prompt = loader.get_prompt("system_assistant")
        print(system_prompt)
        
        # Display prompt integrity hash
        print("\n" + "="*50)
        print("Prompt Integrity:")
        print("="*50)
        hash_value = loader.get_prompt_hash("system_assistant")
        print(f"SHA-256: {hash_value}")
        
        # Show audit log if enabled
        print("\n" + "="*50)
        print("Audit Log:")
        print("="*50)
        audit_log = loader.get_audit_log()
        if audit_log:
            for entry in audit_log:
                print(f"{entry['timestamp']} - {entry['prompt_id']}: {entry['action']}")
        else:
            print("Audit logging is not enabled or no entries recorded.")
        
        print("\n" + "="*50)
        print("Application completed successfully!")
        print("="*50)
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
