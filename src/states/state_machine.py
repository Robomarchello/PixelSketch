from states.state import State


class StateMachine:
    def __init__(self, screen_manager, initial_state):
        self.screen_manager = screen_manager
        self.state: State = State(self, self.screen_manager) # creating dummy state

        # start the state
        self.change_state(initial_state)

    def update(self):
        self.state.update()
        self.state.draw()

    def change_state(self, new_state):
        self.state.on_exit()
        self.state = new_state(self, self.screen_manager)
        self.state.on_enter()