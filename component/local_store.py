import json
from pathlib import Path
from typing import Any
import streamlit as st

class LocalStorageManager:
    def __init__(self, user_name: str, storage_dir: str = "user_storage"):
        self.user_name = user_name
        self.storage_dir = Path(storage_dir)
        self.storage_file = self.storage_dir / f"{self.user_name}.json"
        self.load_storage()

    def load_storage(self) -> None:
        """Loads storage from the user-specific JSON file."""
        if self.storage_file.exists():
            with open(self.storage_file, 'r') as f:
                st.session_state['local_storage'] = json.load(f)
        else:
            st.session_state['local_storage'] = {}

    def save_storage(self) -> None:
        """Saves storage to the user-specific JSON file."""
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(st.session_state['local_storage'], f)

    def set_item(self, key: str, value: Any) -> None:
        """Sets a value in local storage and persists it."""
        st.session_state['local_storage'][key] = value
        self.save_storage()

    def get_item(self, key: str) -> Any:
        """Gets a value from local storage."""
        return st.session_state['local_storage'].get(key, None)
