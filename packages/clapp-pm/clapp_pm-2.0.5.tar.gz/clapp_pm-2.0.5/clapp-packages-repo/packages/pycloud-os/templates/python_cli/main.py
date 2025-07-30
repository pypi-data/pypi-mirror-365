#!/usr/bin/env python3
"""
{{project_name}}
{{description}}

Author: {{author_name}}
"""

import argparse
import sys


def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="{{description}}")
    parser.add_argument("--version", action="version", version="1.0.0")
    
    args = parser.parse_args()
    
    print("Merhaba, {{project_name}}!")


if __name__ == "__main__":
    main()
