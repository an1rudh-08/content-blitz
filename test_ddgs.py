try:
    import duckduckgo_search
    print("Successfully imported duckduckgo_search")
    print(f"Version: {duckduckgo_search.__version__}")
    from duckduckgo_search import DDGS
    print("Successfully imported DDGS from duckduckgo_search")
except ImportError as e:
    print(f"Failed to import duckduckgo_search: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
