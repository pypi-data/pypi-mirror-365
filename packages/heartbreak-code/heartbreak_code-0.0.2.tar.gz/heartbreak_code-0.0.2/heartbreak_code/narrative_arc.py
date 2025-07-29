

class NarrativeArc:
    def __init__(self, initial_state=None):
        self._state = initial_state if initial_state is not None else {}
        self._subscribers = []
        print("Narrative Arc initialized with initial state.")

    def get_state(self):
        """Returns the current state of the application."""
        return self._state

    def dispatch(self, plot_point, payload=None):
        """Dispatches a 'Plot Point' (action) to update the state."""
        print(f"Dispatching Plot Point: {plot_point} with payload: {payload}")
        new_state = self._reduce(self._state, plot_point, payload)
        if new_state != self._state:
            self._state = new_state
            self._notify_subscribers()
        return self._state

    def _reduce(self, state, plot_point, payload):
        """Internal reducer function to handle state transitions."
        # This is where the core logic for state changes resides.
        # Developers would extend this method or provide their own reducer logic.
        # For demonstration, we'll handle a simple 'UPDATE_VALUE' plot point.
        if plot_point == 'UPDATE_VALUE':
            key = payload.get('key')
            value = payload.get('value')
            if key:
                return {**state, key: value}
        elif plot_point == 'ADD_ITEM':
            item = payload.get('item')
            if item:
                current_list = state.get('items', [])
                return {**state, 'items': current_list + [item]}
        elif plot_point == 'REMOVE_ITEM':
            item_to_remove = payload.get('item')
            if item_to_remove:
                current_list = state.get('items', [])
                return {**state, 'items': [item for item in current_list if item != item_to_remove]}
        # Default: return current state if plot_point is not recognized
        return state

    def subscribe(self, callback):
        """Subscribes a callback function to state changes."""
        self._subscribers.append(callback)
        print("New subscriber added.")
        # Immediately notify new subscriber with current state
        callback(self._state)
        return lambda: self._subscribers.remove(callback) # Return unsubscribe function

    def _notify_subscribers(self):
        """Notifies all subscribed callbacks about state changes."""
        print("Notifying subscribers of state change.")
        for callback in self._subscribers:
            callback(self._state)

if __name__ == "__main__":
    # Example Usage (for testing purposes)
    # This block will only run if narrative_arc.py is executed directly

    def render_ui(state):
        print(f"\n--- UI Rendered with State: {state} ---")

    # Initialize Narrative Arc
    initial_app_state = {"user": "Guest", "theme": "light", "items": []}
    narrative_arc = NarrativeArc(initial_app_state)

    # Subscribe UI component to state changes
    unsubscribe = narrative_arc.subscribe(render_ui)

    # Dispatch Plot Points to change state
    print("\n--- Dispatching UPDATE_VALUE (user) ---")
    narrative_arc.dispatch('UPDATE_VALUE', {'key': 'user', 'value': 'Taylor Swift'})

    print("\n--- Dispatching UPDATE_VALUE (theme) ---")
    narrative_arc.dispatch('UPDATE_VALUE', {'key': 'theme', 'value': 'dark'})

    print("\n--- Dispatching ADD_ITEM ---")
    narrative_arc.dispatch('ADD_ITEM', {'item': 'Love Story'})
    narrative_arc.dispatch('ADD_ITEM', {'item': 'Blank Space'})

    print("\n--- Dispatching REMOVE_ITEM ---")
    narrative_arc.dispatch('REMOVE_ITEM', {'item': 'Love Story'})

    print("\n--- Current State ---")
    print(narrative_arc.get_state())

    # Unsubscribe a component (optional)
    unsubscribe()
    print("\n--- Dispatching another UPDATE_VALUE (should not notify unsubscribed) ---")
    narrative_arc.dispatch('UPDATE_VALUE', {'key': 'status', 'value': 'logged_in'})


