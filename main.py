from src.app import App, run_with_error_screen

if __name__ == '__main__':
    run_with_error_screen(App().loop)