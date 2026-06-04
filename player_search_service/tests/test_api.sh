#!/bin/bash

# ============================================================================
# MISISTUBE Player Search Service - API Test Suite
# ============================================================================
# Автоматическое тестирование всех эндпоинтов
# Результаты сохраняются в curl_tests.log
#
# Использование:
#   ./tests/test_api.sh                    # запуск из корня проекта
#   cd tests && ./test_api.sh              # запуск из папки tests
#   BASE_URL=http://prod:8000 ./test_api.sh  # с другим URL
# ============================================================================

set -e  # Остановка при ошибке

# ============================================================================
# Автоопределение путей
# ============================================================================

# Определяем директорию, где лежит скрипт
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Поднимаемся к корню проекта (если скрипт в tests/, то на уровень выше)
if [[ "$(basename "$SCRIPT_DIR")" == "tests" ]]; then
    PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
else
    PROJECT_ROOT="$SCRIPT_DIR"
fi

cd "$PROJECT_ROOT" || exit 1

# ============================================================================
# Конфигурация (можно переопределить через переменные окружения)
# ============================================================================

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
LOG_FILE="${LOG_FILE:-$PROJECT_ROOT/curl_tests.log}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yaml}"
REDIS_CONTAINER="${REDIS_CONTAINER:-player_search_service-redis-1}"

# Автопоиск лога сервиса
# Логи могут лежать в нескольких местах:
# - misistube/logs/player_search_service.log (основной путь)
# - misistube/player_search_service/logs/player_search_service.log
# - misistube/player_search_service/player_search_service.log
SERVICE_LOG=""
for candidate in \
    "$(dirname "$PROJECT_ROOT")/logs/player_search_service.log" \
    "$PROJECT_ROOT/logs/player_search_service.log" \
    "$PROJECT_ROOT/player_search_service.log"; do
    if [ -f "$candidate" ]; then
        SERVICE_LOG="$candidate"
        break
    fi
done

# Если не нашли в известных местах — ищем через find
if [ -z "$SERVICE_LOG" ]; then
    SERVICE_LOG=$(find "$(dirname "$PROJECT_ROOT")" -maxdepth 4 -name "player_search_service.log" 2>/dev/null | head -n 1)
fi

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Счётчики
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================================
# Проверка зависимостей
# ============================================================================

check_dependencies() {
    local missing=()
    
    for cmd in curl jq docker; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}✗ Отсутствуют необходимые инструменты: ${missing[*]}${NC}"
        echo "Установите их перед запуском тестов."
        exit 1
    fi
    
    # Проверка docker compose (v2) или docker-compose (v1)
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
    else
        echo -e "${RED}✗ Не найден docker compose или docker-compose${NC}"
        exit 1
    fi
}

# ============================================================================
# Функции
# ============================================================================

init_log() {
    cat > "$LOG_FILE" << EOF
================================================================
MISISTUBE Player Search Service - API Test Results
================================================================
Date: $(date '+%Y-%m-%d %H:%M:%S')
Base URL: $BASE_URL
Project Root: $PROJECT_ROOT
Service Log: ${SERVICE_LOG:-не найден}
================================================================

EOF
}

run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}[$TOTAL_TESTS] $test_name${NC}"
    echo -e "${YELLOW}$description${NC}"
    
    # Записываем в лог
    {
        echo "================================================================"
        echo "TEST [$TOTAL_TESTS]: $test_name"
        echo "Description: $description"
        echo "Command: $test_cmd"
        echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "----------------------------------------------------------------"
    } >> "$LOG_FILE"
    
    # Выполняем команду
    local output
    output=$(eval "$test_cmd" 2>&1)
    local exit_code=$?
    
    echo "$output" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "$output"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED (exit code: $exit_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
}

