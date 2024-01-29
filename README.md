# Celery Task
```
@app.task
@block_task(timeout_limit=180)
def task_example():
    result = example_function()
    return result
```