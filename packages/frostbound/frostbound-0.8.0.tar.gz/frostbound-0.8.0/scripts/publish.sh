#!/usr/bin/env bash
set -euo pipefail

readonly PACKAGE_NAME="frostbound"
readonly PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly DIST_DIR="${PROJECT_ROOT}/dist"

info() { echo "▶ $*"; }
success() { echo "✓ $*"; }
error() { echo "✗ $*" >&2; }
die() { error "$@"; exit 1; }

check_prerequisites() {
    info "Checking prerequisites..."
    
    command -v uv >/dev/null 2>&1 || die "uv not found. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    
    [[ -f "${PROJECT_ROOT}/pyproject.toml" ]] || die "pyproject.toml not found"
    
    [[ -n "${PYPI_TOKEN:-}" ]] || die "PYPI_TOKEN environment variable not set"
    
    # Check if semantic-release is available
    if ! uv run --no-project --with python-semantic-release -- semantic-release --help >/dev/null 2>&1; then
        info "Installing python-semantic-release..."
        uv add --dev python-semantic-release
    fi
    
    success "Prerequisites satisfied"
}

clean_artifacts() {
    info "Cleaning build artifacts..."
    rm -rf "${DIST_DIR}"
    success "Build artifacts cleaned"
}

get_current_version() {
    grep '^version = ' "${PROJECT_ROOT}/pyproject.toml" | head -1 | cut -d'"' -f2
}


auto_version() {
    info "Analyzing commits for version bump..."
    
    cd "${PROJECT_ROOT}"
    
    # Check what version would be bumped to
    local new_version
    new_version=$(uv run --no-project --with python-semantic-release -- semantic-release version --print 2>/dev/null || echo "")
    
    if [[ -z "${new_version}" ]]; then
        info "No version bump needed based on commit history"
        local current_version
        current_version=$(get_current_version)
        info "Current version: ${current_version}"
        read -p "Continue with current version? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || die "Deployment cancelled"
    else
        info "Version will be bumped to: ${new_version}"
        read -p "Continue with auto-versioning? [y/N] " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] || die "Deployment cancelled"
        
        # Perform the version bump
        uv run --no-project --with python-semantic-release -- semantic-release version --no-commit --no-tag
        success "Version bumped to ${new_version}"
    fi
}

build_package() {
    info "Building package..."
    
    cd "${PROJECT_ROOT}"
    uv build --no-sources
    
    local artifacts
    artifacts=(${DIST_DIR}/*)
    
    [[ ${#artifacts[@]} -gt 0 ]] || die "No build artifacts found"
    
    success "Built ${#artifacts[@]} artifact(s):"
    for artifact in "${artifacts[@]}"; do
        echo "  - $(basename "${artifact}")"
    done
}

publish_package() {
    info "Publishing to PyPI..."
    
    cd "${PROJECT_ROOT}"
    UV_PUBLISH_URL="https://upload.pypi.org/legacy/" \
        uv publish --token "${PYPI_TOKEN}"
    
    success "Published to PyPI"
}

verify_installation() {
    info "Verifying installation..."
    
    sleep 5
    
    if uv run --with "${PACKAGE_NAME}" --no-project -- \
        python -c "import ${PACKAGE_NAME}; print('${PACKAGE_NAME} v' + getattr(${PACKAGE_NAME}, '__version__', 'unknown'))"; then
        success "Package verified"
    else
        error "Could not verify installation (may need more time to propagate)"
    fi
}

main() {
    check_prerequisites
    auto_version
    clean_artifacts
    build_package
    publish_package
    verify_installation
    
    success "Deployment completed successfully! 🎉"
}

main "$@"