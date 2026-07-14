#!/usr/bin/env bash

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 切换到项目根目录
cd "${PROJECT_ROOT}"
log_info "定位到项目根目录: ${PROJECT_ROOT}"

# 检查依赖环境
log_info "正在检查运行环境..."
if ! command -v pytest &> /dev/null; then
    log_warn "未检测到 pytest，正在尝试为您自动安装所需的测试依赖..."
    if command -v pip &> /dev/null; then
        pip install pytest pandas numpy
        log_success "依赖安装成功！"
    else
        log_error "未找到 pip，请手动安装 pytest, pandas, numpy 后再运行此脚本。"
        exit 1
    fi
fi

# 执行测试
log_info "🚀 开始运行问卷清洗流水线测试..."
echo -e "${YELLOW}------------------------------------------------------------${NC}"

if pytest "$@"; then
    echo -e "${YELLOW}------------------------------------------------------------${NC}"
    log_success "🎉 所有测试用例全部通过！数据清洗契约完美对账。"
    exit 0
else
    echo -e "${YELLOW}------------------------------------------------------------${NC}"
    log_error "❌ 测试未通过，请根据上方错误日志调整清洗器 (QuestionnaireCleaner) 规则。"
    exit 1
fi