import time
import timeit
import matplotlib.pyplot as plt
from functools import lru_cache
import pandas as pd


# LRU кеш для вычисления чисел Фибоначчи
@lru_cache(maxsize=None)
def fibonacci_lru(n):
    """
    Вычисление числа Фибоначчи с использованием LRU-кеша
    """
    if n <= 1:
        return n
    return fibonacci_lru(n-1) + fibonacci_lru(n-2)


# Узел для Splay Tree
class Node:
    def __init__(self, key, value, parent=None):
        self.key = key
        self.value = value
        self.parent = parent
        self.left_node = None
        self.right_node = None


# Реализация Splay Tree
class SplayTree:
    def __init__(self):
        self.root = None

    def insert(self, key, value):
        """Вставка нового элемента в дерево."""
        if self.root is None:
            self.root = Node(key, value)
        else:
            self._insert_node(key, value, self.root)

    def _insert_node(self, key, value, current_node):
        """Рекурсивная вставка элемента в дерево."""
        if key < current_node.key:
            if current_node.left_node:
                self._insert_node(key, value, current_node.left_node)
            else:
                current_node.left_node = Node(key, value, current_node)
                self._splay(current_node.left_node)
        elif key > current_node.key:
            if current_node.right_node:
                self._insert_node(key, value, current_node.right_node)
            else:
                current_node.right_node = Node(key, value, current_node)
                self._splay(current_node.right_node)
        else:  # Если ключ уже существует, обновляем значение
            current_node.value = value
            self._splay(current_node)

    def find(self, key):
        """Поиск элемента в дереве с применением splay."""
        node = self.root
        while node is not None:
            if key < node.key:
                node = node.left_node
            elif key > node.key:
                node = node.right_node
            else:
                self._splay(node)
                return node.value
        return None  # Если элемент не найден

    def _splay(self, node):
        """Реализация сплаювания для перемещения узла к корню."""
        while node.parent is not None:
            if node.parent.parent is None:  # Zig-ситуация
                if node == node.parent.left_node:
                    self._rotate_right(node.parent)
                else:
                    self._rotate_left(node.parent)
            elif node == node.parent.left_node and node.parent == node.parent.parent.left_node:  # Zig-Zig
                self._rotate_right(node.parent.parent)
                self._rotate_right(node.parent)
            elif node == node.parent.right_node and node.parent == node.parent.parent.right_node:  # Zig-Zig
                self._rotate_left(node.parent.parent)
                self._rotate_left(node.parent)
            elif node == node.parent.left_node and node.parent == node.parent.parent.right_node:  # Zig-Zag
                self._rotate_right(node.parent)
                self._rotate_left(node.parent)
            else:  # Zig-Zag (node.parent.left_node == node and node.parent.parent.right_node == node.parent)
                self._rotate_left(node.parent)
                self._rotate_right(node.parent)

    def _rotate_right(self, node):
        """Правая ротация узла."""
        left_child = node.left_node
        if left_child is None:
            return

        node.left_node = left_child.right_node
        if left_child.right_node:
            left_child.right_node.parent = node

        left_child.parent = node.parent
        if node.parent is None:
            self.root = left_child
        elif node == node.parent.left_node:
            node.parent.left_node = left_child
        else:
            node.parent.right_node = left_child

        left_child.right_node = node
        node.parent = left_child

    def _rotate_left(self, node):
        """Левая ротация узла."""
        right_child = node.right_node
        if right_child is None:
            return

        node.right_node = right_child.left_node
        if right_child.left_node:
            right_child.left_node.parent = node

        right_child.parent = node.parent
        if node.parent is None:
            self.root = right_child
        elif node == node.parent.left_node:
            node.parent.left_node = right_child
        else:
            node.parent.right_node = right_child

        right_child.left_node = node
        node.parent = right_child


# Вычисление Фибоначчи с использованием Splay Tree
def fibonacci_splay(n, tree):
    """
    Вычисление числа Фибоначчи с использованием Splay Tree
    """
    # Проверяем, есть ли уже вычисленное значение в дереве
    result = tree.find(n)
    
    if result is not None:
        return result
    
    # Если значение еще не вычислено
    if n <= 1:
        result = n
    else:
        result = fibonacci_splay(n-1, tree) + fibonacci_splay(n-2, tree)
    
    # Сохраняем результат в дереве
    tree.insert(n, result)
    
    return result


def measure_time(func, n, number=10, *args):
    """
    Измерение среднего времени выполнения функции
    """
    # Для прогрева кеша или структуры данных (особенно для больших n)
    if n > 100:
        func(n, *args) if args else func(n)
    
    # Измеряем время выполнения
    total_time = timeit.timeit(lambda: func(n, *args) if args else func(n), number=number)
    return total_time / number


def run_benchmark():
    """
    Запуск тестирования производительности и построение графика
    """
    # Значения n для тестирования
    n_values = list(range(0, 951, 50))
    
    # Массивы для хранения времени выполнения
    lru_times = []
    splay_times = []
    
    # Таблица результатов
    results = []
    
    print(f"{'n':<10} {'LRU Cache Time (s)':<20} {'Splay Tree Time (s)':<20}")
    print("-" * 50)
    
    # Измерение времени для каждого значения n
    for n in n_values:
        # Для LRU Cache
        lru_time = measure_time(fibonacci_lru, n)
        lru_times.append(lru_time)
        
        # Для Splay Tree (создаем новое дерево для каждого измерения)
        tree = SplayTree()
        splay_time = measure_time(fibonacci_splay, n, 10, tree)
        splay_times.append(splay_time)
        
        # Добавление результатов в таблицу
        results.append([n, lru_time, splay_time])
        
        # Вывод результатов
        print(f"{n:<10} {lru_time:<20.8f} {splay_time:<20.8f}")
    
    # Построение графика
    plt.figure(figsize=(10, 6))
    plt.plot(n_values, lru_times, marker='o', label='LRU Cache')
    plt.plot(n_values, splay_times, marker='x', label='Splay Tree')
    plt.xlabel('Число Фібоначчі (n)')
    plt.ylabel('Середній час виконання (секунди)')
    plt.title('Порівняння часу виконання для LRU Cache та Splay Tree')
    plt.legend()
    plt.grid(True)
    plt.savefig('fibonacci_comparison.png')
    plt.show()
    
    # Создание таблицы DataFrame
    df = pd.DataFrame(results, columns=['n', 'LRU Cache Time (s)', 'Splay Tree Time (s)'])
    
    # Анализ результатов
    print("\nАналіз результатів:")
    if sum(lru_times) < sum(splay_times):
        print("LRU Cache виявився більш ефективним для обчислення чисел Фібоначчі.")
    else:
        print("Splay Tree виявився більш ефективним для обчислення чисел Фібоначчі.")
    
    # Вычисление отношения скорости
    avg_ratio = sum(splay_times) / sum(lru_times) if sum(lru_times) > 0 else float('inf')
    print(f"В середньому, Splay Tree в {avg_ratio:.2f} разів повільніший, ніж LRU Cache.")


if __name__ == "__main__":
    print("Запуск порівняння ефективності обчислення чисел Фібоначчі")
    print("=" * 50)
    print("Порівнюємо два підходи:")
    print("1. LRU Cache (вбудований @lru_cache)")
    print("2. Splay Tree (власна реалізація)")
    print("=" * 50)
    
    run_benchmark() 