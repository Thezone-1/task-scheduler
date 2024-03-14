## Behaviour Driven Development

1. A thread needs to run.
2. Sleep for certain amount of time depending on time delta (first and second task).
3. Whenever a new task comes
    - **Execution time before current system time**
        - drop that request.
    - **Execution time at current system time**
        - execute instantaneously.
    - **Execution time in between current time and next scheduled task time**
        - put the new request in front of the queue and recalculate sleeping time.
    - **Execution time after next scheduled task time**
        - put the new request in the appropriate position in the database.
