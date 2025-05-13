import random
import time
from typing import List, Tuple


class Node:
    """Вузол для двозв'язного списку"""
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None


class DoublyLinkedList:
    """Двозв'язний список для LRU-кешу"""
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        """Додає новий вузол на початок списку"""
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        """Видаляє вказаний вузол зі списку"""
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        """Переміщує вузол на початок списку"""
        if node != self.head:
            self.remove(node)
            node.next = self.head
            self.head.prev = node
            self.head = node

    def remove_last(self):
        """Видаляє останній вузол у списку"""
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None


class LRUCache:
    """Реалізація LRU-кешу"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def get(self, key):
        """Отримує значення за ключем"""
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return None

    def put(self, key, value):
        """Додає або оновлює пару ключ-значення"""
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node
            
    def delete_key(self, key):
        """Видаляє значення за ключем"""
        if key in self.cache:
            node = self.cache[key]
            self.list.remove(node)
            del self.cache[key]


# Функції для роботи з масивом без кешування
def range_sum_no_cache(array: List[int], L: int, R: int) -> int:
    """Обчислює суму елементів на відрізку без використання кешу"""
    # Імітуємо важкі обчислення
    time.sleep(0.0001)  # Маленька затримка для імітації складних обчислень
    return sum(array[L:R+1])


def update_no_cache(array: List[int], index: int, value: int) -> None:
    """Оновлює значення елемента масиву без використання кешу"""
    array[index] = value


# Функції для роботи з масивом з використанням кешу
def range_sum_with_cache(array: List[int], L: int, R: int, cache: LRUCache) -> int:
    """Обчислює суму елементів на відрізку з використанням LRU-кешу"""
    cache_key = f"range_{L}_{R}"
    result = cache.get(cache_key)
    
    if result is None:
        # Імітуємо важкі обчислення (так само, як у версії без кешу)
        time.sleep(0.0001)  # Маленька затримка для імітації складних обчислень
        result = sum(array[L:R+1])
        cache.put(cache_key, result)
        
    return result


def update_with_cache(array: List[int], index: int, value: int, cache: LRUCache) -> None:
    """
    Оновлює значення елемента масиву та видаляє неактуальні значення з кешу
    """
    # Оновлюємо значення в масиві
    array[index] = value
    
    # Видаляємо всі кешовані запити, які включають змінений індекс
    keys_to_delete = []
    for key in list(cache.cache.keys()):
        if key.startswith("range_"):
            _, L, R = key.split("_")
            L, R = int(L), int(R)
            if L <= index <= R:
                keys_to_delete.append(key)
    
    for key in keys_to_delete:
        cache.delete_key(key)


def generate_test_data(array_size: int, num_queries: int) -> Tuple[List[int], List[Tuple]]:
    """Генерує тестові дані для експерименту"""
    # Створюємо масив випадкових чисел
    array = [random.randint(1, 1000) for _ in range(array_size)]
    
    # Генеруємо запити
    queries = []
    
    # Додаємо запити з оновлення (менше, ніж запитів Range)
    for _ in range(num_queries // 10):  # 10% запитів - оновлення
        index = random.randint(0, array_size - 1)
        value = random.randint(1, 1000)
        queries.append(("Update", index, value))
    
    # Генеруємо обмежену кількість унікальних запитів Range
    unique_ranges = []
    
    # Створюємо невелику кількість унікальних запитів Range
    num_unique_ranges = min(1000, num_queries // 10)
    for _ in range(num_unique_ranges):
        L = random.randint(0, array_size - 1000)
        R = random.randint(L, min(L + 1000, array_size - 1))
        unique_ranges.append((L, R))
    
    # Додаємо ці запити з повтореннями у довільному порядку
    for _ in range(num_queries - len(queries)):
        L, R = random.choice(unique_ranges)
        queries.append(("Range", L, R))
    
    # Перемішуємо всі запити
    random.shuffle(queries)
    
    return array, queries


def run_tests(array_size: int = 100_000, num_queries: int = 50_000, cache_size: int = 1000):
    """Запускає тести та порівнює швидкість виконання з кешем та без нього"""
    # Генеруємо тестові дані
    array, queries = generate_test_data(array_size, num_queries)
    
    # Копіюємо масив для тестів без кешування
    array_no_cache = array.copy()
    
    # Тестування без кешування
    start_time = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_no_cache(array_no_cache, query[1], query[2])
        else:  # Update
            update_no_cache(array_no_cache, query[1], query[2])
    no_cache_time = time.time() - start_time
    
    # Тестування з кешуванням
    array_with_cache = array.copy()
    cache = LRUCache(cache_size)
    
    start_time = time.time()
    for query in queries:
        if query[0] == "Range":
            range_sum_with_cache(array_with_cache, query[1], query[2], cache)
        else:  # Update
            update_with_cache(array_with_cache, query[1], query[2], cache)
    with_cache_time = time.time() - start_time
    
    # Виведення результатів
    print(f"Час виконання без кешування: {no_cache_time:.2f} секунд")
    print(f"Час виконання з LRU-кешем: {with_cache_time:.2f} секунд")


if __name__ == "__main__":
    # Запускаємо тести з параметрами з завдання
    print("Тестування LRU-кешу для оптимізації запитів до масиву")
    print("-" * 50)
    run_tests(array_size=100_000, num_queries=50_000, cache_size=1_000) 