#!/usr/bin/env bash

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

# Default settings
CLEAN_BEFORE=1
NO_SOURCES=1
VERIFY=0

# Usage function
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Build Python package for distribution.

OPTIONS:
    --no-clean         Don't clean before building
    --with-sources     Include source distributions (default: wheel only)
    --verify           Verify the built package can be installed
    --debug            Enable debug output
    -h, --help         Show this help message

EXAMPLES:
    $(basename "$0")                    # Build package (wheel only)
    $(basename "$0") --with-sources     # Build wheel and sdist
    $(basename "$0") --verify           # Build and verify installation
    $(basename "$0") --no-clean         # Build without cleaning first
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-clean)
            CLEAN_BEFORE=0
            shift
            ;;
        --with-sources)
            NO_SOURCES=0
            shift
            ;;
        --verify)
            VERIFY=1
            shift
            ;;
        --debug)
            export DEBUG=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        -*)
            error "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            error "Unexpected argument: $1"
            usage
            exit 1
            ;;
    esac
done

# Check uv availability
check_uv || exit 1

# Clean if requested
if [[ ${CLEAN_BEFORE} -eq 1 ]]; then
    info "Cleaning build artifacts..."
    "${SCRIPT_DIR}/clean.sh" --build-only || exit 1
fi

info "🏗️  Building package..."

# Build command
BUILD_CMD="uv build"
if [[ ${NO_SOURCES} -eq 1 ]]; then
    BUILD_CMD="${BUILD_CMD} --no-sources"
fi

# Run build
if ! run_command ${BUILD_CMD}; then
    error "Build failed"
    exit 1
fi

# List built artifacts
info "Built artifacts:"
for artifact in "${PROJECT_ROOT}/dist/"*; do
    if [[ -f "${artifact}" ]]; then
        echo "  - $(basename "${artifact}")"
    fi
done

success "✅ Build complete! Artifacts in dist/"

# Verify if requested
if [[ ${VERIFY} -eq 1 ]]; then
    info "🔍 Verifying package installation..."
    
    # Create temporary virtual environment
    temp_dir=$(mktemp -d)
    trap "rm -rf ${temp_dir}" EXIT
    
    # Find the wheel file
    wheel_file=$(find "${PROJECT_ROOT}/dist" -name "*.whl" | head -1)
    if [[ -z "${wheel_file}" ]]; then
        error "No wheel file found in dist/"
        exit 1
    fi
    
    # Test installation in isolated environment
    cd "${temp_dir}"
    if uv venv && \
       uv pip install "${wheel_file}" && \
       uv run python -c "import ${PACKAGE_NAME}; print('${PACKAGE_NAME} v' + getattr(${PACKAGE_NAME}, '__version__', 'unknown'))"; then
        success "✅ Package verified successfully!"
    else
        error "❌ Package verification failed"
        exit 1
    fi
fi