import functools
# import time
from django.core.cache import cache


def _is_task_blocked(key: str) -> bool:
    """Checks if the task is blocked in the cache (Проверяет, заблокирована ли задача в кэше).
    Args:
        key (str): the name of the key with the lock status (название ключа со статусом блокировки).
    """
    value = cache.get(key)
    if value:
        return True
    return False


def _block_launch_of_task(key: str, value, timeout) -> bool:
    """Sets a flag for blocking in the cache (Устанавливает флаг на блокировку в кэш).

    Args:
        key (str): The lock key (ключ блокировки)
        value (_type_): the value written to the cache (значение записанное в кеш)
        timeout (_type_): The lifetime of the lock (время жизни блокировки)
    """
    cache.set(key, "locked", timeout)


def _unblock_launch_of_task(key: str) -> bool:
    """EN: Removes the lock flag in the cache.
    RU: Удаляет флаг блокировки в кэше.

    Args:
        key (str): The lock key
    """
    return cache.delete(key)


def block_task(*args, name_of_lock='', timeout_limit=0, **opts):
    """
    EN: When starting a task, it is checked whether it is blocked, if not,
    it creates a lock for the duration of the task,
    after the task is completed, the lock is lifted.

    RU: При запуске задачи проверяет заблокирована ли она, если нет то создает блокировку на время выполнения задачи,
    после завершении задачи блокировка снимается.
    :param name_of_lock: the name of the lock, if it is not specified, takes the name of the function being decorated.
                        (имя блокировки, если не задано то принимает имя декорируемой функции).
    :param args:
    :param timeout_limit: the maximum time for blocking a task, after which the lock is lifted automatically.
                        (максимальное время блокировки задачи, после которого блокировка снимается автоматически)
    :param opts:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            if name_of_lock:
                task_name = name_of_lock
            else:
                task_name = func.__name__

            if _is_task_blocked(task_name):
                message = 'There is a task execution lock [timeout_limit: {} сек.] [name_of_lock: {}]'
                message = message.format(timeout_limit, task_name)
                return message
            else:
                if timeout_limit:
                    _block_launch_of_task(task_name, "locked", timeout_limit)
                res = func(*args, **kwargs)
                # time.sleep(5)
                _unblock_launch_of_task(task_name)
                return res
        return wrapper

    if not isinstance(name_of_lock, str):
        print(f'name_of_lock: {name_of_lock}')
        raise TypeError('the name_of_lock variable is not a string type')
    if len(args) == 1:
        if callable(args[0]):
            return decorator(args[0])
            # return decorator(**opts)(*args)
        raise TypeError('argument 1 to @block_task() must be a callable')
    if args:
        raise TypeError(
            '@block_task() takes exactly 1 argument ({} given)'.format(
                sum([len(args), len(opts)])))

    return decorator