# Безопасный tail для лога сервиса
tail_service_log() {
    if [ -n "$SERVICE_LOG" ] && [ -f "$SERVICE_LOG" ]; then
        echo "Последние 20 строк из лога сервиса ($SERVICE_LOG):" >> "$LOG_FILE"
        tail -n 20 "$SERVICE_LOG" >> "$LOG_FILE" 2>&1
        tail -n 20 "$SERVICE_LOG"
    else
        echo "Лог-файл сервиса не найден" >> "$LOG_FILE"
        echo -e "${YELLOW}⚠ Лог-файл сервиса не найден${NC}"
    fi
}

# Поиск по логу сервиса
grep_service_log() {
    local pattern="$1"
    if [ -n "$SERVICE_LOG" ] && [ -f "$SERVICE_LOG" ]; then
        echo "Поиск '$pattern' в логах:" >> "$LOG_FILE"
        grep "$pattern" "$SERVICE_LOG" | tail -n 5 >> "$LOG_FILE" 2>&1
        grep "$pattern" "$SERVICE_LOG" | tail -n 5
    else
        echo "Лог-файл не найден" >> "$LOG_FILE"
    fi
}

# ============================================================================
# Начало тестирования
# ============================================================================

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}MISISTUBE Player Search Service - API Test Suite${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "Project Root: ${YELLOW}$PROJECT_ROOT${NC}"
echo -e "Base URL:     ${YELLOW}$BASE_URL${NC}"
echo -e "Log file:     ${YELLOW}$LOG_FILE${NC}"
echo -e "Service log:  ${YELLOW}${SERVICE_LOG:-не найден}${NC}"
echo -e "${BLUE}================================================================${NC}"

check_dependencies
init_log

# ============================================================================
# 1. Базовые эндпоинты
# ============================================================================

echo -e "\n${BLUE}=== 1. БАЗОВЫЕ ЭНДПОИНТЫ ===${NC}"

run_test "Root endpoint" \
    "curl -s $BASE_URL/ | jq" \
    "Проверка корневого эндпоинта"

run_test "Health check" \
    "curl -s $BASE_URL/health | jq" \
    "Проверка health endpoint"

run_test "Swagger docs" \
    "curl -s $BASE_URL/docs | head -n 5" \
    "Проверка доступности Swagger UI"

# ============================================================================
# 2. Поиск видео
# ============================================================================

echo -e "\n${BLUE}=== 2. ПОИСК ВИДЕО ===${NC}"

run_test "Все видео" \
    "curl -s '$BASE_URL/api/v1/search' | jq" \
    "Получение всех видео без параметров"

run_test "С лимитом" \
    "curl -s '$BASE_URL/api/v1/search?limit=2' | jq" \
    "Получение 2 видео"

run_test "Пагинация (стр. 1)" \
    "curl -s '$BASE_URL/api/v1/search?offset=0&limit=2' | jq" \
    "Первая страница"

run_test "Пагинация (стр. 2)" \
    "curl -s '$BASE_URL/api/v1/search?offset=2&limit=2' | jq" \
    "Вторая страница"

run_test "Поиск по тексту (python)" \
    "curl -s '$BASE_URL/api/v1/search?q=python' | jq" \
    "Поиск видео с 'python'"

run_test "Поиск по тексту (КОТ - кириллица)" \
    "curl -s -G --data-urlencode 'q=КОТ' '$BASE_URL/api/v1/search' | jq" \
    "Поиск с кириллицей"

run_test "Поиск несуществующего" \
    "curl -s -G --data-urlencode 'q=несуществующее' '$BASE_URL/api/v1/search' | jq" \
    "Пустой результат"

run_test "Фильтр по тегу (python)" \
    "curl -s '$BASE_URL/api/v1/search?tags=python' | jq" \
    "Фильтрация по тегу"

run_test "Фильтр по тегу (коты)" \
    "curl -s -G --data-urlencode 'tags=коты' '$BASE_URL/api/v1/search' | jq" \
    "Фильтрация по тегу с кириллицей"

run_test "Множественные теги" \
    "curl -s '$BASE_URL/api/v1/search?tags=docker&tags=devops' | jq" \
    "Несколько тегов"

run_test "Комбинированный поиск" \
    "curl -s '$BASE_URL/api/v1/search?q=tutorial&tags=python&limit=5' | jq" \
    "Текст + теги"

# ============================================================================
# 3. Валидация ошибок
# ============================================================================

echo -e "\n${BLUE}=== 3. ВАЛИДАЦИЯ ОШИБОК ===${NC}"

run_test "limit < 1" \
    "curl -s '$BASE_URL/api/v1/search?limit=0' | jq" \
    "Ожидается 422"

run_test "limit > 100" \
    "curl -s '$BASE_URL/api/v1/search?limit=1000' | jq" \
    "Ожидается 422"

run_test "limit не число" \
    "curl -s '$BASE_URL/api/v1/search?limit=abc' | jq" \
    "Ожидается 422"

run_test "offset отрицательный" \
    "curl -s '$BASE_URL/api/v1/search?offset=-5' | jq" \
    "Ожидается 422"

run_test "q слишком длинный" \
    "LONG_Q=\$(python3 -c \"print('a' * 300)\") && curl -s \"$BASE_URL/api/v1/search?q=\$LONG_Q\" | jq" \
    "Ожидается 422"

# ============================================================================
# 4. Playback URL
# ============================================================================

echo -e "\n${BLUE}=== 4. PLAYBACK URL ===${NC}"

run_test "Presigned URL" \
    "curl -s '$BASE_URL/api/v1/playback/f9383c4e-8b2d-4a8b-8ca8-5249a1318fbf' | jq" \
    "Получение URL для видео"

run_test "Несуществующее видео" \
    "curl -s '$BASE_URL/api/v1/playback/00000000-0000-0000-0000-000000000000' | jq" \
    "URL генерируется, но файла нет"

run_test "Невалидный UUID" \
    "curl -s '$BASE_URL/api/v1/playback/not-a-uuid' | jq" \
    "Поведение без валидации"

# ============================================================================
# 5. CORS
# ============================================================================

echo -e "\n${BLUE}=== 5. CORS ТЕСТЫ ===${NC}"

run_test "Preflight OPTIONS" \
    "curl -s -I -X OPTIONS $BASE_URL/api/v1/search -H 'Origin: http://example.com' -H 'Access-Control-Request-Method: GET'" \
    "CORS preflight"

run_test "CORS заголовки" \
    "curl -s -I $BASE_URL/api/v1/search -H 'Origin: http://example.com'" \
    "Проверка CORS заголовков"

# ============================================================================
# 6. Graceful degradation (Redis)
# ============================================================================

echo -e "\n${BLUE}=== 6. GRACEFUL DEGRADATION ===${NC}"

echo -e "${YELLOW}Останавливаем Redis...${NC}"
$COMPOSE_CMD -f "$COMPOSE_FILE" --profile testing stop redis 2>&1 | tee -a "$LOG_FILE"

run_test "Запрос без Redis (1-й)" \
    "time curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Первый запрос"

run_test "Запрос без Redis (2-й)" \
    "time curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Второй запрос"

run_test "Запрос без Redis (3-й)" \
    "time curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Circuit breaker открывается"

run_test "Запрос без Redis (4-й)" \
    "time curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Должен быть быстрым"

run_test "Запрос без Redis (5-й)" \
    "time curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Должен быть быстрым"

echo -e "${YELLOW}Проверяем логи...${NC}"
tail_service_log

echo -e "${YELLOW}Запускаем Redis...${NC}"
$COMPOSE_CMD -f "$COMPOSE_FILE" --profile testing start redis 2>&1 | tee -a "$LOG_FILE"

echo -e "${YELLOW}Ожидаем 60 секунд (recovery)...${NC}"
sleep 60

run_test "Запрос с Redis (после восстановления)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Redis восстановлен"

# ============================================================================
# 7. Кэширование
# ============================================================================

echo -e "\n${BLUE}=== 7. КЭШИРОВАНИЕ ===${NC}"

run_test "Cache miss" \
    "time curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "Первый запрос"

run_test "Cache hit" \
    "time curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "Повторный запрос"

echo -e "${YELLOW}Очищаем кэш...${NC}"
$COMPOSE_CMD -f "$COMPOSE_FILE" --profile testing exec redis redis-cli FLUSHALL 2>&1 | tee -a "$LOG_FILE"

run_test "Cache miss (после очистки)" \
    "time curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "После очистки"

# ============================================================================
# 8. Correlation ID
# ============================================================================

echo -e "\n${BLUE}=== 8. CORRELATION ID ===${NC}"

run_test "Автогенерация" \
    "curl -s $BASE_URL/api/v1/search?limit=1 -D -" \
    "Без заголовка"

run_test "Кастомный ID" \
    "curl -s $BASE_URL/api/v1/search?limit=1 -H 'X-Correlation-ID: my-custom-id-123' -D -" \
    "С заголовком"

echo -e "${YELLOW}Проверяем логи...${NC}"
grep_service_log "my-custom-id-123"

# ============================================================================
# 9. Производительность
# ============================================================================

echo -e "\n${BLUE}=== 9. ПРОИЗВОДИТЕЛЬНОСТЬ ===${NC}"

run_test "Замер времени" \
    "time curl -s '$BASE_URL/api/v1/search?limit=10' > /dev/null" \
    "Один запрос"

echo -e "${YELLOW}Нагрузочный тест (100 запросов)...${NC}"
echo "Load test: 100 parallel requests" >> "$LOG_FILE"

START_TIME=$(date +%s.%N)
for i in {1..100}; do
    curl -s "$BASE_URL/api/v1/search?limit=5" > /dev/null &
done
wait
END_TIME=$(date +%s.%N)

DURATION=$(echo "$END_TIME - $START_TIME" | bc)
echo "Duration: ${DURATION}s" >> "$LOG_FILE"
echo -e "${GREEN}✓ 100 requests in ${DURATION}s${NC}"

# ============================================================================
# 10. Edge cases
# ============================================================================

echo -e "\n${BLUE}=== 10. EDGE CASES ===${NC}"

run_test "Пустой запрос" \
    "curl -s '$BASE_URL/api/v1/search?q=' | jq" \
    "Пустой q"

run_test "Пробел в запросе" \
    "curl -s '$BASE_URL/api/v1/search?q=python%20tutorial' | jq" \
    "URL-encoded пробел"

run_test "Амперсанд в запросе" \
    "curl -s '$BASE_URL/api/v1/search?q=python%26tutorial' | jq" \
    "URL-encoded амперсанд"

run_test "Unicode в тегах" \
    "curl -s -G --data-urlencode 'tags=милота' '$BASE_URL/api/v1/search' | jq" \
    "Кириллица в тегах"

run_test "Большой offset" \
    "curl -s '$BASE_URL/api/v1/search?offset=10000&limit=10' | jq" \
    "Пустой результат"

run_test "404 Not Found" \
    "curl -s '$BASE_URL/api/v1/nonexistent' | jq" \
    "Несуществующий эндпоинт"

# ============================================================================
# Итоги
# ============================================================================

echo -e "\n${BLUE}================================================================${NC}"
echo -e "${BLUE}ИТОГОВАЯ СТАТИСТИКА${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "Всего тестов: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Пройдено:     ${GREEN}$PASSED_TESTS${NC}"
echo -e "Провалено:    ${RED}$FAILED_TESTS${NC}"
echo -e "${BLUE}================================================================${NC}"

cat >> "$LOG_FILE" << EOF

================================================================
ИТОГОВАЯ СТАТИСТИКА
================================================================
Всего тестов: $TOTAL_TESTS
Пройдено: $PASSED_TESTS
Провалено: $FAILED_TESTS
================================================================
EOF

echo -e "\n${GREEN}✓ Результаты сохранены в: $LOG_FILE${NC}"

# Возвращаем код ошибки, если были провалы
[ $FAILED_TESTS -eq 0 ] && exit 0 || exit 1