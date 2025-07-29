import random
import itertools
from tabulate import tabulate
from pprint import pprint


# import gymnasium as gym
import gymnasium
import gym_walk, gym_aima

import numpy as np

def print_policy(pi, P, action_symbols=('<', '>'), n_cols=4, title='Policy:', terminal_marker='■'):
    arrs = {k: v for k, v in enumerate(action_symbols)}

    n_states = len(P)
    cell_width = 9
    n_rows = int(np.ceil(n_states / n_cols))

    # Borders
    top_border = "╔" + ("═" * cell_width + "╦") * (n_cols - 1) + "═" * cell_width + "╗"
    row_sep =    "╠" + ("═" * cell_width + "╬") * (n_cols - 1) + "═" * cell_width + "╣"
    bottom_border = "╚" + ("═" * cell_width + "╩") * (n_cols - 1) + "═" * cell_width + "╝"

    print(title)
    print(top_border)
    for row in range(n_rows):
        print("║", end="")
        for col in range(n_cols):
            s = row * n_cols + col
            if s >= n_states:
                print(" " * cell_width + "║", end="")
                continue

            is_terminal = np.all([done for action in P[s].values() for _, _, _, done in action])
            symbol = terminal_marker if is_terminal else arrs[pi(s)]

            state_str = str(s).zfill(2)
            padding = cell_width - len(state_str) - len(symbol) - 2
            cell = f" {state_str}{' ' * padding}{symbol} "
            print(cell + "║", end="")
        print()
        if row < n_rows - 1:
            print(row_sep)
    print(bottom_border)


def print_action_value_function(Q,
                                optimal_Q=None,
                                action_symbols=('<', '>'),
                                prec=3,
                                title='Action-value function:'):
    vf_types=('',) if optimal_Q is None else ('', '*', 'err')
    headers = ['s',] + [' '.join(i) for i in list(itertools.product(vf_types, action_symbols))]
    print(title)
    states = np.arange(len(Q))[..., np.newaxis]
    arr = np.hstack((states, np.round(Q, prec)))
    if not (optimal_Q is None):
        arr = np.hstack((arr, np.round(optimal_Q, prec), np.round(optimal_Q-Q, prec)))
    print(tabulate(arr, headers, tablefmt="fancy_grid"))


def probability_success(env, pi, goal_state, n_episodes=100, max_steps=200):
    random.seed(123); np.random.seed(123) #; env.seed(123)
    results = []
    for _ in range(n_episodes):
        state, info = env.reset(seed=123)
        done = False
        steps = 0
        while not done and steps < max_steps:
            # state, _, done, h, _ = env.step(pi(state[0]))
            state, reward, terminated, truncated, info = env.step(pi(state))
            done = terminated or truncated
            steps += 1
        results.append(state == goal_state)
    return np.sum(results)/len(results)


def mean_return(env, pi, n_episodes=100, max_steps=200):
    random.seed(123); np.random.seed(123)
    results = []
    for _ in range(n_episodes):
        state, info = env.reset(seed=123)
        done = False
        steps = 0
        results.append(0.0)
        while not done and steps < max_steps:
            # state, reward, done, _ = env.step(pi(state))
            state, reward, done, truncated, info = env.step(pi(state))
            results[-1] += reward
            steps += 1
    return np.mean(results)


if __name__ == "__main__":
    # Dummy transition model: P[s][a] = list of (prob, next_state, reward, done)
    # For simplicity, we assume
    # - 6 states and
    # - 2 actions (0: left, 1: right)

    env = gymnasium.make('SlipperyWalkFive-v0')
    P_env = env.unwrapped.P
    P = {}
    action_space = env.action_space
    for st in range(5):
        P[st] = {}
        next_state = st
        for act in range(action_space.n):
            P[st][act] = [(1.0, st, 0, False)]
            next_state = next_state + 1
    P[5] = {a: [(1.0, 5, 1, True)] for a in range(2)}


    def biased_policy(prob_action_0=0.5):
        def pi(s):
            return 0 if random.random() < prob_action_0 else 1
        return pi

    pi = biased_policy(0.5)

    Q = np.array([
        [0.2, 0.5],  # state 0
        [0.8, 0.4],  # state 1
        [0.1, 0.9],  # state 2
    ]) # (=) 3 state rows x 2 action columns

    optimal_Q = np.array([
        [0.3, 0.6],
        [0.7, 0.5],
        [0.2, 1.0],
    ])

    print_policy(pi, P, n_cols=6, title="Test Policy:")

    print_action_value_function(Q, optimal_Q)

    # p_success and E[return]
    print(f"probability_success: {probability_success(env, pi, 6)}")
    print(f"mean_return: {mean_return(env, pi)}")
