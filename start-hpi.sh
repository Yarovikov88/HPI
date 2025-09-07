#!/bin/bash

# Скрипт для запуска всего проекта HPI.EXPERT
# Включает сайт и Telegram ботов

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для вывода сообщений
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
}

# Функция запуска
start_project() {
    log_info "Запускаю проект HPI.EXPERT..."
    
    # Проверяем, какой файл docker-compose использовать
    if [ -f "docker-compose.simple.yml" ]; then
        log_info "Использую простую конфигурацию (только боты)"
        docker-compose -f docker-compose.simple.yml up -d
    elif [ -f "docker-compose.bots-only.yml" ]; then
        log_info "Использую конфигурацию только для ботов"
        docker-compose -f docker-compose.bots-only.yml up -d
    elif [ -f "docker-compose.full.yml" ]; then
        log_info "Использую полную конфигурацию (сайт + боты)"
        docker-compose -f docker-compose.full.yml up -d
    elif [ -f "docker-compose.bots.yml" ]; then
        log_info "Использую конфигурацию только для ботов (старая версия)"
        docker-compose -f docker-compose.bots.yml up -d
    else
        log_error "Не найден файл docker-compose. Убедитесь, что вы находитесь в корневой папке проекта."
        exit 1
    fi
    
    log_success "Проект запущен!"
    log_info "Проверьте статус: $0 status"
    log_info "Посмотрите логи: $0 logs"
}

# Функция остановки
stop_project() {
    log_info "Останавливаю проект HPI.EXPERT..."
    
    if [ -f "docker-compose.simple.yml" ]; then
        docker-compose -f docker-compose.simple.yml down
    elif [ -f "docker-compose.bots-only.yml" ]; then
        docker-compose -f docker-compose.bots-only.yml down
    elif [ -f "docker-compose.full.yml" ]; then
        docker-compose -f docker-compose.full.yml down
    elif [ -f "docker-compose.bots.yml" ]; then
        docker-compose -f docker-compose.bots.yml down
    fi
    
    log_success "Проект остановлен!"
}

# Функция перезапуска
restart_project() {
    log_info "Перезапускаю проект HPI.EXPERT..."
    stop_project
    sleep 2
    start_project
}

# Функция статуса
show_status() {
    log_info "Статус контейнеров:"
    
    if [ -f "docker-compose.simple.yml" ]; then
        docker-compose -f docker-compose.simple.yml ps
    elif [ -f "docker-compose.bots-only.yml" ]; then
        docker-compose -f docker-compose.bots-only.yml ps
    elif [ -f "docker-compose.full.yml" ]; then
        docker-compose -f docker-compose.full.yml ps
    elif [ -f "docker-compose.bots.yml" ]; then
        docker-compose -f docker-compose.bots.yml ps
    fi
}

# Функция логов
show_logs() {
    log_info "Показываю логи (Ctrl+C для выхода):"
    
    if [ -f "docker-compose.simple.yml" ]; then
        docker-compose -f docker-compose.simple.yml logs -f
    elif [ -f "docker-compose.bots-only.yml" ]; then
        docker-compose -f docker-compose.bots-only.yml logs -f
    elif [ -f "docker-compose.full.yml" ]; then
        docker-compose -f docker-compose.full.yml logs -f
    elif [ -f "docker-compose.bots.yml" ]; then
        docker-compose -f docker-compose.bots.yml logs -f
    fi
}

# Функция пересборки
rebuild_project() {
    log_info "Пересобираю проект HPI.EXPERT..."
    
    if [ -f "docker-compose.simple.yml" ]; then
        docker-compose -f docker-compose.simple.yml build --no-cache
        docker-compose -f docker-compose.simple.yml up -d
    elif [ -f "docker-compose.bots-only.yml" ]; then
        docker-compose -f docker-compose.bots-only.yml build --no-cache
        docker-compose -f docker-compose.bots-only.yml up -d
    elif [ -f "docker-compose.full.yml" ]; then
        docker-compose -f docker-compose.full.yml build --no-cache
        docker-compose -f docker-compose.full.yml up -d
    elif [ -f "docker-compose.bots.yml" ]; then
        docker-compose -f docker-compose.bots.yml build --no-cache
        docker-compose -f docker-compose.bots.yml up -d
    fi
    
    log_success "Проект пересобран и запущен!"
}

# Функция помощи
show_help() {
    echo "HPI.EXPERT - Скрипт управления проектом"
    echo ""
    echo "Использование: $0 [команда]"
    echo ""
    echo "Команды:"
    echo "  start     - Запустить проект (сайт + боты)"
    echo "  stop      - Остановить проект"
    echo "  restart   - Перезапустить проект"
    echo "  status    - Показать статус контейнеров"
    echo "  logs      - Показать логи в реальном времени"
    echo "  rebuild   - Пересобрать и запустить проект"
    echo "  help      - Показать эту справку"
    echo ""
    echo "Примеры:"
    echo "  $0 start    # Запустить всё"
    echo "  $0 status   # Проверить статус"
    echo "  $0 logs     # Смотреть логи"
}

# Основная логика
main() {
    check_docker
    
    case "${1:-start}" in
        start)
            start_project
            ;;
        stop)
            stop_project
            ;;
        restart)
            restart_project
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        rebuild)
            rebuild_project
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Неизвестная команда: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Запуск скрипта
main "$@" 