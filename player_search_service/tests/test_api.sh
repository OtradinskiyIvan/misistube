#!/bin/bash

# ============================================================================
# MISISTUBE Player Search Service - API Test Suite
# ============================================================================
# Автоматическое тестирование всех эндпоинтов
# Результаты сохраняются в curl_tests.log
# ============================================================================

# Цвета для вывода в консоль
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
BASE_URL="http://127.0.0.1:8000"
LOG_FILE="curl_tests.log"
REDIS_CONTAINER="player_search_service-redis-1"
COMPOSE_FILE="docker-compose.yaml"

# Счётчики
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================================
# Функции
# ============================================================================

# Инициализация лог-файла
init_log() {
    echo "================================================================" > "$LOG_FILE"
    echo "MISISTUBE Player Search Service - API Test Results" >> "$LOG_FILE"
    echo "Date: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    echo "Base URL: $BASE_URL" >> "$LOG_FILE"
    echo "================================================================" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# Функция для выполнения теста
run_test() {
    local test_name="$1"
    local test_cmd="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}[$TOTAL_TESTS] $test_name${NC}"
    echo -e "${YELLOW}Description: $description${NC}"
    echo -e "${YELLOW}Command: $test_cmd${NC}"
    
    # Записываем в лог
    echo "================================================================" >> "$LOG_FILE"
    echo "TEST [$TOTAL_TESTS]: $test_name" >> "$LOG_FILE"
    echo "Description: $description" >> "$LOG_FILE"
    echo "Command: $test_cmd" >> "$LOG_FILE"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    echo "----------------------------------------------------------------" >> "$LOG_FILE"
    
    # Выполняем команду
    local output
    output=$(eval "$test_cmd" 2>&1)
    local exit_code=$?
    
    # Записываем результат в лог
    echo "$output" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Выводим в консоль
    echo "$output"
    
    # Проверяем результат
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Test completed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ Test failed (exit code: $exit_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo "================================================================" >> "$LOG_FILE"
}

# Функция для тестов с заголовками
run_test_with_headers() {
    local test_name="$1"
    local test_cmd="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}[$TOTAL_TESTS] $test_name${NC}"
    echo -e "${YELLOW}Description: $description${NC}"
    echo -e "${YELLOW}Command: $test_cmd${NC}"
    
    echo "================================================================" >> "$LOG_FILE"
    echo "TEST [$TOTAL_TESTS]: $test_name" >> "$LOG_FILE"
    echo "Description: $description" >> "$LOG_FILE"
    echo "Command: $test_cmd" >> "$LOG_FILE"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    echo "----------------------------------------------------------------" >> "$LOG_FILE"
    
    local output
    output=$(eval "$test_cmd" 2>&1)
    local exit_code=$?
    
    echo "$output" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "$output"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Test completed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ Test failed (exit code: $exit_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo "================================================================" >> "$LOG_FILE"
}

# Функция для замера времени
run_test_with_timing() {
    local test_name="$1"
    local test_cmd="$2"
    local description="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -e "\n${BLUE}[$TOTAL_TESTS] $test_name${NC}"
    echo -e "${YELLOW}Description: $description${NC}"
    echo -e "${YELLOW}Command: time $test_cmd${NC}"
    
    echo "================================================================" >> "$LOG_FILE"
    echo "TEST [$TOTAL_TESTS]: $test_name" >> "$LOG_FILE"
    echo "Description: $description" >> "$LOG_FILE"
    echo "Command: time $test_cmd" >> "$LOG_FILE"
    echo "Time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
    echo "----------------------------------------------------------------" >> "$LOG_FILE"
    
    local output
    output=$({ time eval "$test_cmd" ; } 2>&1)
    local exit_code=$?
    
    echo "$output" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    echo "$output"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Test completed${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ Test failed (exit code: $exit_code)${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    echo "================================================================" >> "$LOG_FILE"
}

# ============================================================================
# Начало тестирования
# ============================================================================

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}MISISTUBE Player Search Service - API Test Suite${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "${YELLOW}Starting tests at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${YELLOW}Results will be saved to: $LOG_FILE${NC}"
echo -e "${BLUE}================================================================${NC}"

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
    "Проверка доступности Swagger UI (первые 5 строк)"

# ============================================================================
# 2. Поиск видео (Search)
# ============================================================================

echo -e "\n${BLUE}=== 2. ПОИСК ВИДЕО ===${NC}"

run_test "Все видео (без фильтров)" \
    "curl -s '$BASE_URL/api/v1/search' | jq" \
    "Получение всех видео без параметров"

run_test "С лимитом" \
    "curl -s '$BASE_URL/api/v1/search?limit=2' | jq" \
    "Получение 2 видео"

run_test "С пагинацией (страница 1)" \
    "curl -s '$BASE_URL/api/v1/search?offset=0&limit=2' | jq" \
    "Первая страница (offset=0, limit=2)"

run_test "С пагинацией (страница 2)" \
    "curl -s '$BASE_URL/api/v1/search?offset=2&limit=2' | jq" \
    "Вторая страница (offset=2, limit=2)"

run_test "Поиск по тексту (python)" \
    "curl -s '$BASE_URL/api/v1/search?q=python' | jq" \
    "Поиск видео с 'python' в названии"

run_test "Поиск по тексту (КОТ - кириллица)" \
    "curl -s -G --data-urlencode 'q=КОТ' '$BASE_URL/api/v1/search' | jq" \
    "Поиск видео с 'КОТ' в названии (кириллица)"

run_test "Поиск несуществующего" \
    "curl -s -G --data-urlencode 'q=несуществующее' '$BASE_URL/api/v1/search' | jq" \
    "Поиск несуществующего видео"

run_test "Фильтрация по тегу (python)" \
    "curl -s '$BASE_URL/api/v1/search?tags=python' | jq" \
    "Фильтрация по тегу 'python'"

run_test "Фильтрация по тегу (коты)" \
    "curl -s -G --data-urlencode 'tags=коты' '$BASE_URL/api/v1/search' | jq" \
    "Фильтрация по тегу 'коты'"

run_test "Множественные теги" \
    "curl -s '$BASE_URL/api/v1/search?tags=docker&tags=devops' | jq" \
    "Фильтрация по нескольким тегам"

run_test "Комбинированный поиск" \
    "curl -s '$BASE_URL/api/v1/search?q=tutorial&tags=python&limit=5' | jq" \
    "Поиск с текстом и тегами"

# ============================================================================
# 3. Валидация ошибок (422)
# ============================================================================

echo -e "\n${BLUE}=== 3. ВАЛИДАЦИЯ ОШИБОК ===${NC}"

run_test "limit < 1" \
    "curl -s '$BASE_URL/api/v1/search?limit=0' | jq" \
    "Ожидается 422: limit должен быть >= 1"

run_test "limit > 100" \
    "curl -s '$BASE_URL/api/v1/search?limit=1000' | jq" \
    "Ожидается 422: limit должен быть <= 100"

run_test "limit не число" \
    "curl -s '$BASE_URL/api/v1/search?limit=abc' | jq" \
    "Ожидается 422: limit должен быть числом"

run_test "offset отрицательный" \
    "curl -s '$BASE_URL/api/v1/search?offset=-5' | jq" \
    "Ожидается 422: offset должен быть >= 0"

run_test "q слишком длинный" \
    "LONG_Q=\$(python3 -c \"print('a' * 300)\") && curl -s \"$BASE_URL/api/v1/search?q=\$LONG_Q\" | jq" \
    "Ожидается 422: q должен быть <= 255 символов"

# ============================================================================
# 4. Playback URL
# ============================================================================

echo -e "\n${BLUE}=== 4. PLAYBACK URL ===${NC}"

run_test "Получить presigned URL" \
    "curl -s '$BASE_URL/api/v1/playback/f9383c4e-8b2d-4a8b-8ca8-5249a1318fbf' | jq" \
    "Получение presigned URL для существующего видео"

run_test "Несуществующее видео" \
    "curl -s '$BASE_URL/api/v1/playback/00000000-0000-0000-0000-000000000000' | jq" \
    "Получение URL для несуществующего видео"

run_test "Невалидный UUID" \
    "curl -s '$BASE_URL/api/v1/playback/not-a-uuid' | jq" \
    "Ожидается ошибка: невалидный формат UUID"

# ============================================================================
# 5. CORS тесты
# ============================================================================

echo -e "\n${BLUE}=== 5. CORS ТЕСТЫ ===${NC}"

run_test_with_headers "Preflight OPTIONS запрос" \
    "curl -I -X OPTIONS $BASE_URL/api/v1/search -H 'Origin: http://example.com' -H 'Access-Control-Request-Method: GET'" \
    "Проверка CORS preflight"

run_test_with_headers "CORS заголовки в ответе" \
    "curl -I $BASE_URL/api/v1/search -H 'Origin: http://example.com'" \
    "Проверка наличия CORS заголовков"

# ============================================================================
# 6. Graceful degradation (Redis)
# ============================================================================

echo -e "\n${BLUE}=== 6. GRACEFUL DEGRADATION (REDIS) ===${NC}"

echo -e "${YELLOW}Останавливаем Redis...${NC}"
docker compose -f "$COMPOSE_FILE" --profile testing stop redis 2>&1 | tee -a "$LOG_FILE"

run_test_with_timing "Запрос без Redis (1-й)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Первый запрос при недоступном Redis"

run_test_with_timing "Запрос без Redis (2-й)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Второй запрос (circuit breaker)"

run_test_with_timing "Запрос без Redis (3-й)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Третий запрос (circuit breaker должен открыться)"

run_test_with_timing "Запрос без Redis (4-й)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Четвёртый запрос (должен быть быстрым)"

run_test_with_timing "Запрос без Redis (5-й)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Пятый запрос (должен быть быстрым)"

echo -e "${YELLOW}Проверяем логи...${NC}"
echo "Последние 20 строк из лога сервиса:" >> "$LOG_FILE"
tail -n 20 ~/Projects/misistube/player_search_service.log >> "$LOG_FILE" 2>&1

echo -e "${YELLOW}Запускаем Redis обратно...${NC}"
docker compose -f "$COMPOSE_FILE" --profile testing start redis 2>&1 | tee -a "$LOG_FILE"

echo -e "${YELLOW}Ожидаем 60 секунд (recovery_timeout)...${NC}"
echo "Waiting 60 seconds for Redis recovery..." >> "$LOG_FILE"
sleep 60

run_test "Запрос с Redis (после восстановления)" \
    "curl -s '$BASE_URL/api/v1/search?limit=5' | jq" \
    "Запрос после восстановления Redis"

# ============================================================================
# 7. Кэширование
# ============================================================================

echo -e "\n${BLUE}=== 7. КЭШИРОВАНИЕ ===${NC}"

run_test_with_timing "Cache miss (1-й запрос)" \
    "curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "Первый запрос (должен быть медленнее)"

run_test_with_timing "Cache hit (2-й запрос)" \
    "curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "Повторный запрос (должен быть быстрее)"

echo -e "${YELLOW}Очищаем кэш...${NC}"
docker compose -f "$COMPOSE_FILE" --profile testing exec redis redis-cli FLUSHALL 2>&1 | tee -a "$LOG_FILE"

run_test_with_timing "Cache miss (после очистки)" \
    "curl -s '$BASE_URL/api/v1/search?q=python&limit=5' | jq" \
    "Запрос после очистки кэша"

# ============================================================================
# 8. Correlation ID
# ============================================================================

echo -e "\n${BLUE}=== 8. CORRELATION ID ===${NC}"

run_test_with_headers "Без заголовка (генерируется автоматически)" \
    "curl -s $BASE_URL/api/v1/search?limit=1 -D -" \
    "Проверка автоматической генерации correlation ID"

run_test_with_headers "С кастомным correlation ID" \
    "curl -s $BASE_URL/api/v1/search?limit=1 -H 'X-Correlation-ID: my-custom-id-123' -D -" \
    "Проверка кастомного correlation ID"

echo -e "${YELLOW}Проверяем логи на наличие my-custom-id-123...${NC}"
echo "Поиск 'my-custom-id-123' в логах:" >> "$LOG_FILE"
grep "my-custom-id-123" ~/Projects/misistube/player_search_service.log | tail -n 5 >> "$LOG_FILE" 2>&1

# ============================================================================
# 9. Производительность
# ============================================================================

echo -e "\n${BLUE}=== 9. ПРОИЗВОДИТЕЛЬНОСТЬ ===${NC}"

run_test_with_timing "Замер времени ответа" \
    "curl -s '$BASE_URL/api/v1/search?limit=10' > /dev/null" \
    "Замер времени одного запроса"

echo -e "${YELLOW}Нагрузочный тест (100 параллельных запросов)...${NC}"
echo "Load test: 100 parallel requests" >> "$LOG_FILE"
echo "Start time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"

START_TIME=$(date +%s.%N)
for i in {1..100}; do
    curl -s "$BASE_URL/api/v1/search?limit=5" > /dev/null &
done
wait
END_TIME=$(date +%s.%N)

DURATION=$(echo "$END_TIME - $START_TIME" | bc)
echo "End time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "Total duration: ${DURATION}s" >> "$LOG_FILE"
echo -e "${GREEN}✓ 100 requests completed in ${DURATION}s${NC}"

echo -e "${YELLOW}Параллельные запросы с разными тегами...${NC}"
echo "Parallel requests with different tags" >> "$LOG_FILE"
for tag in python docker коты tutorial; do
    curl -s "$BASE_URL/api/v1/search?tags=$tag&limit=5" > /dev/null &
done
wait
echo -e "${GREEN}✓ Parallel tag requests completed${NC}"

# ============================================================================
# 10. Edge cases
# ============================================================================

echo -e "\n${BLUE}=== 10. EDGE CASES ===${NC}"

run_test "Пустой запрос" \
    "curl -s '$BASE_URL/api/v1/search?q=' | jq" \
    "Поиск с пустым q"

run_test "Специальные символы (пробел)" \
    "curl -s '$BASE_URL/api/v1/search?q=python%20tutorial' | jq" \
    "Поиск с пробелом в запросе"

run_test "Специальные символы (амперсанд)" \
    "curl -s '$BASE_URL/api/v1/search?q=python%26tutorial' | jq" \
    "Поиск с амперсандом в запросе"

run_test "Unicode в тегах" \
    "curl -s -G --data-urlencode 'tags=милота' '$BASE_URL/api/v1/search' | jq" \
    "Поиск по тегу с кириллицей"

run_test "Очень большой offset" \
    "curl -s '$BASE_URL/api/v1/search?offset=10000&limit=10' | jq" \
    "Запрос с большим offset (должен вернуть пустой результат)"

run_test "Несуществующий эндпоинт" \
    "curl -s '$BASE_URL/api/v1/nonexistent' | jq" \
    "Ожидается 404"

# ============================================================================
# Итоговая статистика
# ============================================================================

echo -e "\n${BLUE}================================================================${NC}"
echo -e "${BLUE}ИТОГОВАЯ СТАТИСТИКА${NC}"
echo -e "${BLUE}================================================================${NC}"
echo -e "Всего тестов: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Пройдено: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Провалено: ${RED}$FAILED_TESTS${NC}"
echo -e "${BLUE}================================================================${NC}"

echo "" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"
echo "ИТОГОВАЯ СТАТИСТИКА" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"
echo "Всего тестов: $TOTAL_TESTS" >> "$LOG_FILE"
echo "Пройдено: $PASSED_TESTS" >> "$LOG_FILE"
echo "Провалено: $FAILED_TESTS" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"

echo -e "\n${GREEN}✓ Все результаты сохранены в: $LOG_FILE${NC}"
echo -e "${BLUE}================================================================${NC}"