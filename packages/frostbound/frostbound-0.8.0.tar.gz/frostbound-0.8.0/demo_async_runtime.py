#!/usr/bin/env python3
"""Demo script showcasing the improved async runtime with rich console output."""

import random
import time

from improved_async_runtime import (
    AsyncQueue,
    Event,
    Lock,
    Semaphore,
    TaskGroup,
    ThreadSafeEventLoop,
    TimeoutError,
    console,
    gather,
    sleep,
    wait_for,
)


async def demo_concurrent_tasks():
    """Demonstrate concurrent task execution with visual feedback."""
    if console:
        console.rule("[bold cyan]Concurrent Task Execution[/bold cyan]")

    async def worker(name: str, duration: float, color: str) -> str:
        if console:
            console.print(f"[{color}]🚀 {name} starting (duration: {duration}s)[/{color}]")
        start = time.monotonic()
        await sleep(duration)
        elapsed = time.monotonic() - start
        if console:
            console.print(f"[{color}]✅ {name} completed in {elapsed:.2f}s[/{color}]")
        return f"{name} result"

    # Run multiple tasks concurrently
    results = await gather(
        worker("FastTask", 0.5, "green"),
        worker("MediumTask", 1.0, "yellow"),
        worker("SlowTask", 1.5, "red"),
    )

    if console:
        console.print(f"\n[bold]Results:[/bold] {results}")


async def demo_synchronization():
    """Demonstrate synchronization primitives."""
    if console:
        console.rule("[bold magenta]Synchronization Primitives[/bold magenta]")

    # Shared resources
    counter = 0
    lock = Lock()

    async def critical_section(worker_id: int):
        nonlocal counter
        if console:
            console.print(f"[yellow]Worker-{worker_id} waiting for lock...[/yellow]")

        await lock.acquire()
        try:
            if console:
                console.print(f"[green]Worker-{worker_id} acquired lock![/green]")

            # Simulate critical work
            old_value = counter
            await sleep(0.2)
            counter = old_value + 1

            if console:
                console.print(f"[blue]Worker-{worker_id} updated counter: {old_value} → {counter}[/blue]")
        finally:
            lock.release()
            if console:
                console.print(f"[red]Worker-{worker_id} released lock[/red]")

    # Run workers concurrently
    await gather(*[critical_section(i) for i in range(1, 4)])

    if console:
        console.print(f"\n[bold green]Final counter value: {counter}[/bold green]")


async def demo_rate_limiting():
    """Demonstrate rate limiting with semaphore."""
    if console:
        console.rule("[bold yellow]Rate Limiting with Semaphore[/bold yellow]")

    # Limit to 2 concurrent operations
    semaphore = Semaphore(2)
    active_count = 0

    async def rate_limited_task(task_id: int):
        nonlocal active_count

        if console:
            console.print(f"[dim]Task-{task_id} waiting for permit...[/dim]")

        async with semaphore:
            active_count += 1
            if console:
                console.print(f"[green]Task-{task_id} running (active: {active_count}/2)[/green]")

            # Simulate work
            await sleep(random.uniform(0.5, 1.0))

            active_count -= 1
            if console:
                console.print(f"[red]Task-{task_id} completed (active: {active_count}/2)[/red]")

    # Launch more tasks than the limit
    await gather(*[rate_limited_task(i) for i in range(6)])


async def demo_producer_consumer():
    """Demonstrate producer-consumer pattern with queues."""
    if console:
        console.rule("[bold blue]Producer-Consumer Pattern[/bold blue]")

    queue = AsyncQueue[str](maxsize=3)

    async def producer(name: str, count: int):
        for i in range(count):
            item = f"{name}-Item-{i}"
            if console:
                console.print(f"[cyan]📦 Producer {name} creating: {item}[/cyan]")
            await queue.put(item)
            await sleep(0.3)
        if console:
            console.print(f"[dim]Producer {name} finished[/dim]")

    async def consumer(name: str, count: int):
        consumed = []
        for _ in range(count):
            item = await queue.get()
            consumed.append(item)
            if console:
                console.print(f"[green]🍽️  Consumer {name} consumed: {item}[/green]")
            await sleep(0.5)
        return consumed

    # Run producers and consumers concurrently
    results = await gather(
        producer("P1", 3),
        producer("P2", 3),
        consumer("C1", 3),
        consumer("C2", 3),
    )

    if console:
        console.print(f"\n[bold]Consumer C1: {results[2]}")
        console.print(f"[bold]Consumer C2: {results[3]}")


