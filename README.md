# Sysroot Manipulation Utilities

This repository contains a collection of scripts designed to create, clean, and manage `sysroot` environments. These tools are useful for preparing environments for cross-compilation, chrooting, or system analysis.

## Scripts

### 1. `sysroot_rsync.sh`

This script is used to create a `sysroot` by copying a remote root filesystem to a local directory using `rsync`. It is configured to exclude system-specific, temporary, and other non-essential directories to create a clean and portable `sysroot`.

**Usage:**

```bash
./sysroot_rsync.sh
```

**Note:** You need to edit the script to set the `source-root` and `dest-sysroot` variables to your desired source and destination.

### 2. `fix_sysroot_symlink_enhace.py`

This Python script recursively finds all symbolic links within a given `sysroot` directory and fixes them to point to their final, resolved targets. This is particularly useful for correcting broken or nested symlinks that can occur after copying a filesystem.

**Usage:**

```bash
python3 fix_sysroot_symlink_enhace.py <sysroot_dir> [options]
```

**Arguments:**

*   `sysroot_dir`: The path to the `sysroot` directory you want to process.

**Options:**

*   `-n`, `--dry-run`: Run the script in simulation mode. It will print the changes that would be made without actually modifying any files.
*   `-v`, `--verbose`: Enable verbose output to see detailed information about the operations being performed.

### 3. `replace_symlink_with_file.py`

This script recursively finds all symbolic links within a specified directory and replaces each link with a copy of the actual file it points to. This can be useful when the build or runtime environment does not handle symbolic links correctly.

**Usage:**

```bash
python3 replace_symlink_with_file.py <directory> [options]
```

**Arguments:**

*   `directory`: The path to the directory you want to process.

**Options:**

*   `-n`, `--dry-run`: Run the script in simulation mode. It will show which symlinks would be replaced without performing any actual file operations.
*   `-v`, `--verbose`: Enable verbose output for detailed logging of the replacement process.

## Typical Workflow

1.  **Create the Sysroot**: Use `sysroot_rsync.sh` to copy the root filesystem from a source machine to your local `sysroot` directory.
2.  **Fix Symlinks**: Run `fix_sysroot_symlink_enhace.py` on the newly created `sysroot` to ensure all symbolic links are correctly resolved and pointing to valid targets within the `sysroot`.
3.  **Replace Symlinks (Optional)**: If your use case requires it, use `replace_symlink_with_file.py` to replace all symbolic links with the actual files.
