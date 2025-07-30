#!/usr/bin/env python3

# Standard libraries
from pathlib import Path
from typing import List

# Components
from ..system.commands import Commands

# Git class
class Git:

    # Constants
    BINARY: str = 'git'

    # Commit exists
    @staticmethod
    def commit_exists(reference: str) -> bool:

        # Check commit existance
        return bool(
            Commands.output(Git.BINARY, [
                'rev-parse',
                '--quiet',
                '--verify',
                reference,
            ]))

    # Diff
    @staticmethod
    def diff(files: List[str]) -> bool:

        # Detect files differences
        return not Commands.run(
            Git.BINARY,
            [
                'diff',
                '--quiet',
            ] + files,
            check=False,
        )

    # Hooks directory
    @staticmethod
    def hooks_dir() -> str:

        # Result
        return Commands.output(Git.BINARY, [
            'rev-parse',
            '--git-path',
            'hooks',
        ])

    # Hooks files
    @staticmethod
    def hooks_files() -> List[str]:

        # Variables
        hooks_dir: Path = Path(Git.hooks_dir())

        # Result
        return [
            hook.name for hook in Path(hooks_dir).iterdir()
            if hook.is_file() and '.' not in hook.name
        ]

    # Remotes
    @staticmethod
    def remotes() -> List[str]:

        # List git remotes
        return [
            remote.lstrip('*').strip()
            for remote in Commands.output(Git.BINARY, [
                'remote',
            ]).splitlines()
        ]

    # Staging empty
    @staticmethod
    def staging_empty() -> bool:

        # Detect empty staging area
        return Commands.run(
            Git.BINARY,
            [
                'diff',
                '--cached',
                '--quiet',
            ],
            check=False,
        )

    # Status
    @staticmethod
    def status(untracked: bool) -> bool:

        # Show git status
        return Commands.run(Git.BINARY, [
            'status',
        ] + ([
            '--untracked-files',
        ] if untracked else []))

    # Update remote head
    @staticmethod
    def update_remote_head(remote: str) -> bool:

        # Fetch remote branches
        Commands.run(Git.BINARY, [
            'fetch',
            f'{remote}',
        ])

        # Update remote head
        return Commands.run(Git.BINARY, [
            'remote',
            'set-head',
            f'{remote}',
            '-a',
        ])

    # URLs
    @staticmethod
    def urls() -> List[str]:

        # List git remotes URLs
        return [
            url.strip() for url in Commands.output(Git.BINARY, [
                'ls-remote',
                '--get-url',
            ]).splitlines()
        ]
