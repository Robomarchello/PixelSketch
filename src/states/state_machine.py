from states.state import State


class StateMachine:
    def __init__(self, initial_state):
        self.state: State = State(self) # creating dummy state

        # start the state
        self.change_state(initial_state)

    def update(self):
        self.state.logic()

    def change_state(self, new_state_instance):
        self.state.on_exit()
        self.state = new_state_instance
        self.state.on_enter()