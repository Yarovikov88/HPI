#!/bin/bash

# Скрипт для запуска рабочей конфигурации HPI.EXPERT
# Исправляет все проблемы с API и сетями

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

# Подготовка файлов
prepare_files() {
    log_info "Подготавливаю файлы конфигурации..."
    
    # Копируем рабочий server.cjs
    if [ -f "server-working.cjs" ]; then
        cp server-working.cjs server.cjs
        log_success "Скопирован рабочий server.cjs"
    else
        log_error "Файл server-working.cjs не найден!"
        exit 1
    fi
    
    # Проверяем наличие nginx конфигурации
    if [ ! -f "nginx-working.conf" ]; then
        log_error "Файл nginx-working.conf не найден!"
        exit 1
    fi
    
    log_success "Файлы подготовлены"
}

# Остановка всех контейнеров
stop_all_containers() {
    log_info "Останавливаю все контейнеры..."
    
    # Останавливаем все docker-compose проекты
    docker-compose -f docker-compose.yml down 2>/dev/null || true
    docker-compose -f docker-compose.full.yml down 2>/dev/null || true
    docker-compose -f docker-compose.simple.yml down 2>/dev/null || true
    docker-compose -f docker-compose.bots-only.yml down 2>/dev/null || true
    docker-compose -f docker-compose.bots.yml down 2>/dev/null || true
    docker-compose -f docker-compose.feedback.yml down 2>/dev/null || true
    
    # Останавливаем отдельные контейнеры
    docker stop hpi-web-1 nginx fastapi_app hpi-frontend hpi-telegram-bots hpi-feedback-server 2>/dev/null || true
    docker rm hpi-web-1 nginx fastapi_app hpi-frontend hpi-telegram-bots hpi-feedback-server 2>/dev/null || true
    
    log_success "Все контейнеры остановлены"
}

# Запуск рабочей конфигурации
start_working_config() {
    log_info "Запускаю рабочую конфигурацию..."
    
    if [ ! -f "docker-compose.working.yml" ]; then
        log_error "Файл docker-compose.working.yml не найден!"
        exit 1
    fi
    
    # Запускаем рабочую конфигурацию
    docker-compose -f docker-compose.working.yml up -d --build
    
    log_success "Рабочая конфигурация запущена!"
}

# Проверка статуса
check_status() {
    log_info "Проверяю статус контейнеров..."
    
    echo ""
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # Проверяем API
    log_info "Проверяю API..."
    sleep 5
    
    if curl -k -s https://hpi.expert/api/profile > /dev/null 2>&1; then
        log_success "API работает!"
    else
        log_warning "API еще не готов, подождите немного..."
    fi
}

# Показать логи
show_logs() {
    log_info "Логи контейнеров:"
    echo ""
    docker-compose -f docker-compose.working.yml logs --tail=20
}

# Основная функция
main() {
    case "${1:-start}" in
        "start")
            check_docker
            prepare_files
            stop_all_containers
            start_working_config
            check_status
            log_success "Проект запущен! Откройте https://hpi.expert"
            ;;
        "stop")
            log_info "Останавливаю проект..."
            docker-compose -f docker-compose.working.yml down
            log_success "Проект остановлен"
            ;;
        "restart")
            log_info "Перезапускаю проект..."
            docker-compose -f docker-compose.working.yml restart
            log_success "Проект перезапущен"
            ;;
        "status")
            check_status
            ;;
        "logs")
            show_logs
            ;;
        "rebuild")
            log_info "Пересобираю проект..."
            docker-compose -f docker-compose.working.yml down
            docker-compose -f docker-compose.working.yml up -d --build
            log_success "Проект пересобран"
            ;;
        "clean")
            log_info "Очищаю все контейнеры и образы..."
            stop_all_containers
            docker system prune -f
            log_success "Очистка завершена"
            ;;
        "help"|"-h"|"--help")
            echo "Использование: $0 [команда]"
            echo ""
            echo "Команды:"
            echo "  start     - Запустить проект (по умолчанию)"
            echo "  stop      - Остановить проект"
            echo "  restart   - Перезапустить проект"
            echo "  status    - Показать статус"
            echo "  logs      - Показать логи"
            echo "  rebuild   - Пересобрать проект"
            echo "  clean     - Очистить все контейнеры"
            echo "  help      - Показать эту справку"
            ;;
        *)
            log_error "Неизвестная команда: $1"
            echo "Используйте '$0 help' для справки"
            exit 1
            ;;
    esac
}

# Запуск основной функции
main "$@" 