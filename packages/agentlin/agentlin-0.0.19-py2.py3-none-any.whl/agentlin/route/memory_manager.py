class MemoryManager:
    """
    MemoryManager is responsible for managing the memory of the agent.
    It provides methods to store, retrieve, and delete memory entries.
    """

    def __init__(self):
        self.memory = {}

    def store_memory(self, key: str, value: str):
        """Store a memory entry."""
        self.memory[key] = value

    def retrieve_memory(self, key: str) -> str:
        """Retrieve a memory entry."""
        return self.memory.get(key, "")

    def delete_memory(self, key: str):
        """Delete a memory entry."""
        if key in self.memory:
            del self.memory[key]

            