async def demo_event_coordination():
    """Demonstrate event-based coordination."""
    if console:
        console.rule("[bold green]Event-Based Coordination[/bold green]")

    start_event = Event()

    async def racer(name: str, speed: float):
        if console:
            console.print(f"[yellow]🏃 {name} at starting line...[/yellow]")

        await start_event.wait()

        if console:
            console.print(f"[green]🏃 {name} started running![/green]")

        # Race!
        race_time = 2.0 / speed
        await sleep(race_time)

        if console:
            console.print(f"[bold green]🏁 {name} finished in {race_time:.2f}s![/bold green]")

        return name, race_time

    # Create racers
    racers = [
        racer("Speedy", 1.5),
        racer("Quick", 1.2),
        racer("Swift", 1.3),
    ]

    # Start race after delay
    async def starter():
        if console:
            console.print("[bold red]🚦 Ready...[/bold red]")
        await sleep(1)
        if console:
            console.print("[bold yellow]🚦 Set...[/bold yellow]")
        await sleep(1)
        if console:
            console.print("[bold green]🚦 GO![/bold green]")
        start_event.set()

    # Run race
    results = await gather(starter(), *racers)

    # Show results
    race_results = sorted(results[1:], key=lambda x: x[1] if x else float("inf"))
    if console:
        console.print("\n[bold]🏆 Race Results:[/bold]")
        for i, (name, time) in enumerate(race_results, 1):
            medal = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else "  "
            console.print(f"{medal} {i}. {name} - {time:.2f}s")


async def demo_timeout_handling():
    """Demonstrate timeout handling."""
    if console:
        console.rule("[bold red]Timeout Handling[/bold red]")

    async def slow_operation():
        if console:
            console.print("[yellow]Starting slow operation...[/yellow]")
        await sleep(5)  # This will timeout
        return "This won't be reached"

    try:
        if console:
            console.print("[dim]Attempting operation with 2s timeout...[/dim]")
        result = await wait_for(slow_operation(), timeout=2.0)
        if console:
            console.print(f"[green]Result: {result}[/green]")
    except TimeoutError:
        if console:
            console.print("[red]⏱️  Operation timed out after 2 seconds![/red]")


async def demo_structured_concurrency():
    """Demonstrate structured concurrency with TaskGroup."""
    if console:
        console.rule("[bold purple]Structured Concurrency with TaskGroup[/bold purple]")

    async def background_task(name: str, interval: float):
        count = 0
        while True:
            count += 1
            if console:
                console.print(f"[dim]{name} heartbeat #{count}[/dim]")
            await sleep(interval)

    async def main_work():
        if console:
            console.print("[green]Starting main work...[/green]")

        async with TaskGroup() as tg:
            # Start background tasks
            tg.create_task(background_task("Monitor", 0.5), name="Monitor")
            tg.create_task(background_task("Logger", 0.7), name="Logger")

            # Do main work
            if console:
                console.print("[yellow]Performing main operations...[/yellow]")
            await sleep(2)

            if console:
                console.print("[green]Main work completed![/green]")

        # All background tasks are automatically cancelled here
        if console:
            console.print("[red]All background tasks stopped[/red]")

    await main_work()


async def main():
    """Run all demos."""
    if console:
        console.print("\n[bold]🚀 Enhanced Async Runtime Demo[/bold]\n")

    demos = [
        ("Concurrent Tasks", demo_concurrent_tasks),
        ("Synchronization", demo_synchronization),
        ("Rate Limiting", demo_rate_limiting),
        ("Producer-Consumer", demo_producer_consumer),
        ("Event Coordination", demo_event_coordination),
        ("Timeout Handling", demo_timeout_handling),
        ("Structured Concurrency", demo_structured_concurrency),
    ]

    for name, demo_func in demos:
        try:
            await demo_func()
            if console:
                console.print("\n")
        except Exception as e:
            if console:
                console.print(f"[red]Error in {name}: {e}[/red]")

    if console:
        console.print("[bold green]✨ All demos completed![/bold green]")


if __name__ == "__main__":
    # Create event loop with debugging enabled
    loop = ThreadSafeEventLoop(debug=True)

    # Run the demos
    loop.run_until_complete(main())
