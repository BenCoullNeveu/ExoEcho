import time
import threading
from IPython.display import clear_output, display, update_display

# Define frames for the coffee cup with animated steam.
frames = [
    f"""
     ( )
     ) (
    (   )
   .-====-.__
   |      |  | 
   \      |__|
    `----'
    """,
    f"""
     ) (
    (   )
    )   (
   .-====-.__
   |      |  | 
   \      |__|
    `----'
    """,
    f"""
    (   )
    (   )
     ) (
   .-====-.__
   |      |  | 
   \      |__|
    `----'
    """,
    f"""
    )   (
     ) (
     ( )
   .-====-.__
   |      |  | 
   \      |__|
    `----'
    """
]


def coffee_animation(stop_event, frame_delay=0.3):
    """
    Continuously updates the same display area with the coffee cup animation.
    Uses a longer delay between frames to reduce CPU usage.
    """
    # Create an initial display handle that we can update.
    display_handle = display("", display_id=True)
    
    while not stop_event.is_set():
        for frame in frames:
            if stop_event.is_set():
                break
            update_display(frame, display_id=display_handle.display_id)
            time.sleep(frame_delay)
    
    # Optionally clear the display once animation is finished.
    clear_output(wait=True)

def animated_coffee(func):
    """
    A decorator that shows a coffee cup animation in a Jupyter Notebook
    while the decorated function runs.
    """
    def wrapper(*args, **kwargs):
        stop_event = threading.Event()
        anim_thread = threading.Thread(target=coffee_animation, args=(stop_event,))
        anim_thread.start()
        try:
            result = func(*args, **kwargs)
        finally:
            # Stop the animation and clear the output once the function is done.
            stop_event.set()
            anim_thread.join()
            clear_output(wait=True)
        return result
    return wrapper

# Example usage:
# @animated_coffee
# def long_running_task():
#     # Simulate a long-running task
#     time.sleep(5)
#     return "Task Complete!"