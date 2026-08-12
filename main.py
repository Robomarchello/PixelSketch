import sys

if __name__ == '__main__':
    try:
        from src.app import App, run_with_error_screen
        run_with_error_screen(App().loop)
    except Exception as e:
        with open('error.log', 'a') as f:
            f.write('\n--- Unhandled Exception ---\n')
            sys.print_exception(e, f)
        raise