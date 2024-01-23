
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 100
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    # Check if the current node is a terminal node
    if(board.is_ended(state)):
        return node, state
    
    # Check if the current node is a leaf node
    # print(len(node.child_nodes))
    if(len(node.untried_actions) != 0):
        return node, state
    
    # Find the child with the highest UCT score
    # print("Got past end conds (Traversal)")
    max_node = None
    max_score = 0
    for action, child in node.child_nodes.items():
        # Calculate child UCT score
        # Do you use current's state or child's state?
        UCT_score = ucb(child, board.current_player(state) != bot_identity)
        # print(UCT_score)

        # Set the child if it has a higher UCT score
        if UCT_score > max_score:
            max_node = child
            max_state = board.next_state(state, action)
            max_score = UCT_score
    
    # Take the node and action and recursively continue
    # print(max_score)
    return traverse_nodes(max_node, board, max_state, board.current_player(max_state))

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    # Check if current node is a terminal node
    if(board.is_ended(state)):
        return node, state
    
    # Define the action that is to be taken from parent -> child (randomly?)
    # Use the list of legal actions or the list of untried actions???
    action_taken = choice(node.untried_actions)

    # Make the new child node
    child_state = board.next_state(state, action_taken)
    child = MCTSNode(parent=node, parent_action=action_taken, action_list=board.legal_actions(child_state))

    # Update the parent's info
    node.child_nodes[action_taken] = child
    node.untried_actions.remove(action_taken)

    return child, child_state

def rollout(board: Board, state):
    """ Given the state of the game, the rollout plays out the remainder randomly.

    Args:
        board:  The game setup.
        state:  The state of the game.
    
    Returns:
        state: The terminal game state

    """
    # Recursively call rollout() with a random action until game end
    if(not board.is_ended(state)):
        final_state = rollout(board, board.next_state(state, choice(board.legal_actions(state))))
    else:
        final_state = state
    
    return final_state

def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # Check if node is root
    if(node.parent is None):
        node.visits += 1
        return
    
    # Update the node's statistics otherwise
    node.visits += 1
    if(won):
        node.wins += 1
    
    # Recursively backpropagate up the tree
    backpropagate(node.parent, won)
    return

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    # Calculate the child's win rate
    exploit = node.wins / node.visits

    # If opponent, calculate the opponent's win rate
    if(is_opponent):
        exploit = 1 - exploit

    # Calculate the inside of the root
    if(node.parent.visits == 0):
        explore = 0
    else:
        explore = log(node.parent.visits) / node.visits

    # Combine the exploitation and exploration calculations
    ucb = exploit + (explore_faction * sqrt(explore))

    return ucb

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    # Find the child with the most wins
    best_action = None
    best_score = 0

    for action, child in root_node.child_nodes.items():
        if(child.wins > best_score):
            best_score = child.wins
            best_action = action

    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!
        # print("Traversing the tree...")
        node, state = traverse_nodes(node, board, state, board.current_player(state))
        # print("Expanding a leaf...")
        node, state = expand_leaf(node, board, state)
        # print("Rollout + Backpropagation...")
        backpropagate(node, is_win(board, rollout(board, state), board.current_player(state)))

        # print("Do it all again...")

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    
    print(f"Action chosen: {best_action}")
    return best_action
